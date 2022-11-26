import random
import numpy as np


class Individual:
    """
    Class representing one individual in population. Each individual can have encoded chromosome (e.g. list of countries
    representing one route in TSP). Individual can also mutate the individual genes in chromosome and count the distance
    of route using fitness method.
    """
    def __init__(self, distance_coords_dict, countries_list, mut_prob, mutation_gene_change_percent):
        self.chromosome = None
        self.distance_coords_dict = distance_coords_dict
        self.countries_list = countries_list
        self.mutation_prob = mut_prob
        self.mutation_gene_change_percent = mutation_gene_change_percent

    def set_chromosome(self, chromosome):
        self.chromosome = chromosome

    def create_route_chromosome(self):
        self.chromosome = random.sample(self.countries_list, len(self.countries_list))

    def fitness(self):
        """
        Computes the distance based on chromosome.
        """
        path_distance = 0
        for idx in range(0, len(self.chromosome)):
            from_ = self.chromosome[idx]
            if idx + 1 < len(self.chromosome):
                to = self.chromosome[idx + 1]
            else:
                to = self.chromosome[0]

            path_distance += self.distance_coords_dict[from_ + "-" + to][0]
        return path_distance

    def mutate(self):
        """
        Mutates the chromosome using the random multiple point mutation. If the one gene is being mutated, we always
        need to swap the indices with countries so there is always fulfilled the TSP constraint.
        """
        len_ = round(len(self.chromosome) * self.mutation_gene_change_percent)
        for idx in range(len_):
            # check if the probability of mutation is satisfied
            if np.random.uniform(0, 1) <= self.mutation_prob:
                # save index in chromosome for mutation
                swap_idx = int(random.random() * len(self.chromosome))

                country1 = self.chromosome[idx]
                country2 = self.chromosome[swap_idx]

                self.chromosome[idx] = country2
                self.chromosome[swap_idx] = country1
