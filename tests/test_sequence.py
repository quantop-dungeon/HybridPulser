import unittest

from riopulse import Sequence
from riopulse import DigitalChannel
from riopulse import translate


class SequenceTest(unittest.TestCase):
    # TODO: test the sequence extension for negative times.

    def test_default(self):
        """Tests different ways to define channel defaults."""
        t0 = -1e3
        t1 = 1e3

        seq1 = Sequence(nchannels=2, start_time=t0, stop_time=t1)
        seq1.add_pulse(0, 5e-6, 10e-6)
        seq1.add_pulse(1, 5e-6, 10e-6)
        seq1.add_pulse(1, t0, t1-t0)

        seq2 = Sequence(nchannels=2, start_time=t0, stop_time=t1)
        seq2.add_pulse(0, 5e-6, 10e-6)
        seq2.add_pulse(1, 5e-6, 10e-6)
        seq2.channels[1].default = True

        # The two sequences are not equal (which makes sense since they 
        # will behave differently if more pulses are added) but as they are now
        # they should translate into identical sets of state machine 
        # instructions.
        self.assertNotEqual(seq1, seq2)
        self.assertEqual(translate(seq1), translate(seq2))

    def test_pulse_def(self):
        """Tests the equivalence between different ways of defining 
        the same sequence of pulses and the sequence comparison operation."""

        seq1 = Sequence(nchannels=1)  # Reference
        seq1.add_pulse(0, 5e-6, 10e-6)
        seq1.add_pulse(0, 25e-6, 20e-6)
        seq1.stop_time = 75e-6

        seq2 = Sequence(nchannels=1)  # Should be the same as seq1
        seq2.append_pulse(0, 5e-6, 10e-6)
        seq2.append_pulse(0, 10e-6, 20e-6)
        seq2.stop_time = 75e-6

        seq3 = Sequence(nchannels=1)  # Should be the same as seq1
        seq3.add_pulse(0, 5e-6, 40e-6)
        seq3.add_pulse(0, 15e-6, 10e-6)
        seq3.stop_time = 75e-6

        seq4 = Sequence(nchannels=2)  # Only different number of cahnnels
        seq4.add_pulse(0, 5e-6, 10e-6)
        seq4.add_pulse(0, 25e-6, 20e-6)
        seq4.stop_time = 75e-6

        seq5 = Sequence(nchannels=1, defaults=[True]) # Only different default
        seq5.add_pulse(0, 5e-6, 10e-6)
        seq5.add_pulse(0, 25e-6, 20e-6)
        seq5.stop_time = 75e-6

        seq6 = Sequence(nchannels=1)  # Only different state switch times
        seq6.add_pulse(0, 5e-6, 10e-6)
        seq6.add_pulse(0, 25e-6, 21e-6)
        seq6.stop_time = 75e-6

        seq7 = Sequence(nchannels=1)  # Only different stop time
        seq7.add_pulse(0, 5e-6, 10e-6)
        seq7.add_pulse(0, 25e-6, 21e-6)
        seq7.stop_time = 77e-6

        # seq1, seq2, and seq3 are not necessarily equal because of roundoff 
        # errors but they translate into the same state machine code. 
        self.assertEqual(translate(seq1, dt=10e-9), translate(seq2, dt=10e-9))
        self.assertEqual(translate(seq1, dt=10e-9), translate(seq3, dt=10e-9))

        self.assertNotEqual(seq1, seq4)
        self.assertNotEqual(seq1, seq5)
        self.assertNotEqual(seq1, seq6)
        self.assertNotEqual(seq1, seq7)

    def test_pulse_subtraction(self):
        seq1 = Sequence(nchannels=8)
        seq1.add_pulse(7, 5e-6, 40e-6)
        seq1.add_pulse(7, 40e-6, 40e-6)
        seq1.stop_time = 105e-6

        seq2 = Sequence(nchannels=8)
        seq2.add_pulse(7, 5e-6, 75e-6)
        seq2.add_pulse(7, 40e-6, 5e-6)
        seq2.stop_time = 105e-6

        seq3 = Sequence(nchannels=8)
        seq3.add_pulse(7, 5e-6, 35e-6)
        seq3.add_pulse(7, 45e-6, 35e-6)
        seq3.stop_time = 105e-6

        # Again, the sequences are not necessarily equal because of floating
        # point arithmetic with finite precision, but the translated code
        # should be the same.
        self.assertEqual(translate(seq1, dt=10e-9), translate(seq2, dt=10e-9))
        self.assertEqual(translate(seq2, dt=10e-9), translate(seq3, dt=10e-9))


    def test_pulse_merging(self):
        """Tests that adding two pulses with the same edge creates a single 
        pulse without a gap in between."""

        seq1 = Sequence(nchannels=1, start_time=10e-6)
        seq1.append_pulse(0, 5e-6, 10e-6)
        seq1.append_pulse(0, 0, 20e-6)
        seq1.stop_time = 75e-6

        # seq1 should have only two transitions because the pulses 
        # should have been merged.
        self.assertEqual(len(seq1.channels[0].switch_times), 2)

        seq2 = Sequence(nchannels=1, start_time=10e-6)
        seq2.add_pulse(0, 15e-6, 10e-6)
        seq2.add_pulse(0, 25e-6, 20e-6)
        seq2.stop_time = 75e-6

        self.assertEqual(len(seq2.channels[0].switch_times), 2)

        seq3 = Sequence(nchannels=1, start_time=10e-6)
        seq3.add_pulse(0, 15e-6, 30e-6)
        seq3.stop_time = 75e-6

        self.assertEqual(seq2, seq3)

        seq4 = Sequence(nchannels=1, start_time=10e-6)
        seq4.append_pulse(0, 5e-6, 10e-6)
        seq4.append_pulse(0, 1e-15, 20e-6) 
        seq4.stop_time = 75e-6

        # The gap between pulses is smaller than the discretezation period 
        # (10 ns) - the sequences are not equal, by they translate into the 
        # same set of instructions. 
        self.assertNotEqual(seq1, seq4)

        self.assertEqual(reduce(translate(seq1, dt=10e-9)), reduce(translate(seq4, dt=10e-9)))



    def test_comparison(self):
        t = [1e-3, 5e-3, 222e-2, 4e-3]
        
        ch1 = DigitalChannel()
        ch1.add_state_switch(t[0])
        ch1.add_state_switch(t[1])

        ch2 = DigitalChannel()
        ch2.add_state_switch(t[1])
        ch2.add_state_switch(t[0])

        ch3 = DigitalChannel(default=True)
        ch3.add_state_switch(t[1])
        ch3.add_state_switch(t[0])

        ch4 = DigitalChannel()
        ch4.add_state_switch(t[1])
        ch4.add_state_switch(t[0])
        ch4.add_state_switch(t[2])

        ch5 = DigitalChannel()
        
        ch6 = DigitalChannel()

        ch7 = []  # Tests for an obvious error

        # State switch cancellation
        ch8 = DigitalChannel()
        ch8.add_state_switch(t[0])
        ch8.add_state_switch(t[1])
        ch8.add_state_switch(t[0])

        ch9 = DigitalChannel()
        ch9.add_state_switch(t[1])

        ch10 = DigitalChannel()
        ch10.add_state_switch(t[1])
        ch10.add_state_switch(t[1])
        ch10.add_state_switch(t[1])

        # Same as an empty channel
        ch11 = DigitalChannel()
        ch11.add_state_switch(t[1]) 
        ch11.add_state_switch(t[1])

        self.assertEqual(ch1, ch2)
        self.assertEqual(ch5, ch6)
        self.assertNotEqual(ch1, ch3)
        self.assertNotEqual(ch1, ch4)
        self.assertNotEqual(ch3, ch7)
        self.assertNotEqual(ch6, ch7)

        self.assertEqual(ch8, ch9)
        self.assertEqual(ch8, ch10)

        self.assertEqual(ch11, ch6)

    def test_translation(self):

        seq1 = Sequence(nchannels=2, start_time=10e-6)
        seq1.append_pulse(0, 5e-6, 10e-6)
        seq1.append_pulse(0, 0, 20e-6)

        # The rising edge of this pulse is at the same clock cycle as for 
        # the pulse in ch0
        seq1.add_pulse(1, 15e-6, 15e-6)

        seq1.stop_time = 75e-6

        cmd = translate(seq1, dt=10e-9)

        ref = [['trigwait', 0, 0], 
               ['cout', 0, 499], 
               ['cout', 3, 1499],
               ['cout', 1, 1499], 
               ['cout', 0, 2999], 
               ['init', 0, 0]]

        self.assertEqual(cmd, ref)

def reduce(cmd):
    """Merges sequential cout commands with the same outputs into one
    command"""

    new_cmd = []

    for c in cmd:
        if (len(new_cmd) >=1 
            and c[0] == 'cout' and new_cmd[-1][0] == 'cout' 
            and c[1] == new_cmd[-1][1]):

            new_cmd[-1][2] += (c[2]+1)
        else:
            new_cmd.append(c)

    return new_cmd

if __name__ == "__main__":
    unittest.main()
