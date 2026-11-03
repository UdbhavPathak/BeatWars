# """
# Song BPM detector
# Install: python -m pip install librosa soundfile
# Run: python bpm_finder.py "path/to/song.mp3"
# """
#
# import argparse
# import sys
# from pathlib import Path
#
#
# def detect_bpm(audio_path: Path, min_bpm: float, max_bpm: float) -> None:
#     try:
#         import librosa
#         import numpy as np
#     except ImportError:
#         print("Missing dependency. Install with: python -m pip install librosa soundfile")
#         raise SystemExit(1)
#
#     if not audio_path.is_file():
#         print(f"File not found: {audio_path}")
#         raise SystemExit(1)
#
#     print(f"Analyzing: {audio_path.name} ...")
#     try:
#         # Mono, 22.05 kHz audio is usually sufficient for tempo analysis.
#         y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
#         if y.size == 0:
#             print("The audio file appears to be empty.")
#             raise SystemExit(1)
#
#         onset_env = librosa.onset.onset_strength(y=y, sr=sr)
#         tempo, beat_frames = librosa.beat.beat_track(
#             onset_envelope=onset_env, sr=sr, start_bpm=120.0
#         )
#         bpm = float(np.asarray(tempo).reshape(-1)[0])
#
#         print(f"\nEstimated BPM: {bpm:.1f}")
#
#
#         beat_times = librosa.frames_to_time(beat_frames, sr=sr)
#         if len(beat_times) >= 2:
#             median_interval = float(np.median(np.diff(beat_times)))
#             if median_interval > 0:
#                 print(f"Median-interval BPM: {60.0 / median_interval:.1f}")
#
#         if not min_bpm <= bpm <= max_bpm:
#             print(f"Note: estimate is outside your expected range ({min_bpm:g}–{max_bpm:g} BPM).")
#         print("Tip: some songs may be interpreted at half-time or double-time (e.g. 80 vs 160 BPM).")
#     except SystemExit:
#         raise
#     except Exception as exc:
#         print(f"Could not analyze this audio file: {exc}")
#         print("Try an MP3, WAV, FLAC, or OGG file.")
#         raise SystemExit(1)
#
#
# def main(path) -> None:
#     parser = argparse.ArgumentParser(description="Estimate a song's beats per minute (BPM).")
#     parser.add_argument("audio", nargs="?", help="Path to an audio file")
#     parser.add_argument("--min-bpm", type=float, default=50, help="Expected minimum BPM (default: 50)")
#     parser.add_argument("--max-bpm", type=float, default=220, help="Expected maximum BPM (default: 220)")
#     args = parser.parse_args()
#
#     if args.min_bpm <= 0 or args.max_bpm <= args.min_bpm:
#         parser.error("BPM range must be positive and max must be greater than min.")
#
#     if args.audio:
#         audio_path = Path(args.audio).expanduser()
#     else:
#         audio_path = Path(path.strip().strip('"')).expanduser()
#
#     detect_bpm(audio_path, args.min_bpm, args.max_bpm)
#
#
# if __name__ == "__main__":
#     main("sounds/sample.mp3")

import librosa
import numpy as np

def get_bpm(song_path):
    y, sr = librosa.load(song_path, sr=22050, mono=True)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    tempo = librosa.feature.tempo(
        onset_envelope=onset_env,
        sr=sr
    )

    return float(np.asarray(tempo).reshape(-1)[0])
