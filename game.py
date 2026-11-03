import pygame
import math
import random
import bpm_finder
import animation
import sprite
from pygame.locals import *
import test_algo
pygame.init()
pygame.mixer.init()

class Camera:
    def __init__(self,size):
        self.size = size
        self.half_size = [self.size[0]//2,self.size[1]//2]
        self.scale = 1
        self.offset = pygame.math.Vector2()

    def targetcenter(self,center):
        self.offset.x = self.scale*center[0]-self.half_size[0]*self.scale
        self.offset.y = self.scale*center[1]-self.half_size[1]*self.scale


class Game:
    def __init__(self):
        self.size = (1280,720)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Space Wars 2")
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.window = pygame.Surface((self.size[0]*3,self.size[1]*3)).convert_alpha()
        self.wincenter = ((self.size[0]*3)//2,(self.size[1]*3)//2)

        # print(self.window.get_size())
        self.player = sprite.Player(self.wincenter,self.window.get_size())
        self.player.rect.center = self.wincenter
        self.stars = animation.Stars(self.window.get_size())
        self.reference_point = [0,0]
        self.camera = Camera(self.size)
        self.camera.scale = 1

        pygame.mixer.set_num_channels(30)
        pygame.mixer.music.load("sounds/sample.mp3")
        self.bpm = int(bpm_finder.get_bpm("sounds/sample.mp3"))
        print(self.bpm)
        self.shaders = pygame.Surface(self.size, flags=pygame.SRCALPHA).convert_alpha()
        self.shaders.fill((25,112,112,50))
        # self.beat_interval = 60/self.bpm
        self.song_data = test_algo.analyze_rhythm_track("sounds/sample.mp3")
        '''Effects ->'''
        self.sparks = []
        self.asteroid_spark = animation.Sparks((152, 182, 183),(2,8),limit=15,bd= [False,0])
        # self.asteroid_spark.limit = 15
        # self.beat_index = 0  # Track which beat we are looking for next
        '''Trackers ->'''
        self.beats_data = [0,len(self.song_data["individual_onsets"])] #index , len
        self.fast_pace_data = [0,len(self.song_data["fast_paced_sections"])]
        self.build_ups_data = [0,len(self.song_data["buildups"])]
        self.song_duration = self.song_data["metadata"]['duration']

        self.sounds = {
            'rock':pygame.mixer.Sound('sounds/rockbreak.mp3'),
        }


        # self.circles = []
        # self.spawn_timer = 0
        self.circles = []
        self.asteroids = []
        self.asteroids_group = pygame.sprite.Group()


        # self.song_data= test_algo.analyze_rhythm_track("sounds/sample.mp3")
        # self.beats_tracker = [0,len(self.song_data["beats"])]
        # self.beat_interval = self.song_data["beats"][self.beats_tracker[0]]
        self.e = sprite.Enemy([100,200],0,self.player,self.window.get_size())
        self.e.follow_target()

        self.r = 50
        pygame.mixer.music.play(-1)
        self.music_start_ticks = pygame.time.get_ticks()

        # pygame.mixer.music.play(-1)

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.isMoving[0] = True
                    # if self.player.thrust < 0:
                    #     self.player.thrust *= -1
                if event.key == pygame.K_DOWN:
                    self.player.isMoving[1] = True
                    # if self.player.thrust > 0:
                    #     self.player.thrust *= -1


            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.player.isMoving[0] = False
                if event.key == pygame.K_DOWN:
                    self.player.isMoving[1] = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.angle -= self.player.angularVel
        if keys[pygame.K_RIGHT]:
            self.player.angle += self.player.angularVel
        if keys[pygame.K_SPACE]:
            self.player.fire()
            # self.player.all_direction_bullet(360//10)
        # if keys[pygame.K_1]:
        #
        #     if not self.player.max_vel > 10: self.player.max_vel += 5
        # else:
        #     self.player.max_vel = 5
        # if pygame.key.get_pressed()[pygame.K_LEFT]:
        #     self.player.angle -= self.player.angularVel
        # if pygame.key.get_pressed()[pygame.K_RIGHT]:
        #     self.player.angle += self.player.angularVel

        if len(self.stars.stars) < 3 * self.stars.maxstars:
            self.stars.addstar()
            self.stars.addstar()
            self.stars.addstar()



        # if self.spawn_timer >= self.beat_interval:
        #     self.circles.append([*self.player.rect.center])
        #     if self.beats_tracker[0] >= self.beats_tracker[1]:
        #         self.beats_tracker[0] = 0
        #         self.spawn_timer = 0
        #     self.beats_tracker[0] += 1
        #     self.beat_interval = self.song_data["beats"][self.beats_tracker[0]]
        #     print(self.beat_interval)
        # Calculate exact elapsed song time in seconds
        current_song_time = (pygame.time.get_ticks() - self.music_start_ticks) / 1000.0
        '''beats'''
        beats = self.song_data["individual_onsets"]
        '''fast_pace'''
        fast_pace = self.song_data["fast_paced_sections"][self.fast_pace_data[0]]
        fp_s = fast_pace['start']
        fp_e = fast_pace['end']
        '''buildups'''
        buildups = self.song_data["buildups"][self.build_ups_data[0]]
        bu_s = buildups['start']
        bu_e = buildups['end']


        # fp_interval = fast_pace['']
        # if self.fast_pace_data[0] < self.fast_pace_data[1]:
        #     self.fast_pace_data[0] =

        if current_song_time >= fp_e:
            if self.fast_pace_data[0] >= self.fast_pace_data[1] - 1:
                self.fast_pace_data[0] = 0
            else:
                self.fast_pace_data[0] += 1

        if current_song_time >= bu_e:
            if self.build_ups_data[0] >= self.build_ups_data[1] - 1:
                self.build_ups_data[0] = 0
            else:
                self.build_ups_data[0] += 1

        color = (255, 255, 100)

        if current_song_time >= fp_s and current_song_time <= fp_e:
            color = (255, 0, 0)
        if current_song_time >= bu_s and current_song_time <= bu_e:
            color = (0, 0, 255)

        if self.beats_data[0] < self.beats_data[1]:
            if current_song_time >= beats[self.beats_data[0]]:
                # self.circles.append([[*self.player.rect.center],color])
                self.spawn_asteroid()
                # self.player.all_direction_bullet(360//10)
                # self.player.fire()
                self.beats_data[0] += 1
                self.r = max(60,random.randint(60,100))
        else:
            self.beats_data[0] = 0
            self.fast_pace_data[0] = 0
            self.build_ups_data[0] = 0
            self.music_start_ticks = pygame.time.get_ticks()
        self.r -= 0.5

        # Limit max circles on screen
        if len(self.circles) >= int(self.bpm):
            self.circles.pop(0)


        # if len(self.circles) >= int(self.bpm):
        #     self.circles.pop(0)

        # pygame.draw.rect(self.screen,(255,255,255),self.player)

        self.player.update_velocity()
        self.player.move()

        self.e.update_velocity()
        self.e.follow_target()
        self.e.move()



        self.screen.fill((0,0,0))
        self.window.fill((0,0,0))


        win_render_pos = self.reference_point-self.camera.offset

        self.stars.show(self.window,self.screen,win_render_pos,self.player.movement)
        self.player.show(self.window)
        self.e.show(self.window)
        self.asteroid_spark.show(self.window)
        # pygame.draw.circle(self.window,color,self.player.rect.center,self.r,2)
        self.player.move_bullets(self.window)
        self.e.move_bullets(self.window)
        # collision = pygame.sprite.Sp(self.asteroids_group,self.player.bullets_group,False,False)
        # for ast in collision:
        #     print("asteroid");ast.alive = False

        for circle in self.circles:
            pygame.draw.circle(self.window, circle[1], circle[0], random.randint(10,30))

        for i,asteroid in enumerate(self.asteroids):
            bullet = pygame.sprite.spritecollideany(asteroid,self.player.bullets_group)
            if bullet:
                bullet.alive = False
                self.sounds['rock'].play()
                self.asteroid_spark.add(*bullet.rect.center,scale=asteroid.scale*2)
                asteroid.alive = False


            if not asteroid.alive:
                self.asteroids.pop(i)
                asteroid.kill()
            else:
                asteroid.move(self.window.get_size())
                asteroid.show(self.window)


        pygame.draw.rect(self.window,(100,100,100),self.window.get_rect(),1)

        self.camera.targetcenter(self.player.rect.center)

        self.screen.blit(self.window,self.reference_point-self.camera.offset)
        # self.screen.blit(pygame.transform.scale_by(self.window,0.1),(10,10))
        # self.screen.blit(self.shaders, (0, 0))

        self.draw_minimap()
        self.draw_music_progress(
            current_song_time,
            self.song_duration,
            color
        )
        pygame.display.update()
        time = self.clock.tick(self.fps) /1000
        # self.spawn_timer += time

    def spawn_asteroid(self):

        # center = [random.randint(100,self.window.get_width()-200),
        #           random.randint(100,self.window.get_height()-200)]

        cx,cy = self.player.rect.center
        x_limits = [cx-self.size[0]//2,cx+self.size[0]//2]
        # xrange = [0,0]
        print(x_limits)
        if x_limits[0] <= 200:
            xrange = (x_limits[1],self.window.get_width())
        elif self.window.get_width()-x_limits[1] <= 200:
            xrange = (0,x_limits[0])
        else :
            idx = random.choice((0,1))
            if idx != 0:
                xrange = (x_limits[1],self.window.get_width())
            else:
                xrange = (0,x_limits[0])


        y_limits = [cy - self.size[1] // 2, cy + self.size[1] // 2]
        if y_limits[0] <= 200:
            yrange = (y_limits[1], self.window.get_height())
        elif self.window.get_height()-y_limits[1] <= 200:
            yrange = (0, y_limits[0])
        else:
            idx = random.choice((0, 1))
            if idx != 0:
                yrange = (y_limits[1], self.window.get_height())
            else:
                yrange = (0, y_limits[0])

        x = random.randint(*xrange)
        y = random.randint(*yrange)
        center = [x,y]
        angle = math.atan2(self.player.rect.centery-center[1],
                           self.player.rect.centerx-center[0])


        asteroid = sprite.Asteroid(center,angle)
        self.asteroids.append(asteroid)
        self.asteroids_group.add(asteroid)


    def draw_minimap(self,grid = False):
        map_width = 240
        map_height = 135
        padding = 15

        scale_x = map_width / self.window.get_width()
        scale_y = map_height / self.window.get_height()


        minimap = pygame.Surface(
            (map_width, map_height), pygame.SRCALPHA
        )

        minimap.fill((10, 15, 25, 210))

        if grid:
            for x in range(0, map_width, 30):
                pygame.draw.line(
                    minimap, (35, 45, 60, 150),
                    (x, 0), (x, map_height), 1
                )

            for y in range(0, map_height, 30):
                pygame.draw.line(
                    minimap, (35, 45, 60, 150),
                    (0, y), (map_width, y), 1
                )


        for asteroid in self.asteroids:

            if not asteroid.alive:
                continue

            x = int(asteroid.rect.centerx * scale_x)
            y = int(asteroid.rect.centery * scale_y)

            pygame.draw.circle(
                minimap,
                (255, 65, 65),
                (x, y),
                3)

        # Player position on minimap
        px = self.player.rect.centerx * scale_x
        py = self.player.rect.centery * scale_y

        # Triangle pointing in player's current direction
        angle = math.radians(self.player.angle)

        tip = (
            px + 7 * math.cos(angle),
            py + 7 * math.sin(angle)
        )

        left = (
            px + 5 * math.cos(angle + 2.5),
            py + 5 * math.sin(angle + 2.5)
        )

        right = (
            px + 5 * math.cos(angle - 2.5),
            py + 5 * math.sin(angle - 2.5)
        )

        pygame.draw.polygon(
            minimap,
            (50, 255, 120),
            [tip, left, right]
        )

        # Minimap border
        pygame.draw.rect(minimap,
            (100, 120, 145),
            minimap.get_rect(),
            1
        )


        map_x = self.size[0] - map_width - padding
        map_y = self.size[1]-map_height - padding
        self.screen.blit(minimap, (map_x, map_y))



    def draw_music_progress(self, elapsed, duration, color):

        bar_width = self.size[0]//4
        bar_height = 6

        x = 20
        y = 20

        # Prevent division by zero and clamp progress
        progress = min(1.0, max(0.0, elapsed / duration))

        # Background
        pygame.draw.rect(
            self.screen,
            (45, 45, 55),
            (x, y, bar_width, bar_height),
            border_radius=5
        )

        # Filled portion
        surf = pygame.Surface((int(bar_width * progress), bar_height+6))
        surf.fill((0,0,0))
        surf.set_colorkey((0,0,0))
        color2 = (color[0]//2, color[1]//2, color[2]//2)

        pygame.draw.rect(
            surf,
            color2,
            (0,0, int(bar_width * progress), bar_height+6),
            border_radius=5
        )
        # surf.fill(color2)
        pygame.draw.rect(
            self.screen,
            color2,
            (x, y, int(bar_width * progress), bar_height),
            border_radius=5
        )
        # self.screen.blit(surf,(x,y-3),special_flags=pygame.BLEND_RGBA_ADD)

if __name__ == '__main__':
    game = Game()
    while game.running:
        game.run()