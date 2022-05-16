import operator
import random

import numpy
import math

from deap import base
from deap import benchmarks
from deap import creator
from deap import tools


class PSOwithDEAP:
    def __init__(self, params):
        self.setup_creator()
        self.setup_toolbox()


    def setup_creator(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Particle", list, fitness=creator.FitnessMax, speed=list, 
                       smin=None, smax=None, best=None)

    def setup_toolbox(self, eval_func, particle_size=2, psmaxmin=[-6, 6, -3, 3], phi1=2.0, phi2=2.0):
        self.particle_size = particle_size
        self.psmaxmin = psmaxmin
        self.toolbox = base.Toolbox()
        self.toolbox.register("particle", self.generate, size=self.particle_size, 
                              pmin=self.psmaxmin[0], pmax=self.psmaxmin[1], 
                              smin=self.psmaxmin[2], smax=self.psmaxmin[3])
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.particle)
        self.toolbox.register("update", self.updateParticle, phi1=phi1, phi2=phi2)
        self.toolbox.register("evaluate", eval_func)

    def generate(self, size, pmin, pmax, smin, smax):
        part = creator.Particle(random.uniform(pmin, pmax) for _ in range(size)) 
        part.speed = [random.uniform(smin, smax) for _ in range(size)]
        part.smin = smin
        part.smax = smax
        return part
    
    def updateParticle(self, part, best, phi1, phi2):
        u1 = (random.uniform(0, phi1) for _ in range(len(part)))
        u2 = (random.uniform(0, phi2) for _ in range(len(part)))
        v_u1 = map(operator.mul, u1, map(operator.sub, part.best, part))
        v_u2 = map(operator.mul, u2, map(operator.sub, best, part))
        part.speed = list(map(operator.add, part.speed, map(operator.add, v_u1, v_u2)))
        for i, speed in enumerate(part.speed):
            if abs(speed) < part.smin:
                part.speed[i] = math.copysign(part.smin, speed)
            elif abs(speed) > part.smax:
                part.speed[i] = math.copysign(part.smax, speed)
        part[:] = list(map(operator.add, part, part.speed))

    def start(self):
        self.pop = self.toolbox.population(n=5)
        self.stats = tools.Statistics(lambda ind: ind.fitness.values)
        self.stats.register("avg", numpy.mean)
        self.stats.register("std", numpy.std)
        self.stats.register("min", numpy.min)
        self.stats.register("max", numpy.max)

        self.logbook = tools.Logbook()
        self.logbook.header = ["gen", "evals"] + self.stats.fields

        self.GEN = 1000
        self.best = None

        for g in range(self.GEN):
            for part in self.pop:
                part.fitness.values = self.toolbox.evaluate(part)
                if not part.best or part.best.fitness < part.fitness:
                    part.best = creator.Particle(part)
                    part.best.fitness.values = part.fitness.values
                if not best or best.fitness < part.fitness:
                    best = creator.Particle(part)
                    best.fitness.values = part.fitness.values
            for part in self.pop:
                self.toolbox.update(part, best)

            # Gather all the fitnesses in one list and print the stats
            self.logbook.record(gen=g, evals=len(self.pop), **self.stats.compile(self.pop))
            print(self.logbook.stream)

        return self.pop, self.logbook, best