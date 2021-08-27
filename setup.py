import os
from setuptools import setup

setup(
    name="riopulse",  
    version="0.9.0",
    packages=['riopulse'],
    include_package_data=True,
    package_data={'': [os.path.join('FPGA bitfiles', '*.lvbitx')]}
)