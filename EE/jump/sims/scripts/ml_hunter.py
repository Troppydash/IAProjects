import math
import pickle
from multiprocessing import freeze_support

import neat
import os
import multiprocessing

import matplotlib.pyplot as plt
from numba import jit

# global variables
generation = 0
processes = 6  # change this if you want more or less processes
thread_pool = None


### START::ENGINE DETAILS ###
@jit(nopython=True, fastmath=True)
def vec_add(ax, ay, bx, by):
    return ax + bx, ay + by


@jit(nopython=True, fastmath=True)
def vec_sub(ax, ay, bx, by):
    return ax - bx, ay - by


@jit(nopython=True, fastmath=True)
def vec_mag(ax, ay):
    return math.sqrt(ax ** 2 + ay ** 2)


@jit(nopython=True, fastmath=True)
def vec_scale(ax, ay, c):
    mag = vec_mag(ax, ay) + 0.0001
    return ax / mag * c, ay / mag * c


@jit(nopython=True, fastmath=True)
def exe_once(rx, ry, tx, ty, bx, by):
    """
    Executes a single step

    :param rx: delta rabbit X
    :param ry: delta rabbit Y
    :param tx: delta tracker X
    :param ty: delta tracker Y
    :param bx: current rabbit X
    :param by: current rabbit Y
    :return: new rabbit X, new rabbit Y
    """
    # this is where the rabbit goes to
    rabbit_pos = vec_scale(rx, ry, 1)

    # ensures the tracker is always 1 unit away from the rabbit
    tracker_pos = vec_scale(tx, ty, 1)

    # move rabbit
    nbx, nby = vec_add(bx, by, rabbit_pos[0], rabbit_pos[1])

    # move hunter towards tracker
    ntx, nty = vec_add(nbx, nby, tracker_pos[0], tracker_pos[1])
    if vec_mag(ntx, nty) <= 1:
        ax, ay = ntx, nty
    else:
        ax, ay = vec_scale(ntx, nty, 1)

    # center on a
    bx, by = vec_sub(nbx, nby, ax, ay)
    return bx, by


def discrete_distance(w):
    """
    A discrete distance simulation using exe_once

    :param w:
    :return:
    """

    # starting position
    bx = 0.0
    by = 2
    limit = 1_000

    n = 0
    while n < limit:
        output = w(n, bx, by)

        bx, by = exe_once(output[0], output[1], output[2], output[3], bx, by)

        if vec_mag(bx, by) >= 100:
            break

        n += 1

    return vec_mag(bx, by), n


def data_discrete_distance(w):
    """
    A discrete distance simulation to collect data
    Same as discrete_distance but returns a list of data

    :param w:
    :return:
    """

    # starting position
    ax = 0.0
    ay = 0.0
    bx = 0.0
    by = 2
    limit = 1000

    data = []

    n = 0
    while n < limit:

        output = w(n, *vec_sub(bx, by, ax, ay))
        rx, ry, tx, ty = output

        rabbit_pos = vec_scale(rx, ry, 1)
        tracker_pos = vec_scale(tx, ty, 1)
        by, by = vec_add(bx, by, rabbit_pos[0], rabbit_pos[1])
        ntx, nty = vec_add(bx, by, tracker_pos[0], tracker_pos[1])

        dx, dy = vec_sub(ntx, nty, ax, ay)
        if vec_mag(dx, dy) <= 1:
            ax, ay = ntx, nty
        else:
            ax, ay = vec_add(ax, ay, *vec_scale(dx, dy, 1))

        data.append([n, bx, by, ntx, nty, ax, ay])
        n += 1

    return vec_mag(*vec_sub(bx, by, ax, ay)), data


### END::ENGINE DETAILS ###

### START:MODEL SAVING ###

def save_model(winner, path='saved_hunter.pkl'):
    """
    Saves the best genome

    :param winner: The best genome
    :param path: Model path
    :return:
    """
    with open(path, 'wb') as f:
        pickle.dump(winner, f)


def open_model(config, path='saved_hunter.pkl'):
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


### END:MODEL SAVING ###

### START:TRAINING ###

def worker(inputs):
    """
    Returns the fitness value of the given genome

    :param inputs: A tuple of (network, genome)
    :return: The fitness
    """
    network, _ = inputs

    # run simulation
    def w(n, bx, by):
        return network.activate(
            [
                n,
                bx,
                by
            ]
        )

    dist, n = discrete_distance(w)
    return dist - math.log10(n)


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

    :param n: Number of generations
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


### END:TRAINING ###


### START:EVALUATION ###
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
    def w(n, bx, by):
        return network.activate(
            [
                n,
                bx,
                by
            ]
        )

    mag, data = data_discrete_distance(w)
    print(mag)

    # plot
    ts = [d[0] for d in data]
    rxs = [d[1] for d in data]
    rys = [d[2] for d in data]
    txs = [d[3] for d in data]
    tys = [d[4] for d in data]
    axs = [d[5] for d in data]
    ays = [d[6] for d in data]

    fig = plt.figure(figsize=(6, 6))
    ax = plt.gca()
    ax.scatter(rxs, rys, c=ts, cmap='viridis', s=0.1)
    ax.scatter(txs, tys, c=ts, cmap='gray', s=0.1)
    ax.scatter(axs, ays, c=ts, cmap='magma', s=0.1)

    fig.savefig(f'hunting.png', bbox_inches='tight', dpi=600)


### END:EVALUATION ###

def setup(is_train=True):
    """
    Boostrap the model

    :param is_train: Show train or show execution
    :return:
    """
    # get config
    config_path = os.path.join(os.path.dirname(__file__), 'hunter.config.txt')

    if is_train:
        train(config_path, n=100)
    else:
        run(config_path)


if __name__ == '__main__':
    freeze_support()
    setup(is_train=False)
