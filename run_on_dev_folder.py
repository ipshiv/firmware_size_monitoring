import os
import argparse
from git import Repo

from StatsParser import StatsParserZephyr


def main(path):
    output_data = {
        "current_build": {
            "build_sha": "",
            "warnings": 0,
            "build_stats_text": "",
            "build_stats_row": "",
            "lib_stats_markdown": "",
        },
        "retrospective": {
            "warnings_markdown": {"size": 0, "table_rows": []},
            "stats": {"size": 0, "table_rows": []},
        },
    }
    root_path = path
    res_path = os.path.join(path, "resources")
    repo = Repo(root_path)
    output_data["current_build"]["build_sha"] = "#" + repo.heads[0].commit.hexsha[:7]
    sparser = StatsParserZephyr(
        os.path.join(root_path, "output.txt"), os.path.join(root_path, "status.txt"),
        output_data["current_build"]["build_sha"]
    )
    output_data["current_build"]["warnings"] = sparser.countWarnings
    output_data["current_build"]["build_stats_text"] = sparser.buildStats
    output_data["current_build"]["build_stats_row"] = sparser.buildStatsRow
    output_data["current_build"]["build_stats_row"][0] = output_data["current_build"][
        "build_sha"
    ]
    if not os.access(os.path.join(root_path, "resources/STATS.md"), os.R_OK):
        output_data["current_build"][
            "lib_stats_markdown"
        ] = sparser.generateLibsTable()
    else:
        output_data["current_build"]["lib_stats_markdown"] = sparser.generateDiffTable(
            os.path.join(root_path, "resources/STATS.md")
        )

    print(output_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", help="firmware folder to analyze")
    args = parser.parse_args()
    main(vars(args)["path"])
