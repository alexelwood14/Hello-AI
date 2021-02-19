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
        self.agents = np.array([])
        for num in range(self.agents_num):
            if num % 4 == 0:
                self.agents = np.append(self.agents, [Agent(self.window, self.track, self.shape, True)])
            else:
                self.agents = np.append(self.agents, [Agent(self.window, self.track, self.shape)])

        f = open("data/average_progress", "w")
        f.write("AVG_PROGRESS")
        f.close()

    def run(self, frame_time):
        for agent in self.agents:
            agent.run(frame_time)


    def render(self):
        for agent in self.agents:
            agent.render()

    
    def sort_agents(self):
        temp_agents = np.copy(self.agents)
        sorted_agents = np.array([])
        for i in range(self.agents_num):
            highest, index = self.find_top_agent(temp_agents)
            sorted_agents = np.append(sorted_agents, [highest])
            temp_agents = np.delete(temp_agents, index)
        
        self.agents = np.flip(sorted_agents)

    
    def find_top_agent(self, temp_agents):
        index = 0
        highest = self.agents[index]
        for agent in range(1, len(temp_agents)):
            if self.agents[agent].get_progress() > highest.get_progress():
                highest = self.agents[agent]
                index = agent

        return highest, index


    def next_gen(self):
        self.sort_agents()
        
        #Create an array of parents
        parents = []
        for i in range(int(self.agents_num/10)):
            parents.append(self.agents[int(9*self.agents_num/10) + i])

        #Copy cars to a new array
        start_ang = self.track.get_start_ang()
        new_agents = []
        for agent in range(self.agents_num):
            if agent % 4 == 0:
                new_agents.append(Agent(self.window, self.track, self.shape, True))
            else:
                new_agents.append(Agent(self.window, self.track, self.shape))

        for agent in range(self.agents_num):
            new_agents[agent].set_biases(self.agents[agent].get_biases())
            new_agents[agent].set_weights(self.agents[agent].get_weights())        

        #Replace least performing cars with children of parents and mutate
        for i in range(3):
            for agent in range(len(parents)):
                new_agents[agent + (i*10)].set_biases(parents[agent].get_biases())
                new_agents[agent + (i*10)].set_weights(parents[agent].get_weights())        
                new_agents[agent + (i*10)].mutate_biases()
                new_agents[agent + (i*10)].mutate_weights()
                
        self.agents = new_agents


    def gen_over(self):
        pass


    def write_progress(self):
        average_progress = 0
        for agent in self.agents:
            average_progress += agent.get_progress()
        average_progress /= self.agents_num
        f = open("data/average_progress", "a")
        f.write("\n")
        f.write(str(average_progress))
        f.close()


    def write_snapshot(self):
        f = open("data\snapshot", "w")
        f.close()
        f = open("data\snapshot", "a")

        for agent in range(int(self.agents_num - self.agents_num/10), self.agents_num):
            f.write("NETWORK_{}\n".format(agent))
            weights = self.agents[agent].get_weights()
            biases = self.agents[agent].get_biases()
            f.write(str(weights))
            f.write("\n")
            f.write(str(biases))
            f.write("\n")
        
        f.close()


class Agent():
    def __init__(self, window, track, shape, renderable=False):
        self.window = window
        self.track = track
        self.shape = shape
        self.renderable = renderable
        self.car = car_o.Car(self.window, self.track, 10)
        self.neural_net = neural_network.Neural_Network(self.window, self.shape)


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
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
