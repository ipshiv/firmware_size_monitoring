from copy import deepcopy
import re
import os
import matplotlib.pyplot as plt
import numpy as np

from footprint_tool.footprint_monitor.FootprintMonitor import (
    FootprintMonitorZephyr,
    FootprintMonitorMbed,
)


class FootprintTool:
    @staticmethod
    def monitor(type, build_hash):
        monitors = {
            "zephyr": FootprintMonitorZephyr,
            "mbed": FootprintMonitorMbed,
        }

        assert type in monitors, f'Monitor type "{type}" is not supported'

        return monitors[type](type, build_hash)
