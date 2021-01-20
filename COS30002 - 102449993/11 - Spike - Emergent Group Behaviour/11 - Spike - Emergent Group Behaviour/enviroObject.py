
from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from random import random, randrange, uniform, randint

class enviroObject(object):

      

     def __init__(self,name="",world=None):
         self.name = name
         self.world = world
         self.radius = 40
         self.color = 'GREY'
         self.pos = Vector2D(randint(100,self.world.screen_width-100), randint(100,self.world.screen_height-100))



     def render(self):
         
       
         egi.set_pen_color(name=self.color)
         if self.name.lower() == 'circle':
             egi.circle(self.pos,self.radius,)