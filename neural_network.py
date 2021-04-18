import copy
import numpy as np


class NeuralNetwork:
    def __init__(self, window, shape):
        self.window = window
        self._weights = []
        self._biases = []
        self.shape = shape
        self.inputs = shape[0]
        self.hidden = shape[1:-1]
        self.outputs = shape[-1]
        self.mean = 0
        self.std_dev = 0.1

    def process(self, layer_data):
        layer_data = np.array(layer_data)
                
        for layer in range(len(self.shape)-1):
            layer_data = 1/(1+np.exp(-(np.matmul(self._weights[layer], layer_data) + self._biases[layer])))

        return layer_data

    def crossover(self, parent1, parent2):
        biases1 = parent1.get_biases()
        biases2 = parent2.get_biases()
        for layer in range(len(self._biases)):
            for bias in range(len(self._biases[layer])):
                if layer*bias % 2 == 0:
                    self._biases[layer][bias] = biases1[layer][bias]
                else:
                    self._biases[layer][bias] = biases2[layer][bias]

        weights1 = parent1.get_weights()
        weights2 = parent2.get_weights()
        for layer in range(len(self._weights)):
            for node in range(len(self._weights[layer])):
                for w in range(len(self._weights[layer][node])):
                    if layer*node % 2 == 0:
                        self._weights[layer][node][w] = weights1[layer][node][w]
                    else:
                        self._weights[layer][node][w] = weights2[layer][node][w]

    def mutate_biases(self):
        var = 1
        std_dev = var**2 
        for layer in range(len(self._biases)):
            for bias in range(len(self._biases[layer])):
                mutation = np.random.normal(0, std_dev)
                if abs(mutation) > 2 * np.sqrt(std_dev): 
                    self._biases[layer][bias] += mutation

    def mutate_weights(self):
        var = 1
        std_dev = var**2 
        for layer in range(len(self._weights)):
            for node in range(len(self._weights[layer])):
                for w in range(len(self._weights[layer][node])):
                    mutation = np.random.normal(0, std_dev)
                    if abs(mutation) > 2 * np.sqrt(std_dev):
                        self._weights[layer][node][w] += mutation

    @property
    def weights(self):
        return self._weights

    @weights.setter
    def weights(self, weights):
        self._weights = copy.deepcopy(weights)

    @property
    def biases(self):
        return self._biases

    @biases.setter
    def biases(self, biases):
        self._biases = copy.deepcopy(biases)


class UnevolvedNeuralNetwork(NeuralNetwork):
    def __init__(self, window, shape):
        super().__init__(window, shape)

        # Initiate weights and biases for the first hidden layer
        self._biases.append([np.random.normal(self.mean, self.std_dev) for i in range(self.hidden[0])])
        self._weights.append([[np.random.normal(self.mean, self.std_dev)
                               for i in range(self.inputs)] for j in range(self.hidden[0])])
        
        # Initiate weights and biases for subsequent hidden layers
        for layer in range(1, len(self.hidden)):
            self._biases.append([np.random.normal(self.mean, self.std_dev) for i in range(self.hidden[layer])])
            self._weights.append([[np.random.normal(self.mean, self.std_dev)
                                   for i in range(self.hidden[layer-1])] for j in range(self.hidden[layer])])

        # Initiate weights and biases for the output layer
        self._biases.append([np.random.normal(self.mean, self.std_dev) for i in range(self.outputs)])
        self._weights.append([[np.random.normal(self.mean, self.std_dev)
                               for i in range(self.hidden[-1])] for j in range(self.outputs)])


class EvolvedNeuralNetwork(NeuralNetwork):
    def __init__(self, window, shape, weights, biases):
        super().__init__(window, shape)
        assert len(biases) == sum(shape[1:])
        assert len(weights) == sum([self.shape[i] * self.shape[i-1] for i in range(1, len(self.shape))])

        for i in range(1, len(self.shape)):
            layer_biases = []
            layer_weights = []
            for j in range(self.shape[i]):
                node_weights = []
                layer_biases.append(biases.pop(0))
                for k in range(self.shape[i-1]):
                    node_weights.append(weights.pop(0))
                layer_weights.append(node_weights)
            self._biases.append(layer_biases)
            self._weights.append(layer_weights)
