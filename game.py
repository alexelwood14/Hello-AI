import const
import pygame
import math
import numpy as np
import car_o
import map_o
import pygame_ui
from pygame.locals import *

def menu():
    pass


def find_top_cars(cars):
    temp_cars = cars[:]
    top_cars = []
    for i in range(5):
        highest, index = find_top_car(temp_cars)
        top_cars.append(highest)
        temp_cars.pop(index)

    return top_cars


def find_top_car(cars):
    highest = cars[0]
    index = -1
    for car in range(len(cars)):
        if cars[car].get_progress() > highest.get_progress():
            highest = cars[car]
            index = car

    return highest, index


def next_gen_cars(top_cars, window, cars):
    cars = []
    asp_ratio = window.get_size()[1] / const.BASE_RES
    for i in range(50):
        cars.append(car_o.Car(window, [asp_ratio*300, asp_ratio*300], 10))

    for car in range(len(top_cars)):
        for i in range(10):
            cars[(car * 10) + i].set_biases(top_cars[car].get_biases())
            cars[(car * 10) + i].set_weights(top_cars[car].get_weights())

    return cars

#----------------------------------------------------------------------------------------------------------------------------------
def race(window, clock, action, mouse_used):
    paused = False
    display_debug = True
    car_debug = False
    simulating = True
    gen_time = 0
    gen = 0
    cars = [] 

    asp_ratio = window.get_size()[1] / const.BASE_RES

    track_points = [asp_ratio*np.array([300, 300]), asp_ratio*np.array([1620, 300]),
                    asp_ratio*np.array([1620, 800]), asp_ratio*np.array([300, 800])]

    track_1 = map_o.Map(window, const.COL["light_grey"], track_points, 100)

    for car in range(50):
        cars.append(car_o.Car(window, [asp_ratio*300, asp_ratio*300], 10))

    while action == "race":
        window.fill(const.COL["black"])
        frame_time = clock.tick() / 1000
        if not paused:
            gen_time += frame_time
        if gen_time >= 10:
            pass
            #simulating = False

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
                    action = "main"
                
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
 
        #Track Processing
        track_1.render()

        #Car Processing
        if simulating:
            if not paused:
                for car in cars:
                    if not car.get_crashed():
                        car.find_distances()
                        car.inputs(frame_time)
                        car.dynamics(frame_time)
                        car.find_progress(track_1)
                        car.crash_check()

            for car in cars:
                car.render()

            simulating = False
            for car in cars:
                if not car.get_crashed():
                    simulating = True
            
        else:
            average_progress = 0
            for car in cars:
                if car.get_progress() < 0 or car.get_progress() > 0.5:
                    print("error")
                    print(car.get_progress())
            
            top_cars = find_top_cars(cars)
            cars = next_gen_cars(top_cars, window, cars)

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
