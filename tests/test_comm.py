from riopulse.pulsegen import PulseGen
from riopulse.sequence import Sequence

seq = Sequence(nchannels=3, start_time=0)
seq.append_pulse(0, 1e-3, 0.2e-3)
seq.append_pulse(1, 1.2e-3, 0.3e-3)
seq.append_pulse(1, 0.3e-3, 0.6e-3)
seq.stop_time = 10e-3  # (s)

p = PulseGen('rio://172.22.11.2/RIO0')
p.program(seq)

# seq = Sequence(nchannels=3, start_time=0)
# seq.append_pulse(0, 0.9e-6, 0.1e-6)
# seq.append_pulse(1, 4e-6, 1e-6)
# seq.append_pulse(1, 2.5e-6, 0.5e-6)
# seq.stop_time = 15e-6  # (s)

# p = PulseGen('rio://172.22.11.2/RIO0')
# p.program(seq)