from StatsParser import StatsParserZephyr


from StatsParser import StatsParserZephyr


def main():
    print("I'm main mock!")
    sparser = StatsParserZephyr("output.txt", "status.txt")
    sparser.printStatsWarnings()
    sparser.printStatsMemory()
    sparser.printStatsTable()


if __name__ == '__main__':
    main()
