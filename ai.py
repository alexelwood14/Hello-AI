import const
import neural_network
import car_o
import numpy as np
import time


class AI():
    def __init__(self, window, track, agents_num, ai_mode, target):
        self.window = window
        self.agents_num = agents_num
        self.shape = [9, 10, 4]
        self.track = track
        self.gen = 0
        if ai_mode != const.AI_MODE.START: 
            weights, biases = self.parse_snapshot(target)
            self.agents = [Agent(self.window, self.track, self.shape, ai_mode, weights[i], biases[i], True) for i in range(agents_num)]
        else:
            self.agents = [Agent(self.window, self.track, self.shape, ai_mode, None, None, True) for i in range(agents_num)]
        self.__init_time = name = time.ctime(time.time()).replace(' ', '-').replace(':', '-')

        with open("logs/average_progress", "w") as f:
            f.write("AVG_PROGRESS")

    def run(self, frame_time):
        for agent in self.agents:
            agent.run(frame_time)

    def render(self):
        for agent in self.agents:
            agent.render()

    def next_gen(self):
        self.agents = sorted(self.agents)

        for i in range(self.agents_num):
            self.agents[i].reset(const.COL["blue"])  

        #Create an array of parents
        parents = []
        for i in range(int(self.agents_num/10)):
            parents.append(self.agents[int(9*self.agents_num/10) + i])
            self.agents[int(9*self.agents_num/10) + i].reset(const.COL["green"])

        start_ang = self.track.start_ang

        #Replace least performing cars with children of parents and mutate
        for i in range(3):
            for agent in range(len(parents)):
                self.agents[agent + (i*10)].biases = parents[agent].biases
                self.agents[agent + (i*10)].weights = parents[agent].weights     
                self.agents[agent + (i*10)].mutate_biases()
                self.agents[agent + (i*10)].mutate_weights()
                self.agents[agent + (i*10)].reset()

    def gen_over(self):
        over = True
        for agent in self.agents:
            if not agent.crashed:
                over = False
        return over
        
    def write_progress(self):
        average_progress = 0
        for agent in self.agents:
            average_progress += agent.progress
        average_progress /= self.agents_num
        with open("logs/average_progress", "at") as f:
            f.write("\n")
            f.write(str(average_progress))

    def write_snapshot(self, gen):
        with open("logs\\{}".format(self.__init_time), "wt") as f:
            f.write(str(gen) + '\n')
            for agent in range(self.agents_num):
                f.write("NETWORK_{}\n".format(agent))
                weights = self.agents[agent].weights
                biases = self.agents[agent].biases
                f.write(str(weights).replace('[', '').replace(']', ''))
                f.write("\n")
                f.write(str(biases).replace('[', '').replace(']', ''))
                f.write("\n")

    def parse_snapshot(self, snapshot):
        all_weights = []
        all_biases = []
        with open('logs\\{}'.format(snapshot), 'rt') as f:
            file = [f.readline().replace('\n', '') for i in range(self.agents_num * 3+1)]
            self.gen = int(file[0])
        for line in range(1, len(file)):
            if (line - 2) % 3 == 0: all_weights.append(list(np.float_(file[line].split(', '))))
            if line % 3 == 0: all_biases.append(list(np.float_(file[line].split(', '))))
        return all_weights, all_biases


class Agent():
    def __init__(self, window, track, shape, ai_mode, weights, biases, renderable=False):
        self.window = window
        self.track = track
        self.shape = shape
        self.renderable = renderable
        self._car = car_o.Car(self.window, self.track, 10)
        if ai_mode == const.AI_MODE.START: self.neural_net = neural_network.Unevolved_Neural_Network(self.window, self.shape)
        elif ai_mode == const.AI_MODE.RESUME: self.neural_net = neural_network.Evolved_Neural_Network(self.window, self.shape, weights, biases)

    def __le__(self, other):
        return self.progress <= other.progress

    def __lt__(self, other):
        return self.progress < other.progress

    def run(self, frame_time):
        if not self._car.crashed:
            self._car.find_distances()
            inputs = self._car.network_inputs(frame_time)
            outputs = self.neural_net.process(inputs)
            self._car.network_outputs(outputs, frame_time)
            self._car.dynamics(frame_time)
            self._car.crash_check()

    def render(self):
        if self.renderable:
            self._car.render()

    def reset(self, colour=const.COL["red"]):
        self._car = car_o.Car(self.window, self.track, 10, colour)

    def mutate_weights(self):
        self.neural_net.mutate_weights()
    
    def mutate_biases(self):
        self.neural_net.mutate_biases()
    
    @property
    def progress(self):
        return self._car.progress

    @property
    def weights(self):
        return self.neural_net.weights

    @weights.setter
    def weights(self, weights):
        self.neural_net.weights = weights

    @property
    def biases(self):
        return self.neural_net.biases

    @biases.setter
    def biases(self, biases):
        self.neural_net.biases = biases

    @property
    def crashed(self):
        return self._car.crashed

    @property
    def colour(self):
        return self.colour 

    @colour.setter
    def colour(self, colour):
        self._car.colour = colour