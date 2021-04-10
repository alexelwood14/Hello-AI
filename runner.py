import const
import pygame
import numpy as np
import ai
import map_o
import pygame_ui
from pygame.locals import *

class Runner():
    __instance = None

    def __init__(self, window, ai_mode, snapshot):
        self.window = window
        self.running = True
        self.paused = False
        self.display_debug = True
        self.gen_over = False
        self.gen_time = 0
        self.track = map_o.Map(window, "track3", const.COL["light_grey"], 100)

        agents_num = 100
        self.race_ai = ai.AI(window, self.track, agents_num, ai_mode, snapshot)
        
        if Runner.__instance is None:
            Runner.__instance = self
        else:
            raise Exception('Singleton instance already exists')

    @staticmethod
    def instance(window, ai_mode, snapshot):
        if not Runner.__instance:
            Runner(window, ai_mode, snapshot)
        return Runner.__instance

    @staticmethod
    def debug(window, clock, gen):
        pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                [window.get_size()[0]/32, window.get_size()[1]/14], int(window.get_size()[0]/72), const.COL["white"], "calibri", "ml")
        pygame_ui.draw_text(window, "generation {}".format(str(gen)),
                [window.get_size()[0]/32, window.get_size()[1]/10], int(window.get_size()[0]/72), const.COL["white"], "calibri", "ml")

    def parse_keyboard_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if self.display_debug:
                        self.display_debug = False
                    else:
                        self.display_debug = True
                if event.key == K_p:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True
                if event.key == K_x:
                    self.gen_over = True
                if event.key == K_m:
                    self.running = False                
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()

    def run(self, clock):
        while self.running:
            self.window.fill(const.COL["black"])
            frame_time = clock.tick() / 1000

            if not self.paused:
                self.gen_time += frame_time
            if self.gen_time >= 30:
                self.gen_over = True

            # Parse and act on keyboard inputs
            self.parse_keyboard_input()
    
            self.track.render()

            # Call functions to control AI
            if self.race_ai.gen_over() or self.gen_time >= 30 or self.gen_over:
                self.race_ai.next_gen()
                self.gen_over = False
                self.gen_time = 0
            elif not self.paused:
                self.race_ai.run(frame_time)

            self.race_ai.render()                

            # Display debug infomation
            if self.display_debug:
                self.debug(self.window, clock, self.race_ai.gen)

            pygame.display.update()

        return const.MODE.MAIN