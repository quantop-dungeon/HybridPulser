# A myRIO-based TTL pulse generator with a python interface.

The generator operates as a pseudocklock - it defines pulses using sequences of channel state transitions rather than their states at every clock cycle. In this way, the generator can produce long pulses timed with the precision of the FPGA clock, which has a frequency of 100 MHz in the current version. 

The repository consists of two parts: 
 * A Labview FPGA project for a National Instruments myRIO-1900 board that implements a programmable TTL pulse generator. The generator is a state machine defined within the FPGA that reads instructions from the memory and updates the outputs accordingly. Sets of instructions have to be transferred to the FPGA from a host PC.
 * `riopulse` - a python package that implements a high-level interface to the pulse generator. It uses [nifpga API](https://nifpga-python.readthedocs.io/) for communication with the hardware.
 
 FPGA bitfiles can be found in the python module directory. 

# Limitations
* 8 digital output channels (DIO 0-7).
* The time resolution for the definition of pulse edges is 10 ns.
* Maximum 10 000 output state transitions per sequence (the state transitions of all channels during one clock cycle count as one).
* The maximum pulse duration is 2^48 clock cycles = appoximately 782 hours.

# Requirements
The pulse generator can be used without LabVIEW running on the host computer. 

# Installation
Download this repo, extract the files and change into its root directory. Then install `riopulse` as a python package:

```bash
pip install .
```

To install this package in the editable mode, use

```bash
pip install -e .
```


