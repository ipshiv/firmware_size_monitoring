from StatsParser import StatsParserZephyr


from StatsParser import StatsParserZephyr


def main():
    print("I'm main mock!")
    sparser = StatsParserZephyr("test_input/output.txt", "test_input/status.txt")
    sparser.printStatsWarnings()
    sparser.printStatsMemory()
    sparser.printStatsTable()
    sparser.printDiffwarnings("templates/STATS.md")
    sparser.printDiffLibraries("templates/STATS.md")
    sparser.plotAsciiGraphWarnings("templates/STATS.md")
    sparser.plotGraphStats("templates/STATS.md")
    sparser.plotGraphWarnings("templates/STATS.md")


if __name__ == '__main__':
    main()
