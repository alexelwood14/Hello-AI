import const
import copy
import numpy as np

class Neural_Network():
    def __init__(self, window, shape):
        self.window = window
        self.weights = []
        self.biases = []
        inputs = shape[0]
        hidden = shape[1]
        outputs = shape[2]
        mean = 0
        std_dev = 0.1
        self.layers = len(hidden) + 1

        #Initiate weights and biases for the first hidden layer
        self.biases.append([np.random.normal(mean, std_dev) for i in range(hidden[0])])
        self.weights.append([[np.random.normal(mean, std_dev) for i in range(inputs)] for j in range(hidden[0])])
        
        #Initiate weights and biases for subsequent hidden layers
        for layer in range(1, len(hidden)):
            self.biases.append([np.random.normal(mean, std_dev) for i in range(hidden[layer])])
            self.weights.append([[np.random.normal(mean, std_dev) for i in range(hidden[layer-1])] for j in range(hidden[layer])])

        #Initiate weights and biases for the output layer
        self.biases.append([np.random.normal(mean, std_dev) for i in range(outputs)])
        self.weights.append([[np.random.normal(mean, std_dev) for i in range(hidden[-1])] for j in range(outputs)])


    def process(self, layer_data):
        layer_data = np.array(layer_data)
                
        for layer in range(self.layers):
            layer_data = 1/(1+np.exp(-(np.matmul(self.weights[layer], layer_data) + self.biases[layer])))

        return layer_data


    def set_weights(self, weights):
        self.weights = copy.deepcopy(weights)


    def set_biases(self, biases):
        self.biases = copy.deepcopy(biases)


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