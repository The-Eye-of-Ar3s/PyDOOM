"""Entrypoint for the PyDOOM Game"""

from lib.wad import WAD


class Game:
    """Class for the entirety of the DOOM Game"""
    def __init__(self, path):
        self.wad = WAD(path)


Game("DOOM.WAD")
