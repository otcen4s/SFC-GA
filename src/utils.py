import json


def get_lon_lat(individual):
    """
    Extracting latitude, longitude and corresponding distances with countries included for further processing.
    """
    chromosome = individual.chromosome
    paths = []
    for idx in range(0, len(chromosome)):
        from_ = chromosome[idx]
        if idx + 1 < len(chromosome):
            to = chromosome[idx + 1]
        else:
            to = chromosome[0]
        paths.append([individual.distance_coords_dict[from_ + "-" + to][1], from_, to,
                      individual.distance_coords_dict[from_ + "-" + to][0]])
    return paths


def add_routes(best_individual, generation):
    """
    Creates data list with corresponding values for graph plot.
    """
    data = []
    paths = get_lon_lat(best_individual[0])
    first_path = True

    for path in paths:
        color = "#32CD32"
        if first_path:
            color = "firebrick"
        data.append([path[0][0], path[0][1], generation, path[1],
                     str(path[1]) + "-" + str(path[2]) + ": " + str(path[3]) + " km", best_individual[1], color])
        data.append([path[0][2], path[0][3], generation, path[2],
                     str(path[2]) + "-" + str(path[1]) + ": " + str(path[3]) + " km", best_individual[1], color])
        first_path = False
    return data


def json_str_or_path(s):
    """
    JSON parser for argument parsing, when JSON file is provided.
    """
    try:
        value = json.loads(s)
        return value
    except ValueError:
        pass
    with open(s) as f:
        return json.load(f)


def json_init_args(args, ga_config, data_config):
    """
    Setting values from parsed JSON to corresponding args.
    """
    if ga_config is not None:
        args.population = ga_config["population"]
        args.generations = ga_config["generations"]
        args.elitism = ga_config["elitism"]
        args.crossover_prob = ga_config["crossover_prob"]
        args.mutation_prob = ga_config["mutation_prob"]
        args.k_best = ga_config["k_best"]
        args.selection = ga_config["selection"]
        args.mut_change = ga_config["mut_change"]
        args.iter_stop = ga_config["iter_stop"]
        args.tournament_k = ga_config["tournament_k"]
        args.same_parents = ga_config["same_parents"]
    if data_config is not None:
        args.csv_data_path = data_config["csv_data_path"]
        args.n_rows = data_config["n_rows"]
        args.random_pick_dataset = data_config["random_pick_dataset"]
        args.save_path = data_config["save_path"]
        args.selected_places = data_config["selected_places"]
        args.choose_my_route = data_config["choose_my_route"]

    return args
