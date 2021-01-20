'''Autonomous Agent Movement: Seek, Arrive and Flee

Created for COS30002 AI for Games, Lab 05
By Clinton Woodward cwoodward@swin.edu.au

'''
from graphics import egi, KEY
from pyglet import window, clock
from pyglet.gl import *

from vector2d import Vector2D
from world import World
from agent import Agent, AGENT_MODES  


def on_mouse_press(x, y, button, modifiers):
    if button == 1: 
        world.target = Vector2D(x, y)


def on_key_press(symbol, modifiers):
    if symbol == KEY.P:
        world.paused = not world.paused
    elif symbol == KEY.M:  
        world.showinfo = not world.showinfo
    elif symbol == KEY.A in AGENT_MODES:
        for agent in world.agents:
            agent.mode = AGENT_MODES[symbol]
   
    
    
    elif symbol == KEY.R:
        for agent in world.agents:
            agent.randomise_path()
   
    elif symbol == KEY.I:
        for agent in world.agents:
            agent.show_info = not agent.show_info
    elif symbol == KEY.Z:
        world.agents.append(Agent(world))
    elif symbol == KEY.Q:
        for agent in world.agents:
           agent.max_force -= 10;
    elif symbol == KEY.W:
        for agent in world.agents:
           agent.max_force += 10;
    elif symbol == KEY.A:
        for agent in world.agents:
           agent.SeperationWeight += 10;
    elif symbol == KEY.S:
        for agent in world.agents:
           agent.SeperationWeight -= 0.5;
    elif symbol == KEY.T:
        for agent in world.agents:
           agent.CohesionWeight += 10;
    elif symbol == KEY.Y:
        for agent in world.agents:
           agent.CohesionWeight -= 0.5;
    elif symbol == KEY.D:
        for agent in world.agents:
           agent.AlignmentWeight += 10;
    elif symbol == KEY.F:
        for agent in world.agents:
           agent.AlignmentWeight -= 0.5;
    elif symbol == KEY.N:
        world.separation = 0
        world.alignment = 0
        world.cohesion = 0
        world.radius = 10



def on_resize(cx, cy):
    world.cx = cx
    world.cy = cy


if __name__ == '__main__':

    # create a pyglet window and set glOptions
    win = window.Window(width=500, height=500, vsync=True, resizable=True)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # needed so that egi knows where to draw
    egi.InitWithPyglet(win)
    # prep the fps display
    fps_display = window.FPSDisplay(win)
    # register key and mouse event handlers
    win.push_handlers(on_key_press)
    win.push_handlers(on_mouse_press)
    win.push_handlers(on_resize)

    # create a world for agents
    world = World(500, 500)
    # add one agent
    world.agents.append(Agent(world))
    # unpause the world ready for movement
    world.paused = False

    while not win.has_exit:
        win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # show nice FPS bottom right (default)
        delta = clock.tick()
        world.update(delta)
        world.render()
        fps_display.draw()
        # swap the double buffer
        win.flip()