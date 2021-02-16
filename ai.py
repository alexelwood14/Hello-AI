import const
import pygame
import math
import random
import numpy as np
from pygame.locals import *

class Neuron():
    def __init__(self, window, pos):
        self.window = window
        self.pos = [int(pos[0]), int(pos[1])]
        self.display_biases = False

    def render(self):
        pygame.draw.circle(self.window, const.COL["grey"], self.pos, 12)
        if self.display_biases:
            pygame.draw.circle(self.window, self.bias_colour, self.pos, 10)
        else:
            pygame.draw.circle(self.window, self.colour, self.pos, 10)

    def get_pos(self):
        return self.pos

    def set_display_biases(self, display):
        self.display_biases = display

    def set_activation(self, activation):
        self.activation = activation
        self.colour = (255 * activation, 255 * activation, 255 * activation)


class Input_Neuron(Neuron):
    def __init__(self, window, pos):
        super().__init__(window, pos)

        self.colour = const.COL["white"]
        self.bias_colour = (0, 0, 0)


class Hidden_Neuron(Neuron):
    def __init__(self, window, pos, bias):
        super().__init__(window, pos)

        self.colour = const.COL["white"]
        self.bias = bias
        if abs(self.bias) > 10:
            colour = 1
        else:
            colour = abs(self.bias) / 10
        if self.bias >= 0:
            self.bias_colour = (0, 0, 255*colour)
        else:
            self.bias_colour = (255*colour, 0, 0)


class Output_Neuron(Neuron):
    def __init__(self, window, pos, bias):
        super().__init__(window, pos)

        self.colour = const.COL["white"]
        self.bias = bias
        if abs(self.bias) > 10:
            colour = 1
        else:
            colour = abs(self.bias) / 10
        if self.bias >= 0:
            self.bias_colour = (0, 0, 255*colour)
        else:
            self.bias_colour = (255*colour, 0, 0)


#----------------------------------------------------------------------------------------------------------------------------------
class Axon():
    def __init__(self, window, start, end, weight):
        self.window = window
        self.start = start
        self.end = end
        self.weight = weight

        if abs(self.weight) > 1.7:
            colour = 1
        else:
            colour = abs(self.weight) / 1.7
        if self.weight >= 0:
            self.colour = (0, 0, 255*colour)
        else:
            self.colour = (255*colour, 0, 0)

    def render(self):
        pygame.draw.line(self.window, self.colour, self.start, self.end, 1)


