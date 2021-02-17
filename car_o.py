import const
import pygame
import math
import map_o
import ai
import numpy as np
from pygame.locals import *

class Wheel():
    def __init__(self, window, colour, pos, size):
        self.window = window
        self.colour = colour
        self.size = size
        self.pos = np.matrix([[pos[0]],
                              [pos[1]]])
        self.ang = 0.0
        self.mat = np.matrix([[math.cos(self.ang), -math.sin(self.ang)],
                              [math.sin(self.ang),  math.cos(self.ang)]])

        self.points_mat = np.matrix([[-self.size / 2,  self.size / 2, self.size / 2, -self.size / 2],
                                     [-self.size,     -self.size,     self.size,      self.size]])

    def render(self):
        points = np.asarray(np.transpose(np.matmul(self.mat, self.points_mat) + self.pos))
        pygame.draw.polygon(self.window, self.colour, points)


    def set_pos(self, pos):
        self.pos = np.matrix([[pos[0]],
                              [pos[1]]])

    def set_ang(self, ang):
        self.ang = ang
        self.mat = np.matrix([[math.cos(self.ang), -math.sin(self.ang)],
                              [math.sin(self.ang),  math.cos(self.ang)]])


#----------------------------------------------------------------------------------------------------------------------------------

class Car():
    def __init__(self, window, pos, size, ang):
        self.window = window
        self.size = size
        self.crashed = False
        self.progress = 0
        self.manual = False

        #Setup AI
        self.ai = ai.Neural_Network(window, 9, [10, 10], 4)

        #Setup dynamic attributes
        self.pos = pos
        self.speed = 0.0
        self.vel = np.matrix([[0.0],[0.0]])
        self.acc = 0.0
        self.term_speed = 200*window.get_size()[1]/const.BASE_RES 

        self.ang = math.pi * 3 / 2
        self.ang_mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                   [math.sin(self.ang), math.cos(self.ang)]])

        self.wheel_vel = 0.0
        self.wheel_ang = 0.00001
        self.max_wheel_ang = math.pi/6

        #Setup geometry matrix
        self.points_mat = np.matrix([[-self.size,      self.size,     self.size,    -self.size],
                                     [-self.size*2.5, -self.size*2.5, self.size*2.5, self.size*2.5]])
        self.points_mat = np.matmul(self.ang_mat, self.points_mat)
        self.points_mat += self.pos

        #Default wheel positions
        self.wheel_pos = np.matrix([[-self.size,      self.size,     self.size,    -self.size,     0,              0], 
                                    [-self.size*1.6, -self.size*1.6, self.size*1.6, self.size*1.6, self.size*1.6, -self.size*1.6]])

        #Setup steering normals
        self.front_axel = self.pos + np.matrix([[0.0], [self.size * 1.6]])
        self.rear_axel = self.pos + np.matrix([[0.0], [-self.size * 1.6]])
        self.turning_point = np.matrix([[0.0], [0.0]])

        #Setup normals
        self.front_norm = np.matmul(self.ang_mat, np.matrix([[1.0], [0.0]]))
        self.rear_norm = np.matmul(self.ang_mat, np.matrix([[1.0], [0.0]]))
        self.anti_rear_norm = np.matmul(self.ang_mat, np.matrix([[-1.0], [0.0]]))
        self.direcion_norm = np.matmul(self.ang_mat, np.matrix([[0.0], [1.0]]))
        self.ne_ray = np.matmul(self.ang_mat, np.matrix([[1.0], [1.0]]))
        self.nw_ray = np.matmul(self.ang_mat, np.matrix([[-1.0], [1.0]]))

        #Set location of wheels
        self.wheels = []
        self.wheels.append(Wheel(window, const.COL["grey"], [self.pos.item(0) - self.size, self.pos.item(1) - self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, const.COL["grey"], [self.pos.item(0) + self.size, self.pos.item(1) - self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, const.COL["grey"], [self.pos.item(0) + self.size, self.pos.item(1) + self.size * 1.6], size / 3))
        self.wheels.append(Wheel(window, const.COL["grey"], [self.pos.item(0) - self.size, self.pos.item(1) + self.size * 1.6], size / 3))


#----------------------------------------------------------------------------------------------------------------------------------

    def manual_input(self, frame_time):
        pressed = pygame.key.get_pressed()

        #Rotation inputs
        if (pressed[pygame.K_a] and not pressed[pygame.K_d]) or (not pressed[pygame.K_a] and pressed[pygame.K_d]):
            if pressed[pygame.K_a] and not pressed[pygame.K_d]:
                self.wheel_vel = -2
            elif not pressed[pygame.K_a] and pressed[pygame.K_d]:
                self.wheel_vel = 2
            
        else:
            if self.wheel_ang > 0.01:
                self.wheel_vel = -2
            elif self.wheel_ang < -0.01:
                self.wheel_vel = 2
            else:
                self.wheel_vel = 0

        #Limit rotation angle to maximum
        self.wheel_ang += self.wheel_vel * frame_time
        if self.wheel_ang > self.max_wheel_ang:
            self.wheel_ang = self.max_wheel_ang
        elif self.wheel_ang < -self.max_wheel_ang:
            self.wheel_ang = -self.max_wheel_ang

        
        #Translation inputs
        if pressed[pygame.K_w] and not pressed[pygame.K_s]:
            self.acc = 100
        elif not pressed[pygame.K_w] and pressed[pygame.K_s]:
            self.acc = -100
        else:
            if self.speed > 0.0001:
                self.acc = -50
            elif self.speed < 0.0001:
                self.acc = 50
            else:
                self.acc = 0

        #Limit speed to terminal speed
        if self.speed > self.term_speed:
            self.speed = self.term_speed
        elif self.speed < -self.term_speed/3:
            self.speed = -self.term_speed/3


    def network_input(self, frame_time):
        #Calculate network speed inputs
        if self.speed >= 0:
            speed_forwards = self.speed / self.term_speed
            speed_backwards = 0.0
        else:
            speed_forwards = 0.0
            speed_backwards = self.speed / self.term_speed/3

        #Calculate network turning inputs
        if self.wheel_ang >= 0:
            wheel_right = self.wheel_ang / self.max_wheel_ang
            wheel_left = 0.0
        else:
            wheel_right = 0.0
            wheel_left = self.wheel_ang / self.max_wheel_ang
            
        inputs = self.ai.process([speed_forwards, speed_backwards, wheel_right, wheel_left,
                                  self.forward_dist, self.right_dist, self.left_dist, self.ne_dist, self.nw_dist])

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
            

#----------------------------------------------------------------------------------------------------------------------------------
    def inputs(self, frame_time):
        if self.manual:
            self.manual_input(frame_time)
        else:
            self.network_input(frame_time)


    def dynamics(self, frame_time):  
        #Recalculate wheel positions
        wheel_pos = np.matmul(self.ang_mat, self.wheel_pos)

        #Find axel pivot points
        self.front_axel = wheel_pos[:, [4]]
        self.rear_axel = wheel_pos[:, [5]]

        #Recalculate wheel matrix
        self.front_mat = np.array([[math.cos(self.wheel_ang + self.ang), -math.sin(self.wheel_ang + self.ang)],
                                [math.sin(self.wheel_ang + self.ang), math.cos(self.wheel_ang + self.ang)]])
        
        #Calculate wheel normals and direction normal
        self.front_norm = np.matmul(self.front_mat, np.matrix([[1.0], [0.0]]))
        self.rear_norm = np.matmul(self.ang_mat, np.matrix([[1.0], [0.0]]))
        self.anti_rear_norm = np.matmul(self.ang_mat, np.matrix([[-1.0], [0.0]]))
        self.direcion_norm = np.matmul(self.ang_mat, np.matrix([[0.0], [1.0]]))
        self.ne_ray = np.matmul(self.ang_mat, np.matrix([[1.0], [1.0]]))
        self.nw_ray = np.matmul(self.ang_mat, np.matrix([[-1.0], [1.0]]))

        #Find turing point
        if (self.rear_norm.item(0) * self.front_norm.item(1) - self.rear_norm.item(1) * self.front_norm.item(0)) != 0:
            mu = ((self.rear_norm.item(0)*(self.rear_axel.item(1) - self.front_axel.item(1)) - self.rear_norm.item(1)*(self.rear_axel.item(0) - self.front_axel.item(0)))
                  / (self.rear_norm.item(0) * self.front_norm.item(1) - self.rear_norm.item(1) * self.front_norm.item(0)))
            self.turning_point = self.front_axel + mu * self.front_norm + self.pos
        else:
            mu = 100000
            self.turning_point = self.rear_axel + mu * self.rear_norm + self.pos

        #Move car geomery away from turning point
        self.points_mat = self.points_mat - self.turning_point

        
        #Calculate rotation angle
        vector = self.pos - self.turning_point
        radius = (np.sqrt(np.matmul(np.transpose(vector), vector))).item()
        self.speed += self.acc * frame_time
        displacement = self.speed * frame_time
        angle = displacement / radius
        if self.wheel_ang < 0:
            angle *= -1
        self.ang += angle
        self.ang_mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                 [math.sin(self.ang), math.cos(self.ang)]])
        translation_mat = np.array([[math.cos(angle), -math.sin(angle)],
                                    [math.sin(angle), math.cos(angle)]])

        #Apply translation matrix
        self.points_mat = np.matmul(translation_mat, self.points_mat)

        #Move car geometry back from turning point
        self.points_mat = self.points_mat + self.turning_point

        #Update position based on average points
        self.pos = np.matrix([[(self.points_mat.item((0,0)) + self.points_mat.item((0,1)) + self.points_mat.item((0,2)) + self.points_mat.item((0,3))) / 4],
                              [(self.points_mat.item((1,0)) + self.points_mat.item((1,1)) + self.points_mat.item((1,2)) + self.points_mat.item((1,3))) / 4]])

        #Recalculate wheel positions
        wheel_pos = np.matmul(self.ang_mat, self.wheel_pos)
        
        #Apply new wheel_positions
        self.wheels[0].set_pos([wheel_pos.item((0,0)) + self.pos.item(0), wheel_pos.item((1,0)) + self.pos.item(1)])
        self.wheels[1].set_pos([wheel_pos.item((0,1)) + self.pos.item(0), wheel_pos.item((1,1)) + self.pos.item(1)])
        self.wheels[2].set_pos([wheel_pos.item((0,2)) + self.pos.item(0), wheel_pos.item((1,2)) + self.pos.item(1)])
        self.wheels[3].set_pos([wheel_pos.item((0,3)) + self.pos.item(0), wheel_pos.item((1,3)) + self.pos.item(1)])

        #Apply new wheel rotations
        self.wheels[0].set_ang(self.ang)
        self.wheels[1].set_ang(self.ang)
        self.wheels[2].set_ang(self.wheel_ang + self.ang)
        self.wheels[3].set_ang(self.wheel_ang + self.ang)


    def render(self):
        for wheel in self.wheels:
            wheel.render()

        points = np.asarray(np.transpose(self.points_mat))
        pygame.draw.polygon(self.window, const.COL["red"], points)


