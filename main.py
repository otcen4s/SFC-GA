from typing import Any
from src.dataset import Dataset
from argparse import ArgumentParser
from src.ga import GA
import src.app as app
from src.utils import add_routes, json_str_or_path, json_init_args
import os


def parse_arguments():
    """
    Argument parsing
    """
    parser = ArgumentParser()
    parser.add_argument("--ga-config", help="Path to json config with GA parameters.", type=json_str_or_path)
    parser.add_argument("--data-config", help="Path to json config for dataset.", type=json_str_or_path)
    parser.add_argument("--csv-data-path", help="Path to csv data.", type=str, default="./csv")
    parser.add_argument("--generations", help="Number of generations.", type=int, default=500)
    parser.add_argument("--population", help="Size of population.", type=int, default=5000)
    parser.add_argument("--crossover-prob", help="Probability of crossover.", type=float, default=0.95)
    parser.add_argument("--mutation-prob", help="Probability of mutation.", type=float, default=0.95)
    parser.add_argument("--tournament-k", help="Number of individuals for tournament.", type=int, default=10)
    parser.add_argument("--elitism", help="Bool parameter to preserve elitism.", type=bool, default=True)
    parser.add_argument("--k-best", help="Number of k best individuals to preserve in next generation.", type=int,
                        default=100)
    parser.add_argument("--same-parents", help="Same individuals can be generated as parents.", type=bool, default=False)
    parser.add_argument("--selection", help="Type of selection for parents.", type=str, default="tournament")
    parser.add_argument("--mut-change", help="How big part of chromosome will be potentially changed in % / 100.",
                        type=float, default=0.0005)
    parser.add_argument("--show-only-changes", help="The graph animation will be showing only the generations where "
                                                    "the individual chromosome changed", type=bool, default=True)
    parser.add_argument("--iter-stop", help="Max number of iterations for no change fitness.", type=int, default=100)
    parser.add_argument("--n-rows",
                        help="Choose number of rows to be processed. If None is set, all rows will be processed.",
                        type=Any, default=None)
    parser.add_argument("--random-pick-dataset", help="Randomly pick entries from dataset.", type=bool, default=False)
    parser.add_argument("--save-path", help="Animation plots save path.", type=str, default="./animations/tsp.html")
    parser.add_argument("--choose-my-route", help="If set to True, your own route path for TSP will be selected.", type=bool, default=False)
    parser.add_argument("--selected-places", help="If choose-my-route is set to True, enter the path in list format.", type=list, default=[])

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    args = json_init_args(args, args.ga_config, args.data_config)

    # dataset parsing
    dataset = Dataset(args.csv_data_path, args.n_rows, args.random_pick_dataset, args.choose_my_route, args.selected_places)
    dataset.__build__()

    # genetic algorithm initial setting
    ga = GA(pop_size=args.population, dataset=dataset, elitism=args.elitism, crossover_prob=args.crossover_prob,
            mutation_prob=args.mutation_prob, k_parents=args.k_best, selection=args.selection,
            mutation_gene_change_percent=args.mut_change, tournament_k=args.tournament_k, same_parents=args.same_parents)
    ga.init_population()

    no_change_iter = 0
    data = []
    last_best_fitness = None

    # main loop of the program executing generation based on genetic algorithm
    for i in range(args.generations):
        # early stopping if there is no change in fitness for given number of generations
        if no_change_iter == args.iter_stop:
            break

        # compute fitness for all individuals
        ga.fitness()

        # save last best fitness [Individual, fitness]
        if last_best_fitness is not None:
            if last_best_fitness[1] == ga.rated_population[0][1]:
                no_change_iter += 1
            else:
                no_change_iter = 0

        print(f"Generation #{i}")
        print(f"Best fitness: {ga.rated_population[0][1]}")

        # appending data
        if not args.show_only_changes or i == 0:
            data += add_routes(ga.rated_population[0], i)
        elif args.show_only_changes:
            if last_best_fitness[0] != ga.rated_population[0][0] or (last_best_fitness[1] > ga.rated_population[0][1]):
                data += add_routes(ga.rated_population[0], i)

        last_best_fitness = ga.rated_population[0]
        # recreate population
        ga.new_population()

    scope = "world"
    if os.path.basename(args.csv_data_path) != "world.csv":
        scope = "europe"

    # plot and save data
    app.run(data, args.save_path, scope=scope)


if __name__ == '__main__':
    main()
