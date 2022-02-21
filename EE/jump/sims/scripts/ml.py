import math
import pickle
from multiprocessing import freeze_support

import neat
import time
import os
import random
import multiprocessing

import matplotlib.pyplot as plt

from notebooks.scripts.vectors import *

# global variables
generation = 0
thread_pool = None
processes = 6

default_j = (-800, 250, 10, [0, 250])


### START::ENGINE DETAILS ###

def air_time_discrete(g, tau, v0=280):
    height = 0.0001
    vel_height = v0

    t = 0
    while height > 0:
        height = height + vel_height * tau + 0.5 * g * tau ** 2
        vel_height = vel_height + g * tau
        t += tau

    return t


def pos(x):
    if x > 0:
        return 1
    else:
        return 0


def discrete_distance(w, h=1 / 64, j=None):
    """
    not needed, but why not

    :param w:
    :param h:
    :param j:
    :return:
    """

    # source engine constants
    if j is None:
        j = default_j

    g, l, A, v0 = j

    tf = air_time_discrete(g, h)

    data = [[0, 0, 0]]

    # state variables
    v = v0
    p = [0, 0]
    t = 0
    for n in range(0, math.ceil(tf / h)):
        # update position
        p = vec_add(p, vec_scale(v, h))

        data.append([t, p[0], p[1]])

        # obtain acceleration
        a = w(t, p, v)

        gamma1 = l * A * h
        gamma2 = l - vec_dot(v, a)
        f = pos(gamma2) * (gamma2 * pos(gamma1 - gamma2) + gamma1 * pos(gamma2 - gamma1)) / h

        # update velocity
        v = vec_add(v, vec_scale(a, h * f))

        # update time
        t += h

    return p, data


### END::ENGINE DETAILS ###


def worker(inputs):
    """
    Returns the fitness value of the given genome

    :param inputs: A tuple of (network, genome)
    :return: The fitness
    """
    network, _ = inputs

    # run simulation
    def w(t, p, v):
        output = network.activate(
            [
                t,
                p[0],
                p[1],
                v[0],
                v[1]
            ]
        )

        # fix output
        x = max(min(output[0], 1), 0)
        y = math.sqrt(1 - x ** 2)
        return [x, y]

    pos, _ = discrete_distance(w)
    return pos[1]


def compute(genomes, config):
    """
    Computes the fitness of the given genomes, this is a single generation

    :param genomes: The list of genomes
    :param config: Config
    :return: None
    """
    global generation
    global thread_pool

    if thread_pool is None:
        thread_pool = multiprocessing.Pool(processes=processes)

    generation += 1

    print(f"Generation {generation}:")
    networks = []
    new_genomes = []

    for genome_id, genome in genomes:
        genome.fitness = 0

        network = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(network)

        new_genomes.append(genome)

    fitnesses = thread_pool.map(worker, zip(networks, new_genomes))

    # map fitnesses to genomes
    for genome, fitness in zip(new_genomes, fitnesses):
        genome.fitness = fitness

    print(f"Best Fitness: {max(fitnesses)}")


def train(config_path, n=100):
    """
    Trains the model

    :param config_path: The path to the config file
    :return:
    """
    global thread_pool

    # configurations
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    thread_pool = multiprocessing.Pool(processes=processes)
    try:
        population.run(compute, n)
    except KeyboardInterrupt:
        pass

    # get the best genome
    winner = population.best_genome

    save_model(winner)


def save_model(winner, path='saved.pkl'):
    """
    Saves the best genome

    :param winner: The best genome
    :param path: Model path
    :return:
    """
    with open(path, 'wb') as f:
        pickle.dump(winner, f)


def open_model(config, path='saved.pkl'):
    """
    Opens the best genome

    :param config: Config
    :param path: Model path
    :return: A list of genomes
    """
    with open(path, 'rb') as f:
        genome = pickle.load(f)

    genomes = [(1, genome)]

    return genomes


def run(config_path):
    """
    Runs the model

    :param config_path: Config path
    :return:
    """
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    genomes = open_model(config)
    execute(genomes[0], config)


def execute(genome, config):
    """
    Executes and graphs the model

    :param genome:
    :param config:
    :return:
    """
    network = neat.nn.FeedForwardNetwork.create(genome[1], config)

    # run simulation
    def w(t, p, v):
        output = network.activate(
            [
                t,
                p[0],
                p[1],
                v[0],
                v[1]
            ]
        )

        # fix output
        x = max(min(output[0], 1), 0)
        y = math.sqrt(1 - x ** 2)
        return [x, y]

    pos, data = discrete_distance(w)
    print(pos)

    # plot
    ts = [d[0] for d in data]
    xs = [d[1] for d in data]
    ys = [d[2] for d in data]

    fig = plt.figure(figsize=(6, 6))
    ax = plt.gca()
    sca = ax.scatter(xs, ys, c=ts)
    # show legends
    legends = ax.legend(*(sca.legend_elements()),
                        loc="lower right", title="Time / t / s")
    ax.add_artist(legends)

    fig.savefig(f'path.png', bbox_inches='tight', dpi=600)


def setup(is_train=True):
    # get config
    config_path = os.path.join(os.path.dirname(__file__), 'config.feedforward.txt')

    if is_train:
        train(config_path, n=1000)
    else:
        run(config_path)


if __name__ == '__main__':
    freeze_support()
    setup(is_train=False)
