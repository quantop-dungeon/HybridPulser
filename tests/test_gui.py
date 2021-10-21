from riopulse.gui import gui

class DummyPulseGen:

    def run_continuous(self):
        print('Initiates periodic sequences.')

    def run_single(self):
        print('Initiates a single sequence.')

    def stop(self):
        print('Stops pulsing.')


dp = DummyPulseGen()
window = gui(dp)