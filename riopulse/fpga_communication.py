import os

from typing import Union
from nifpga import Session

from .sequence import Sequence


def program(data: Union[Sequence, list], bitfile: str = '',
            resource: str = 'RIO0') -> None:
    """Converts a sequence to state machine code and programs it to the memory 
    on the FPGA board.

    Args:
        data: 
            A Sequence, or state machine code (e.g. produced by compile).
        bitfile, resource: 
            Arguments required by nifpga.Session. 
    """

    if not bitfile:
        bitfile = get_bitfile()

    if isinstance(data, Sequence):
        mcode = compile(data)
    else:
        mcode = data

    with Session(bitfile, resource) as se:
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


def init_fpga(bitfile: str = '', resource: str = 'RIO0') -> None:
    """Loads the bitfile to the FPGA target and runs it."""

    if not bitfile:
        bitfile = get_bitfile()

    with Session(bitfile, resource) as se:
        se.download()
        se.run()


def get_bitfile() -> str:
    """Returns the name with the path of the default bitfile."""
    s = os.path.join(os.path.dirname(__file__), 'FPGA bitfiles',
                     'myriopulsegen_FPGATarget_fpgamain_cSZ+wOME15E.lvbitx')
    return s


def run_continuous(bitfile: str = '', resource: str = 'RIO0') -> None:
    """Initiates periodic generation of pulse sequences."""
    
    if not bitfile:
        bitfile = get_bitfile()

    with Session(bitfile, resource) as se:
        se.registers['persistent trig'].write(True)


def run_single(bitfile: str = '', resource: str = 'RIO0') -> None:
    """Initiates the generation of a single sequence of pulses."""
    
    if not bitfile:
        bitfile = get_bitfile()

    with Session(bitfile, resource) as se:
        # Switches off the continuous trigger.
        se.registers['persistent trig'].write(False)

        # Makes a rising edge on the software trigger.
        se.registers['software trig'].write(False)
        se.registers['software trig'].write(True)


def stop(bitfile: str = '', resource: str = 'RIO0') -> None:
    """Stops the generation of pulses and sets the outputs of all channels 
    to the default state.
    """
    
    if not bitfile:
        bitfile = get_bitfile()

    with Session(bitfile, resource) as se:
        # Eventially the machine will finish the current sequence and return
        # to the first instruction, which is always waiting for a trigger with
        # all outputs in the default states. Switching off the persistent 
        # trigger will make the machine stay there unitil further command.
        se.registers['persistent trig'].write(False)

