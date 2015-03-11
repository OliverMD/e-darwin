"""
In this file I define an evolutionary algorithm for evolving programs
"""
import Forests
import random
import numpy.random as npr

class Darwinator:
    def __init__(self, popsize, fitnesstester, inputsize, outputsize, treeconfig=Forests.DefaultTreeConfig):
        self.popSize = popsize
        self.fitnessTester = fitnesstester
        self.inputSize = inputsize
        self.outputSize = outputsize
        self.treeConfig = treeconfig
        self.mutateRate = 0.4

        # Generate Population
        self.population = []
        for i in xrange(self.popSize):
            self.population.append(Forests.generateRandomProgram(self.treeConfig.functions,
                                                                 mindatasize=max(self.inputSize, self.outputSize)))

    def __rankPopulation(self):
        self.fitnessTester.newTest()
        scores = [(self.fitnessTester.test(prog), prog) for prog in self.population]
        scores.sort()
        return scores

    def evolve(self, gens):
        for gen in xrange(gens):
            scores = self.__rankPopulation()
            # Elitism
            newpop = [scores[0][1]]
            while len(newpop) < len(self.population):

                if random.random() < self.mutateRate:

                    newpop.append(Forests.randomMutate(
                        Forests.randomSwapCrossover(self.population[int(npr.beta(1.2) * len(self.population) - 1)],
                                                    self.population[int(npr.beta(1.2) * len(self.population) - 1)])))
                else:
                    newpop.append(
                        Forests.randomSwapCrossover(self.population[int(npr.beta(1.2) * len(self.population) - 1)],
                                                    self.population[int(npr.beta(1.2) * len(self.population) - 1)]))

            self.population = newpop

    def getBestProgram(self):
        self.population = [score[1] for score in self.__rankPopulation()]
        return self.population[0]