from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import *
from random import random, randrange, uniform
import copy
import time

GUN_MODES = {
    KEY._1: 'Rifle',
    KEY._2: 'Rocket',
    KEY._3: 'HandGun',
    KEY._4: 'HandGrenade',
}

GUN_COOLDOWNS = {
    'Rifle': 0.8,
    'Rocket': 2,
    'HandGun': 0.5,
    'HandGrenade': 1.4
}


class Hunter(object):
    def __init__(self, world=None, mode='Patrol', gun='Rifle'):
        self.world = world
        self.mode = mode
        self.pos = Vector2D(world.cx/2, world.cy/2)
        self.radius = 10
        self.gun = Gun(self.pos, world, gun)
        self.time = 0
        self.aim = True
        self.speed = 4

        #Waypoint init
        self.waypoints = [self.pos.copy()]
        self.current_waypoint = 0

        #States
        self.mode_attack = 'Firing'
        self.mode_patrol = 'Walking'

        #Transitions
        self.last_fire = time.time()
        self.last_idle = time.time()

    def update(self, delta):
        target = self.find_prey(200)
        self.gun.update_firing_pos(self.pos)
        if self.mode == 'Patrol' and target is not None:
            self.mode = 'Attack'
        elif self.mode == 'Attack' and target is None:
            self.mode = 'Patrol'

        self.perform(self.mode, target)


    def render(self):
        egi.green_pen()
        egi.set_stroke(2)
        egi.circle(self.pos, self.radius, True)

    def perform(self, mode, target=None):
        if mode == 'Patrol':
            self.patrol()
        if mode == 'Attack':
            self.attack(target)


    def patrol(self):
        if(self.mode_patrol == 'Idle' and self.last_idle > 1):
            self.mode_patrol = 'Walking'

        if self.mode_patrol == 'Walking':

            direction = (self.waypoints[self.current_waypoint] - self.pos).normalise()
            self.pos += direction * self.speed

            if self.pos.distance_sq(self.waypoints[self.current_waypoint]) < 25:
                self.next_waypoint()
                self.last_idle = time.time()
                self.mode_patrol = 'Idle'


    def attack(self, target):
        if self.mode_attack == 'Reloading' and time.time() - self.last_fire > GUN_COOLDOWNS[self.gun.mode]:
            self.mode_attack = 'Firing'
        if self.mode_attack == 'Firing':
            self.gun.fire(target)
            self.last_fire = time.time()
            self.mode_attack = 'Reloading'






    def add_waypoint(self, x, y):
        self.waypoints.append(Vector2D(x,y))
    def next_waypoint(self):
        self.current_waypoint += 1
        if self.current_waypoint >= len(self.waypoints):
            self.current_waypoint = 0

    def find_prey(self, radius):

        tagged_prey = []
        for prey in self.world.preyList:
            if Vector2D.distance(self.pos, prey.pos) < radius:
                tagged_prey.append(prey)

        shortest_dist = 999999999999999

        closest_prey = None
        for prey in tagged_prey:
            if Vector2D.distance(self.pos, prey.pos) < shortest_dist:
                shortest_dist = Vector2D.distance(self.pos, prey.pos)
                closest_prey = prey
        return closest_prey





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
        'HandGrenade': 250
    }


    def __init__(self, firing_pos, world=None, mode="Rifle"):
        self.init_pos = Vector2D.copy(firing_pos)
        self.world = world
        self.mode = mode
        self.bullet_speed = self.BULLET_VELOCITY[mode]

    def update_firing_pos(self, firing_pos):
        self.init_pos = Vector2D.copy(firing_pos)

    def aim(self, enemy):
        timeToHit = Vector2D.distance(enemy.pos, self.init_pos) / self.bullet_speed
        return enemy.pos + enemy.vel * timeToHit

    def fire(self, target):
        enemy = target
        if self.world.hunter.aim is True:
            enemy_pos = self.aim(enemy)

        if self.mode == "Rifle":
            self.world.add(RifleBullet(self.init_pos, enemy_pos))
        elif self.mode == "HandGun":
            self.world.add(HandGunBullet(self.init_pos, enemy_pos))
        elif self.mode == "Rocket":
            self.world.add(RocketBullet(self.init_pos, enemy_pos))
        elif self.mode == "HandGrenade":
            self.world.add(HandGrenadeBullet(self.init_pos, enemy_pos))


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
       for prey in self.world.preyList:
        if Vector2D.distance(self.pos, prey.pos) <= (self.radius - 10)**2:
           self.active = False
           prey.color = 'BLUE'
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

        
