import const
import neural_network
import car_o
import numpy as np

class AI():
    def __init__(self, window, track, agents_num):
        self.window = window
        self.agents = []
        self.agents_num = agents_num
        self.shape = [9, [10], 4]
        self.track = track
        for i in range(self.agents_num):
            self.agents.append(Agent(self.window, self.track, self.shape))

    
    def sort_cars(self, cars):
        temp_cars = cars[:]
        sorted_cars = []
        for i in range(len(cars)):
            highest, index = self.find_top_car(temp_cars)
            sorted_cars.append(highest)
            temp_cars.pop(index)
        sorted_cars.reverse()

        return sorted_cars

    
    def find_top_car(self, cars):
        highest = cars[0]
        index = 0
        for car in range(len(cars)):
            if cars[car].get_progress() > highest.get_progress():
                highest = cars[car]
                index = car

        return highest, index


    def next_gen_cars(self, window, cars, track):
        car_num = len(cars)
        
        #Create an array of parents
        parents = []
        for i in range(int(car_num/10)):
            parents.append(cars[int(9*car_num/10) + i])

        #Copy cars to a new array
        start_ang = track.get_start_ang()
        new_cars = []
        for car in range(car_num):
            new_cars.append(car_o.Car(window, track.get_points()[:, [0]], 10, start_ang))

        for car in range(car_num):
            new_cars[car].set_biases(cars[car].get_biases())
            new_cars[car].set_weights(cars[car].get_weights())        

        #Replace least performing cars with children of parents and mutate
        for i in range(3):
            for car in range(len(parents)):
                new_cars[car + (i*10)].set_biases(parents[car].get_biases())
                new_cars[car + (i*10)].set_weights(parents[car].get_weights())        
                new_cars[car + (i*10)].mutate_biases()
                new_cars[car + (i*10)].mutate_weights()
                
        return new_cars

    
    def write_snapshot(self, cars):
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

    def run(self, frame_time):
        for agent in self.agents:
            agent.run(frame_time)


class Agent():
    def __init__(self, window, track, shape):
        self.window = window
        self.track = track
        self.shape = shape
        self.car = car_o.Car(self.window, self.track, 10)
        self.neural_net = neural_network.Neural_Network(self.window, self.shape)

    def run(self, frame_time):
        if not self.car.get_crashed():
            self.car.find_distances()
            inputs = self.car.network_inputs(frame_time)
            outputs = self.neural_net.process(inputs)
            self.car.network_outputs(outputs, frame_time)
            self.car.dynamics(frame_time)
            self.car.find_progress(self.track)
            self.car.crash_check()
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
