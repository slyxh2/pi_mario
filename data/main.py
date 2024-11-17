__author__ = 'justinarmstrong'

from . import setup,tools
from .states import main_menu,load_screen,level1
from . import constants as c
from .pi import sensor_factory

import _thread

def main():
    """Add states to control here."""
    run_it = tools.Control(setup.ORIGINAL_CAPTION)

    sensor = sensor_factory.SensorFactory(run_it)

    state_dict = {c.MAIN_MENU: main_menu.Menu(),
                  c.LOAD_SCREEN: load_screen.LoadScreen(),
                  c.TIME_OUT: load_screen.TimeOut(),
                  c.GAME_OVER: load_screen.GameOver(),
                  c.LEVEL1: level1.Level1()}

    run_it.setup_states(state_dict, c.MAIN_MENU)

    try:
       _thread.start_new_thread(sensor.detect_motion_sensor, ())
    except:
       print ("Error")
       
    run_it.main()





