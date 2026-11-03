"""Offline music analysis for rhythm-game chart generation.

Vocal activity is a signal-feature estimate, not a trained speech/singer detector.
It is useful as a gameplay cue, but may confuse sustained synths or guitars with vocals.
"""

from __future__ import annotations

import librosa
import numpy as np


_DEFAULT_SR = 22_050
_HOP_LENGTH = 512
_N_FFT = 2_048


def _window_sums(times: np.ndarray, values: np.ndarray, starts: np.ndarray, duration: float) -> np.ndarray:
    """Sum frame/event values in [start, start + duration) using sorted timestamps."""
    if times.size == 0:
        return np.zeros(starts.size, dtype=float)
    cumulative = np.concatenate(([0.0], np.cumsum(values, dtype=float)))
    left = np.searchsorted(times, starts, side="left")
    right = np.searchsorted(times, starts + duration, side="left")
    return cumulative[right] - cumulative[left]


def _merge_windows(windows: list[dict], *, include_count: bool = False) -> list[dict]:
    """Merge overlapping windows into continuous sections."""
    if not windows:
        return []
    merged = []
    for window in windows:
        if merged and window["start"] <= merged[-1]["end"] + 0.01:
            merged[-1]["end"] = max(merged[-1]["end"], window["end"])
            if include_count:
                merged[-1]["peak_onset_count"] = max(
                    merged[-1]["peak_onset_count"], window["onset_count"]
                )
        else:
            item = {"start": window["start"], "end": window["end"]}
            if include_count:
                item["peak_onset_count"] = window["onset_count"]
            merged.append(item)
    return merged


def _vocal_activity_features(
    spectrum: np.ndarray, rms: np.ndarray, sr: int
) -> np.ndarray:
    """Estimate voice-like activity from harmonicity and vocal-band spectral energy.

    This deliberately avoids a large external model. It is a heuristic: instruments
    with sustained harmonics can score as vocal-like, so callers should treat it as
    a gameplay intensity cue rather than definitive source separation.
    """
    power = spectrum**2
    freqs = librosa.fft_frequencies(sr=sr, n_fft=_N_FFT)[:, None]
    total_power = np.sum(power, axis=0) + 1e-12
    voice_band_power = np.sum(power[(freqs[:, 0] >= 250) & (freqs[:, 0] <= 4_000)], axis=0)
    voice_band_share = voice_band_power / total_power

    # Low spectral flatness favors voiced/harmonic sounds. The band share suppresses
    # bass-only content, while normalized RMS prevents near-silence from scoring.
    flatness = librosa.feature.spectral_flatness(S=spectrum, power=2.0)[0]
    harmonicity = np.clip(1.0 - flatness, 0.0, 1.0)
    rms_scale = np.percentile(rms, 95) if rms.size else 0.0
    loudness = np.clip(rms / max(rms_scale, 1e-8), 0.0, 1.0)
    return np.clip(harmonicity * np.sqrt(np.clip(voice_band_share, 0.0, 1.0)) * loudness, 0.0, 1.0)


