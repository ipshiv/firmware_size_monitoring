from StatsParser import StatsParserZephyr


def main():
    sparser = StatsParserZephyr("test_input/output.txt", "test_input/status.txt")
    sparser.printStatsWarnings()
    sparser.printStatsMemory()
    sparser.printStatsTable()
    sparser.printDiffwarnings("templates/STATS_ex.md")
    sparser.printDiffLibraries("templates/STATS_ex.md")
    sparser.plotAsciiGraphWarnings("templates/STATS_ex.md")
    sparser.plotGraphStats("templates/STATS_ex.md")
    sparser.plotGraphWarnings("templates/STATS_ex.md")


if __name__ == "__main__":
    main()
