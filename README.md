# A myRIO-based TTL pulse generator with a python interface.

The generator operates as a pseudocklock - it defines pulses using sequences of channel state transitions rather than their states at every clock cycle. In this way, the generator can produce long pulses timed with the resolution limited by the frequency of the FPGA clock, which is 100 MHz in the current version. 

The repository consists of two parts: 
 * A LabVIEW FPGA project for a National Instruments myRIO-1900 board that implements a programmable TTL pulse generator. The generator is a state machine defined within the FPGA that reads instructions from the memory and updates the outputs accordingly. Sets of instructions have to be transferred to the FPGA from a host PC.
 * `riopulse` - a python package that implements a high-level interface to the pulse generator. It uses [nifpga API](https://nifpga-python.readthedocs.io/) for communication with the hardware.
 
 FPGA bitfiles can be found in the python module directory. 

## Requirements
* [nifpga](https://nifpga-python.readthedocs.io/) 
* numpy
* matplotlib
* PyQt5 if used with the GUI.

The software can be used without LabVIEW running on the host computer. 

## Installation
Download this repo, extract the files and change into its root directory. Then install `riopulse` as a python package:

```bash
pip install .
```

To install this package in the editable mode, use instead:

```bash
pip install -e .
```

## Basic usage

The code below defines a sequence of pulses in three synchronized channels. The outputs of all the channels of myRIO for which pulse sequences are not defined will be set to zero.

```python
from riopulse import Sequence

seq = Sequence(nchannels=3, defaults=[False, True, False], start_time=0)

# Signature: seq.append_pulse(ch, delay, duration), all times are in seconds
seq.append_pulse(0, 0.9e-6, 0.1e-6)
seq.append_pulse(1, 4e-6, 1e-6)
seq.append_pulse(1, 2.5e-6, 0.5e-6)
seq.stop_time = 15e-6 

# An alternative way of adding pulses is by using 
# seq.add_pulse(self, ch, t0, duration)
```
Here a pulse consists of switching the channel state from the previous one, keeping the new state for the duration of time, and then switching the state back.

The sequence can be plotted by calling

```python
seq.plot()
```

The sequence can be loaded into the memory of the FPGA board as

```python
from riopulse import PulseGen

p = PulseGen('rio://172.22.11.2/RIO0')
p.program(seq)
```

By default, pulse sequences are executed as soon as they are loaded and repeated periodically - when one sequence is finished, another one is started without a delay. In order to stop and start generation, use

```python
p.stop()  # Stops the generation
p.run_continuous()  # Starts the generation again
```

Starting/stopping the generation can be also performed from a simple GUI, which is created as

```python
from riopulse import gui

g = gui(p)  # In IPython, this does not block the console
```

## Limitations
* 10 ns pulse definition resolution.
* 8 digital output channels (DIO 0-7 on myRIO).
* The time resolution for the definition of pulse edges is 10 ns.
* Maximum 10 000 output state transitions per sequence (the state transitions of all channels during one clock cycle count as one).
* The maximum pulse duration is 2^48 clock cycles = appoximately 782 hours.


