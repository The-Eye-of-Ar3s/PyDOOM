""" Module for PyDOOM Exceptions"""

class UnrecognizedWADFormat(Exception):
    """UnrecognizedWADFormat
    Exception which is raised when the loaded WAD is neither IWAD nor PWAD
    """
    def __init__(self):
        super().__init__("Loaded WAD is neither an IWAD nor a PWAD")