#----------------------------------------------------------------------------------------------------------------------------------
    def crash_check(self):
        if (self.window.get_at([int(self.points_mat.item((0,0))), int(self.points_mat.item((1,0)))])[0] == 0 or
            self.window.get_at([int(self.points_mat.item((0,1))), int(self.points_mat.item((1,1)))])[0] == 0 or
            self.window.get_at([int(self.points_mat.item((0,2))), int(self.points_mat.item((1,2)))])[0] == 0 or
            self.window.get_at([int(self.points_mat.item((0,3))), int(self.points_mat.item((1,3)))])[0] == 0):
            self.crashed = True
        else:
            self.crashed = False


    def find_distances(self):
        #Calculate distance to wall in front of car
        forward_pos = self.iterate_distance(self.direcion_norm, self.pos, const.COL["light_grey"][0], 100, 1)
        vector = self.pos - forward_pos
        self.forward_dist = (np.sqrt(np.matmul(np.transpose(vector), vector)) / const.BASE_RES).item()
        
        #Calculate distance to wall left of car
        left_pos = self.iterate_distance(self.rear_norm, self.pos, const.COL["light_grey"][0], 10, 1)
        vector = self.pos - left_pos
        self.left_dist = (np.sqrt(np.matmul(np.transpose(vector), vector)) / const.BASE_RES).item()
        
        #Calculate distance to wall right of car
        right_pos = self.iterate_distance(self.anti_rear_norm, self.pos, const.COL["light_grey"][0], 10, 1)
        vector = self.pos - right_pos
        self.right_dist = (np.sqrt(np.matmul(np.transpose(vector), vector)) / const.BASE_RES).item()

        ne_pos = self.iterate_distance(self.ne_ray, self.pos, const.COL["light_grey"][0], 10, 1)
        vector = self.pos - ne_pos
        self.ne_dist = (np.sqrt(np.matmul(np.transpose(vector), vector)) / const.BASE_RES).item()

        nw_pos = self.iterate_distance(self.nw_ray, self.pos, const.COL["light_grey"][0], 10, 1)
        vector = self.pos - nw_pos
        self.nw_dist = (np.sqrt(np.matmul(np.transpose(vector), vector)) / const.BASE_RES).item()


    #Recursive method for finding the distance from the car to a wall
    def iterate_distance(self, vector, start_pos, start_colour, incriment_length, direction):

        #Stopping condition is that the inctiment is less than 1 pixel
        if incriment_length > 1:
            if start_pos[0] < self.window.get_size()[0] and start_pos[0] >= 0 and start_pos[1] < self.window.get_size()[1] and start_pos[1] >= 0: 
                colour = self.window.get_at([int(start_pos[0]), int(start_pos[1])])[0]
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
            
