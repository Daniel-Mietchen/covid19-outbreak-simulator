import argparse
from covid19_outbreak_simulator.simulator import Event, EventType


class PlugInEvent(object):

    def __init__(self, time, plugin, args):
        self.time = time
        self.plugin = plugin
        self.args = args
        self.action = EventType.PLUGIN

    def apply(self, population, simu_args):
        return self.plugin.apply_plugin(self.time, population, self.args,
                                        simu_args)

    def __str__(self):
        return f'Call {self.plugin} at {self.time}'


class BasePlugin(object):

    def __init__(self, simulator, *args, **kwargs):
        self.simulator = simulator
        self.logger = self.simulator.logger if self.simulator else None
        self.last_applied = None
        self.applied_at = set()

    def __str__(self):
        return self.__class__.__name__

    def get_parser(self):
        parser = argparse.ArgumentParser(
            '--plugin', description='A plugin for covid19-outbreak-simulator')
        parser.add_argument(
            '--start',
            type=float,
            help='''Start time. Default to 0 no parameter is defined so the
                plugin will be called once at the beginning.''')
        parser.add_argument(
            '--end',
            type=float,
            help='''End time, default to none, meaning there is no end time.''')
        parser.add_argument(
            '--at',
            nargs='+',
            type=float,
            help='''Specific time at which the plugin is applied.''')
        parser.add_argument(
            '--interval',
            type=float,
            help='''Interval at which plugin is applied, it will assume
             a 0 starting time if --start is left unspecified.''')
        return parser

    def get_plugin_events(self, args):
        events = []
        if args.start is not None:
            events.append(PlugInEvent(time=args.start, plugin=self, args=args))

        if args.interval is not None and args.start is None:
            events.append(PlugInEvent(time=0, plugin=self, args=args))

        if args.at is not None:
            for t in args.at:
                events.append(PlugInEvent(time=t, plugin=self, args=args))

        if not events:
            events.append(PlugInEvent(time=0, plugin=self, args=args))
        return events

    def can_apply(self, time, args):
        # the plugin could be applied multiple times at a timepoint
        # due to the generation of more events at the same time point.
        if time in self.applied_at:
            return False

        if args.end is not None and time > args.end:
            return False

        if args.start is not None:
            if self.last_applied is None and time >= args.start:
                self.applied_at.add(time)
                self.last_applied = time
                return True

        if args.interval is not None:
            # if start is not applied, the first call should start it
            if (self.last_applied is None and args.start is None) or (
                    self.last_applied is not None and
                    time - self.last_applied >= args.interval):
                self.applied_at.add(time)
                self.last_applied = time
                return True

        if args.at is not None and time in args.at:
            self.applied_at.add(time)
            self.last_applied = time
            return True

        return False

    def apply(self, time, population, args=None, simu_args=None):
        # redefined by subclassed
        raise ValueError('This function should be redefined.')

    def apply_plugin(self, time, population, args=None, simu_args=None):

        events = self.apply(time, population, args, simu_args)

        # schedule the next call
        if args.interval is not None and (args.end is None or
                                          time + args.interval <= args.end):
            events.append(
                PlugInEvent(time=time + args.interval, plugin=self, args=args))
        return events