# A myRIO-based TTL pulse generator with a python interface.

The generator operates as a pseudocklock - it defines pulses using sequences of channel state transitions rather than their states at every clock cycle. In this way, the generator can produce long pulses timed with the resolution limited by the frequency of the FPGA clock, which is 100 MHz in the current version. 

The repository consists of two parts: 
 * A LabVIEW FPGA project for a National Instruments myRIO-1900 board that implements a programmable TTL pulse generator. The generator is a state machine defined within the FPGA that reads instructions from the memory and updates the outputs accordingly. Sets of instructions have to be transferred to the FPGA from a host PC.
 * `riopulse` - a python package that implements a high-level interface to the pulse generator. It uses [nifpga API](https://nifpga-python.readthedocs.io/) for communication with the hardware.
 
 FPGA bitfiles can be found in the python module directory. 

## Limitations
* 10 ns pulse definition resolution.
* 8 digital output channels (DIO 0-7 on myRIO).
* The time resolution for the definition of pulse edges is 10 ns.
* Maximum 10 000 output state transitions per sequence (the state transitions of all channels during one clock cycle count as one).
* The maximum pulse duration is 2^48 clock cycles = appoximately 782 hours.

## Requirements
* [nifpga](https://nifpga-python.readthedocs.io/) 
* numpy
* matplotlib
* PyQt5 if used with the GUI.

The software can be used without LabVIEW running on the host computer. 

## Installation
Download this repo, extract the files and open a terminal in its root directory. Then install `riopulse` as a python package by executing

```bash
pip install .
```

To install this package in the editable mode, use instead

```bash
pip install -e .
```
Note that this will not install any of the dependencies.

## Basic usage

### Definition of pulses

A pulse is a switching the state of one digital channel of the RIO board, keeping the new state for some duration of time, and then switching the state back. Configurations of pulses are represented by `Sequence` objects and defined using their two methods, `add_pulse` and `append_pulse`.

For example, a simple sequence of two pulses in one channel can be created as follows 
```python
from riopulse import Sequence

seq = Sequence(nchannels=1)
seq.add_pulse(0, 5e-6, 10e-6)
seq.add_pulse(0, 25e-6, 20e-6)
# Signature: seq.add_pulse(self, ch, t0, duration),
# t0 and duration are in seconds

seq.stop_time = 75e-6

seq.plot()
```
The plotted result is
![seq1ch1](doc\sequence_1ch.png)

Pulses in a sequence can be overlapped, in which case they subtract
```python
seq.add_pulse(0, 40e-6, 10e-6)
seq.plot()
```
![seq1ch2](doc\sequence_1ch_2.png)

The default outputs can be set either on construction of `Sequence`, or via `default` attribute of the digital channels. Setting `default` to `True` inverts the sequence
```python
seq.channels[0].default = True
seq.plot()
```
![seq1ch3](doc\sequence_1ch_3.png)

To give another example, a sequence of pulses in three synchronized channels is defined below.
```python
seq = Sequence(nchannels=3, defaults=[False, True, False],
               start_time=0, stop_time=15e-6)

seq.append_pulse(0, 0.9e-6, 0.1e-6)
seq.append_pulse(0, 0.9e-6, 0.1e-6)
seq.append_pulse(1, 4e-6, 1e-6)
seq.append_pulse(1, 2.5e-6, 0.5e-6)
# Signature: seq.append_pulse(ch, delay, duration), 
# delay and duration are in seconds

seq.plot()
```
![seq3ch](doc\sequence_3ch.png)

Sequence channels are mapped into DIO 0-7 channels of the RIO board. The outputs of all the channels for which pulse sequences are not defined will be set to zero.

### Running pulse sequences

In order to generate physical output, a `Sequence` object needs to be compiled into state machine code and loaded into the memory of the FPGA board. This can be done as

```python
from riopulse import PulseGen

p = PulseGen('rio://172.22.11.2/RIO0')
p.program(seq)
```

By default, pulses are started as soon as a new sequence is loaded and they are repeated periodically - when one sequence is finished, another one is started without a delay. In order to manually stop and start generation, one can use

```python
p.stop()  # Stops the pulse generation
p.run_continuous()  # Starts the generation again
```

Starting/stopping the generation can be also performed from a simple GUI, which is created as

```python
from riopulse import gui

g = gui(p)  # In IPython, this does not block the console
```

### A comment on setting default channel states
The following three ways of setting default states produce identical physical outputs
```python
# 1st
seq = Sequence(nchannels=3, defaults=[False, True, False])

# 2nd
seq = Sequence(nchannels=3)
seq.channels[1].default = True  
# This can also be done at any time after pulses are added 

# 3rd
t0 = 0
t1 = 2e-3
seq = Sequence(nchannels=3, start_time=t0, stop_time=t1)
seq.add_pulse(1, t0, t1-t0)  
# This does not generate a switching at 0 time, 
# the 1st output will stay continuously in the 'on' state
```


