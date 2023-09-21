from abc import ABC, abstractmethod

from ..parser.Parser import ParserMbed, ParserZephyr

class __FootprintMonitor(ABC):
    def __init__(self, type="", build_hash=""):
        self.type = type

     def __calculateLibraries(self):
        self.statsLibraries = {}
        for file in self.statsFiles:
            if file["lib"] not in list(self.statsLibraries.keys()):
                self.statsLibraries.update(
                    {
                        file["lib"]: {
                            "text": 0,
                            "data": 0,
                            "bss": 0,
                            "total": 0,
                            "diffs": {"text": 0, "data": 0, "bss": 0, "total": 0},
                        }
                    }
                )
            self.statsLibraries[file["lib"]]["text"] += file["text"]
            self.statsLibraries[file["lib"]]["data"] += file["data"]
            self.statsLibraries[file["lib"]]["bss"] += file["bss"]
            self.statsLibraries[file["lib"]]["total"] += file["total"]

    def __calculateDiffWarnings(self, previousWarnings):
        return self.countWarnings - previousWarnings

    def __calculateDiffLibraries(self, libraries):
        diffLibraries = deepcopy(self.statsLibraries)
        for lib, data in libraries.items():
            if lib not in list(self.statsLibraries.keys()):
                if data["total"] == 0:
                    print("library {} was dropped".format(lib))
                    pass
                data["diffs"]["text"] = -data["text"]
                data["diffs"]["data"] = -data["data"]
                data["diffs"]["bss"] = -data["bss"]
                data["diffs"]["total"] = -data["total"]
                data["text"] = 0
                data["data"] = 0
                data["bss"] = 0
                data["total"] = 0
                diffLibraries.update({lib: data})
            else:
                diffLibraries[lib]["diffs"]["text"] = (
                    self.statsLibraries[lib]["text"] - data["text"]
                )
                diffLibraries[lib]["diffs"]["data"] = (
                    self.statsLibraries[lib]["data"] - data["data"]
                )
                diffLibraries[lib]["diffs"]["bss"] = (
                    self.statsLibraries[lib]["bss"] - data["bss"]
                )
                diffLibraries[lib]["diffs"]["total"] = (
                    self.statsLibraries[lib]["total"] - data["total"]
                )

        return diffLibraries

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