#----------------------------------------------------------------------------------------------------------------------------------
class Neural_Network():
    def __init__(self, window, inputs, hidden, outputs):
        self.window = window
        self.inputs = []
        self.hidden = []
        self.axons = []
        self.weights = []
        self.biases = []
        mean = 0
        std_dev = 0.1
        self.layers = len(hidden) + 1

        #Initiate input nodes
        start = [window.get_size()[0]/5, window.get_size()[1]/5]
        incriment = window.get_size()[1] * 3 / 5 / (inputs-1)
        for node in range(inputs):
            self.inputs.append(Input_Neuron(window, [start[0], start[1] + incriment * node]))


        #---INITIATE HIDDEN LAYER BIASES AND NODES---
        
        #Initiate weights leading to hidden layers
        start = [window.get_size()[0]/5, window.get_size()[1]/8]
        for layer in range(len(hidden)):
            
            #Node position incriment
            incriment = [window.get_size()[0]*3/5/(len(hidden)+1), window.get_size()[1] * 3 / 4 / (hidden[layer]-1)]

            #Setup biases matrix using first element
            pos = [start[0] + incriment[0] * (layer+1), start[1]]
            bias = np.random.normal(mean, std_dev)
            nodes = [Hidden_Neuron(window, pos, bias)]
            temp_3 = np.array([bias])

            #Append all other biases to the matrix
            for i in range(1, hidden[layer]):
                pos = [start[0] + incriment[0] * (layer+1), start[1] + incriment[1] * i]
                bias = np.random.normal(mean, std_dev)
                nodes.append(Hidden_Neuron(window, pos, bias))
                temp_3 = np.append(temp_3, bias)

            self.hidden.append(nodes)
            self.biases.append(temp_3)

            #---INITATE HIDDEN LAYER WEIGHTS AND AXONS

            #Setup weights matrix using first weights of array
            temp_2 = []
            pos = [start[0] + incriment[0] * (layer+1), start[1]]
            if layer == 0:
                for j in range(inputs):
                    weight = np.random.normal(mean, std_dev)
                    self.axons.append(Axon(window, pos, self.inputs[j].get_pos(), weight))
                    temp_2.append(weight)
            else:
                for j in range(hidden[layer-1]):
                    weight = np.random.normal(mean, std_dev)
                    self.axons.append(Axon(window, pos, self.hidden[layer-1][j].get_pos(), weight))
                    temp_2.append(weight)
            temp_1 = np.array([temp_2])

            #Append all other weights to the martix
            for i in range(1, hidden[layer]):
                temp_2 = []

                pos = [start[0] + incriment[0] * (layer+1), start[1] + incriment[1] * i]
                if layer == 0:
                    for j in range(inputs):
                        weight = np.random.normal(mean, std_dev)
                        self.axons.append(Axon(window, pos, self.inputs[j].get_pos(), weight))
                        temp_2.append(weight)
                else:
                    for j in range(hidden[layer-1]):
                        weight = np.random.normal(mean, std_dev)
                        self.axons.append(Axon(window, pos, self.hidden[layer-1][j].get_pos(), weight))
                        temp_2.append(weight)

                temp_1 = np.append(temp_1, [temp_2], axis=0)
                    

            self.weights.append(temp_1)



        #---INITIATE OUTPUT BIASES AND NODES---

        #Set output node positioning variables
        start = [window.get_size()[0] - window.get_size()[0]/5, window.get_size()[1]/5]
        incriment = window.get_size()[1] * 3 / 5 / (outputs-1)

        #Setup biases matrix using first element
        pos = start
        bias = np.random.normal(mean, std_dev)
        self.outputs = [Output_Neuron(window, pos, bias)]
        temp_3 = np.array([bias])

        #Append all other biases to the matrix
        for i in range(1, outputs):
            pos = [start[0], start[1] + incriment * i]
            bias = np.random.normal(mean, std_dev)
            self.outputs.append(Output_Neuron(window, pos, bias))
            temp_3 = np.append(temp_3, bias)
        self.biases.append(temp_3)


        #---INITIATE OUTPUT WEIGHTS AND AXONS---

        #Setup weights matrix using first weights of array
        temp_2 = []
        for j in range(hidden[len(hidden)-1]):
            weight = np.random.normal(mean, std_dev)
            self.axons.append(Axon(window, start, self.hidden[len(hidden)-1][j].get_pos(), weight))
            temp_2.append(np.random.normal(mean, std_dev))
        temp_1 = np.array([temp_2])

        #Append all other weights to the matrix
        for i in range(1, outputs):
            temp_2 = []

            pos = [start[0], start[1] + incriment * i]
            for j in range(hidden[len(hidden)-1]):
                weight = np.random.normal(mean, std_dev)
                self.axons.append(Axon(window, pos, self.hidden[len(hidden)-1][j].get_pos(), weight))
                temp_2.append(np.random.normal(mean, std_dev))

            temp_1 = np.append(temp_1, [temp_2], axis=0)

        self.weights.append(temp_1)


    def render(self):
        #Render axons
        for axon in self.axons:
            axon.render()
            
        #Render input nodes
        for node in self.inputs:
            node.render()

        #Render hidden nodes
        for layer in self.hidden:
            for node in layer:
                node.render()

        #Render output nodes
        for node in self.outputs:
            node.render()


    def process(self, layer_data, set_activations=False):
        layer_data = np.array(layer_data)
        activations = [layer_data]
                
        for layer in range(self.layers):
            
            layer_data = 1/(1+np.exp(-(np.matmul(self.weights[layer], layer_data) + self.biases[layer])))
            activations.append(layer_data)

        if set_activations:
            self.set_activations(activations)
            
        return layer_data


    def set_display_biases(self, display):
        for node in self.inputs:
            node.set_display_biases(display)

        for layer in self.hidden:
            for node in layer:
                node.set_display_biases(display)

        for node in self.outputs:
            node.set_display_biases(display)


    def set_activations(self, activations):
        for node in range(len(self.inputs)):
            self.inputs[node].set_activation(activations[0][node])

        for layer in range(len(self.hidden)):
            for node in range(len(self.hidden[layer])):
                self.hidden[layer][node].set_activation(activations[layer+1][node])

        for node in range(len(self.outputs)):
            self.outputs[node].set_activation(activations[len(activations)-1][node])


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
