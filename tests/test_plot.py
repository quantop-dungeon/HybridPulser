import sys
sys.path
sys.path.append('../')

%matplotlib qt

from riopulse.sequence import Sequence

p = Sequence(nchannels=3, start_time=0)
p.append_pulse(1, 1, 0.3)
p.append_pulse(1, 0.3, 0.6)
p.stop_time=4  # (s)
p.plot()