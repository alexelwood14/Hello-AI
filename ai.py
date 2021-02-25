import const
import neural_network
import car_o
import numpy as np

class AI():
    def __init__(self, window, track, agents_num):
        self.window = window
        self.agents_num = agents_num
        self.shape = [9, [10], 4]
        self.track = track
        self.agents = []
        for num in range(self.agents_num):
            if num % 4 == 0:
                self.agents.append(Agent(self.window, self.track, self.shape, True))
            else:
                self.agents.append(Agent(self.window, self.track, self.shape))

        with open("logs/average_progress", "w") as f:
            f.write("AVG_PROGRESS")


    def run(self, frame_time):
        for agent in self.agents:
            agent.run(frame_time)


    def render(self):
        for agent in self.agents:
            agent.render()


    def merge(self, a1, a2):
        out = []
        while len(a1) > 0 and len(a2) > 0:
            if a1[0] <= a2[0]:
                out.append(a1[0])
                a1.pop(0)
            else:
                out.append(a2[0])
                a2.pop(0)
        
        if len(a1) == 0:
            out.extend(a2)
        elif len(a2) == 0:
            out.extend(a1)

        return out

    def merge_sort(self, array):
        if len(array) <= 1:
            return array
        middle = int(len(array) / 2)
        r1 = self.merge_sort(array[0 : middle])
        r2 = self.merge_sort(array[middle : len(array)])
        array = self.merge(r1, r2)
        return array


    def next_gen(self):
        self.agents = self.merge_sort(self.agents)

        #Create an array of parents
        parents = []
        for i in range(int(self.agents_num/10)):
            parents.append(self.agents[int(9*self.agents_num/10) + i])

        #Copy cars to a new array
        start_ang = self.track.get_start_ang()
        for agent in range(len(self.agents)):
            self.agents[agent].reset()   

        #Replace least performing cars with children of parents and mutate
        for i in range(3):
            for agent in range(len(parents)):
                self.agents[agent + (i*10)].set_biases(parents[agent].get_biases())
                self.agents[agent + (i*10)].set_weights(parents[agent].get_weights())        
                self.agents[agent + (i*10)].mutate_biases()
                self.agents[agent + (i*10)].mutate_weights()


    def gen_over(self):
        over = True
        for agent in self.agents:
            if not agent.get_crashed():
                over = False
        return over
        

    def write_progress(self):
        average_progress = 0
        for agent in self.agents:
            average_progress += agent.get_progress()
        average_progress /= self.agents_num
        with open("logs/average_progress", "a") as f:
            f.write("\n")
            f.write(str(average_progress))


    def write_snapshot(self):
        with open("logs\snapshot", "w") as f:
            pass

        with open("logs\snapshot", "a") as f:
            for agent in range(int(self.agents_num - self.agents_num/10), self.agents_num):
                f.write("NETWORK_{}\n".format(agent))
                weights = self.agents[agent].get_weights()
                biases = self.agents[agent].get_biases()
                f.write(str(weights))
                f.write("\n")
                f.write(str(biases))
                f.write("\n")

class Agent():
    def __init__(self, window, track, shape, renderable=False):
        self.window = window
        self.track = track
        self.shape = shape
        self.renderable = renderable
        self.car = car_o.Car(self.window, self.track, 10)
        self.neural_net = neural_network.Neural_Network(self.window, self.shape)


    def __le__(self, other):
        return self.get_progress() <= other.get_progress()


    def run(self, frame_time):
        if not self.car.get_crashed():
            self.car.find_distances()
            inputs = self.car.network_inputs(frame_time)
            outputs = self.neural_net.process(inputs)
            self.car.network_outputs(outputs, frame_time)
            self.car.dynamics(frame_time)
            self.car.find_progress()
            self.car.crash_check()


    def render(self):
        if self.renderable:
            self.car.render()


    def reset(self):
        self.car = car_o.Car(self.window, self.track, 10)

    
    def get_progress(self):
        return self.car.get_progress()


    def mutate_weights(self):
        self.neural_net.mutate_weights()

    
    def mutate_biases(self):
        self.neural_net.mutate_biases()


    def set_weights(self, weights):
        self.neural_net.set_weights(weights)


    def set_biases(self, biases):
        self.neural_net.set_biases(biases)


    def get_weights(self):
        return self.neural_net.get_weights()


    def get_biases(self):
        return self.neural_net.get_biases()


    def get_crashed(self):
        return self.car.get_crashed()
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
