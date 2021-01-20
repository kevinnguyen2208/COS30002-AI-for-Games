from graphics import egi, KEY
from pyglet import window, clock
from pyglet.gl import *

from world import World
from agent import *


def on_key_press(symbol, modifiers):
    if symbol == KEY.P:
        world.paused = not world.paused

    elif symbol in GUN_MODES:
        world.hunter.mode = GUN_MODES[symbol]
    elif symbol == KEY.SPACE:
        world.hunter.aim = not world.hunter.aim
    # Toggle debug force line info on the agent
    elif symbol == KEY.I:
        for agent in world.agents:
            agent.show_info = not agent.show_info


def on_resize(cx, cy):
    world.cx = cx
    world.cy = cy


if __name__ == '__main__':

    # create a pyglet window and set glOptions
    win = window.Window(width=1200, height=800, vsync=True, resizable=True)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # needed so that egi knows where to draw
    egi.InitWithPyglet(win)
    # prep the fps display
    fps_display = window.FPSDisplay(win)
    # register key and mouse event handlers
    win.push_handlers(on_key_press)
    win.push_handlers(on_resize)

    # create a world for agents
    world = World(1200, 800)
    # add one agent
    hunter = Hunter(world)
    hunter.add_waypoint(400, 600)
    hunter.add_waypoint(800, 800)
    hunter.add_waypoint(250, 300)

    world.hunter = hunter
    for i in range(0,10):
        world.preyList.append(Prey(world))
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
