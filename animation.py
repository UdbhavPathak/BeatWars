import math

import pygame
import random
from pygame.locals import *
pygame.init()


class Stars:
    def __init__(self, size):
        self.size = [*size]
        self.starsize = 3
        self.maxstars = 200
        self.stars = []
        self.smooth_velocity = pygame.math.Vector2(0, 0)
        self.smoothing = 0.3

    def show(self, win, win2, rp, vel):

        move_x, move_y = vel

        # Smoothly interpolate star movement
        self.smooth_velocity.x += (
                                move_x - self.smooth_velocity.x
                                  ) * self.smoothing

        self.smooth_velocity.y += (
                                    move_y - self.smooth_velocity.y
                                  ) * self.smoothing

        for star in self.stars:

            pos, size, drift_speed = star

            if size == 1:
                color = (170, 170, 170)
                parallax = 0.10
            else:
                color = (255, 255, 255)
                parallax = size * 0.10

            # Use smoothed velocity
            pos[0] += self.smooth_velocity.x * (1.0 - parallax)
            pos[1] += self.smooth_velocity.y * (1.0 - parallax)

            # Wrap around world
            if pos[0] < 0:
                pos[0] += self.size[0]
            elif pos[0] >= self.size[0]:
                pos[0] -= self.size[0]

            if pos[1] >= self.size[1]:
                pos[1] = -10
            elif pos[1] < -10:
                pos[1] = self.size[1]

            pygame.draw.circle(
                win,
                color,
                (round(pos[0]), round(pos[1])),
                size
            )

    # def show(self, win, win2, rp, vel):
    #     move_x, move_y = vel
    #
    #     for star in self.stars:
    #         pos, size, drift_speed = star
    #         if size == 1:
    #             parallax = 0.10  # distant stars move slowly on screen
    #         else:
    #             # color = (, 255, 255)
    #             parallax = size*0.10 # closer stars move faster on screen
    #         color = (min(255, int(100 * size)), min(255, int(100 * size)), min(255, int(100 * size)))
    #
    #
    #         pos[0] += move_x * (1.0 - parallax)
    #         pos[1] += move_y * (1.0 - parallax)
    #
    #
    #         # Wrap stars around the world surface so they never disappear.
    #         if pos[0] < 0:
    #             pos[0] += self.size[0]
    #         elif pos[0] >= self.size[0]:
    #             pos[0] -= self.size[0]
    #
    #         if pos[1] >= self.size[1]:
    #             pos[1] = -10
    #         elif pos[1] < -10:
    #             pos[1] = self.size[1]
    #
    #         # surf = self.circle_surf(size*2,(150,150,0))
    #         pygame.draw.circle(win, color, (round(pos[0]), round(pos[1])), size)
    #         # win.blit(surf, (round(pos[0])-2*size, round(pos[1])-2*size),special_flags = pygame.BLEND_RGB_ADD)


    def addstar(self):
        pos = [
            random.randint(0, self.size[0] - 1),
            random.randint(0, self.size[1] - 1),
        ]
        size = random.randint(1, self.starsize)
        # drift_speed = 0.5 if size >= 2 else 0.25
        self.stars.append([pos, size, 0])

    def circle_surf(self, radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf


class ThrustParticles:
    def __init__(self, size):
        self.size = size
        self.color = [(230,230,250),(80,0,140)] #80,0,140

        self.particles = []

    def update(self,win):
        for i , particle in enumerate(self.particles):
            if particle[1] <= 0:
                self.particles.pop(i)

            else:
                particle[0][0] += particle[2]*math.cos(particle[3])
                particle[0][1] += particle[2]*math.sin(particle[3])
                particle[1] -= 0.25
                particle[2] -= 0.25

                surf = self.circle_surf(particle[1]*2, self.color[1])

                pygame.draw.circle(win,self.color[0],particle[0],particle[1])
                win.blit(surf,(particle[0][0]-2*particle[1],particle[0][1]-2*particle[1])
                         ,special_flags=pygame.BLEND_RGBA_ADD)




    def add(self,center,angle):
        size = random.randint(*self.size)
        x,y = center
        vel = size
        angle = angle

        self.particles.append([[x,y],size,vel,angle])

    def circle_surf(self, radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

class SparkParticle:
    def __init__(self,**kwargs):
        self.pos = kwargs['pos']
        self.color = kwargs['color']
        self.scale = kwargs['scale']
        self.speed = kwargs['speed']
        self.angle = math.radians(kwargs['angle'])
        self.bd = kwargs['bd']
        self.omega = 0
        self.alive = True
    def displacement(self,dt):
        dx = math.cos(self.angle)*self.speed*dt
        dy = math.sin(self.angle)*self.speed*dt
        return dx,dy

    def move(self):
        movement = self.displacement(1)
        self.pos[0] += movement[0]
        self.pos[1] += movement[1]
        self.speed -= 0.3
        self.angle += self.omega
        if self.speed <=0:
            self.alive = False

    def show(self,win):
        points = [
            [self.pos[0] + math.cos(self.angle) * self.speed * self.scale,
             self.pos[1] + math.sin(self.angle) * self.speed * self.scale],

            [self.pos[0] + math.cos(self.angle+math.pi/2) * self.speed * self.scale * 0.4,
             self.pos[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.4],

            [self.pos[0] - math.cos(self.angle) * self.speed * self.scale * 3.5,
             self.pos[1] - math.sin(self.angle) * self.speed * self.scale * 3.5],

            [self.pos[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.4,
             self.pos[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.4],
        ]
        pygame.draw.polygon(win,self.color,points)
        if self.bd[0]:
            pygame.draw.polygon(win,self.bd[1],points,1)



class Sparks:
    def __init__(self,color,speed,scale = 1,**kwargs):
        self.particles = []
        self.color = color
        self.speed = speed
        self.scale = scale
        self.limit = kwargs['limit']
        self.bd = kwargs['bd']

    def add(self,x,y,scale = 1):

        for i in range(self.limit):
            s = SparkParticle(pos = [x,y],color = self.color,scale=scale,
                                         speed = random.randint(*self.speed),angle=random.randint(0,360),
                                             bd= self.bd)
            # s.omega = -0.1
            self.particles.append(s)

    def show(self,win):
        for i,spark in enumerate(self.particles):
            spark.move()
            spark.show(win)
            if not spark.alive:
                self.particles.pop(i)
                # print(len(self.sparks))

    def add2(self,x,y,omega):
        for i in range(self.limit):
            s = SparkParticle(pos = [x,y],color = self.color,scale=self.scale,
                                         speed = random.randint(*self.speed),angle=random.randint(0,360),
                                             bd= self.bd)
            s.omega = omega
            self.particles.append(s)

    def add_one(self,x,y,omega):
        s = SparkParticle(pos=[x, y], color=self.color, scale=self.scale,
                          speed=random.randint(*self.speed), angle=random.randint(0, 360),
                          bd=self.bd)
        s.omega = omega
        self.particles.append(s)

