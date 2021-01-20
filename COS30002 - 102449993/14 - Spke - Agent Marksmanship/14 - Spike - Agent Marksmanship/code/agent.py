from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import *
from random import random, randrange, uniform


GUN_MODES = {
    KEY._1: 'Rifle',
    KEY._2: 'Rocket',
    KEY._3: 'HandGun',
    KEY._4: 'HandGrenade',
    KEY._5: 'Shotgun'
}

GUN_COOLDOWNS = {
    'Rifle': 0.8,
    'Rocket': 2,
    'HandGun': 0.5,
    'HandGrenade': 1.4,
    'Shotgun': 0.6
}


class Hunter(object):
    def __init__(self, world=None, mode='Shotgun'):
        self.world = world
        self.mode = mode
        self.pos = Vector2D(world.cx/2, world.cy/2)
        self.radius = 10
        self.gun = Gun(self.pos, world, mode)
        self.time = 0
        self.aim = True

    def update(self, delta):
        if self.mode is not self.gun.mode:
            self.gun.mode = self.mode

        self.time += delta
        if self.time >= GUN_COOLDOWNS[self.gun.mode]:
            target = self.world.prey.pos
            self.gun.fire(target)
            self.time = 0

    def render(self):
        egi.green_pen()
        egi.set_stroke(2)
        egi.circle(self.pos, self.radius, True)



class Prey(object):
    def __init__(self, world=None, scale=10.0):
        self.world = world
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.accel = Vector2D()
        dir = radians(random() * 360)
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.shape = [
            Point2D(-1.0, 0.6),
            Point2D(1.0, 0.0),
            Point2D(-1.0, -0.6)
        ]
        self.color = 'RED'

        self.scale = Vector2D(scale, scale)
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale

        # limits?
        self.max_speed = 20.0 * scale
        ## max_force ??
        self.max_force = 500.0

    def update(self, delta):
            # calculate the current steering force
            force = self.wander(delta)

            force.truncate(self.max_force)
            # determine the new acceleration
            self.accel = force  # not needed if mass = 1.0
            # new velocity
            self.vel += self.accel * delta
            # check for limits of new velocity
            self.vel.truncate(self.max_speed)
            # update position
            self.pos += self.vel * delta

            # treat world as continuous space - wrap new position if needed
            self.world.wrap_around(self.pos)

    def render(self):
        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.shape, self.pos,
                                          self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)

    def speed(self):
        return self.vel.length()

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return desired_vel - self.vel

    def wander(self, delta):
        wt = self.wander_target
        jitter_tts = self.wander_jitter * delta
        inc = Vector2D(uniform(-1, 1) * jitter_tts, uniform(-1, 1) * jitter_tts)
        wt += inc
        wt.normalise()

        wt *= self.wander_radius
        target = wt + Vector2D(self.wander_dist, 0)
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        return self.seek(wld_target)


class Gun(object):
    BULLET_VELOCITY = {
        'Rifle': 500,
        'HandGun': 500,
        'Rocket': 300,
        'HandGrenade': 250,
        'Shotgun': 150
    }


    def __init__(self, firing_pos, world=None, mode="Shotgun"):
        self.init_pos = Vector2D.copy(firing_pos)
        self.world = world
        self.mode = mode
        self.bullet_speed = self.BULLET_VELOCITY[mode]

    def aim(self):
        timeToHit = Vector2D.distance(self.world.prey.pos, self.init_pos) / self.bullet_speed
        return self.world.prey.pos + self.world.prey.vel * timeToHit

    def fire(self, target_pos):
        enemy_pos = target_pos
        if self.world.hunter.aim is True:
            bullet_speed = 20 if self.mode in ['Shotgun'] else 10
            target_pos = self.aim()
# enemy_pos,self.world.prey.vel, bullet_speed
        if self.mode == "Rifle":
            self.world.add(RifleBullet(self.init_pos, enemy_pos))
        elif self.mode == "HandGun":
            self.world.add(HandGunBullet(self.init_pos, enemy_pos))
        elif self.mode == "Rocket":
            self.world.add(RocketBullet(self.init_pos, enemy_pos))
        elif self.mode == "HandGrenade":
            self.world.add(HandGrenadeBullet(self.init_pos, enemy_pos))
        elif self.mode == 'Shotgun':
            for i in range(5):
                self.world.add(ShotgunBullet(self.init_pos, enemy_pos))


class Bullet(object):
    def __init__(self, firing_pos, target_pos):
        self.init_pos = Vector2D.copy(firing_pos)
        self.pos = self.init_pos
        self.direction = Vector2D.normalise(target_pos - self.init_pos)
        self.velocity = 10
        self.radius = 5
        self.collision = None
        self.active = True

    def update(self, delta):
       self.pos += (self.direction * self.velocity) * delta
       if (self.pos.x > self.world.cx or self.pos.x < 0) or (self.pos.y > self.world.cy or self.pos.y < 0):
           self.active = False
           return
       elif Vector2D.distance(self.pos, self.world.prey.pos) <= (self.radius - 10)**2:
           self.active = False
           self.world.prey.color = 'WHITE'
           return


    def render(self):
        egi.white_pen()
        egi.set_stroke(3)
        egi.circle(self.pos, self.radius)


class RifleBullet(Bullet):
    def __init__(self, firing_pos, target_pos):
        Bullet.__init__(self, firing_pos, target_pos)
        self.radius = 12
        self.velocity = 500

class RocketBullet(Bullet):
    def __init__(self, firing_pos, target_pos):
        Bullet.__init__(self, firing_pos, target_pos)
        self.radius = 15
        self.velocity = 300

class HandGunBullet(Bullet):
    def __init__(self, firing_pos, target_pos):
        Bullet.__init__(self, firing_pos, target_pos + Vector2D(randrange(-50,50),randrange(-50,50)))
        self.radius = 12
        self.velocity = 500

class HandGrenadeBullet(Bullet):
    def __init__(self, firing_pos, target_pos):
        Bullet.__init__(self,firing_pos, target_pos + Vector2D(randrange(-50,50),randrange(-50,50)))
        self.radius = 15
        self.velocity = 250


class ShotgunBullet(Bullet):  
    def __init__(self, firing_pos, target_pos):
        Bullet.__init__(self, firing_pos, target_pos +
                        Vector2D(randrange(-100, 100), randrange(-100, 100)))
        self.radius = 5
        self.velocity = randrange(18, 22)
