import const
import time
import pygame
import numpy as np
import ai
import map_o
import pygame_ui
from pygame.locals import *

class Runner():
    __instance = None

    def __init__(self):
        if Runner.__instance is None:
            Runner.__instance = self
        else:
            raise Exception('Singleton instance already exists')

    @staticmethod
    def instance():
        if not Runner.__instance:
            Runner()
        return Runner.__instance
    
    def get_track_points(self, file, asp_ratio):
        with open("data\\{}".format(file), "r") as f:
            line = f.readline()
            point = line.split()
            track_points = asp_ratio * np.matrix([[int(point[0])],
                                                [int(point[1])]])
            for l in f:
                point = l.split()
                point = asp_ratio * np.matrix([[int(point[0])],
                                            [int(point[1])]])
                track_points = np.concatenate((track_points, point), 1)
            return track_points

    def run(self, window, clock, mode, ai_mode, snapshot, mouse_used):
        paused = True
        display_debug = True
        simulating = True
        wait_time = 0
        gen_time = 1
        agents_num = 100

        asp_ratio = window.get_size()[1] / const.BASE_RES
        track_points = self.get_track_points("track3", asp_ratio)
        track = map_o.Map(window, const.COL["light_grey"], track_points, 100)

        race_ai = ai.AI(window, track, agents_num, ai_mode, snapshot)
        gen = race_ai.gen 
        
        while mode == const.MODE.RACE:
            window.fill(const.COL["black"])
            frame_time = clock.tick() / 1000
            if wait_time > 1:
                paused = False 
            else:
                wait_time += frame_time
            if not paused:
                gen_time += frame_time
            if gen_time >= 30:
                simulating = False

            # Parse and act on keyboard inputs
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_down = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        if display_debug:
                            display_debug = False
                        else:
                            display_debug = True
                    if event.key == K_p:
                        if paused:
                            paused = False
                        else:
                            paused = True
                    if event.key == K_x:
                        simulating = False
                    if event.key == K_m:
                        action = const.MODE.MAIN                
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        quit()
    
            # Track Processing
            track.render()

            # Car Processing
            if simulating:
                if not paused:
                    race_ai.run(frame_time)
                if wait_time > 0.5:
                    race_ai.render()
                if race_ai.gen_over():
                    simulating = False
            else:
                race_ai.write_progress()
                race_ai.write_snapshot(gen)
                race_ai.next_gen()
                gen += 1
                simulating = True
                gen_time = 0
                wait_time = 0
                paused = True

            # Display debug info
            if display_debug:
                pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                        [window.get_size()[0]/32, window.get_size()[1]/14], int(window.get_size()[0]/72), const.COL["white"], "calibri", "ml")
                pygame_ui.draw_text(window, "generation {}".format(str(gen)),
                        [window.get_size()[0]/32, window.get_size()[1]/10], int(window.get_size()[0]/72), const.COL["white"], "calibri", "ml")

            pygame.display.update()
        
        return action, mouse_used