import os

from typing import Union
from nifpga import Session

from .sequence import Sequence
from .compilation import compile_


class PulseGen:
    """A class that communicates with the FPGA board. It programs pulse
    sequences to execute, initiates and stops pulse generation etc.

    Args:
        bitfile, resource: 
            Arguments required by nifpga.Session
    """

    def __init__(self, resource: str, bitfile: str = ''):
        if not bitfile:
            bitfile = get_bitfile()
        self.bitfile = bitfile
        self.resource = resource

    def program(self, data: Union[Sequence, list]) -> None:
        """Converts a Sequence object to state machine code and programs it to  
        the FPGA memory.

        Args:
            data: 
                A Sequence object, or directly a list of state machine code 
                (e.g. produced by compile). 
        """

        if isinstance(data, Sequence):
            mcode = compile_(data)
        else:
            mcode = data

        with Session(self.bitfile, self.resource) as se:
            se.registers['prog ncmd'].write(len(mcode))

            # Sends the data to the board in batches not exceeding one half
            # of the FPGA-side buffer (1024 byte = 128 64-bit integers).
            while True:
                if len(mcode) > 128:
                    se.fifos['command'].write(mcode[:128])
                    mcode = mcode[128:]
                else:
                    se.fifos['command'].write(mcode)
                    break

            ncmd = se.registers['prog ncmd'].read()
            if ncmd != 0:
                print(f'Warning ncmd = {ncmd}.')

    def init_fpga(self) -> None:
        """Loads the bitfile to the FPGA target and runs it."""

        with Session(self.bitfile, self.resource) as se:
            se.download()
            se.run()

    def run_continuous(self) -> None:
        """Initiates the periodic generation of pulse sequences."""

        with Session(self.bitfile, self.resource) as se:
            se.registers['persistent trig'].write(True)

    def run_single(self) -> None:
        """Initiates the generation of a single pulse sequence."""

        with Session(self.bitfile, self.resource) as se:
            # Switches off the continuous trigger.
            se.registers['persistent trig'].write(False)

            # Makes a rising edge on the software trigger.
            se.registers['software trig'].write(False)
            se.registers['software trig'].write(True)

    def stop(self) -> None:
        """Stops the generation of pulses with the outputs of channels in 
        the default state.
        """

        with Session(self.bitfile, self.resource) as se:
            # Eventially the machine will finish the current sequence and
            # return to the first instruction, which is always waiting for
            # a trigger with all outputs in the default states. Switching off
            # the persistent trigger will make the machine stay there unitil
            # further command.
            se.registers['persistent trig'].write(False)


def get_bitfile() -> str:
    """Returns the name with the path of the default bitfile."""

    s = os.path.join(os.path.dirname(__file__), 'FPGA bitfiles',
                     'myriopulsegen_FPGATarget_fpgamain_cSZ+wOME15E.lvbitx')
    return s
