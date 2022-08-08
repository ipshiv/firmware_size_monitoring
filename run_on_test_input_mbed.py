from StatsParser import StatsParserMbed


def main():
    sparser = StatsParserMbed("test_input/mbed.txt", "#31344", 1000000, 512000)
    sparser.printStatsWarnings()
    sparser.printStatsMemory()
    sparser.generateLibsTable()
    # sparser.printDiffwarnings("templates/STATS_ex.md")
    # sparser.printDiffLibraries("templates/STATS_ex.md")
    # sparser.plotAsciiGraphWarnings("templates/STATS_ex.md")
    # sparser.plotGraphStats("templates/STATS_ex.md")
    # sparser.plotGraphWarnings("templates/STATS_ex.md")


if __name__ == "__main__":
    main()
