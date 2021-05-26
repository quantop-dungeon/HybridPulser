#%%
from SeqControl import Sequence
default_s = 0b000000000010
s=Sequence(dur=2e-3,defaults=default_s)

#s.pulse(0, 1e-6, 1e-6) # ch, delay, duration
#s.pulse(2, 1e-6, 71e-6)
#s.pulse(7, 0.5e-6, 1.123e-3) # ch,  delay, duration
s.pulse(0, 0e-6, 30e-6)
for i in range(50):
    s.pulse(1, i* 1/1.3e6, 200e-9)
s.compile()
print(s.commands)
print(s.duration)
print(len(s.mcode))
s.program()
#%%