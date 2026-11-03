import random
import pygame,math,animation
from pygame.sprite import Sprite

pygame.init()

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,winsize):
        super().__init__()
        self.pos = [*pos]
        self.rect = pygame.Rect(pos[0],pos[1],10,10)
        self.movement = [0,0]
        self.velocity = 0
        self.thrust = [1,0.1]
        self.max_vel = 5
        self.isMoving = [False,False]
        self.angle = 0
        self.image = pygame.image.load('images/image.png').convert_alpha()

        self.angularVel = 3
        self.bullets = []
        self.bullets_group = pygame.sprite.Group()
        self.winsize = [*winsize]
        self.bullet_timer = [0,15]#15 [timer ,limit]
        self.relode_speed = 2
        self.recoil = [0,0]
        self.bulletsound = pygame.mixer.Sound('sounds/bullet.mp3')
        self.thrustparticles = animation.ThrustParticles([2,5])
        # self.bulletsound.set_volume(0.5)


    def update_velocity(self):
        self.movement = [0,0]
        if self.isMoving[0]:
            if self.velocity < self.max_vel:
                self.velocity += self.thrust[0]
        else:
            if self.velocity > 0:
                self.velocity -= self.thrust[1]

        if self.isMoving[1]:
            if self.velocity > -self.max_vel:
                self.velocity -= self.thrust[0]
        else:
            if self.velocity < 0:
                self.velocity += self.thrust[1]

        self.movement[0] += self.velocity*math.cos(math.radians(self.angle))
        self.movement[1] += self.velocity*math.sin(math.radians(self.angle))
        # self.recoil = [0,0]




    def move(self):
        if self.bullet_timer[0] < self.bullet_timer[1]:
            self.bullet_timer[0] += self.relode_speed
        if self.bullet_timer[0] >= self.bullet_timer[1]:
            self.bullet_timer[0] = self.bullet_timer[1]


        self.rect.x += self.movement[0]
        if self.rect.left < 0:
            self.rect.left = 0
            # self.movement[0] *= -1
            # self.velocity *= -2
            # self.movement = [0,0]
            self.movement[0] = 0

        elif self.rect.right > self.winsize[0]:
            self.rect.right = self.winsize[0]
            # self.movement[0] *= -1
            # self.movement = [0,0]
            self.movement[0] = 0


            # self.velocity *= -2

        self.rect.y += self.movement[1]
        if self.rect.top < 0:
            self.rect.top = 0
            # self.movement[1] *= -1
            # self.velocity *= -2
            # self.movement = [0,0]
            self.movement[1] = 0

        elif self.rect.bottom > self.winsize[1]:
            self.rect.bottom = self.winsize[1]
            # self.movement = [0,0]
            # self.movement[1] *= -1
            # self.velocity *= -2
            self.movement[1] = 0

        if self.isMoving[0] or self.isMoving[1]:
            self.thrustparticles.add(self.rect.center, math.radians(self.angle-180))

        # self.rect.x += self.velocity*math.cos(math.radians(self.angle))
        # self.rect.y += self.velocity*math.sin(math.radians(self.angle))

    # def movement(self):
    #     return (self.velocity * math.cos(math.radians(self.angle)), self.velocity * math.sin(math.radians(self.angle)))

    def show(self,win):
        img = pygame.transform.rotozoom(self.image,-self.angle,0.75)
        rect = img.get_rect(center=self.rect.center)
        self.thrustparticles.update(win)

        win.blit(img,rect)
        pygame.draw.rect(win,(255,255,255),self.rect,1)
        # pygame.draw.line(win,(255,255,255),self.rect.center,
        #                  (self.rect.centerx+100*math.cos(math.radians(self.angle)),
        #                   self.rect.centery+100*math.sin(math.radians(self.angle))))


    def move_bullets(self,win):
        for i,bullet in enumerate(self.bullets):

            # if pygame.sprite.spritecollide(bullet,asteroids,False):
            #     bullet.alive = False
            #     self.bullets.pop(i)
            #     bullet.kill()

            if not bullet.alive:
                self.bullets.pop(i)
                bullet.kill()
            else:
                bullet.move(self.winsize)
                bullet.show(win)
                # print(i,bullet)

    def fire(self):
        if self.bullet_timer[0] == self.bullet_timer[1]:
            self.bulletsound.play()
            center = (self.rect.centerx + 50*math.cos(math.radians(self.angle)),
                      self.rect.centery + 50*math.sin(math.radians(self.angle)))
            bullet = Bullet(center,self.angle)
            self.bullets.append(bullet)
            self.bullet_timer[0] = 0
            # self.velocity = -bullet.velocity//5
            self.bullets_group.add(bullet)



    def all_direction_bullet(self,limit):
        # angle = 0
        if self.bullet_timer[0] == self.bullet_timer[1]:
            for i in range(0,360,limit):
                center = (self.rect.centerx + 50 * math.cos(math.radians(i)),
                          self.rect.centery + 50 * math.sin(math.radians(i)))
                bullet = Bullet(center,i)
                self.bullets.append(bullet)
                self.bullets_group.add(bullet)
            self.bullet_timer[0] = 0

            # self.bullet_timer[0] = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self,center,angle):
        super().__init__()
        self.image = pygame.image.load('images/bullet.png').convert_alpha()
        # self.image = pygame.transform.
        self.rect = self.image.get_rect(center=center)
        self.angle = angle
        self.velocity = 20
        self.alive = True

    def move(self,winsize):
        self.rect.x += self.velocity*math.cos(math.radians(self.angle))
        self.rect.y += self.velocity*math.sin(math.radians(self.angle))
        if (self.rect.right < 0 or self.rect.left > winsize[0]) or (self.rect.bottom < 0 or self.rect.top > winsize[1]):
            self.alive = False

    def show(self,win):
        img = pygame.transform.rotozoom(self.image,-self.angle,1)
        rect = img.get_rect(center=self.rect.center)
        win.blit(img,rect)


