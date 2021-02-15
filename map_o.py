import pygame
import math
import numpy as np
from pygame.locals import *
        

class Map():
    def __init__(self, window, colour, points, width):
        self.window = window
        self.colour = colour
        self.width = width

        self.points = points
        self.lines = []

        self.track_length = 0
        for point in range(len(self.points)):
            if point == len(self.points) - 1:
                self.lines.append(self.points[0] - self.points[point])
            else:
                self.lines.append(self.points[point + 1] - self.points[point])
            self.track_length += np.sqrt((self.lines[len(self.lines)-1]).dot(self.lines[len(self.lines)-1]))

        vector = self.points[1] - self.points[0]
        vector /= np.sqrt(vector.dot(vector))
        if (vector[1] >= 0):
            self.start_ang = np.arccos(vector.dot(np.array([1,0])))
        else:
            self.start_ang = np.arccos(-vector.dot(np.array([1,0])))

    def render(self):
        for point in self.points:
            pygame.draw.circle(self.window, self.colour, point, int(self.width/2))
        for point in range(len(self.points)-1):
            vector = self.points[point+1] - self.points[point]
            vector /= np.sqrt(vector.dot(vector))
            normal = np.array([-vector[1], vector[0]])
            poly_points = [self.points[point] + normal*self.width/2, self.points[point] - normal*self.width/2,
                           self.points[point+1] - normal*self.width/2, self.points[point+1] + normal*self.width/2]
            pygame.draw.polygon(self.window, self.colour, poly_points)


    def on_track(self, coords):
        on_track = True
        for coord in coords:
            for point in range(len(self.points)):
                line_v = self.lines[point]
                line_s = self.points[point]
                mu = (line_v[0]*(coord[0] - line_s[0]) + line_v[1]*(coord[1] - line_s[1])) / (line_v[0]**2 + line_v[1]**2)

                vector = coord - line_s - mu * line_v
                distance = np.sqrt((vector).dot(vector))
                if distance > self.width/2 and mu > 0 and mu < 1:
                    on_track = False

        return on_track

    def progress(self, coord):
        progress = 0
        for point in range(len(self.points)):
            line_v = self.lines[point]
            line_s = self.points[point]
            
            mu = (line_v[0]*(coord[0] - line_s[0]) + line_v[1]*(coord[1] - line_s[1])) / (line_v[0]**2 + line_v[1]**2)

            fringe = self.width / 2 / np.sqrt((line_v).dot(line_v))

            vector = coord - line_s - mu * line_v
            distance = np.sqrt((vector).dot(vector))
            
            if mu <= -fringe or mu >= 1 + fringe or distance > self.width/2:
                progress += np.sqrt((line_v).dot(line_v))
            else:
                vector = mu * line_v
                progress += np.sqrt((vector).dot(vector))
                break
            

        progress /= self.track_length

        return progress

    def get_start_ang(self):
        return self.start_ang

    def get_points(self):
        return self.points
                

        
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