def analyze_rhythm_track(
    audio_path: str,
    window_duration: float = 2.0,
    window_step: float = 1.0,
    buildup_window: float = 2.0,
) -> dict:
    """Analyze a song for rhythm-game beats, activity, buildups, and vocal-like cues.

    Args:
        audio_path: Path to an audio file supported by librosa.
        window_duration: Window size in seconds for fast-paced detection.
        window_step: Step in seconds between fast-paced analysis windows.
        buildup_window: Length of each of the three blocks used for buildup checks.

    Returns:
        A JSON-friendly dictionary of timestamps and section ranges.
    """
    if window_duration <= 0 or window_step <= 0 or buildup_window <= 0:
        raise ValueError("window durations and steps must be greater than zero")

    # Resampling to a fixed rate makes the analysis cost predictable across files.
    y, sr = librosa.load(audio_path, sr=_DEFAULT_SR, mono=True)
    song_duration = float(librosa.get_duration(y=y, sr=sr))
    if y.size == 0:
        raise ValueError(f"Audio file contains no samples: {audio_path}")

    # Reuse one STFT for onset, RMS, and spectral features instead of recomputing it.
    spectrum = np.abs(librosa.stft(y, n_fft=_N_FFT, hop_length=_HOP_LENGTH))
    onset_env = librosa.onset.onset_strength(
        S=librosa.amplitude_to_db(spectrum, ref=np.max),
        sr=sr,
        hop_length=_HOP_LENGTH,
    )
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, hop_length=_HOP_LENGTH
    )
    tempo_value = float(np.asarray(tempo).reshape(-1)[0]) if np.size(tempo) else 0.0
    beat_times = librosa.frames_to_time(
        beat_frames, sr=sr, hop_length=_HOP_LENGTH
    ).tolist()

    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=_HOP_LENGTH,
        backtrack=True,
    )
    onset_times = librosa.frames_to_time(
        onset_frames, sr=sr, hop_length=_HOP_LENGTH
    )

    rms = librosa.feature.rms(S=spectrum, frame_length=_N_FFT)[0]
    frame_times = librosa.frames_to_time(
        np.arange(rms.size), sr=sr, hop_length=_HOP_LENGTH
    )
    vocal_score = _vocal_activity_features(spectrum, rms, sr)

    # Sliding-window event counts use binary searches rather than rescanning every onset.
    if song_duration > 0:
        starts = np.arange(0.0, song_duration, window_step)
    else:
        starts = np.array([], dtype=float)
    onset_counts = _window_sums(
        onset_times, np.ones(onset_times.size), starts, window_duration
    ).astype(int)
    density_threshold = max(float(np.percentile(onset_counts, 75)) if onset_counts.size else 0.0, 6.0)
    fast_windows = [
        {"start": round(float(start), 2),
         "end": round(float(min(start + window_duration, song_duration)), 2),
         "onset_count": int(count)}
        for start, count in zip(starts, onset_counts)
        if count >= density_threshold
    ]
    fast_paced_sections = _merge_windows(fast_windows, include_count=True)

    # Prefix sums make block means/counts cheap for the buildup scan.
    energy_prefix = np.concatenate(([0.0], np.cumsum(rms, dtype=float)))

    def mean_in_range(values: np.ndarray, prefix: np.ndarray, start: float, end: float) -> float:
        left = int(np.searchsorted(frame_times, start, side="left"))
        right = int(np.searchsorted(frame_times, end, side="left"))
        return float((prefix[right] - prefix[left]) / (right - left)) if right > left else 0.0

    def onset_count(start: float, end: float) -> int:
        return int(np.searchsorted(onset_times, end, side="left") - np.searchsorted(onset_times, start, side="left"))

    def scan_buildups(
        activity: np.ndarray,
        *,
        min_final: float,
        min_increase: float,
        active_mask: np.ndarray | None = None,
        min_final_active_ratio: float = 0.0,
    ) -> list[dict]:
        activity_prefix = np.concatenate(([0.0], np.cumsum(activity, dtype=float)))
        sections = []
        step = min(1.0, buildup_window / 2.0)
        start = 0.0
        span = buildup_window * 3.0
        while start + span <= song_duration:
            points = (start, start + buildup_window, start + 2 * buildup_window, start + span)
            means = [mean_in_range(activity, activity_prefix, points[i], points[i + 1]) for i in range(3)]
            final_active_ratio = 1.0
            if active_mask is not None:
                left = int(np.searchsorted(frame_times, points[2], side="left"))
                right = int(np.searchsorted(frame_times, points[3], side="left"))
                final_active_ratio = float(np.mean(active_mask[left:right])) if right > left else 0.0
            if (means[1] >= means[0] and means[2] >= means[1]
                    and means[2] >= min_final
                    and means[2] - means[0] >= min_increase
                    and final_active_ratio >= min_final_active_ratio):
                sections.append({"start": round(start, 2), "end": round(points[-1], 2)})
                start += span
            else:
                start += step
        return _merge_windows(sections)

    buildups = []
    # Keep the original joint density + loudness cue, with tolerant non-decreasing trends.
    start = 0.0
    span = buildup_window * 3.0
    step = min(1.0, buildup_window / 2.0)
    while start + span <= song_duration:
        bounds = (start, start + buildup_window, start + 2 * buildup_window, start + span)
        counts = [onset_count(bounds[i], bounds[i + 1]) for i in range(3)]
        energies = [mean_in_range(rms, energy_prefix, bounds[i], bounds[i + 1]) for i in range(3)]
        if (counts[1] >= counts[0] and counts[2] >= counts[1] and counts[2] >= 5
                and energies[1] >= energies[0] and energies[2] >= energies[1]):
            buildups.append({"start": round(start, 2), "end": round(bounds[-1], 2)})
            start += span
        else:
            start += step
    buildups = _merge_windows(buildups)

    # Smooth and use a stricter adaptive threshold so ordinary harmonics are less
    # likely to become isolated "vocal" hits. Merge short gaps between syllables.
    smooth_frames = max(1, int(round(0.5 * sr / _HOP_LENGTH)))
    smoothed_score = np.convolve(vocal_score, np.ones(smooth_frames) / smooth_frames, mode="same")
    vocal_threshold = max(0.40, float(np.percentile(smoothed_score, 85))) if smoothed_score.size else 1.0
    vocal_mask = smoothed_score >= vocal_threshold
    raw_vocal_windows = []
    if vocal_mask.size:
        changes = np.diff(np.r_[False, vocal_mask, False].astype(np.int8))
        for left, right in zip(np.where(changes == 1)[0], np.where(changes == -1)[0]):
            if right - left >= int(0.6 * sr / _HOP_LENGTH):
                raw_vocal_windows.append({
                    "start": round(float(frame_times[left]), 2),
                    "end": round(float(min(frame_times[min(right, frame_times.size - 1)], song_duration)), 2),
                    "mean_score": round(float(np.mean(smoothed_score[left:right])), 3),
                })

    vocal_windows = []
    for window in raw_vocal_windows:
        if vocal_windows and window["start"] <= vocal_windows[-1]["end"] + 0.35:
            previous = vocal_windows[-1]
            previous_duration = previous["end"] - previous["start"]
            window_duration = window["end"] - window["start"]
            total_duration = previous_duration + window_duration
            previous["mean_score"] = round(
                (previous["mean_score"] * previous_duration + window["mean_score"] * window_duration)
                / max(total_duration, 1e-8),
                3,
            )
            previous["end"] = window["end"]
        else:
            vocal_windows.append(dict(window))

    # Vocal buildups require a rising voice-like score across three blocks.
    vocal_buildups = scan_buildups(
        smoothed_score,
        min_final=max(vocal_threshold, 0.35),
        min_increase=0.10,
        active_mask=vocal_mask,
        min_final_active_ratio=0.30,
    )

    return {
        "metadata": {
            "duration": round(song_duration, 2),
            "tempo": round(tempo_value, 2),
            "sample_rate": sr,
            "vocal_detection": "heuristic voice-like spectral activity; may include sustained instruments",
        },
        "beats": [round(float(t), 4) for t in beat_times],
        "individual_onsets": [round(float(t), 4) for t in onset_times],
        "fast_paced_sections": fast_paced_sections,
        "buildups": buildups,
        "intense_vocal_sections": vocal_windows,
        "vocal_buildups": vocal_buildups,
    }


if __name__ == "__main__":
    for key, items in analyze_rhythm_track("sounds/sample.mp3").items():
        print(f"{key}: {items}")
