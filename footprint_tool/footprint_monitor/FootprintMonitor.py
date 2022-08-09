from abc import ABC, abstractmethod

from ..parser.Parser import ParserMbed, ParserZephyr


class __FootprintMonitor(ABC):
    def __init__(self, type="", build_hash=""):
        self.type = type

    @abstractmethod
    def parse_input(self):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def plot(self):
        pass


class FootprintMonitorMbed(__FootprintMonitor):
    def __init__(self, type, build_hash):
        super().__init__(type)
        self.parser = ParserMbed(build_hash)

    def parse_input(self):
        print("I'm {} and I parse".format(self.type))
        self.parser.parse_build("  ")

    def render(self):
        print("I'm {} and I render".format(self.type))

    def plot(self):
        print("I'm {} and I plot".format(self.type))


class FootprintMonitorZephyr(__FootprintMonitor):
    def __init__(self, type, build_hash):
        super().__init__(type)
        self.parser = ParserZephyr(build_hash)

    def parse_input(self):
        print("I'm {} and I parse".format(self.type))
        self.parser.parse_build("  ")

    def render(self):
        print("I'm {} and I render".format(self.type))

    def plot(self):
        print("I'm {} and I plot".format(self.type))