class Asteroid(pygame.sprite.Sprite):
    def __init__(self,center,angle):
        super().__init__()
        self.pos = pygame.Vector2(center)
        self.image = pygame.image.load('images/asteroid.png').convert_alpha()
        self.rect = self.image.get_rect(center=center)
        self.angle = angle
        self.velocity = random.randint(3,5)
        self.alive = True
        self.imgangle = 0
        self.scale = random.uniform(0.1,0.5)
        self.rect.w *= self.scale
        self.rect.h *= self.scale
        # self.rect.center = center
        # self.id = 0


    def move(self,winsize):
        # self.rect.x += self.velocity*math.cos(self.angle)
        # self.rect.y += self.velocity*math.sin(self.angle)
        self.pos.x += self.velocity * math.cos(self.angle)
        self.pos.y += self.velocity * math.sin(self.angle)

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        if (self.rect.right < 0 or self.rect.left > winsize[0]) or (self.rect.bottom < 0 or self.rect.top > winsize[1]):
            self.alive = False


    def show(self,win):
        img = pygame.transform.rotozoom(self.image,self.imgangle,self.scale)
        rect = img.get_rect(center=self.rect.center)
        win.blit(img,rect)
        self.imgangle += 2
        # pygame.draw.rect(win,(255,0,0),self.rect,1)
        # pygame.draw.circle(win,(0,255,0),self.rect.center,self.rect.w//2,1)


class Enemy(pygame.sprite.Sprite):
    def __init__(self,center,angle,target,winsize):
        super().__init__()
        self.image = pygame.image.load('images/enemy.png').convert_alpha()
        self.rect = self.image.get_rect(center=center)
        self.target = target
        self.angle = angle
        self.velocity = 4
        self.alive = True
        self.scale = 0.75
        self.movement = [0,0]
        self.winsize = [*winsize]
        self.bullets = []
        self.bullets_group = pygame.sprite.Group()
        self.bullet_timer = [0,30]
        self.bulletimage = pygame.image.load('images/enemybullet.png').convert_alpha()
        self.relode_speed = 1
        self.bulletsound = pygame.mixer.Sound('sounds/bullet.mp3')
        self.thrustparticles = animation.ThrustParticles([2, 5])
        self.fire_radius = 400
        self.thrustparticles.color = ((100,60,0),(100,60,0))

    def show(self,win):
        img = pygame.transform.rotozoom(self.image,-int(math.degrees(self.angle)),self.scale)
        rect = img.get_rect(center=self.rect.center)
        pygame.draw.circle(win,(255,255,255),(rect.centerx,rect.centery),200,1)
        pygame.draw.circle(win,(255,0,0),(rect.centerx,rect.centery),self.fire_radius,1)

        self.thrustparticles.update(win)

        win.blit(img,rect)

    def update_velocity(self):
        self.movement = [0,0]
        self.movement[0] += self.velocity*math.cos(self.angle)
        self.movement[1] += self.velocity*math.sin(self.angle)

    def move(self):
        if self.bullet_timer[0] < self.bullet_timer[1]:
            self.bullet_timer[0] += self.relode_speed
        if self.bullet_timer[0] >= self.bullet_timer[1]:
            self.bullet_timer[0] = self.bullet_timer[1]


        self.rect.x += self.movement[0]
        if self.rect.left < 0:
            self.rect.left = 0
            self.movement[0] = 0

        elif self.rect.right > self.winsize[0]:
            self.rect.right = self.winsize[0]
            self.movement[0] = 0

        self.rect.y += self.movement[1]
        if self.rect.top < 0:
            self.rect.top = 0
            self.movement[1] = 0

        elif self.rect.bottom > self.winsize[1]:
            self.rect.bottom = self.winsize[1]
            self.movement[1] = 0

        # self.rect.x += self.velocity * math.cos(self.angle)
        # self.rect.y += self.velocity * math.sin(self.angle)

    def follow_target(self):
        if self.target_distance() < 200:
            self.velocity = 0
        else:
            self.velocity = 4

        if self.target_distance() < self.fire_radius:
            self.fire()

        if self.velocity > 0:
            self.thrustparticles.add(self.rect.center, self.angle - math.pi)

        self.angle = math.atan2((self.target.rect.centery-self.rect.centery),
                                (self.target.rect.centerx-self.rect.centerx))

    def target_distance(self):
        return math.hypot((self.target.rect.centerx-self.rect.centerx),
                          (self.target.rect.centery-self.rect.centery))

    def fire(self):
        if self.bullet_timer[0] == self.bullet_timer[1]:
            self.bulletsound.play()
            center = (self.rect.centerx + 50*math.cos(self.angle),
                      self.rect.centery + 50*math.sin(self.angle))
            bullet = Bullet(center,int(math.degrees(self.angle)))
            bullet.image = self.bulletimage
            self.bullets.append(bullet)
            self.bullet_timer[0] = 0
            # self.velocity = -bullet.velocity//5
            self.bullets_group.add(bullet)

    def move_bullets(self,win):
        for i,bullet in enumerate(self.bullets):
            if not bullet.alive:
                self.bullets.pop(i)
                bullet.kill()
            else:
                bullet.move(self.winsize)
                bullet.show(win)
