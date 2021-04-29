Modified classic FPGA finite state machine (FSM) project from NI RIO PCI card ported to myRIO (Zynq).

Removed all DDS stuff, also removed photon counter and time tagger.

On the computer side on the other hand instead of LabVIEW controller (aka mot_fpga.vi) and compiler (kompilator.vi) we have a python script that connects to a LabVIEW machine code uploader via ZeroMQ.
