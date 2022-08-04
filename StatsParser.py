from copy import deepcopy
import re
import os
import matplotlib.pyplot as plt
import numpy as np


class StatsParserZephyr:
    def __init__(self, buildOutput="", statsOutput="", buildHash=""):
        if not os.access(buildOutput, os.R_OK) or not os.access(statsOutput, os.R_OK):
            raise Exception("Input files are unreadable or not exist!")

        if not buildHash:
            raise Exception("Register build hash, please!")

        self.buildHash = buildHash

        self.buildStats = ""
        self.buildStatsRow = []
        with open(buildOutput, "r") as input:
            txt = input.read()
            txt_array = txt.split("\n")
            self.countWarnings = len([line for line in txt_array if "warning:" in line])
            __num_of_lines_in_mem_stats = 4
            mem_reg_start = txt.find("Memory region")
            line_index = [
                mem_reg_start + i
                for i, c in enumerate(txt[mem_reg_start:])
                if c == "\n"
            ]
            mem_reg_end = line_index[__num_of_lines_in_mem_stats - 1]
            self.buildStats = txt[mem_reg_start:mem_reg_end]
            # | Build   | flash_region, B | flash, B | ram_region, B | ram, B |
            build_stats_array = self.buildStats.split("\n")
            # FLASH
            tmp_arr = build_stats_array[1].replace("FLASH: ", "").strip().split("B")
            flash_util = (
                int(tmp_arr[0])
                if "K" not in tmp_arr[0]
                else int(tmp_arr[0].replace("K", "")) * 1000
            )
            flas_region = (
                int(tmp_arr[1])
                if "K" not in tmp_arr[1]
                else int(tmp_arr[1].replace("K", "")) * 1000
            )
            # RAM
            tmp_arr = build_stats_array[2].replace("SRAM: ", "").strip().split("B")
            sram_util = (
                int(tmp_arr[0])
                if "K" not in tmp_arr[0]
                else int(tmp_arr[0].replace("K", "")) * 1000
            )
            sram_region = (
                int(tmp_arr[1])
                if "K" not in tmp_arr[1]
                else int(tmp_arr[1].replace("K", "")) * 1000
            )
            self.buildStatsRow = [
                self.buildHash,
                flas_region,
                flash_util,
                sram_region,
                sram_util,
            ]

        self.statsLibraries = {}
        self.statsFiles = []

        with open(statsOutput, "r") as input:
            self.statsFiles = self.__extractStats(input.readlines()[2:])
        self.statsOutputTable = {
            "nameLen": len(" Module "),
            ".textLen": len(" .text "),
            ".bssLen": len(" .bss "),
            ".dataLen": len(" .data "),
            ".totalLen": len(" total "),
        }
        self.diFFOutputTable = {
            "nameLen": len(" Module "),
            ".textLen": len(" .text ") * 2 + len("(+)"),
            ".bssLen": len(" .bss ") * 2 + len("(+)"),
            ".dataLen": len(" .data ") * 2 + len("(+)"),
            ".totalLen": len(" total ") * 2 + len("(+)"),
        }

    def __extractStats(self, stats):
        if len(stats) == 0:
            return

        statsFiles = []

        for statLine in stats:
            statLine = statLine.replace("(ex", "")
            statLine = statLine.replace(")\n", "")
            line = statLine.split(" ")
            line = [x for x in line if x]
            if len(line) < 6:
                break
            statsFiles.append(
                {
                    "text": int(line[0]),
                    "data": int(line[1]),
                    "bss": int(line[2]),
                    "total": int(line[3]),
                    "filename": line[4],
                    "lib": line[5],
                }
            )
        return statsFiles

    def __calculateColumnsWidth(self):
        for name, value in self.statsLibraries.items():
            if len(name) > self.statsOutputTable["nameLen"]:
                self.statsOutputTable["nameLen"] = len(name) + len("  ")
                self.diFFOutputTable["nameLen"] = len(name) + len("  ")
            if len(str(value["text"])) > self.statsOutputTable[".textLen"]:
                self.statsOutputTable[".textLen"] = len(str(value["text"])) + len("  ")
                self.diFFOutputTable[".textLen"] = len(str(value["text"])) * 2 + len(
                    " (+) "
                )
            if len(str(value["bss"])) > self.statsOutputTable[".bssLen"]:
                self.statsOutputTable[".bssLen"] = len(str(value["bss"])) + len("  ")
                self.diFFOutputTable[".bssLen"] = len(str(value["bss"])) * 2 + len(
                    " (+) "
                )
            if len(str(value["data"])) > self.statsOutputTable[".dataLen"]:
                self.statsOutputTable[".dataLen"] = len(str(value["data"])) + len("  ")
                self.diFFOutputTable[".dataLen"] = len(str(value["data"])) * 2 + len(
                    " (+) "
                )
            if len(str(value["total"])) > self.statsOutputTable[".totalLen"]:
                self.statsOutputTable[".totalLen"] = len(str(value["total"])) + len(
                    "  "
                )
                self.diFFOutputTable[".totalLen"] = len(str(value["total"])) * 2 + len(
                    " (+) "
                )

        self.diFFOutputTable["nameLen"] += len(":yellow_circle:")

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

    def __parse_retrospective_table(self, table):
        """
        This part is extremly hardcoded and
        depends on valid input format.
        But hey, I need result not flexibility!
        """
        table_dict = {"size": 0, "table": {}}
        table = table.split("\n")
        # get meta info from name
        meta_line = table[0]
        if "##" not in table[0]:
            return
        # ##Stats : 5 e.g.
        table_dict["size"] = int(meta_line.split(":")[-1])
        # get keys from header
        header_line = table[1][1:-1]
        keys = header_line.replace(" ", "").split("|")
        tmp_holder = []
        for key in keys:
            tmp_holder.append([key])
        # parse line by line
        for line in table[3:]:
            if line == "":
                break
            # print(line)
            line_array = line[1:-1].replace(" ", "").split("|")
            for i, data in enumerate(tmp_holder):
                data.append(line_array[i])
        for line in tmp_holder:
            table_dict["table"].update({line[0]: line[1:]})
        return table_dict

    def __parse_lib_table(self, table):
        """
        This part is extremly hardcoded and
        depends on valid input format.
        But hey, I need result not flexibility!
        """
        table_dict = {}
        table = table.split("\n")
        # verify header
        header_line = table[0][1:-1]
        keys = header_line.replace(" ", "").split("|")
        for key in ["Module", ".text", ".bss", ".data"]:
            if key not in keys:
                return {}
        # skip header
        # parse line by line
        for line in table[2:]:
            if line == "":
                break
            line_array = line[1:-1].replace(" ", "").split("|")
            lib = re.sub("(:\w+:)", "", line_array[0])
            for i, txt in enumerate(line_array[1:]):
                # print(str(i), txt)
                line_array[i + 1] = re.sub("(\((\+|\-|)\d+\))", "", txt)

            table_dict.update(
                {
                    lib: {
                        "text": int(line_array[1]),
                        "data": int(line_array[3]),
                        "bss": int(line_array[2]),
                        "total": int(line_array[4]),
                        "diffs": {"text": 0, "data": 0, "bss": 0, "total": 0},
                    }
                }
            )

        return table_dict

    def __invokeSelfWarnings(self, warnings):

        if len(warnings["table"]["Build"]) >= warnings["size"]:
            warnings["table"]["Count"] = warnings["table"]["Count"][1:]
            warnings["table"]["Build"] = warnings["table"]["Build"][1:]

        warnings["table"]["Count"].append(self.countWarnings)
        warnings["table"]["Build"].append(self.buildHash)

        return warnings

    def __invokeSelfStats(self, stats):

        if len(stats["table"]["Build"]) >= stats["size"]:
            stats["table"]["Build"] = stats["table"]["Build"][1:]
            stats["table"]["flash_region,B"] = stats["table"]["flash_region,B"][1:]
            stats["table"]["flash,B"] = stats["table"]["flash,B"][1:]
            stats["table"]["ram_region,B"] = stats["table"]["ram_region,B"][1:]
            stats["table"]["ram,B"] = stats["table"]["ram,B"][1:]

        stats["table"]["Build"].append(self.buildHash)
        stats["table"]["flash_region,B"].append(self.buildStatsRow[1])
        stats["table"]["flash,B"].append(self.buildStatsRow[2])
        stats["table"]["ram_region,B"].append(self.buildStatsRow[3])
        stats["table"]["ram,B"].append(self.buildStatsRow[4])

        return stats

    def __parseInput(self, fileName):

        # TODO Move this to global config
        __defaultSize = 5

        libraries = {}
        warnings = {"size": __defaultSize, "table": {"Build": [], "Count": []}}
        stats = {
            "size": __defaultSize,
            "table": {
                "Build": [],
                "flash_region,B": [],
                "flash,B": [],
                "ram_region,B": [],
                "ram,B": [],
            },
        }
        lib_table_txt = ""
        warning_table_txt = ""
        stats_table_txt = ""
        if os.access(fileName, os.R_OK):
            with open(fileName, "r") as input:
                txt = input.read()
                lib_table_start = txt.find("Libraries data")
                if not lib_table_start:
                    return
                lib_table_start += len("Libraries data\n")
                retr_warnings_start = txt.find("## Warnings :", lib_table_start)
                if not retr_warnings_start:
                    return
                retr_stats_start = txt.find("## Stats :", retr_warnings_start)
                if not retr_stats_start:
                    return
                lib_table_txt = txt[lib_table_start:retr_warnings_start]
                warning_table_txt = txt[retr_warnings_start:retr_stats_start]
                stats_table_txt = txt[retr_stats_start:]

            # print(lib_table_txt)
            # print("_________________________________")
            # print(warning_table_txt)
            # print("_________________________________")
            # print(stats_table_txt)
            # print("_________________________________")

            libraries = self.__parse_lib_table(lib_table_txt)
            warnings = self.__parse_retrospective_table(warning_table_txt)
            stats = self.__parse_retrospective_table(stats_table_txt)

        if self.buildHash not in warnings["table"]["Build"]:
            warnings = self.__invokeSelfWarnings(warnings)

        if self.buildHash not in stats["table"]["Build"]:
            stats = self.__invokeSelfStats(stats)

        # print(warnings)
        # print(stats)
        # print(libraries)

        return {"warnings": warnings, "libraries": libraries, "stats": stats}

    def printStatsWarnings(self):
        print("Warnings >> " + str(self.countWarnings))

    def printStatsMemory(self):
        self.__calculateLibraries()
        print("\n\ntext\tbss\tdata\tModule")
        for key, value in self.statsLibraries.items():
            print(
                "{}\t{}\t{}\t{}".format(value["text"], value["bss"], value["data"], key)
            )

    def generateLibsTable(self):
        self.__calculateLibraries()
        self.__calculateColumnsWidth()
        headerColText = " " * (self.statsOutputTable[".textLen"] - len(" .text"))
        headerColBss = " " * (self.statsOutputTable[".bssLen"] - len(" .bss"))
        headerColData = " " * (self.statsOutputTable[".dataLen"] - len(" .data"))
        headerColLib = " " * (self.statsOutputTable["nameLen"] - len(" Module"))
        headerColTotal = " " * (self.statsOutputTable[".totalLen"] - len(" total"))
        __tableHeader = "| Module{} | .text{} | .bss{} | .data{} | total{} |\n|:{}|:{}:|:{}:|:{}:|:{}:|\n".format(
            headerColLib,
            headerColText,
            headerColBss,
            headerColData,
            headerColTotal,
            "-" * (self.statsOutputTable["nameLen"]),
            "-" * (self.statsOutputTable[".textLen"] - 1),
            "-" * (self.statsOutputTable[".bssLen"] - 1),
            "-" * (self.statsOutputTable[".dataLen"] - 1),
            "-" * (self.statsOutputTable[".totalLen"] - 1),
        )
        markdownTable = __tableHeader
        for key, value in self.statsLibraries.items():
            headerColText = " " * (
                self.statsOutputTable[".textLen"] - len(str(value["text"]))
            )
            headerColBss = " " * (
                self.statsOutputTable[".bssLen"] - len(str(value["bss"]))
            )
            headerColData = " " * (
                self.statsOutputTable[".dataLen"] - len(str(value["data"]))
            )
            headerColLib = " " * (self.statsOutputTable["nameLen"] - len(key))
            headerColTotal = " " * (
                self.statsOutputTable[".totalLen"] - len(str(value["total"]))
            )
            markdownTable += "| {}{}| {}{}| {}{}| {}{}| {}{}|\n".format(
                key,
                headerColLib,
                value["text"],
                headerColText,
                value["bss"],
                headerColBss,
                value["data"],
                headerColData,
                value["total"],
                headerColTotal,
            )
        return markdownTable

    def __generateDiffTable(self, libraries):
        headerColText = " " * (self.diFFOutputTable[".textLen"] - len(" .text"))
        headerColBss = " " * (self.diFFOutputTable[".bssLen"] - len(" .bss"))
        headerColData = " " * (self.diFFOutputTable[".dataLen"] - len(" .data"))
        headerColLib = " " * (self.diFFOutputTable["nameLen"] - len(" Module"))
        headerColTotal = " " * (self.diFFOutputTable[".totalLen"] - len(" total"))
        __tableHeader = "| Module{} | .text{} | .bss{} | .data{} | total{} |\n|:{}|:{}:|:{}:|:{}:|:{}:|\n".format(
            headerColLib,
            headerColText,
            headerColBss,
            headerColData,
            headerColTotal,
            "-" * (self.diFFOutputTable["nameLen"]),
            "-" * (self.diFFOutputTable[".textLen"] - 1),
            "-" * (self.diFFOutputTable[".bssLen"] - 1),
            "-" * (self.diFFOutputTable[".dataLen"] - 1),
            "-" * (self.diFFOutputTable[".totalLen"] - 1),
        )
        markdownTable = __tableHeader
        for key, value in libraries.items():
            sign = ""
            if value["diffs"]["total"] == 0:
                sign = ":white_circle:"
            elif value["diffs"]["total"] > 0:
                sign = ":red_circle:"
            elif value["diffs"]["total"] < 0:
                sign = ":green_circle:"
            headerColText = " " * (
                self.diFFOutputTable[".textLen"]
                - len(str(value["text"]))
                - len("(+)")
                - len(str(value["diffs"]["text"]))
                + 1
            )
            headerColBss = " " * (
                self.diFFOutputTable[".bssLen"]
                - len(str(value["bss"]))
                - len("(+)")
                - len(str(value["diffs"]["bss"]))
                + 1
            )
            headerColData = " " * (
                self.diFFOutputTable[".dataLen"]
                - len(str(value["data"]))
                - len("(+)")
                - len(str(value["diffs"]["data"]))
                + 1
            )
            headerColLib = " " * (
                self.diFFOutputTable["nameLen"] - len(key) - len(sign)
            )
            headerColTotal = " " * (
                self.diFFOutputTable[".totalLen"]
                - len(str(value["total"]))
                - len("(+)")
                - len(str(value["diffs"]["total"]))
                + 1
            )

            markdownTable += (
                "| {}{}{}| {}({}){}| {}({}){}| {}({}){}| {}({}){}|\n".format(
                    sign,
                    key,
                    headerColLib,
                    value["text"],
                    value["diffs"]["text"],
                    headerColText,
                    value["bss"],
                    value["diffs"]["bss"],
                    headerColBss,
                    value["data"],
                    value["diffs"]["data"],
                    headerColData,
                    value["total"],
                    value["diffs"]["total"],
                    headerColTotal,
                )
            )
        return markdownTable

    def generateDiffTable(self, input):
        inputData = self.__parseInput(input)
        self.__calculateColumnsWidth()
        libraries = inputData["libraries"]
        diff = self.__calculateDiffLibraries(libraries)
        markdownTable = self.__generateDiffTable(diff)
        return markdownTable

    def printStatsTable(self):
        mTable = self.generateLibsTable()
        print(mTable)

    def printDiffwarnings(self, input):
        inputData = self.__parseInput(input)
        print(
            "Warnings {} ({})".format(
                str(self.countWarnings),
                str(
                    self.__calculateDiffWarnings(
                        int(inputData["warnings"]["table"]["Count"][-1])
                    )
                ),
            )
        )

    def printDiffLibraries(self, input):
        mTable = self.generateDiffTable(input)
        print(mTable)

    def plotAsciiGraphWarnings(self, input):
        inputData = self.__parseInput(input)
        _steps = 1
        _resolution = 9
        plotWidth = len(inputData["warnings"]["table"]["Count"])
        data = [
            int(warning) / _steps for warning in inputData["warnings"]["table"]["Count"]
        ]
        plotHeigth = int(max(data))
        outputGraph = "warnings /\n"
        for y in reversed(range(plotHeigth + 1)):
            outputGraph += "{}{} | ".format(" " * (len("warnings") - len(str(y))), y)
            for x in range(plotWidth):
                if data[x] < y:
                    outputGraph += " " * _resolution
                else:
                    outputGraph += "x" * _resolution
                outputGraph += " "
            outputGraph += "\n"
        outputGraph += (
            " " * len(str("warnings"))
            + " "
            + "-" * (_resolution + 2) * plotWidth
            + "\\ #build\n"
        )
        outputGraph += " " * len(str("warnings")) + "  "
        for x in range(plotWidth):
            build = inputData["warnings"]["table"]["Build"][x]
            outputGraph += "{}{} ".format(" " * (_resolution - len(build)), build)
        print(outputGraph)

    def plotGraphWarnings(self, input):
        inputData = self.__parseInput(input)
        _steps = 1
        data = [
            int(warning) / _steps for warning in inputData["warnings"]["table"]["Count"]
        ]
        labels = inputData["warnings"]["table"]["Build"]

        x = np.arange(len(labels))  # the label locations
        width = 0.75  # the width of the bars

        fig, ax = plt.subplots()
        # rects1 = ax.bar(x - width/2, dataFlash, width, label='Flash')
        # rects2 = ax.bar(x + width/2, dataRam, width, label='RAM')

        rects1 = ax.bar(labels, data, width, label="Warnings")

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel("Count")
        ax.set_title("# Build")
        ax.set_xticks(x, labels)
        ax.legend()

        ax.bar_label(rects1, padding=3)

        fig.tight_layout()
        input = input.replace("STATS.md", "graphWarnings.svg")
        plt.savefig(input, dpi=150)

    def plotGraphStats(self, input):
        inputData = self.__parseInput(input)
        _delim = 1000
        print(inputData["stats"]["table"])
        dataFlash = [
            int(data) / _delim for data in inputData["stats"]["table"]["flash,B"]
        ]
        dataRam = [int(data) / _delim for data in inputData["stats"]["table"]["ram,B"]]
        labels = inputData["stats"]["table"]["Build"]

        x = np.arange(len(labels))  # the label locations
        width = 0.75  # the width of the bars

        fig, ax = plt.subplots()
        # rects1 = ax.bar(x - width/2, dataFlash, width, label='Flash')
        # rects2 = ax.bar(x + width/2, dataRam, width, label='RAM')

        rects1 = ax.bar(labels, dataRam, width, label="RAM")
        rects2 = ax.bar(labels, dataFlash, width, bottom=dataRam, label="Flash")

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel("Size, KB")
        ax.set_title("# Build")
        ax.set_xticks(x, labels)
        ax.legend()

        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        fig.tight_layout()
        input = input.replace("STATS.md", "graphStats.svg")
        plt.savefig(input, dpi=150)
