from copy import deepcopy
import re
import os
import matplotlib.pyplot as plt
import numpy as np


def __plotGraphWarnings(inputData):
    _steps = 1
    data = [
        int(warning) / _steps for warning in inputData["warnings"]["table"]["Count"]
    ]
    labels = inputData["warnings"]["table"]["Build"]

    x = np.arange(len(labels))  # the label locations
    width = 0.75  # the width of the bars

    fig, ax = plt.subplots()
    # rects1 = ax.bar(x - width/2, dataFlash, width, label='Flash')
    # rects2 = ax.bar(x + width/2, dataRam, width, label='RAM')

    rects1 = ax.bar(labels, data, width, label="Warnings")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Count")
    ax.set_title("# Build")
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)

    fig.tight_layout()
    input = input.replace("STATS.md", "graphWarnings.svg")
    plt.savefig(input, dpi=150)


def __plotGraphStats(inputData):
    _delim = 1000
    print(inputData["stats"]["table"])
    dataFlash = [int(data) / _delim for data in inputData["stats"]["table"]["flash,B"]]
    dataRam = [int(data) / _delim for data in inputData["stats"]["table"]["ram,B"]]
    labels = inputData["stats"]["table"]["Build"]

    x = np.arange(len(labels))  # the label locations
    width = 0.75  # the width of the bars

    fig, ax = plt.subplots()
    # rects1 = ax.bar(x - width/2, dataFlash, width, label='Flash')
    # rects2 = ax.bar(x + width/2, dataRam, width, label='RAM')

    rects1 = ax.bar(labels, dataRam, width, label="RAM")
    rects2 = ax.bar(labels, dataFlash, width, bottom=dataRam, label="Flash")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Size, KB")
    ax.set_title("# Build")
    ax.set_xticks(x, labels)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    input = input.replace("STATS.md", "graphStats.svg")
    plt.savefig(input, dpi=150)


def plotSvgGraph(inputData, type=""):
    plotters = {"stats": __plotGraphStats, "warnings": __plotGraphWarnings}

    assert type in plotters, f'Plotter type "{type}" is not supported'

    plotters[type](inputData)
