#%%
import numpy as np
import zmq
import json

class Command:
    pass

class SwitchPinCommand(Command):
    def __init__(self, ch, state):
        self.ch = ch
        self.state = state

    def __str__(self):
        return 'ch' + str(self.ch) + ',s' + str(self.state)

def set_bit(value, bit):
    return value | (1<<bit)

def clear_bit(value, bit):
    return value & ~(1<<bit)

class Sequence:
    dt = 1e-8 # s

    cmdnr = { 'jmp': 0, 'dly' : 1, 'con' : 2}

    def __init__(self, dur, defaults=0):
        self.dur = dur 
        self.tcommands = []
        self.times = []
        self.commands = []
        self.defaults = defaults
        self.duration = 0

        self.context = zmq.Context()



    def pulse(self, ch, delay, duration):
        logic = (2**ch & self.defaults) >> ch
        self.tcommands.append(SwitchPinCommand(ch, not logic))
        self.times.append(delay)
        self.tcommands.append(SwitchPinCommand(ch, logic))
        self.times.append(delay+duration)
        
    def delay(self, wait):
        if wait > 2**24 - 1:
            # split long delays into many shorter delays (max=2^24-1)
            self.commands.append(['dly', 2**24 - 1])
            self.delay(wait - 2**24) # we take away 1 since it takes 1 tick to run the dly command
        else:
            self.commands.append(['dly', wait])
            
    def compile(self):
        self.times = np.array(self.times)
        self.tcommands = np.array(self.tcommands)
        sidx = np.argsort(self.times)
        self.times = self.times[sidx]
        self.tcommands = self.tcommands[sidx]

        # initialize pins
        self.commands.append(['con',self.defaults])

        prevt = 0
        prevs = self.defaults
        for t, tcommand in zip(self.times, self.tcommands):
            # make the delay for the next command
            if t>prevt:
                wait = int((t-prevt)/self.dt)
                self.delay(wait)
            # unless we want it to happen immediately
            elif t==prevt:
                pass
            # that should never happen
            elif t>prevt:
                pass

            if tcommand.state == 0:
                news = clear_bit(prevs, tcommand.ch)
            elif tcommand.state == 1:
                news = set_bit(prevs, tcommand.ch)

            self.commands.append(['con',news])

            prevs =  news
            prevt = t

        if t < self.dur:
            wait = int((self.dur-t)/self.dt)
            self.delay(wait)
            self.duration = self.dur
        else:
            self.duration = t
            print('duration exceeded')

        self.commands.append(['jmp', 1])
        
        self.mcode = []
        for command in self.commands:
            cmd = self.cmdnr[command[0]]
            data = command[1]
            self.mcode.append((cmd << 24) + (data))


    def program(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        # Nice code bro! BTW, zmq has send_json
        socket.send_string(json.dumps(self.mcode))

        message = socket.recv()
        print(message)

        socket.close()

    def plot(self):
        pass

