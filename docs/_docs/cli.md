---
title: Command line interface
permalink: /docs/cli/
---

## Command line options of the core simulator

```
$ outbreak_simulator -h

usage: outbreak_simulator [-h] [--popsize POPSIZE [POPSIZE ...]] [--susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]]
                          [--symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]] [--asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]]
                          [--incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]] [--repeats REPEATS]
                          [--handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]] [--infectors [INFECTORS [INFECTORS ...]]]
                          [--interval INTERVAL] [--logfile LOGFILE] [--prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]]
                          [--stop-if [STOP_IF [STOP_IF ...]]] [--leadtime LEADTIME] [--plugin ...] [-j JOBS]

optional arguments:
  -h, --help            show this help message and exit
  --popsize POPSIZE [POPSIZE ...]
                        Size of the population, including the infector that will be introduced at the beginning of the simulation. It should
                        be specified as a single number, or a serial of name=size values for different groups. For example "--popsize
                        nurse=10 patient=100". The names will be used for setting group specific parameters. The IDs of these individuals
                        will be nurse0, nurse1 etc.
  --susceptibility SUSCEPTIBILITY [SUSCEPTIBILITY ...]
                        Weight of susceptibility. The default value is 1, meaning everyone is equally susceptible. With options such as "--
                        susceptibility nurse=1.2 patients=0.8" you can give weights to different groups of people so that they have higher or
                        lower probabilities to be infected.
  --symptomatic-r0 SYMPTOMATIC_R0 [SYMPTOMATIC_R0 ...]
                        Production number of symptomatic infectors, should be specified as a single fixed number, or a range, and/or
                        multipliers for different groups such as A=1.2. For example "--symptomatic-r0 1.4 2.8 nurse=1.2" means a general R0
                        ranging from 1.4 to 2.8, while nursed has a range from 1.4*1.2 and 2.8*1.2.
  --asymptomatic-r0 ASYMPTOMATIC_R0 [ASYMPTOMATIC_R0 ...]
                        Production number of asymptomatic infectors, should be specified as a single fixed number, or a range and/or
                        multipliers for different groups
  --incubation-period INCUBATION_PERIOD [INCUBATION_PERIOD ...]
                        Incubation period period, should be specified as "lognormal" followed by two numbers as mean and sigma, or "normal"
                        followed by mean and sd, and/or multipliers for different groups. Default to "lognormal 1.621 0.418"
  --repeats REPEATS     Number of replicates to simulate. An ID starting from 1 will be assinged to each replicate and as the first columns
                        in the log file.
  --handle-symptomatic [HANDLE_SYMPTOMATIC [HANDLE_SYMPTOMATIC ...]]
                        How to handle individuals who show symptom, which should be "keep" (stay in population), "remove" (remove from
                        population), and "quarantine" (put aside until it recovers). all options can be followed by a "proportion", and
                        quarantine can be specified as "quarantine_7" etc to specify duration of quarantine.
  --infectors [INFECTORS [INFECTORS ...]]
                        Infectees to introduce to the population. If you would like to introduce multiple infectees to the population, or if
                        you have named groups, you will have to specify the IDs of carrier such as --infectors nurse1 nurse2.
  --interval INTERVAL   Interval of simulation, default to 1/24, by hour
  --logfile LOGFILE     logfile
  --prop-asym-carriers [PROP_ASYM_CARRIERS [PROP_ASYM_CARRIERS ...]]
                        Proportion of asymptomatic cases. You can specify a fix number, or two numbers as the lower and higher CI (95%) of
                        the proportion. Default to 0.10 to 0.40. Multipliers can be specified to set proportion of asymptomatic carriers for
                        particular groups.
  --stop-if [STOP_IF [STOP_IF ...]]
                        Condition at which the simulation will end. By default the simulation stops when all individuals are affected or all
                        infected individuals are removed. Current you can specify a time after which the simulation will stop in the format
                        of `--stop-if "t>10"' (for 10 days).
  --leadtime LEADTIME   With "leadtime" infections are assumed to happen before the simulation. This option can be a fixed positive number
                        `t` when the infection happens `t` days before current time. If can also be set to 'any' for which the carrier can be
                        any time during its course of infection, or `asymptomatic` for which the leadtime is adjust so that the carrier does
                        not show any symptom at the time point (in incubation period for symptomatic case). All events triggered before
                        current time are ignored.
  --plugin ...          One or more of "--plugin MODULE.PLUGIN [args]" to specify one or more plugins. FLUGIN will be assumed to be MODULE
                        name if left unspecified. Each plugin has its own parser and can parse its own args.
  -j JOBS, --jobs JOBS  Number of process to use for simulation. Default to number of CPU cores.

```



# Examples

## A small population with the introduction of one carrier

Assuming that there is no asymptomatic carriers, we can introduce one infected
carrier to a population of size 64, and observe the development of the outbreak.

```sh
outbreak_simulator --infector 0  --rep 10000 --prop-asym-carriers 0 --logfile simu_remove_symptomatic.log
```

We can also assume from 20% to 40% of infected individuals will not show any symptom
the default parameters for `prop-asym-carriers` is `0.2` to `0.4` so it is actually
not needed.

```sh
outbreak_simulator --infector 0  --rep 10000 --prop-asym-carriers .20 .40 --logfile simu_with_asymptomatic.log
```

We can quarantine the carrier for 7 days, but here we need to use a plugin that applies at time 0

```sh
outbreak_simulator --infector 0  --rep 10000 --logfile simu_quarantine_7.log \
  --plugin quarantine --at 0 --duration 7
