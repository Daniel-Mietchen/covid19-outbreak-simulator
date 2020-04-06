from enum import Enum

import random
import numpy as np
from collections import defaultdict

from .model import Model


class Individual(object):

    def __init__(self, id, model, logger):
        self.id = id
        self.model = model
        self.logger = logger

        self.infected = None
        self.quarantined = None
        self.n_infectee = 0

        self.r0 = None
        self.incubation_period = None
        self.trans_prob = None
        self.REMOVALd = None

    def quarantine(self, till):
        self.quarantined = till
        return [Event(till, EventType.REINTEGRATION, self, logger=self.logger)]

    def reintegrate(self):
        self.quarantined = None
        return []

    def symptomatic_infect(self, time, **kwargs):
        self.infected = time
        self.r0 = self.model.draw_rand_r0(symptomatic=True)
        self.incubation_period = self.model.draw_random_incubation_period()

        by = kwargs.get('by',)
        keep_symptomatic = kwargs.get('keep_symptomatic', False)

        # REMOVAL ...
        evts = []
        if not keep_symptomatic:
            if self.quarantined and time + self.incubation_period < self.quarantined:
                # scheduling ABORT
                evts.append(
                    Event(
                        time + self.incubation_period,
                        EventType.ABORT,
                        self,
                        logger=self.logger))
            else:
                evts.append(
                    # scheduling REMOVAL
                    Event(
                        time + self.incubation_period,
                        EventType.REMOVAL,
                        self,
                        logger=self.logger))
        #
        x_grid, self.trans_prob = self.model.get_symptomatic_transmission_probability(
            self.incubation_period, self.r0, 1 / 24)
        # infect only before removal
        if keep_symptomatic:
            x_before = x_grid
        else:
            x_before = [x for x in x_grid if x < self.incubation_period]
        infected = np.random.binomial(1, self.trans_prob[:len(x_before)],
                                      len(x_before))
        presymptomatic_infected = [
            xx for xx, ii in zip(x_before, infected)
            if ii and xx < self.incubation_period
        ]
        symptomatic_infected = [
            xx for xx, ii in zip(x_before, infected)
            if ii and xx >= self.incubation_period
        ]
        if self.quarantined:
            for idx, x in enumerate(x_before):
                if time + x < self.quarantined and infected[idx] != 0:
                    evts.append(
                        Event(
                            time + x,
                            EventType.INFECTION_AVOIDED,
                            self.id,
                            logger=self.logger,
                            by=self.id))
                    infected[idx] = 0
        #
        for x, infe in zip(x_before, infected):
            if infe:
                evts.append(
                    Event(
                        time + x,
                        EventType.INFECTION,
                        None,
                        logger=self.logger,
                        by=self))

        if by:
            by.n_infectee += 1
            params = [f'by={by.id}']
        else:
            params = []
        #
        params.extend([
            f'r0={self.r0:.2f}',
            f'r={sum(infected)}',
            f'r_presym={len(presymptomatic_infected)}',
            f'r_sym={len(symptomatic_infected)}',
            f'incu={self.incubation_period:.2f}',
        ])
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION.name}\t{self.id}\t{",".join(params)}\n'
        )
        return evts

    def asymptomatic_infect(self, time, **kwargs):
        if self.infected is not None:
            self.logger.write(
                f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION_IGNORED.name}\t{self.id}\tby={kwargs["by"]}\n'
            )
            return []

        self.infected = time
        self.r0 = self.model.rand_r0(symptomatic=True)
        self.incubation_period = self.model.rand_incu()

        by = kwargs.get('by',)
        keep_symptomatic = kwargs.get('keep_symptomatic', False)

        # REMOVAL ...
        evts = []
        if not keep_symptomatic:
            if self.quarantined and time + self.incubation_period < self.quarantined:
                # scheduling ABORT
                evts.append(
                    Event(
                        time + self.incubation_period,
                        EventType.ABORT,
                        self,
                        logger=self.logger))
            else:
                evts.append(
                    # scheduling REMOVAL
                    Event(
                        time + self.incubation_period,
                        EventType.REMOVAL,
                        self,
                        logger=self.logger))
        #
        x_grid, self.trans_prob = self.model.get_symptomatic_transmission_probability(
            self.incubation_period, self.r0, 1 / 24)
        # infect only before removal
        if keep_symptomatic:
            x_before = x_grid
        else:
            x_before = [x for x in x_grid if x < self.incubation_period]
        infected = np.random.binomial(1, self.trans_prob[:len(x_before)],
                                      len(x_before))
        presymptomatic_infected = [
            xx for xx, ii in zip(x_before, infected)
            if ii and xx < self.incubation_period
        ]
        symptomatic_infected = [
            xx for xx, ii in zip(x_before, infected)
            if ii and xx >= self.incubation_period
        ]
        if self.quarantined:
            for idx, x in enumerate(x_before):
                if time + x < self.quarantined and infected[idx] != 0:
                    evts.append(
                        Event(
                            time + x,
                            EventType.INFECTION_AVOIDED,
                            self.id,
                            logger=self.logger,
                            by=self.id))
                    infected[idx] = 0
        #
        for x, infe in zip(x_before, infected):
            if infe:
                evts.append(
                    Event(
                        time + x,
                        EventType.INFECTION,
                        None,
                        logger=self.logger,
                        by=self))

        if by:
            by.n_infectee += 1
            params = [f'by={by.id}']
        else:
            params = []
        #
        params.extend([
            f'r0={self.r0:.2f}',
            f'r={sum(infected)}',
            f'r_presym={len(presymptomatic_infected)}',
            f'r_sym={len(symptomatic_infected)}',
            f'incu={self.incubation_period:.2f}',
        ])
        self.logger.write(
            f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION.name}\t{self.id}\t{",".join(params)}\n'
        )
        return evts

    def infect(self, time, **kwargs):
        if self.infected is not None:
            self.logger.write(
                f'{self.logger.id}\t{time:.2f}\t{EventType.INFECTION_IGNORED.name}\t{self.id}\tby={kwargs["by"]}\n'
            )
            return []

        if self.model.drawn_is_asymptomatic():
            return self.asymptomatic_infect(time, **kwargs)
        else:
            return self.symptomatic_infect(time, **kwargs)


