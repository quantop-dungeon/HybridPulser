import matplotlib.pyplot as plt


class Sequence:
    """Defines a realization of pulses in multiple synchronized digital 
    channels.

    Pulses can be added to the sequence using add_pulse and append_pulse 
    methods, which are different only in the way they parametrize timing. 

    The duration of the sequence equals (stop_time - start_time) and can be 
    set via the stop_time and start_time attributes. When new pulses are added 
    that go beyond the current interval [stop_time, start_time], the start and 
    the stop times are automatically updated to accommodate all pulses.

    Attributes:
        channels: 
            A list of DigitalChannel objects containing the channel state 
            transitions. 
        start_time: 
            See the __init__ args.
        stop_time: 
            See the __init__ args.
    """

    def __init__(self, nchannels: int = 8, defaults=None, start_time: float = 0,
                 stop_time: float = 0):
        """Creates an empty pulse sequence.

        Args:
            nchannels: 
                Number of channels.
            defaults (List[bool] or None):
                The default states of the channels. Must be a list of logical
                values with the length equal to nchannels or None, the latter
                is interpreted as setting all default states to False.
            start_time:
                The beginning time of the pulse sequence (in seconds). When new 
                pulses are added, this time is automatically updated to 
                accomodate them.
            stop_time:
                The end time of the pulse sequence (in seconds). When new 
                pulses are added, this time is automatically updated to 
                accomodate them. 
        """

        if not stop_time >= start_time:
            raise ValueError('stop_time must be >= start_time')

        self._interval = [start_time, stop_time]

        if defaults:
            if len(defaults) != nchannels:
                raise ValueError(f'The number of defaults ({len(defaults)}) '
                                 'must be equal to the number of channels '
                                 f'({nchannels})')
        else:
            defaults = [False]*nchannels

        self.channels = [DigitalChannel(defaults[i]) for i in range(nchannels)]

    def add_pulse(self, ch: int, t0: float, duration: float) -> None:
        """Adds a pulse to the specified channel. A pulse consists of switching
        the channel state from the previous one, keeping the new state for the
        duration of time, and then switching the state back.

        Args:
            ch: 
                Channel number.
            t0: 
                The time of the front edge of the pulse (s).
            duration:
                The duration of the pulse (s) - the interval between the front 
                and the back edges.
        """
        if not duration > 0:
            raise ValueError('Duration must be greater than zero.')

        c = self.channels[ch]  # A short-hand notation

        t1 = t0 + duration  # The back edge of the pulse

        # Checks that there are no existing state switches between the front
        # and the back edges of the pulse.
        ft = [t for t in c.switch_times if (t > t0 and t < t1)]
        if ft:
            raise ValueError(f'There must be no existing transitions in the '
                             f'channel {ch} during the interval of the new '
                             f'pulse, [{t0}, {t1}]. Currently, there are '
                             f'transitions at t = {ft}.')

        # Adds a new pulse to the channel.
        c.add_state_switch(t0)
        c.add_state_switch(t1)

    def append_pulse(self, ch: int, delay: float, duration: float) -> None:
        """Appends a pulse to the specified channel. A pulse consists of
        switching the channel state from the defult, keeping the new state 
        for the duration of time, and then switching the state back.

        Args:
            ch: 
                Channel number.
            delay: 
                The delay (s) between the latest existing state transition in 
                the channel and the front edge of the new pulse.
            duration:
                The duration (s) of the pulse - the interval between the front 
                and the back edges.
        """
        if not delay >= 0:
            raise ValueError('Delay must be greater or equal to zero.')
        if not duration > 0:
            raise ValueError('Duration must be greater than zero.')

        c = self.channels[ch]  # A short-hand notation

        # The front edge of the pulse.
        if c.switch_times:
            t0 = c.switch_times[-1] + delay
        else:
            t0 = self.start_time + delay

        t1 = t0 + duration  # The back edge of the pulse

        # Adds a new pulse to the channel.
        c.add_state_switch(t0)
        c.add_state_switch(t1)

    @property
    def start_time(self):

        # Finds the minimum of the internally stored start time and
        # the time of the earliest state transition in the channels.
        value = self._interval[0]
        for c in self.channels:
            if c.switch_times and value > c.switch_times[0]:
                value = c.switch_times[0]

        return value

    @start_time.setter
    def start_time(self, value):
        for i, c in enumerate(self.channels):
            if c.switch_times and value > c.switch_times[0]:
                raise ValueError('The start time cannot be greater than '
                                 'the time of the first transition '
                                 f'in channel {i} (t={c.switch_times[0]}).')

        if value > self.stop_time:
            raise ValueError('The start time cannot be greater than '
                             'the stop time.')

        self._interval[0] = value

    @property
    def stop_time(self):

        # Finds the maximum of the internally stored stop time and
        # the time of the latest state transition in the channels.
        value = self._interval[1]
        for c in self.channels:
            if c.switch_times and value < c.switch_times[-1]:
                value = c.switch_times[-1]

        return value

    @stop_time.setter
    def stop_time(self, value):
        for i, c in enumerate(self.channels):
            if c.switch_times and value < c.switch_times[-1]:
                raise ValueError('The stop time cannot be smaller than '
                                 'the time of the last transition '
                                 f'in channel {i} (t={c.switch_times[-1]}).')

        if value < self.start_time:
            raise ValueError('The stop time cannot be smaller than '
                             'the start time.')

        self._interval[1] = value

    def plot(self, fig=None):
        """Plots the channel states versus time using matplotlib.

        Args:
            fig (matplotlib Figure, optional)
        """

        if not self.channels:
            # There needs to be at least one channel to plot.
            return

        channel_no = len(self.channels)

        if not fig:
            h = min(8, channel_no + 1)
            fig = plt.figure(figsize=(10, h))

        tlim = [self.start_time, self.stop_time]

        gs = fig.add_gridspec(channel_no, hspace=0)
        axs = gs.subplots(sharex=True, sharey=True)

        fig.suptitle('Channel states')

        for i in range(channel_no):
            axs[i].plot(*self.channels[i].curve(interval=tlim),
                        color=(6/255, 85/255, 170/255), linewidth=1)

            # Configures the axes appearance.
            axs[i].set_ylabel(f'Ch {i}')
            axs[i].set_facecolor('none')
            axs[i].minorticks_on()
            axs[i].tick_params(axis='both', direction='in', which='both',
                               bottom=True, top=False, left=True, right=True)

        axs[-1].set_xlim(tlim)
        axs[-1].set_xlabel('Time (s)')
        axs[-1].set_yticks([0, 1])
        axs[-1].set_ylim(-0.1, 1.1)

        fig.tight_layout()
        plt.show()


