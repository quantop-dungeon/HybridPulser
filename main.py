#%%
from SeqControl import Sequence

s=Sequence(dur=1e-3)

s.pulse(0, 1e-6, 1e-6) # ch, duration, delay
s.pulse(2, 1e-6, 71e-6)
s.pulse(7, 0.5e-6, 1.123e-3) # ch, duration, delay
s.pulse(0, 10e-6, 71e-6)
s.compile()
print(s.commands)
print(s.duration)
s.program()
#%%