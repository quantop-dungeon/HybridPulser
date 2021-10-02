from riopulse import Sequence

seq = Sequence(nchannels=1)
seq.add_pulse(0, 5e-6, 10e-6)
seq.add_pulse(0, 25e-6, 20e-6)
seq.stop_time = 75e-6
seq.plot()

seq.add_pulse(0, 40e-6, 10e-6)
seq.plot()

seq.channels[0].default = True
seq.plot()

seq = Sequence(nchannels=3, defaults=[False, True, False],
               start_time=0, stop_time=15e-6)

seq.append_pulse(0, 0.9e-6, 0.1e-6)
seq.append_pulse(0, 0.9e-6, 0.1e-6)
seq.append_pulse(1, 4e-6, 1e-6)
seq.append_pulse(1, 2.5e-6, 0.5e-6)
# Signature: seq.append_pulse(ch, delay, duration), 
# delay and duration are in seconds

seq.plot()