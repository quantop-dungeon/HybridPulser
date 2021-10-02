from riopulse import Sequence

seq = Sequence(nchannels=1)
seq.add_pulse(0, 5e-6, 10e-6)
seq.add_pulse(0, 25e-6, 20e-6)
seq.stop_time = 75e-6
seq.plot()

seq = Sequence(nchannels=3, start_time=0)
seq.append_pulse(1, 1, 0.3)
seq.append_pulse(1, 0.3, 0.6)
seq.stop_time=4  # (s)
seq.plot()