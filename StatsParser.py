from copy import deepcopy


class StatsParserZephyr:
    def __init__(self, buildOutput="", statsOutput=""):
        with open(buildOutput, 'r') as input:
            self.countWarnings = len(
                [line for line in input.readlines() if "warning:" in line])
        with open(statsOutput, 'r') as input:
            self.statsOutput = input.readlines()[2:]

        self.statsLibraries = {}
        self.statsOutputTable = {
            "nameLen": len(" name "), ".textLen": len(" .text "), ".bssLen": len(" .bss "), ".dataLen": len(" .data "), ".totalLen": len(" total ")}
        self.diFFOutputTable = {
            "nameLen": len(" name "), ".textLen": len(" .text "), ".bssLen": len(" .bss "), ".dataLen": len(" .data "), ".totalLen": len(" total ")}
        self.statsFiles = []

        self.__clearStats()

    def __clearStats(self):
        #TODO: rename method, unclear
        if len(self.statsOutput) == 0:
            return

        self.statsFiles = []
        for statLine in self.statsOutput:
            statLine = statLine.replace('(ex', '')
            statLine = statLine.replace(')\n', '')
            line = statLine.split(' ')
            line = [x for x in line if x]
            print(line)
            self.statsFiles.append({
                "text": int(line[0]),
                "data": int(line[1]),
                "bss": int(line[2]),
                "total": int(line[3]),
                "filename": line[4],
                "lib": line[5]
            })
            print(self.statsFiles[-1])

    def __calculateColumnsWidth(self):
        for name, value in self.statsLibraries.items():
            if len(name) > self.statsOutputTable["nameLen"]:
                self.statsOutputTable["nameLen"] = len(name) + len("  ")
                self.diFFOutputTable["nameLen"] = len(name) + len("  ")
            if len(str(value["text"])) > self.statsOutputTable[".textLen"]:
                self.statsOutputTable[".textLen"] = len(
                    str(value["text"])) + len("  ")
                self.diFFOutputTable[".textLen"] = len(
                    str(value["text"])) * 2 + len(" (+) ")
            if len(str(value["bss"])) > self.statsOutputTable[".bssLen"]:
                self.statsOutputTable[".bssLen"] = len(
                    str(value["bss"])) + len("  ")
                self.diFFOutputTable[".bssLen"] = len(
                    str(value["bss"])) * 2 + len(" (+) ")
            if len(str(value["data"])) > self.statsOutputTable[".dataLen"]:
                self.statsOutputTable[".dataLen"] = len(
                    str(value["data"])) + len("  ")
                self.diFFOutputTable[".dataLen"] = len(
                    str(value["data"])) * 2 + len(" (+) ")
            if len(str(value["total"])) > self.statsOutputTable[".totalLen"]:
                self.statsOutputTable[".totalLen"] = len(
                    str(value["total"])) + len("  ")
                self.diFFOutputTable[".totalLen"] = len(
                    str(value["total"])) * 2 + len(" (+) ")

    def __calculateLibraries(self):
        self.statsLibraries = {}
        for file in self.statsFiles:
            if file["lib"] not in list(self.statsLibraries.keys()):
                self.statsLibraries.update(
                    {file["lib"]: {"text": 0, "data": 0, "bss": 0, "total": 0, "diffs": {"text": 0, "data": 0, "bss": 0, "total": 0}}})
            self.statsLibraries[file["lib"]]["text"] += file["text"]
            self.statsLibraries[file["lib"]]["data"] += file["data"]
            self.statsLibraries[file["lib"]]["bss"] += file["bss"]
            self.statsLibraries[file["lib"]]["total"] += file["total"]

    def __calculateDiffWarnings(self, previousWarnings):
        return (previousWarnings - self.countWarnings)

    def __calculateDiffLibraries(self, libraries):
        for lib, data in libraries.items():
            diffLibraries = deepcopy(self.statsLibraries)
            if lib not in list(self.statsLibraries.keys()) and data["total"] != 0:
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
                diffLibraries[lib]["diffs"]["text"] = self.statsLibraries[lib]["text"] - data["text"]
                diffLibraries[lib]["diffs"]["data"] = self.statsLibraries[lib]["data"] - data["data"]
                diffLibraries[lib]["diffs"]["bss"] = self.statsLibraries[lib]["bss"] - data["bss"]
                diffLibraries[lib]["diffs"]["total"] = self.statsLibraries[lib]["total"] - data["total"]

        return diffLibraries

    def __parseInput(self, fileName):
        warnings = 0
        libraries = {}
        return warnings, libraries

    def printStatsWarnings(self):
        print("Warnings >> " + str(self.countWarnings))

    def printStatsMemory(self):
        self.__calculateLibraries()
        print("\n\ntext\tbss\tdata\tlib")
        for key, value in self.statsLibraries.items():
            print("{}\t{}\t{}\t{}".format(
                value["text"], value["bss"], value["data"], key))

    def genrateStatsTable(self):
        self.__calculateColumnsWidth()
        headerColText = " " * \
            (self.statsOutputTable[".textLen"] - len(" .text"))
        headerColBss = " " * \
            (self.statsOutputTable[".bssLen"] - len(" .bss"))
        headerColData = " " * \
            (self.statsOutputTable[".dataLen"] - len(" .data"))
        headerColLib = " " * \
            (self.statsOutputTable["nameLen"] - len(" lib"))
        __tableHeader = "| .text{} | .bss{} | .data{} | lib{} |\n|:{}:|:{}:|:{}:|:{}:|\n".format(
            headerColText, headerColBss, headerColData, headerColLib, "-" *
            (self.statsOutputTable[".textLen"] - 1),
            "-" * (self.statsOutputTable[".bssLen"] - 1), "-" * (self.statsOutputTable[".dataLen"] - 1), "-" * (self.statsOutputTable["nameLen"] - 1))
        markdownTable = __tableHeader
        for key, value in self.statsLibraries.items():
            headerColText = " " * \
                (self.statsOutputTable[".textLen"] - len(str(value["text"])))
            headerColBss = " " * \
                (self.statsOutputTable[".bssLen"] - len(str(value["bss"])))
            headerColData = " " * \
                (self.statsOutputTable[".dataLen"] - len(str(value["data"])))
            headerColLib = " " * \
                (self.statsOutputTable["nameLen"] - len(key))
            markdownTable += "| {}{}| {}{}| {}{}| {}{}|\n".format(
                value["text"], headerColText, value["bss"], headerColBss, value["data"],  headerColData, key, headerColLib)
        return markdownTable

    def printStatsTable(self):
        mTable = self.genrateStatsTable()
        print(mTable)

    def printDiffwarnings(self, input):
        warnings, libraries = self.__parseInput(input)
        print("Warnings {} ({})".format(
            str(self.countWarnings), str(self.__calculateDiffWarnings(warnings))))

    def printDiffLibraries(self, input):
        warnings, libraries = self.__parseInput(input)
        diff = self.__calculateDiffLibraries(libraries)
        print("\n\ntext\tbss\tdata\tlib")
        for key, value in self.statsLibraries.items():
            print("{}({})\t{}({})\t{}({})\t{}({})".format(
                value["text"], value["diffs"]["text"], value["bss"], value["diffs"]["bss"], value["data"], value["diffs"]["data"], key))
