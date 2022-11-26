from .individual import Individual
import numpy as np
import random


class GA:
    """
    Class for genetic algorithm provides population initialization, fitness function, various parent selection methods,
    crossover method and population recreation method.
    """

    def __init__(self, pop_size, dataset, elitism, crossover_prob, mutation_prob,
                 k_parents, selection, mutation_gene_change_percent, tournament_k, same_parents):
        self.pop_size = pop_size
        self.crossover_prob = crossover_prob
        self.population = []
        self.dataset = dataset
        self.rated_population = []
        self.elitism = elitism
        self.mutation_prob = mutation_prob
        self.k = k_parents
        self.tournament_k = tournament_k
        self.selection_type = selection
        self.mutation_gene_change_percent = mutation_gene_change_percent
        self.same_parents = same_parents
        if elitism:
            self.k = k_parents - 1

    def init_population(self):
        """
        Initialization of the population.
        """
        for i in range(0, self.pop_size):
            individual = Individual(self.dataset.distance_coords_dict, self.dataset.countries,
                                    self.mutation_prob, self.mutation_gene_change_percent)
            self.population.append(individual)
            individual.create_route_chromosome()

    def selection(self, selection_factory):
        """
        Method provides basic factory design for parent selection method.
        """
        if self.pop_size < 2:
            raise Exception("Population size must be greater than number of parents.")

        if selection_factory.lower() == "roulettewheel":
            parents = self.roulette()
        elif selection_factory.lower() == "tournament":
            parents = self.tournament()
        elif selection_factory.lower() == "rankselection":
            parents = self.rank_selection()
        elif selection_factory.lower() == "kbestselection":
            parents = self.k_best_selection()
        elif selection_factory.lower() == "random":
            parents = self.random_select()
        else:
            raise Exception("Unknown selection type.")

        return parents

    def crossover(self, parents):
        """
        Crossover method always takes two random individuals from parents and does two point crossover which means that
        the new individual's chromosome consists of one part of first parent and the second part is provided by next
        parent.
        """
        chromosome_p1 = []

        if len(parents) > 2:  # choose two random parents for crossover
            parents = random.sample(parents, 2)

        # get two random indices in chromosome
        gene1 = int(random.random() * len(parents[0].chromosome))
        gene2 = int(random.random() * len(parents[1].chromosome))

        # find start and end position
        start_pos = min(gene1, gene2)
        end_pos = max(gene1, gene2)

        # append genes to chromosome part one, taken from first parent
        for i in range(start_pos, end_pos):
            chromosome_p1.append(parents[0].chromosome[i])

        # get complement genes (countries) of chromosome_p1 to satisfy TSP
        chromosome_p2 = [item for item in parents[1].chromosome if item not in chromosome_p1]

        # connect two partial chromosomes to create valid one
        child_chromosome = chromosome_p1 + chromosome_p2

        # create new Individual object and set his chromosome
        individual = Individual(self.dataset.distance_coords_dict, self.dataset.countries,
                                self.mutation_prob, self.mutation_gene_change_percent)
        individual.set_chromosome(child_chromosome)

        return individual

    def new_population(self):
        """
        Creation of the new population.
        """

        # selection
        parents = self.selection(self.selection_type)
        parents = [individual[0] for individual in parents]
        new_population = []

        subtract_elitism = 0
        # if elitism is set, we need to have that individual as the first in population
        if self.elitism:
            for obj in parents:
                if id(obj) == id(self.rated_population[0][0]):
                    parents.remove(self.rated_population[0][0])
            subtract_elitism = 1
            parents = [self.rated_population[0][0]] + parents
            new_population = [parents[0]]

        # crossover or completely new individual
        # generates new individuals to satisfy population size
        for idx in range(0, self.pop_size - subtract_elitism):
            # crossover probability is satisfied
            if np.random.uniform(0, 1) <= self.crossover_prob:
                child = self.crossover(parents)
            else:
                child = Individual(self.dataset.distance_coords_dict, self.dataset.countries,
                                   self.mutation_prob, self.mutation_gene_change_percent)
                child.create_route_chromosome()

            new_population.append(child)

        # mutation of the individuals in population
        for idx, individual in enumerate(new_population):
            # do not mutate the first one if elitism
            if self.elitism:
                if idx > 0:
                    individual.mutate()
            else:
                individual.mutate()

        self.population = new_population

    def fitness(self):
        """
        Counts the fitness for entire population.
        """
        results = []
        for individual in self.population:
            results.append([individual, individual.fitness()])
        # we need to minimize fitness, which means sorting in ascending order
        self.rated_population = sorted(results, key=lambda x: x[1])

    def random_select(self):
        """
        Randomly selects k parents.
        """
        return random.choices(self.rated_population, k=self.k)

    def tournament(self):
        """
        Tournament based selection. It takes tournament_k representatives from population and selects the best k
        according to minimal fitness.
        """
        if self.tournament_k > self.pop_size:
            raise Exception("Number of tournament candidates must be less than or equal size of population.")

        parents = []
        while len(parents) != self.k:
            candidates = random.sample(self.rated_population, self.tournament_k)
            parent = [min(candidates, key=lambda candid: candid[1])]

            # check if not already selected
            if parents.count(parent[0]) == 0 or self.same_parents:
                parents += parent

        return parents

    def k_best_selection(self):
        """
        Selects first k-best individuals from population.
        """
        parents = self.rated_population[:self.k]
        return parents

    def rank_selection(self):
        """
        Rank selection uses relative fitness to assign section probabilities. This relative fitness is counted by the
        order of sorted individuals according to their fitness. This selection may be more suitable, if many individuals
        have a very similar fitness value.
        """
        backward_sort_population = sorted(self.rated_population, key=lambda x: -x[1])
        ranks = []
        pop_len = len(backward_sort_population)

        for i in range(1, len(backward_sort_population) + 1):
            ranks.append(i)
        rank_sum = pop_len * (pop_len + 1) / 2

        probabilities = []
        for rank in ranks:
            probabilities.append((float(rank) / rank_sum))

        parents = []
        while len(parents) != self.k:
            parent = random.choices(population=backward_sort_population, weights=probabilities)

            if parents.count(parent[0]) == 0 or self.same_parents:
                parents += parent
        return parents

    def roulette(self):
        """
        Roulette wheel selection is similar to rank selection, but probabilities of selection are not based on ranks
        but the proportional fitness.
        """
        sum_fitness = sum([individual[1] for individual in self.rated_population])

        probabilities = []

        for individual in self.rated_population:
            probabilities.append((individual[1] / sum_fitness))

        parents = []
        while len(parents) != self.k:
            parent = random.choices(population=self.rated_population, weights=probabilities)

            if parents.count(parent[0]) == 0 or self.same_parents:
                parents += parent
        return parents