```

or we can try quarantine for 14 days...

```sh
outbreak_simulator --infector 0  --rep 10000 --logfile simu_quarantine_15.log \
  --plugin quarantine --at 0 --duration 14
```

The above simulation assumes that the carriers are infected right before quarantine, which is not really
realistic. The following add some `leadtime` and simulate scenarios that people enters quarantine
as long as they do not show symptom.

```
outbreak_simulator --infector 0  --rep 10000 --leadtime asymptomatic --logfile simu_leadtime_quarantine_7.log -j 1 \
  --plugin quarantine --at 0 --duration 7
```

## Evolution of a large population

Assuming a population of size `34993` with `85` total cases (in the past few months). Assuming that every case has 4
unreported (asymptomatic etc) cases, there has been `85*5` cases so the population has a seroprevalence of
`85*5/34993=0.01214`. Assuming 8 weeks outbreak duration and 2 week active window, 1/4 cases would be "active",
so the current incidence rate would be `85*5/4 / 34993 = 0.003036`.

We assume that 75% of all symptomatic cases will be quarantined (hospitalized), the rest would be able to infect
others. We only simulate 1 replicate because the population size is large. The command to simulate this population
is as follows:

```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_quarantine_all.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_quarantine_all.txt
```

The simulation shows that the last case will recover after 173 days with 4.18% seroprevalence,
a total of 1462 cases (29 deaths if we assume 2% fatality rate) at the end of the simulation.
Active cases of 104 new cases happens around the 50 days.

However, if people with mild symptoms are not hospitalized (or quarantined) and continue
to infect others, the situation will get much worse.

```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 0.75 \
    --logfile pop_quarantine_.75.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_quarantine_.75.txt
```

The simulation shows that the outbreak will last 223 days with a seroprevalence of `32%`.
A total of 11205 people will be infected (224 deaths if we assume 2% fatality rate). A peak
of 1500 cases per day happens at around 80 days.

Social distancing can slow down the spread of the disease. The current R0 for symptomatic cases
is assumed to be between 1.4 and 2.8.

Let us assume that we can tighten up social distancing to half the R0 from 0.7 to 1.4, at day 20

```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_distancing_at_20.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 > pop_distancing_at_20.txt \
    --plugin setparam --symptomatic-r0 1.2 2.4 --at 20
```

With increased social distancing, the daily number of cases starts to decline shortly after
day 20 (about 346), the outbreak still lasted 263 days but seroprevalence peaked at 4.42%.q

Now, what if we start social distancing earlier, say at day 10?


```sh
outbreak_simulator  --popsize 34993 -j1 --rep 1 --handle-symptomatic quarantine_14 1 \
    --logfile pop_distancing_at_10.log  \
    --plugin init --seroprevalence 0.01214 --incidence-rate 0.003036 \
    --plugin stat --interval 1 \
    --plugin setparam --symptomatic-r0 1.2 2.4 --at 10 \
    > pop_distancing_at_10.txt
```

The peak happens after day 10 at around 200 cases per day. The outbreak stops after 80
days, with an ending seroprevalence of `2.2%`.

## Heterogeneous situation

Now, let us assume that we have a population with two subpopulations `A` and `B`, be they workers and guest, doctors and patients. Now let us assume that subpopulation `A` is more
susceptible (more contact with others), and more infectious. Let us also assume that
there is a intermediate inflow of `A` to the population, half of them would be carriers.
This simulation can be written as

```sh
outbreak_simulator --popsize A=2000 B=500 --rep 10 --handle-symptomatic quarantine_14 1 \
  --susceptibility A=1.2 --symptomatic-r0 A=1.2 B=0.8 --logfile hetero.log \
  --stop-if 't>40' \
  --plugin stat --interval 1 \
  --plugin insert A=5 --prop-of-infected 0.5 --interval 1 \
  > hetero.txt

```

because the continuous injection of cases, the outbreak will not stop by itself so we have
to use `--stop-at 't>40'` to set the duration of the simulation.

### Specigy group-specific parameters

Parameters `symptomatic-r0`, `asymptomatic-r0` and `incubation-period` can be
set to different values for each groups. These are achived by "multipliers",
which multiplies specified values to values drawn from the default distribution.

For example, if in a hospital environment nurses, once affected, tends to have
higher `R0` because he or she contact more patients, and on the other hand
patients are less mobile and should have lower `R0`. In some cases the nurses
are even less protected and are more susceptible. You can run a simulation
with two patients carrying the virus with the following options:

```
outbreak_simulator --popsize nurse=10 patient=100 \
    --symptomatic-r0 nurse=1.5 patient=0.8 \
    --asymptomatic-r0 nurse=1.5 patient=0.8 \
    --susceptibility nurse=1.2 patient=0.8 \
    --infector patient0 patient1
```