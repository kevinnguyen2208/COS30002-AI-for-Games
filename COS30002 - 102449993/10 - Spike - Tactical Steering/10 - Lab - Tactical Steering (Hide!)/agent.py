from path import Path
from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform

AGENT_MODES = {
    KEY._1: 'seek',
    KEY._2: 'arrive_slow',
    KEY._3: 'arrive_normal',
    KEY._4: 'arrive_fast',
    KEY._5: 'flee',
    KEY._6: 'pursuit',
    KEY._7: 'follow_path',
    KEY._8: 'wander',
    KEY._9: 'hide'  # used in spike 8 by the prey agent
}


class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        'normal': 0.5,
        'fast': 0.1,
    }

    def randomise_path(self, looped=True):
        
        cx = self.world.cx
        cy = self.world.cy
        margin = min(cx, cy) * (1/6)
        self.path.create_random_path(10, 0, 0, cx, cy, looped)

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='hide', looped=True):
        # keep a reference to the world object
        self.world = world
        self.mode = mode
        # where am i and where am i going? random
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        self.acceleration = Vector2D()  # current steering force
        self.mass = mass
        # limits?
        self.max_speed = 20.0 * scale / 2
        self.max_force = 500.0
        # Random Path to follow in PathFollow mode
        self.path = Path()
        self.path_looped = looped
        self.randomise_path(looped)
        self.waypoint_threshold = 20
        # Wander Info
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 1.0 * scale
        self.bRadius = scale

        # If Tagged is true, We are part of a neighbourhood
        self.tagged = False

        # data for drawing this agent
        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-1.0,  0.6),
            Point2D(1.0,  0.0),
            Point2D(-1.0, -0.6)
        ]

    def reinit(self):
        self.randomise_path(self.path_looped)
        if self.mode is not 'follow_path':
            self.max_speed = 10 * self.scale.x
            self.max_force = 500.0
        else:
            self.max_speed = 10
            self.max_force = 250.0
        #self.max_speed = 10 * self.scale.x
        #self.max_force = 500.0

    def calculate(self, delta):
        # reset the steering force
        mode = self.mode
        if mode == 'seek':
            force = self.seek(self.world.target)
        elif mode == 'arrive_slow':
            force = self.arrive(self.world.target, 'slow')
        elif mode == 'arrive_normal':
            force = self.arrive(self.world.target, 'normal')
        elif mode == 'arrive_fast':
            force = self.arrive(self.world.target, 'fast')
        elif mode == 'flee':
            if self.world.hunter is not None:
                force = self.flee(self.world.hunter.pos)
            else:
                force = self.flee(self.world.target)
##        elif mode == 'pursuit':
##            force = self.pursuit(self.world.hunter)
        elif mode == 'follow_path':
            force = self.follow_path()
        elif mode == 'wander':
            force = self.wander(delta)
        else:
            force = Vector2D()
        return force

    def update(self, delta):
        ''' update vehicle position and orientation '''
        acceleration = self.calculate(
            delta)  # b <-- Delta Required for Wander Behaviour

        # new velocity
        self.vel += acceleration * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.length_sq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)

    def render(self, color=None):
        ''' Draw the triangle agent with color'''
        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.vehicle_shape, self.pos,
                                          self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)

        #draw the path if following path
        if self.mode == 'follow_path':
            self.path.render()
        # draw wander info
        elif self.mode == 'wander':
            # calculate the center of the wander circle in front of the agent
            wnd_pos = Vector2D(self.wander_dist, 0)
            wld_pos = self.world.transform_point(
                wnd_pos, self.pos, self.heading, self.side)
            # draw the wander circle
            egi.green_pen()
            egi.circle(wld_pos, self.wander_radius)
            # draw the wander target (little circle on the big circle)
            egi.red_pen()
            wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
            wld_pos = self.world.transform_point(
                wnd_pos, self.pos, self.heading, self.side)
            egi.circle(wld_pos, 3)

    

    def speed(self):
        return self.vel.length()

    #--------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        ''' move away from hunter position '''
        #Updated 26/3/18
        # Check if within Panic Radius (currently Hard coded
        if Vector2D.distance(self.pos, hunter_pos) < 200:
            # Flee Velocity Calc
            desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
            return (desired_vel - self.vel)
        else:
            return self.acceleration

    def arrive(self, target_pos, speed):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            # calculate the speed required to reach the target given the
            # desired deceleration rate
            speed = dist / decel_rate
            # make sure the velocity does not exceed the max
            speed = min(speed, self.max_speed)
            # from here proceed just like Seek except we don't need to
            # normalize the to_target vector because we have already gone to the
            # trouble of calculating its length for dist.
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def pursuit(self, evader):
        ''' this behaviour predicts where an agent will be in time T and seeks
            towards that point to intercept it. '''
## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
        return Vector2D()

    def follow_path(self):

        if self.path.is_at_end_of_path():
            if self.pos.distance(self.path.current_pt()) <= self.waypoint_threshold:
                self.path.inc_current_pt()
            else:
                # arrive at current point
                return self.arrive(self.path.current_pt(), 'slow')
        else:
            # if within threashold distance of current point, inc_current_point
            if self.pos.distance(self.path.current_pt()) <= self.waypoint_threshold:
                self.path.inc_current_pt()
            # Else Seek current point
            else:
                return self.seek(self.path.current_pt())
        return Vector2D(0, 0)

    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
        wt = self.wander_target
        # this behaviour is dependent on the update rate, so this line must
        # be included when using time independent framerate.
        jitter_tts = self.wander_jitter * delta  # this time slice
        # first, add a small random vector to the target's position
        wt += Vector2D(uniform(-10, 10) * jitter_tts,
                       uniform(-10, 10) * jitter_tts)
        # re-project this new vector back on to a unit circle
        wt.normalise()
        # increase the length of the vector to the same as the radius
        # of the wander circle
        wt *= self.wander_radius
        # move the target into a position WanderDist in front of the agent
        target = wt + Vector2D(self.wander_dist, 0)
        # project the target into world space
        wld_target = self.world.transform_point(
            target, self.pos, self.heading, self.side)
        # and steer towards it
        return self.seek(wld_target)

    

    
