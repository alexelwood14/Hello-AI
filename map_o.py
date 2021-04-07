import pygame
import numpy as np
from pygame.locals import *
        

class Map():
    def __init__(self, window, colour, points, width):
        self.window = window
        self.colour = colour
        self.width = width

        self.__points = points
        self.__lines = self.__points[:, [1]] - self.__points[:, [0]]

        self.track_length = 0
        for point in range(1, np.shape(self.__points)[1]-1):
            new_line = self.__points[:, [point + 1]] - self.__points[:, [point]]
            self.__lines = np.concatenate((self.__lines, new_line), 1)
            self.track_length += np.linalg.norm(new_line)

        vector = self.__lines[:, [0]]
        vector /= np.linalg.norm(vector)
        if (vector.item(1) < 0):
            self.__start_ang = np.arccos(-np.matmul(np.array([1,0]), vector).item())
        else:
            self.__start_ang = np.arccos(np.matmul(np.array([1,0]), vector).item())

        self.poly_points = []
        for point in range(np.shape(self.__points)[1]-1):
            vector = self.__points[:, [point+1]] - self.__points[:, [point]]
            vector /= np.linalg.norm(vector)
            normal = np.array([[-vector.item(1)], 
                               [ vector.item(0)]])
            new_poly = [self.__points[:, [point]] + normal*self.width/2, self.__points[:, [point]] - normal*self.width/2,
                        self.__points[:, [point+1]] - normal*self.width/2, self.__points[:, [point+1]] + normal*self.width/2]
            for point in range(len(new_poly)):
                new_poly[point] = [new_poly[point].item(0), new_poly[point].item(1)]
            self.poly_points.append(new_poly)
        
    def render(self):
        for point in range(np.shape(self.__points)[1]):
            point = [self.__points[:,[point]].item(0), self.__points[:,[point]].item(1)]
            pygame.draw.circle(self.window, self.colour, point, int(self.width/2))
        for poly in self.poly_points:
            pygame.draw.polygon(self.window, self.colour, poly)

    def on_track(self, coords):
        on_track = True
        for coord in coords:
            for point in range(len(self.__points)):
                line_v = self.__lines[point]
                line_s = self.__points[point]
                mu = (line_v[0]*(coord[0] - line_s[0]) + line_v[1]*(coord[1] - line_s[1])) / (line_v[0]**2 + line_v[1]**2)

                vector = coord - line_s - mu * line_v
                distance = np.linalg.norm(vector)
                if distance > self.width/2 and mu > 0 and mu < 1:
                    on_track = False

        return on_track

    def progress(self, coord):
        progress = 0
        for point in range(len(self.__points)):
            line_v = self.__lines[:, [point]]
            line_s = self.__points[:, [point]]
            
            mu = (line_v.item(0)*(coord.item(0) - line_s.item(0)) + line_v.item(1)*(coord.item(1) - line_s.item(1))) / (line_v.item(0)**2 + line_v.item(0)**2)

            fringe = self.width / 2 / np.linalg.norm(line_v)

            distance = np.linalg.norm(coord - line_s - mu * line_v)
            
            if mu <= -fringe or mu >= 1 + fringe or distance > self.width/2:
                progress += np.sqrt(np.matmul(np.transpose(line_v), line_v)).item()
            else:
                progress += np.linalg.norm(mu * line_v)
                break
            
        progress /= self.track_length
        return progress.item()

    @property
    def start_ang(self):
        return self.__start_ang

    @property
    def points(self):
        return self.__points

    @property
    def start(self):
        return self.__points[:,[0]]