#----------------------------------------------------------------------------------------------------------------------------------        
    def display_debug(self):
        pygame.draw.line(self.window, const.COL["yellow"], self.pos + self.rear_axel + 10000 * self.rear_norm,
                         self.pos + self.rear_axel - 10000 * self.rear_norm)
        pygame.draw.line(self.window, const.COL["yellow"], self.pos + self.front_axel + 10000 * self.front_norm,
                         self.pos + self.front_axel - 10000 * self.front_norm)
        pygame.draw.circle(self.window, const.COL["blue"], [int(self.turning_point[0]), int(self.turning_point[1])], 3)
        

    def find_progress(self, track):
        self.progress = track.progress(self.pos)
        

    def get_crashed(self):
        return self.crashed
    

    def set_ang(self, ang):
        self.ang = ang
        self.ang_mat = np.array([[math.cos(self.ang), -math.sin(self.ang)],
                                   [math.sin(self.ang), math.cos(self.ang)]])


    def get_points_mat(self):
        return self.points_mat


    def set_crashed(self, crashed):
        self.crashed = crashed


    def get_pos(self):
        return self.pos


    def get_progress(self):
        return self.progress
    

    def set_biases(self, biases):
        self.ai.set_biases(biases)
        

    def set_weights(self, weights):
        self.ai.set_weights(weights)
        

    def get_biases(self):
        return self.ai.get_biases()
    

    def get_weights(self):
        return self.ai.get_weights()

    def mutate_biases(self):
        self.ai.mutate_biases()

    def mutate_weights(self):
        self.ai.mutate_weights()

    def crossover(self, parent1, parent2):
        self.ai.crossover(parent1, parent2)
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