class EventType(Enum):
    # Infection
    INFECTION = 1
    # infection failed due to perhaps no more people to infect
    INFECTION_FAILED = 2
    # infection event happens during quarantine
    INFECTION_AVOIDED = 3
    # infection event happens to an infected individual
    INFECTION_IGNORED = 4

    # removal of individual showing symptom
    REMOVAL = 5
    # quarantine individual given a specified time
    QUARANTINE = 6
    # reintegrate individual to the population (release from quarantine)
    REINTEGRATION = 7

    # abort simulation, right now due to infector showing symptoms during quarantine
    ABORT = 8
    # end of simulation
    END = 9


class Event(object):
    '''
    Events that happen during the simulation.
    '''

    def __init__(self, time, action, target=None, logger=None, **kwargs):
        self.time = time
        self.action = action
        self.target = target
        self.logger = logger
        self.kwargs = kwargs

    def apply(self, population, args):
        if self.action == EventType.INFECTION:
            if self.target is not None:
                choice = self.target
            else:
                # select one non-quarantined indivudal to infect
                ids = [
                    id for id, ind in population.items()
                    if (not self.target or id != self.target.id) and
                    not ind.quarantined
                ]
                if not ids:
                    self.logger.write(
                        f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_FAILED.name}\t{self.target.id}\tby={self.kwargs["by"]}\n'
                    )
                    return []
                choice = random.choice(ids)
            return population[choice].infect(
                self.time,
                keep_symptomatic=args.keep_symptomatic,
                **self.kwargs)
        elif self.action == EventType.QUARANTINE:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.QUARANTINE.name}\t{self.target.id}\ttill={self.kwargs["till"]:.2f}\n'
            )
            return population[self.target.id].quarantine(**self.kwargs)
        elif self.action == EventType.REINTEGRATION:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.REINTEGRATION.name}\t{self.target.id}\t.\n'
            )
            return population[self.target.id].reintegrate(**self.kwargs)
        elif self.action == EventType.INFECTION_AVOIDED:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.INFECTION_AVOIDED.name}\t.\tby={self.kwargs["by"]}\n'
            )
            return []
        elif self.action == EventType.REMOVAL:
            self.logger.write(
                f'{self.logger.id}\t{self.time:.2f}\t{EventType.REMOVAL.name}\t{self.target.id}\t.\n'
            )
            population.pop(self.target.id)
            return []
        else:
            raise RuntimeError(f'Unrecognized action {self.action}')

    def __str__(self):
        return f'{self.action.name}_{self.target.id if self.target else ""}_at_{self.time:.2f}'


class Simulator(object):

    def __init__(self, params, logger, args):
        self.logger = logger
        self.args = args
        self.params = params
        self.model = None

    def simulate(self, id):
        #
        # get proportion of asymptomatic
        #
        self.params.draw_proportion_of_asymptomatic_carriers()

        self.model = Model(self.params)

        # collection of individuals
        population = {
            idx: Individual(idx, model=self.model, logger=self.logger)
            for idx in range(self.args.popsize)
        }

        events = defaultdict(list)
        self.logger.id = id

        # quanrantine the first person if args.pre-quarantine > 0
        if self.args.pre_quarantine is not None and self.args.pre_quarantine > 0:
            events[0].append(
                Event(
                    0,
                    EventType.QUARANTINE,
                    population[0],
                    logger=self.logger,
                    till=self.args.pre_quarantine))
        # infect the first person
        events[0].append(Event(0, EventType.INFECTION, target=0, logger=logger))

        while True:
            # find the latest event
            time = min(events.keys())

            new_events = []
            aborted = False
            # processing events
            for evt in events[time]:
                if evt.action == EventType.ABORT:
                    logger.write(
                        f'{logger.id}\t{time:.2f}\t{EventType.ABORT.name}\t{evt.target.id}\t.\n'
                    )
                    aborted = True
                    break
                # event triggers new event
                new_events.extend(evt.apply(population, self.args))
            events.pop(time)
            #
            for evt in new_events:
                # print(f'ADDING\t{evt}')
                events[evt.time].append(evt)

            if not events or aborted:
                break
        logger.write(
            f'{logger.id}\t{time:.2f}\t{EventType.END.name}\t{len(population)}\tpopsize={len(population)}\n'
        )