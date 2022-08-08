import os
import argparse
from git import Repo

from StatsParser import StatsParserMbed


def generateStatsMd(path, data):
    output = """
# Latest build {} stats
## Warnings
{}
## Memory utilization
```
{}
```
## Libraries data
{}

# Retrospective
{}

![img](graphWarnings.svg)

{}

![img](graphStats.svg)
    """.format(
        data["current_build"]["build_sha"],
        data["current_build"]["warnings"],
        data["current_build"]["build_stats_text"],
        data["current_build"]["lib_stats_markdown"],
        data["retrospective"]["warnings_markdown"],
        data["retrospective"]["stats_markdown"],
    )
    print(output)
    with open(path, "w") as file:
        file.write(output)


def main(path):
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
    # FIXME For test purposes only
    # repo = Repo(root_path)
    output_data["current_build"]["build_sha"] = "#" + "31344"

    sparser = StatsParserMbed(
        os.path.join(root_path, "mbed.txt"),
        output_data["current_build"]["build_sha"],
        1000000,
        512000,
    )

    output_data["current_build"]["warnings"] = sparser.countWarnings
    output_data["current_build"]["build_stats_text"] = sparser.buildStats

    if not os.access(res_path, os.R_OK):
        output_data["current_build"]["lib_stats_markdown"] = sparser.generateLibsTable()
    else:
        output_data["current_build"]["lib_stats_markdown"] = sparser.generateDiffTable(
            os.path.join(res_path)
        )

    output_data["retrospective"]["warnings_markdown"] = sparser.generateWarningsTable(
        os.path.join(res_path)
    )
    output_data["retrospective"]["stats_markdown"] = sparser.generateStatsTable(
        os.path.join(res_path)
    )

    # export output
    sparser.plotGraphStats(res_path)
    sparser.plotGraphWarnings(res_path)
    generateStatsMd(res_path, output_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", help="firmware folder to analyze")
    args = parser.parse_args()
    main(vars(args)["path"])
