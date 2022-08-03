import os
import argparse
from git import Repo

from StatsParser import StatsParserZephyr


def main(path):
    root_path = path
    res_path = os.path.join(path, "resources")
    repo = Repo(root_path)
    head = repo.heads[0]
    print(head.name)
    print(head.commit.hexsha)
    sparser = StatsParserZephyr(
        os.path.join(root_path, "output.txt"), os.path.join(root_path, "status.txt")
    )
    sparser.printStatsWarnings()
    sparser.printStatsMemory()
    sparser.printStatsTable()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", help="firmware folder to analyze")
    args = parser.parse_args()
    main(vars(args)["path"])
