#%%
from SeqControl import Sequence
default_s = 0b000000000010
s=Sequence(dur=2,defaults=default_s)

#s.pulse(0, 1e-6, 1e-6) # ch, delay, duration
#s.pulse(2, 1e-6, 71e-6)
#s.pulse(7, 0.5e-6, 1.123e-3) # ch,  delay, duration
s.pulse(0, 0e-6, 1)
s.pulse(1, 0e-6, 0.1*1e-2)
s.pulse(2, 0e-6, 0.1*1e-2)
s.pulse(3, 0e-6, 0.1*1e-2)
#s.pulse(0, 400e-6, 200e-6)
s.compile()
print(s.commands)
print(s.duration)
print(len(s.mcode))
s.program()
#%%

#%%
from SeqControl import Sequence
default_s = 0b000000000010
s=Sequence(dur=0.9,defaults=default_s)

#s.pulse(0, 1e-6, 1e-6) # ch, delay, duration
#s.pulse(2, 1e-6, 71e-6)
#s.pulse(7, 0.5e-6, 1.123e-3) # ch,  delay, duration
s.pulse(0, 0e-6, 0.9*1e-1)
s.pulse(1, 0e-6, 0.1*1e-2)
s.pulse(2, 0e-6, 0.1*1e-2)
s.pulse(3, 0e-6, 0.1*1e-2)
#s.pulse(0, 400e-6, 200e-6)
s.compile()
print(s.commands)
print(s.duration)
print(len(s.mcode))
s.program()