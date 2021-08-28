from riopulse.sequence import Sequence

seq = Sequence(nchannels=3, start_time=0)
seq.append_pulse(1, 1, 0.3)
seq.append_pulse(1, 0.3, 0.6)
seq.stop_time=4  # (s)
seq.plot()