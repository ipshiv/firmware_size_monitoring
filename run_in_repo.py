import os
import argparse
from git import Repo

from footprint_tool.FootprintTool import FootprintTool

tool = FootprintTool()


def main_zephyr(path):
    if path is None:
        raise Exception("Error enter the path using --path or -p argument")
    output_data = {
        "current_build": {
            "build_sha": "",
            "warnings": 0,
            "build_stats_text": "",
            "lib_stats_markdown": "",
        },
        "retrospective": {
            "warnings_markdown": "",
            "stats_markdown": "",
        },
    }
    root_path = path
    res_path = os.path.join(path, "resources/STATS.md")
    repo = Repo(root_path)
    output_data["current_build"]["build_sha"] = "#" + repo.heads[0].commit.hexsha[:7]
    monitor_zephyr = tool.monitor("zephyr", "#3333333")
    monitor_mbed = tool.monitor("mbed", "#3333333")
    monitors = [monitor_zephyr, monitor_mbed]
    for monitor in monitors:
        monitor.parse_input()
        monitor.render()
        monitor.plot()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", help="firmware folder to analyze")
    args = parser.parse_args()
    main_zephyr(vars(args)["path"])
    # main_mbed(vars(args)["path"])
