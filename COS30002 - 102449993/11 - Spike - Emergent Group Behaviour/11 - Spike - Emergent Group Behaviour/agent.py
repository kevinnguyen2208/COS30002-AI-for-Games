'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by Clinton Woodward cwoodward@swin.edu.au

'''

from vector2d import Vector2D
from enviroObject import enviroObject
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform, randint
from path import Path


AGENT_MODES = {
    KEY._1: 'seek',
    KEY._2: 'arrive_slow',
    KEY._3: 'arrive_normal',
    KEY._4: 'arrive_fast',
    KEY._5: 'flee',
    KEY._6: 'pursuit',
    KEY._7: 'follow_path',
    KEY._8: 'wander',
    KEY._9: 'flocking',
    KEY._0: 'hide'

}

class Agent(object):

 
    DECELERATION_SPEEDS = {
        'slow': 0.9,
        'normal' : 0.5,
        'fast' : 0.9
    }

    def __init__(self, world=None, scale=40.0, mass=1.0, mode='flocking'):
      
        self.world = world
        self.mode = mode
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  
        self.force = Vector2D()  
        self.accel = Vector2D() 
        self.mass = mass
        self.tagged = False
        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-0.25,  0.15),
            Point2D( 0.25,  0.0),
            Point2D(-0.25, -0.15)
        ]
        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 50.0
        self.wander_target = Vector2D(1,0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        self.neighbourR = 50;
        self.neighbours = []
        self.CohesionWeight = 0
        self.SeperationWeight = 2.0
        self.AlignmentWeight = 0
        self.max_speed = 20.0 * scale
        self.max_force = 500.0
        self.show_info = False






    def randomise_path(self):
        cx = self.world.cx
        cy = self.world.cy
        margin = min(cx,cy) * (1/6)
        self.path.create_random_path(10,margin,margin,cx-margin,cy-margin)

    def follow_path(self):
        if self.path.is_finished():
            self.arrive(self.path.current_pt(),'slow')
        else:
            if self.pos.distance(self.path.current_pt()) < self.waypoint_threshold:
                self.path.inc_current_pt()
        
        return self.seek(self.path.current_pt())      

    def calculate(self,delta):
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
            force = self.flee(self.world.target)
        elif mode == 'pursuit':
            force = self.pursuit(self.world.hunter)
        elif mode == 'wander':
            force = self.wander(delta)
        elif mode == 'follow_path':
            force = self.follow_path()
        elif mode == 'flocking':
            force = self.sumBehaviours(delta)
        elif mode == 'hide':
            force = self.Hide(delta)
        else:
            force = Vector2D()
        self.force = force
        return force
    
    def update(self, delta):
       
        force = self.calculate(delta)  
        force.truncate(self.max_force)
      
        self.accel = force / self.mass  
        self.vel += self.accel * delta
        self.vel.truncate(self.max_speed)
        self.pos += self.vel * delta
        if self.vel.length_sq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()

        self.world.wrap_around(self.pos)

    def render(self, color=None):
        if self.mode == 'follow_path':
            self.path.render()
        
        if self.mode == "wander":
            wnd_pos = Vector2D(self.wander_dist,0)
            wld_pos = self.world.transform_point(wnd_pos,self.pos,self.heading,self.side)

            if self.tagged :
                 self.color = 'GREEN'
            else:
                self.color = 'ORANGE'
            wnd_pos = (self.wander_target + Vector2D(self.wander_dist,0))
            wld_pos = self.world.transform_point(wnd_pos,self.pos,self.heading,self.side)

        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.vehicle_shape, self.pos,self.heading, self.side, self.scale)
        egi.closed_shape(pts)

        if self.show_info:
            s = 0.5
            egi.red_pen()
            egi.line_with_arrow(self.pos, self.pos + self.force * s, 5)
            egi.grey_pen()
            egi.line_with_arrow(self.pos, self.pos + self.vel * s, 5)
            egi.white_pen()
            egi.line_with_arrow(self.pos+self.vel * s, self.pos+ (self.force+self.vel) * s, 5)
            egi.line_with_arrow(self.pos, self.pos+ (self.force+self.vel) * s, 5)

    def speed(self):
        return self.vel.length()


    def seek(self, target_pos):
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        panic_range = 100
        if self.pos.distance(hunter_pos) > panic_range:
           return Vector2D() 
  
        desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def arrive(self, target_pos, speed):
        
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            speed = dist / decel_rate
           
            speed = min(speed, self.max_speed)
         
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def pursuit(self, evader):
        toEvader = evader.pos - self.pos
        relativeHeading = self.heading.dot(evader.heading)
       
        if (toEvader.dot(self.heading)> 0) and (relativeHeading < 0.95):
            return self.arrive(evader.pos,'slow')

        lookAheadTime = toEvader.length()/(self.max_speed+evader.speed())
        lookAheadTime += (1 - self.heading.dot(evader.heading)) * -1

        
        lookAheadPos = evader.pos + evader.vel*lookAheadTime
        return self.arrive(lookAheadPos, 'slow')

    
    
    def tagNeighbours(self,bots,radius) :
        self.neighbours.clear();
       
        for bot in bots :
        
            if bot != self :
                bot.tagged = False
                to = self.pos - bot.pos
                gap = radius + bot.bRadius
                if to.length_sq() < gap**2 :
                    bot.tagged = True
                    egi.white_pen()
                    egi.text_at_pos(bot.pos.x,bot.pos.y,"Tagged")    
                    self.neighbours.append(bot)
               
       

    def Seperation(self,group):
        SteeringForce = Vector2D()
        for bot in group:
            if bot != self and bot.tagged:
                ToBot = self.pos - bot.pos
                SteeringForce += ToBot.normalise() / ToBot.length()
        return SteeringForce
             
    def Alignment(self,group):
        AvgHeading = Vector2D()
        AvgCount = 0

        for bot in group:
            if bot != self and bot.tagged:
                AvgHeading += bot.heading
                AvgCount +=1
        if AvgCount > 0:
            AvgHeading /= float(AvgCount)
            AvgHeading -= self.heading
        return AvgHeading

    def Cohesion(self,group):
        CentreMass = Vector2D()
        SteeringForce = Vector2D()
        AvgCount = 0

        for bot in group:
            if bot != self and bot.tagged :
                CentreMass += bot.pos
                AvgCount += 1
        if AvgCount > 0 :
            CentreMass /= float(AvgCount)
            SteeringForce = self.seek(CentreMass)
        return SteeringForce
    

    def wander(self, delta):
       wt = self.wander_target

       jitter_tts = self.wander_jitter * delta
       wt += Vector2D(uniform(-1,1) * jitter_tts, uniform(-1,1) * jitter_tts)

       wt.normalise()
       wt *= self.wander_radius

       target = wt + Vector2D(self.wander_dist,0)

       wld_target = self.world.transform_point(target,self.pos,self.heading,self.side)
      
       
       for agent in self.world.agents :
           print(len(agent.neighbours))
       return self.seek(wld_target)


    def sumBehaviours(self,delta):
       self.tagNeighbours(self.world.agents,self.neighbourR)
       if len(self.neighbours) == 0 :
          return self.wander(delta)
       cohesion = self.Cohesion(self.neighbours) * self.CohesionWeight
       alignment = self.Alignment(self.neighbours) * self.AlignmentWeight
       seperation = self.Seperation(self.neighbours) * self.SeperationWeight

       return cohesion + alignment + seperation

    def GetHidingPosition(self,obj):
 
       DistFromBoundary = 30.0
       DistAway = obj.radius + DistFromBoundary
       ToObj = (obj.pos-self.world.hunter.pos).normalise()

       return (ToObj*DistAway)+obj.pos


    def Hide(self,delta):
       DistToClosest = 10000.0;
       BestHidingSpot = None

       if self == self.world.hunter:
           return self.wander(delta)
       
       

       for obj in self.world.enviroObjs:
           HidingSpot = self.GetHidingPosition(obj)
           HidingDist = HidingSpot.distance_sq(self.pos)
           if HidingDist < DistToClosest:
               DistToClosest = HidingDist
               BestHidingSpot = HidingSpot
           else:
               egi.grey_pen()
               egi.line_by_pos(self.world.hunter.pos,HidingSpot)
               egi.red_pen()
               egi.cross(HidingSpot,10)

       if BestHidingSpot:
           egi.yellow_pen()
           egi.line_by_pos(self.world.hunter.pos,BestHidingSpot)
           egi.red_pen()
           egi.cross(BestHidingSpot,10)
           return self.arrive(BestHidingSpot,'fast')
 
      
       return self.flee(self.world.hunter.pos)


   
    
           

