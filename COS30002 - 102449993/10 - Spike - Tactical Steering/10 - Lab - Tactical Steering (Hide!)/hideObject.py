from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi
from math import sin, cos, radians
from random import random, randrange, uniform
from tkinter import Scale
from world import World

class HideObject(object):
    
    def __init__(self, world, radius = 10):
        #Position of this object in the world, is random
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        #Value of this objects radius
        self.radius = radius

    def reinit(self, world):
        #Position of this object in the world, is random
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))

    def render(self):
        '''Draw the circle that represents this object'''
        egi.grey_pen()
        egi.circle(self.pos, self.radius)