class DigitalChannel:
    """Defines a time-dependent state of a single digital channel by specifying 
    its default and a list of state transitions.

    Attributes:
        default (bool):
            The default state of the channel.
        switch_times (List[float]):
            An ordered list containing times (in seconds) at which the channel 
            state is flipped. This list should only be modified by using 
            add_state_switch method. 
    """

    def __init__(self, default=False):
        """Inits a channel instance with a given default state."""

        self.default = bool(default)
        self.switch_times = []

    def add_state_switch(self, t: float) -> None:
        """Adds a state flip at the time t (s)."""

        if t in self.switch_times:
            raise ValueError('A state change at time %.3e already exists' % t)

        # Adds a new state switch in a way that keeps the list time-ordered.
        ind = len([t1 for t1 in self.switch_times if t1 < t])
        self.switch_times.insert(ind, t)

    def state(self, t: float) -> bool:
        """Returns the state at the time t (s). If there is a state transition 
        at t, returns the value before the transition."""

        ind = len([t1 for t1 in self.switch_times if t1 < t])
        if ind % 2 == 0:
            st = self.default
        else:
            st = not self.default
        return st

    def states(self) -> list:
        """Returns a list where the i-th element is the state before the i-th 
        state transition."""

        new_states = []
        for i in range(len(self.switch_times)):
            if i % 2 == 0:
                new_states.append(not self.default)
            else:
                new_states.append(self.default)

        return new_states

    def curve(self, interval=None):
        """Returns the channel state as a function of time over the specified 
        time interval.

        Args:
            interval: A time inteval [t0, t1].

        Returns:
            (times, states)
        """

        if interval:
            t0 = min(interval)
            t1 = max(interval)
            swt = [t for t in self.switch_times if (t >= t0) and (t <= t1)]
        else:
            # Sets the interval to cover all switch times.
            if self.switch_times:
                t0 = self.switch_times[0]
                t1 = self.switch_times[-1]
                swt = self.switch_times
            else:
                return ([], [])

        times = []
        states = []

        if t0 not in swt:
            # Appends the state in the beginning of the interval.
            times.append(t0)
            states.append(self.state(t0))

        for t in swt:
            st = self.state(t)

            # Appends the state before the switch.
            times.append(t)
            states.append(st)

            # Appends the state after the switch.
            times.append(t)
            states.append(not st)

        if t1 not in swt:
            # Appends the state in the end of the interval.
            times.append(t1)
            states.append(self.state(t1))

        return (times, states)

    def __repr__(self):
        """Displays the list of state transitions in a readable form."""

        switches = []
        for t in self.switch_times:
            st = self.state(t)
            switches.append('t=%gs\t%i->%i' % (t, st, not st))

        string_form = ('%s:\n%s' %
                       (type(self).__name__, '\n'.join(switches)))
        return string_form
