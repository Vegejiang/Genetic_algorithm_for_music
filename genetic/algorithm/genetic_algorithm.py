from genetic.terminator.terminator import Terminator
from genetic.fitness.fitness import Fitness
from genetic.item.music_piece import MusicPiece
from genetic.inherit.mutate import Mutate
from genetic.inherit.crossover import Crossover
from genetic.initial.initial import Initial
from genetic.utils.utils import roulette_wheel_selection
import random
import json
import numpy as np



class Genetic_algorithm:
    def __init__(self, terminator: Terminator, fitness: Fitness, mutate: Mutate, crossover: Crossover, initial: Initial, config_path: str):
        self.terminator = terminator
        self.fitness = fitness
        self.mutate = mutate
        self.initial = initial
        self.config_path = config_path
        self.config = None
        self.crossover = crossover
        try:
            with open(config_path, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print(f"Error: 配置文件 {config_path} 未找到！")
            return None
        except json.JSONDecodeError:
            print(f"Error: 配置文件 {config_path} 格式错误！")
            return None
        self.random_seed = self.config.get('random_seed', 0)
        #set random seed
        random.seed(self.random_seed)
        self.population_size = self.config.get('population_size', 100)
        self.mutation_rate = self.config.get('mutation_rate', 0.1)
        self.discard_rate = self.config.get('discard_rate', 0.3)
        self.temperature = self.config.get('temperature', 1.0)
        self.temperature_decay = self.config.get('temperature_decay', 0.99)
        self.round_num = self.config.get('round_num', -1)
        self.population = []

    #generate the initial population
    def start(self):
        self.population = self.initial.generate(self.population_size)

    #single iteration of the genetic algorithm
    def iteration(self, temperature: float):

        fitness = [self.fitness.evaluate(music_piece) for music_piece in self.population]

        #discard using reloulette wheel selection
        selected_population = roulette_wheel_selection(self.population, fitness, int(self.population_size * (1 - self.discard_rate)), temperature)

        #crossover
        crossover_population = []
        while len(crossover_population) < self.population_size - len(selected_population):
            parent1, parent2 = random.sample(selected_population, 2)
            child1, child2 = self.crossover.crossover(parent1, parent2)
            crossover_population.append(child1)
            crossover_population.append(child2)
        
        selected_population.extend(crossover_population)
        selected_population = selected_population[:self.population_size]

        #mutate
        for i in range(len(selected_population)):
            if random.random() < self.mutation_rate:
                selected_population[i] = self.mutate.mutate(selected_population[i])
        self.population = selected_population

    def simulate(self):
        self.start()
        temperature = self.temperature
        round_num = 0
        print("Generated initial population, start simulating")
        if self.round_num != -1:
            for i in range(self.round_num):
                self.iteration(temperature)
                fitness = [self.fitness.evaluate(music_piece) for music_piece in self.population]
                print(f"Round {i}, best fitness: {max(fitness)}")
            best = self.population[np.argmax(fitness)]
            return best, self.population
        else:
            while True:
                self.iteration(temperature)
                temperature *= self.temperature_decay
                fitness = [self.fitness.evaluate(music_piece) for music_piece in self.population]
                round_num += 1
                if self.terminator.check_terminate(fitness, round_num):
                    break
                print(f"Round {round_num}, best fitness: {max(fitness)}")
            best = self.population[np.argmax(fitness)]
            return best, self.population


