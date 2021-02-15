import const
import time
import pygame
import math
import numpy as np
import car_o
import map_o
import pygame_ui
from pygame.locals import *

def sort_cars(cars):
    temp_cars = cars[:]
    sorted_cars = []
    for i in range(len(cars)):
        highest, index = find_top_car(temp_cars)
        sorted_cars.append(highest)
        temp_cars.pop(index)
    sorted_cars.reverse()

    return sorted_cars


def find_top_car(cars):
    highest = cars[0]
    index = 0
    for car in range(len(cars)):
        if cars[car].get_progress() > highest.get_progress():
            highest = cars[car]
            index = car

    return highest, index

def next_gen_cars(window, cars, track):
    car_num = len(cars)
    
    #Create an array of parents
    parents = []
    for i in range(int(3*car_num/10)):
        parents.append(cars[int(7*car_num/10) + i])

    #Copy cars to a new array
    asp_ratio = window.get_size()[1] / const.BASE_RES
    start_ang = track.get_start_ang()
    new_cars = []
    for car in range(car_num):
        new_cars.append(car_o.Car(window, [asp_ratio*300, asp_ratio*300], 10, start_ang))

    for car in range(car_num):
        new_cars[car].set_biases(cars[car].get_biases())
        new_cars[car].set_weights(cars[car].get_weights())        

    #Replace least performing cars with children of parents and mutate
    for car in range(len(parents)):
        new_cars[car].crossover(parents[car], parents[len(parents)-1-car])
        new_cars[car].mutate_biases()
        new_cars[car].mutate_weights()
            
    return new_cars

def get_track_points(file, asp_ratio):
    track_points = []
    f = open("data\{}".format(file), "r")
    for line in f:
        point = line.split()
        track_points.append(asp_ratio*np.array([int(point[0]), int(point[1])]))
    return track_points

def write_snapshot(cars):
    f = open("data\snapshot", "w")
    f.close()
    f = open("data\snapshot", "a")

    for car in range(int(len(cars) - len(cars)/10), len(cars)):
        f.write("NETWORK_{}\n".format(car))
        weights = cars[car].get_weights()
        biases = cars[car].get_biases()
        f.write(str(weights))
        f.write("\n")
        f.write(str(biases))
        f.write("\n")
    
    f.close()


#----------------------------------------------------------------------------------------------------------------------------------
def race(window, clock, action, mouse_used):
    paused = False
    display_debug = True
    car_debug = False
    simulating = True
    gen_time = 0
    gen = 0
    car_num = 100
    cars = [] 
    f = open("data/average_progress", "w")
    f.write("AVG_PROGRESS")
    f.close()
    f = open("data/average_progress", "a")

    asp_ratio = window.get_size()[1] / const.BASE_RES
    track_points = get_track_points("track2", asp_ratio)
    track = map_o.Map(window, const.COL["light_grey"], track_points, 100)

    start_ang = track.get_start_ang()
    for car in range(car_num):
        cars.append(car_o.Car(window, track_points[0], 10, start_ang))
    
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
                for car in cars:
                    if not car.get_crashed():
                        car.find_distances()
                        car.inputs(frame_time)
                        car.dynamics(frame_time)
                        car.find_progress(track)
                        car.crash_check()

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
            f.write("\n")
            f.write(str(average_progress))
            
            cars = sort_cars(cars)
            write_snapshot(cars)
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
        
    f.close()
    return action, mouse_used

#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
