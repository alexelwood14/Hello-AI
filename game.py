import const
import time
import pygame
import numpy as np
import ai
import map_o
import pygame_ui
from pygame.locals import *


def get_track_points(file, asp_ratio):
    f = open("data\{}".format(file), "r")
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


#----------------------------------------------------------------------------------------------------------------------------------
def race(window, clock, action, mouse_used):
    paused = False
    display_debug = True
    simulating = True
    gen_time = 0
    gen = 0
    agents_num = 100
    cars = [] 
    f = open("data/average_progress", "w")
    f.write("AVG_PROGRESS")
    f.close()

    asp_ratio = window.get_size()[1] / const.BASE_RES
    track_points = get_track_points("track1", asp_ratio)
    track = map_o.Map(window, const.COL["light_grey"], track_points, 100)

    race_ai = ai.AI(window, track, agents_num) 
    
    while action == const.MODE.RACE:
        window.fill(const.COL["black"])
        frame_time = clock.tick() / 1000
        if not paused:
            gen_time += frame_time
        if gen_time >= 30:
            simulating = False

        #process inputs
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
 
        #Track Processing
        track.render()

        #Car Processing
        if simulating:
            if not paused:
                race_ai.run(frame_time)

            for car in range(len(cars)):
                if car % (car_num/25) == 0:
                    cars[car].render()

            simulating = False
            for car in cars:
                if not car.get_crashed():
                    simulating = True
            
        else:
            average_progress = 0
            for car in cars:
                if car.get_progress() < 0:
                    print("error")
                    print(car.get_progress())

                average_progress += car.get_progress()
            average_progress /= len(cars)

            f = open("data/average_progress", "a")
            f.write("\n")
            f.write(str(average_progress))
            f.close()
            
            cars = sort_cars(cars)
            race_ai.write_snapshot(cars)
            cars = next_gen_cars(window, cars, track)

            gen += 1
            simulating = True
            gen_time = 0


        #Display debug info
        if display_debug:
            pygame_ui.draw_text(window, "fps: {}".format(str(int(clock.get_fps()))),
                      [window.get_size()[0]/32, window.get_size()[1]/14], int(window.get_size()[0]/72), const.COL["white"], "calibri", "ml")
            pygame_ui.draw_text(window, "generation {}".format(str(gen)),
                      [window.get_size()[0]/32, window.get_size()[1]/10], int(window.get_size()[0]/72), const.COL["white"], "calibri", "ml")

        pygame.display.update()
        
    
    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
