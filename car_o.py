import const
import pygame
import map_o
import numpy as np
from pygame.locals import *


class Wheel():
    def __init__(self, window, colour, pos, size):
        self.window = window
        self.colour = colour
        self.size = size
        self._pos = np.array([[pos[0]],
                              [pos[1]]])
        self._ang = 0.0
        self.mat = np.array([[np.cos(self._ang), -np.sin(self._ang)],
                              [np.sin(self._ang),  np.cos(self._ang)]])

        self.points_mat = np.array([[-self.size / 2,  self.size / 2, self.size / 2, -self.size / 2],
                                     [-self.size,     -self.size,     self.size,      self.size]])

    def render(self):
        points = np.asarray(np.transpose(np.matmul(self.mat, self.points_mat) + self._pos))
        pygame.draw.polygon(self.window, self.colour, points)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = np.array([[pos[0]],
                              [pos[1]]])

    @property
    def ang(self):
        return self._ang

    @ang.setter
    def ang(self, ang):
        self._ang = ang
        self.mat = np.array([[np.cos(self._ang), -np.sin(self._ang)],
                              [np.sin(self._ang),  np.cos(self._ang)]])


class Car():
    def __init__(self, window, track, size, colour=const.COL["red"]):
        self.window = window
        self.size = size
        self.crashed = False
        self._progress = 0
        self.manual = False
        self.track = track
        self.colour = colour

        #Setup dynamic attributes
        self._pos = track.start
        self.speed = 0.0
        self.vel = np.array([[0.0],[0.0]])
        self.acc = 0.0
        self.term_speed = 200*window.get_size()[1]/const.BASE_RES 


        self._ang = track.start_ang + np.pi / 2
        self.ang_mat = np.array([[np.cos(self._ang), -np.sin(self._ang)],
                                 [np.sin(self._ang),  np.cos(self._ang)]])

        self.wheel_vel = 0.0
        self.wheel_ang = 0.0
        self.max_wheel_ang = np.pi/4

        #Setup geometry matrix
        self.points_mat = np.array([[-self.size,      self.size,     self.size,    -self.size],
                                     [-self.size*2.5, -self.size*2.5, self.size*2.5, self.size*2.5]])
        self.points_mat = np.matmul(self.ang_mat, self.points_mat)
        self.points_mat += self._pos

        #Default wheel positions
        self.wheel_pos = np.array([[ self.size,     -self.size,     -self.size,    self.size,     0,              0], 
                                   [-self.size*1.6, -self.size*1.6, self.size*1.6, self.size*1.6, self.size*1.6, -self.size*1.6]])
        self.wheel_pos = np.matmul(self.ang_mat, self.wheel_pos)

        #Setup steering normals
        self.front_axel = self._pos + np.array([[0.0], [self.size * 1.6]])
        self.rear_axel = self._pos + np.array([[0.0], [-self.size * 1.6]])
        self.wheel_base_len = np.linalg.norm(self.rear_axel - self.front_axel)
        self.turning_point = np.array([[0.0], [0.0]])

        #Setup normals
        self.front_norm = np.matmul(self.ang_mat, np.array([[1.0], [0.0]]))
        #[direction norm, rear norm, anti rear norm, ne_ray, nw_ray]
        self.normals = np.matmul(self.ang_mat, np.array([[0.0, 1.0, -1.0,  1.0/np.sqrt(2), -1.0/np.sqrt(2)], 
                                                         [1.0, 0.0,  0.0, -1.0/np.sqrt(2),  1.0/np.sqrt(2)]]))

        #Set location of wheels
        self.wheels = []
        self.wheels.append(Wheel(window, const.COL["grey"], [self._pos.item(0) + self.wheel_pos.item((0,0)), self._pos.item(1) + self.wheel_pos.item((1,0))], size / 3))
        self.wheels.append(Wheel(window, const.COL["grey"], [self._pos.item(0) + self.wheel_pos.item((0,1)), self._pos.item(1) + self.wheel_pos.item((1,1))], size / 3))
        self.wheels.append(Wheel(window, const.COL["grey"], [self._pos.item(0) + self.wheel_pos.item((0,2)), self._pos.item(1) + self.wheel_pos.item((1,2))], size / 3))
        self.wheels.append(Wheel(window, const.COL["grey"], [self._pos.item(0) + self.wheel_pos.item((0,3)), self._pos.item(1) + self.wheel_pos.item((1,3))], size / 3))
        for wheel in self.wheels: 
            wheel.ang = self._ang

    def network_inputs(self, frame_time):
        #Calculate network speed inputs
        if self.speed >= 0:
            speed_forwards = self.speed / self.term_speed
            speed_backwards = 0.0
        else:
            speed_forwards = 0.0
            speed_backwards = self.speed / self.term_speed / 3

        #Calculate network turning inputs
        if self.wheel_ang >= 0:
            wheel_right = self.wheel_ang / self.max_wheel_ang
            wheel_left = 0.0
        else:
            wheel_right = 0.0
            wheel_left = self.wheel_ang / self.max_wheel_ang
            
        inputs = [speed_forwards, speed_backwards, wheel_right, wheel_left,
                  self.distances[0], self.distances[1], self.distances[2], self.distances[3], self.distances[4]]

        return inputs

    def network_outputs(self, inputs, frame_time):
        self.acc = (inputs[0] - inputs[1]) * 200
        self.wheel_vel = (inputs[2] - inputs[3]) * 2

        self.wheel_ang += self.wheel_vel * frame_time
        if self.wheel_ang > self.max_wheel_ang:
            self.wheel_ang = self.max_wheel_ang
        elif self.wheel_ang < -self.max_wheel_ang:
            self.wheel_ang = -self.max_wheel_ang

        #Limit speed to terminal speed
        if self.speed > self.term_speed:
            self.speed = self.term_speed
        elif self.speed < -self.term_speed/3:
            self.speed = -self.term_speed/3
            
    def dynamics(self, frame_time):  
        #Recalculate wheel positions
        #wheel_pos = self.wheel_pos

        #Find axel pivot points
        self.front_axel = self.wheel_pos[:, [4]]
        self.rear_axel = self.wheel_pos[:, [5]]

        #Recalculate wheel matrix
        self.front_mat = np.array([[np.cos(self.wheel_ang + self._ang), -np.sin(self.wheel_ang + self._ang)],
                                [np.sin(self.wheel_ang + self._ang), np.cos(self.wheel_ang + self._ang)]])
        
        #Calculate wheel normals and direction normal
        self.front_norm = np.matmul(self.front_mat, np.array([[1.0], [0.0]]))
        #[direction norm, rear norm, anti rear norm, ne_ray, nw_ray]
        self.normals = np.matmul(self.ang_mat, np.array([[0.0, 1.0, -1.0,  1.0/np.sqrt(2), -1.0/np.sqrt(2)], 
                                                         [1.0, 0.0,  0.0, -1.0/np.sqrt(2),  1.0/np.sqrt(2)]]))

        #Find turing point
        try:
            self.turning_point = self._pos + self.rear_axel + (self.wheel_base_len * self.normals[:, [1]] / -np.tan(self.wheel_ang))
        except ZeroDivisionError:
            self.turning_point = self._pos + self.normals[:, [1]] * 999999

        #Move car geomery away from turning point
        self.points_mat = self.points_mat - self.turning_point

        #Calculate rotation angle
        radius = np.linalg.norm(self._pos - self.turning_point)
        self.speed += self.acc * frame_time
        displacement = self.speed * frame_time
        angle = displacement / radius
        if self.wheel_ang < 0: 
            angle *= -1
        self._ang += angle
        self.ang_mat = np.array([[np.cos(self._ang), -np.sin(self._ang)],
                                 [np.sin(self._ang), np.cos(self._ang)]])
        translation_mat = np.array([[np.cos(angle), -np.sin(angle)],
                                    [np.sin(angle), np.cos(angle)]])

        #Apply translation matrix
        self.points_mat = np.matmul(translation_mat, self.points_mat)

        #Move car geometry back from turning point
        self.points_mat += self.turning_point

        #Update position based on average points
        self._pos = np.average(self.points_mat, 1)

        #Recalculate wheel positions
        self.wheel_pos = np.matmul(translation_mat, self.wheel_pos)
        
        #Apply new wheel_positions
        self.wheels[0].pos = [self.wheel_pos.item((0,0)) + self._pos.item(0), self.wheel_pos.item((1,0)) + self._pos.item(1)]
        self.wheels[1].pos = [self.wheel_pos.item((0,1)) + self._pos.item(0), self.wheel_pos.item((1,1)) + self._pos.item(1)]
        self.wheels[2].pos = [self.wheel_pos.item((0,2)) + self._pos.item(0), self.wheel_pos.item((1,2)) + self._pos.item(1)]
        self.wheels[3].pos = [self.wheel_pos.item((0,3)) + self._pos.item(0), self.wheel_pos.item((1,3)) + self._pos.item(1)]

        #Apply new wheel rotations
        self.wheels[0].ang = self._ang
        self.wheels[1].ang = self._ang
        self.wheels[2].ang = self.wheel_ang + self._ang
        self.wheels[3].ang = self.wheel_ang + self._ang

    def render(self):
        for wheel in self.wheels:
            wheel.render()

        points = np.asarray(np.transpose(self.points_mat))
        pygame.draw.polygon(self.window, self.colour, points)

    def crash_check(self):
        if (self.window.get_at([int(self.points_mat.item((0,0))), int(self.points_mat.item((1,0)))])[0] == 0 or
            self.window.get_at([int(self.points_mat.item((0,1))), int(self.points_mat.item((1,1)))])[0] == 0 or
            self.window.get_at([int(self.points_mat.item((0,2))), int(self.points_mat.item((1,2)))])[0] == 0 or
            self.window.get_at([int(self.points_mat.item((0,3))), int(self.points_mat.item((1,3)))])[0] == 0):
            self.crashed = True
        else:
            self._find_progress()
            self.crashed = False

    def find_distances(self):
        self.distances = []
        for ray in range(np.shape(self.normals)[1]):
            pos = self.iterate_distance(self.normals[:, [ray]], self._pos, const.COL["light_grey"][0], 20, 1)
            self.distances.append(np.linalg.norm(self._pos - pos) / const.BASE_RES)

    #Recursive method for finding the distance from the car to a wall
    def iterate_distance(self, vector, start_pos, start_colour, incriment_length, direction):

        #Stopping condition is that the inctiment is less than 1 pixel
        if incriment_length > 1:
            if start_pos.item(0) < self.window.get_size()[0] and start_pos.item(0) >= 0 and start_pos.item(1) < self.window.get_size()[1] and start_pos.item(1) >= 0: 
                colour = self.window.get_at([int(start_pos.item(0)), int(start_pos.item(1))])[0]
            else:
                colour = 0

            if start_colour != colour:
                direction *= -1
                pos = start_pos + vector * incriment_length * direction
                return self.iterate_distance(vector, pos, colour, incriment_length/2, direction)
            else:            
                pos = start_pos + vector * incriment_length * direction
                return self.iterate_distance(vector, pos, colour, incriment_length, direction)

        else:
            return start_pos
                    
    def display_debug(self):
        pygame.draw.line(self.window, const.COL["yellow"], self._pos + self.rear_axel + 10000 * self.rear_norm,
                         self._pos + self.rear_axel - 10000 * self.rear_norm)
        pygame.draw.line(self.window, const.COL["yellow"], self._pos + self.front_axel + 10000 * self.front_norm,
                         self._pos + self.front_axel - 10000 * self.front_norm)
        pygame.draw.circle(self.window, const.COL["blue"], [int(self.turning_point[0]), int(self.turning_point[1])], 3)
        
    def _find_progress(self):
        self.progress = self.track.progress(self._pos)
    
    @property
    def ang(self):
        return self._ang

    @ang.setter
    def ang(self, ang):
        self._ang = ang
        self.ang_mat = np.array([[np.cos(self._ang), -np.sin(self._ang)],
                                 [np.sin(self._ang), np.cos(self._ang)]])

    @property
    def pos(self):
        return self._pos

    @property
    def progress(self):
        self._find_progress()
        return self._progress

    @progress.setter
    def progress(self, progress):
        self._progress = progress
