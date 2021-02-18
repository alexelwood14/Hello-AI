import const
import pygame
import numpy as np
from pygame.locals import *

class AI():
    def __init__(self, window):
        self.window = window
        self.agents = []
        self.agents_count = 100
        for i in range(self.agents_count):
            self.agents.append(Agent(self.window))

class Agent():
    def __init__(self, window):
        self.window = window
        self.car = 0
        self.neural_net = 0

#----------------------------------------------------------------------------------------------------------------------------------
class Neural_Network():
    def __init__(self, window, inputs, hidden, outputs):
        self.window = window
        self.weights = []
        self.biases = []
        mean = 0
        std_dev = 0.1
        self.layers = len(hidden) + 1
        
        #---INITIATE HIDDEN LAYER BIASES AND NODES---
        
        #Initiate weights leading to hidden layers
        for layer in range(len(hidden)):
            #Setup biases matrix using first element
            bias = np.random.normal(mean, std_dev)
            temp_3 = np.array([bias])

            #Append all other biases to the matrix
            for i in range(1, hidden[layer]):
                bias = np.random.normal(mean, std_dev)
                temp_3 = np.append(temp_3, bias)

            self.biases.append(temp_3)

            #---INITATE HIDDEN LAYER WEIGHTS AND AXONS

            #Setup weights matrix using first weights of array
            temp_2 = []
            if layer == 0:
                for j in range(inputs):
                    weight = np.random.normal(mean, std_dev)
                    temp_2.append(weight)
            else:
                for j in range(hidden[layer-1]):
                    weight = np.random.normal(mean, std_dev)
                    temp_2.append(weight)
            temp_1 = np.array([temp_2])

            #Append all other weights to the martix
            for i in range(1, hidden[layer]):
                temp_2 = []

                if layer == 0:
                    for j in range(inputs):
                        weight = np.random.normal(mean, std_dev)
                        temp_2.append(weight)
                else:
                    for j in range(hidden[layer-1]):
                        weight = np.random.normal(mean, std_dev)
                        temp_2.append(weight)

                temp_1 = np.append(temp_1, [temp_2], axis=0)
                    

            self.weights.append(temp_1)



        #---INITIATE OUTPUT BIASES AND NODES---

        #Setup biases matrix using first element
        bias = np.random.normal(mean, std_dev)
        temp_3 = np.array([bias])

        #Append all other biases to the matrix
        for i in range(1, outputs):
            bias = np.random.normal(mean, std_dev)
            temp_3 = np.append(temp_3, bias)
        self.biases.append(temp_3)


        #---INITIATE OUTPUT WEIGHTS AND AXONS---

        #Setup weights matrix using first weights of array
        temp_2 = []
        for j in range(hidden[len(hidden)-1]):
            weight = np.random.normal(mean, std_dev)
            temp_2.append(np.random.normal(mean, std_dev))
        temp_1 = np.array([temp_2])

        #Append all other weights to the matrix
        for i in range(1, outputs):
            temp_2 = []
            for j in range(hidden[len(hidden)-1]):
                weight = np.random.normal(mean, std_dev)
                temp_2.append(np.random.normal(mean, std_dev))
            temp_1 = np.append(temp_1, [temp_2], axis=0)

        self.weights.append(temp_1)


    def process(self, layer_data, set_activations=False):
        layer_data = np.array(layer_data)
        activations = [layer_data]
                
        for layer in range(self.layers):
            
            layer_data = 1/(1+np.exp(-(np.matmul(self.weights[layer], layer_data) + self.biases[layer])))
            activations.append(layer_data)

        if set_activations:
            self.set_activations(activations)
            
        return layer_data


    def set_weights(self, weights):
        for layer in range(len(weights)):
            for node in range(len(self.weights[layer])):
                self.weights[layer][node] = weights[layer][node][:]


    def set_biases(self, biases):
        for layer in range(len(biases)):
            for b in range(len(biases[layer])):
                self.biases[layer][b] = biases[layer][b]

    def crossover(self, parent1, parent2):
        biases1 = parent1.get_biases()
        biases2 = parent2.get_biases()
        for layer in range(len(self.biases)):
            for bias in range(len(self.biases[layer])):
                if layer*bias % 2 == 0:
                    self.biases[layer][bias] = biases1[layer][bias]
                else:
                    self.biases[layer][bias] = biases2[layer][bias]

        weights1 = parent1.get_weights()
        weights2 = parent2.get_weights()
        for layer in range(len(self.weights)):
            for node in range(len(self.weights[layer])):
                for w in range(len(self.weights[layer][node])):
                    if layer*node % 2 == 0:
                        self.weights[layer][node][w] = weights1[layer][node][w]
                    else:
                        self.weights[layer][node][w] = weights2[layer][node][w]


    def mutate_biases(self):
        var = 1
        std_dev = var**2 
        for layer in range(len(self.biases)):
            for bias in range(len(self.biases[layer])):
                mutation = np.random.normal(0, std_dev)
                if abs(mutation) > 2 * np.sqrt(std_dev): 
                    self.biases[layer][bias] += mutation


    def mutate_weights(self):
        var = 1
        std_dev = var**2 
        for layer in range(len(self.weights)):
            for node in range(len(self.weights[layer])):
                for w in range(len(self.weights[layer][node])):
                    mutation = np.random.normal(0, std_dev)
                    if abs(mutation) > 2 * np.sqrt(std_dev):
                        self.weights[layer][node][w] += mutation

        
    def get_weights(self):
        return self.weights
    

    def get_biases(self):
        return self.biases        
        
        
#----------------------------------------------------------------------------------------------------------------------------------
def main():
    pass

if __name__ == "__main__":
    main()
