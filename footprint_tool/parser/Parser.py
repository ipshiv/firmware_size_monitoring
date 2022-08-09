from abc import ABC, abstractmethod
from copy import deepcopy
import re
import os
import matplotlib.pyplot as plt
import numpy as np


class __Parser(ABC):
    def __init__(self, build_hash="", stats_in_db=5):
        if not build_hash:
            raise Exception("Register build hash, please!")

        self.build_hash = build_hash

        self.statsLibraries = {}
        self.statsFiles = []

        self.buildStats = ""
        self.buildStatsRow = []

        self.__libraries = {}
        self.__warnings = {"size": stats_in_db, "table": {"Build": [], "Count": []}}
        self.__stats = {
            "size": stats_in_db,
            "table": {
                "Build": [],
                "flash_region,B": [],
                "flash,B": [],
                "ram_region,B": [],
                "ram,B": [],
            },
        }

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

    @abstractmethod
    def parse_build(self, **kwargs):
        pass

    def parse_retrospective(self, build_output="", invoke_data=True):
        libraries = {}
        warnings = {
            "size": self.__warnings["size"],
            "table": {"Build": [], "Count": []},
        }
        stats = {
            "size": self.__stats["size"],
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

        if os.access(build_output, os.R_OK):
            with open(build_output, "r") as input:
                txt = input.read()
                lib_table_start = txt.find("Libraries data")
                if not lib_table_start:
                    print("No lib data found!")
                    return
                lib_table_start += len("Libraries data\n")
                retr_warnings_start = txt.find("## Warnings :", lib_table_start)
                if not retr_warnings_start:
                    print("No warnings data found!")
                    return
                retr_stats_start = txt.find("## Stats :", retr_warnings_start)
                if not retr_stats_start:
                    print("No stats data found!")
                    return
                lib_table_txt = txt[lib_table_start:retr_warnings_start]
                warning_table_txt = txt[retr_warnings_start:retr_stats_start]
                stats_table_txt = txt[retr_stats_start:]

            libraries = self.__parse_lib_table(lib_table_txt)
            warnings = self.__parse_retrospective_table(warning_table_txt)
            stats = self.__parse_retrospective_table(stats_table_txt)

        if invoke_data:
            if self.build_hash not in warnings["table"]["Build"]:
                warnings = self.__invokeSelfWarnings(warnings)

            if self.build_hash not in stats["table"]["Build"]:
                stats = self.__invokeSelfStats(stats)

        self.__libraries = deepcopy(libraries)
        self.__warnings = deepcopy(warnings)
        self.__stats = deepcopy(stats)

    def dict_libraries(self):
        return self.__libraries

    def dict_stats(self):
        return self.__stats

    def dict_warnings(self):
        return self.__warnings

    def dict_build_libraries(self):
        return self.statsLibraries

    def arr_stats_files(self):
        return self.statsFiles

    def txt_build_stats(self):
        return self.buildStats

    def arr_build_stats(self):
        return self.buildStatsRow


class ParserZephyr(__Parser):
    def __init__(self, build_hash):
        super().__init__(build_hash)

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

    def parse_build(self, **kwargs):
        print("Zephyr is on the line!" + self.build_hash)

        buildOutput = kwargs["build_output"]
        statsOutput = kwargs["stats_output"]

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
                self.build_hash,
                flas_region,
                flash_util,
                sram_region,
                sram_util,
            ]

        with open(statsOutput, "r") as input:
            self.statsFiles = self.__extractStats(input.readlines()[2:])


class ParserMbed(__Parser):
    def __init__(self, build_hash):
        super().__init__(build_hash)

    def __extractStats(self, stats):
        if len(stats) == 0:
            return

        statsFiles = []

        for statLine in stats:
            statLine = re.sub("(\((\+|\-|)\d+\))", "", statLine)
            print(statLine)
            line = statLine.split("|")
            line = [x for x in line if x]
            print(line)
            if len(line) < 3:
                break
            statsFiles.append(
                {
                    "text": int(line[1]),
                    "data": int(line[2]),
                    "bss": int(line[3]),
                    "total": int(line[3]) + int(line[2]) + int(line[1]),
                    "filename": line[0].strip(),
                    "lib": line[0].strip(),
                }
            )
        return statsFiles

    def parse_build(self, **kwargs):
        print("Zephyr is on the line!" + self.build_hash)
        if not os.access(buildOutput, os.R_OK):
            raise Exception("Input files are unreadable or not exist!")

        stats = ""

        buildOutput = kwargs["build_output"]
        flashTotal = kwargs["flash_total"]
        ramTotal = kwargs["ram_total"]

        with open(buildOutput, "r") as input:
            txt = input.read()
            txt_array = txt.split("\n")
            self.countWarnings = len([line for line in txt_array if "warning:" in line])
            __num_of_lines_in_mem_stats = 2
            stats_reg_start = txt.find("| Module")
            stats_reg_end = txt.find("| Subtotals")
            mem_reg_start = txt.find("Total Static RAM ")
            if not stats_reg_end:
                stats_reg_end = mem_reg_start
            line_index = [
                mem_reg_start + i
                for i, c in enumerate(txt[mem_reg_start:])
                if c == "\n"
            ]
            mem_reg_end = line_index[__num_of_lines_in_mem_stats - 1]
            stats = txt[stats_reg_start:stats_reg_end]
            self.buildStats = txt[mem_reg_start:mem_reg_end]
            # | Build   | flash_region, B | flash, B | ram_region, B | ram, B |
            build_stats_array = self.buildStats.split("\n")
            # FLASH
            txt = build_stats_array[1].replace("bytes", "").split(":")[-1]
            flash_util = re.sub("(\((\+|\-|)\d+\))", "", txt)
            flas_region = flashTotal
            # RAM
            txt = build_stats_array[0].replace("bytes", "").split(":")[-1]
            sram_util = re.sub("(\((\+|\-|)\d+\))", "", txt)
            sram_region = ramTotal
            self.buildStatsRow = [
                self.build_hash,
                flas_region,
                flash_util,
                sram_region,
                sram_util,
            ]

        # print("DBG >> count warnings >> {}".format(self.countWarnings))
        # print("DBG >> build stats txt >>\n{}".format(self.buildStats))
        # print("DBG >> build stats row >>{}".format(self.buildStatsRow))
        # print("DBG >> stats txt >>\n{}".format(stats))

        self.statsFiles = self.__extractStats(stats.split("\n")[2:])

        # print("DBG >> stats >> {}".format(self.statsFiles))
