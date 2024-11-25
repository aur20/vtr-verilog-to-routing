import os
import json
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

def find_and_order_files(root_dir, filename="timing_summary.json"):
    paths = []
    # Get all locations of the file
    for dirpath, _, filenames in os.walk(root_dir):
        if filename in filenames:
            file_path = os.path.join(dirpath, filename)
            paths.append(file_path)

    # Sort the paths by reversed strings
    paths.sort(key=lambda x: x[::-1])

    return paths

@dataclass
class logInfo():
    time_initial_place: float
    time_stroobandt_init: float | None
    time_quench: float
    time_total: float

    cpd_initial_place: float
    cpd_total: float

    wirelength_initial_place: int
    wirelength_total: int

    slacktime_initial_place: float
    slacktime_total: float

    cpd_history: list[float] | None

    def strFromEntry(self, entry):
        if entry == "time_initial_place":
            return ("Initial Placement Time", "s")
        if entry == "time_stroobandt_init":
            return ("Stroobandt Init Time", "s")
        if entry == "time_total":
            return ("Time Total", "s")
        if entry == "cpd_initial_place":
            return ("Initial Placement CPD", "ns")
        if entry == "cpd_total":
            return ("CPD Total", "ns")
        if entry == "wirelength_initial_place":
            return ("Initial Placement Wirelength", "clb segments")
        if entry == "wirelength_total":
            return ("Wirelength Total", "clb segments")
        if entry == "slacktime_initial_place":
            return ("Initial Placement Slacktime", "ns")
        if entry == "slacktime_total":
            return ("Slacktime Total", "ns")
        if entry == "time_quench":
            return ("Quench Time","s")

    def fillFromLog(self, file):
        with open(file, 'r') as file:
            wirelength = False
            start = -2
            nonimportants = 0
            for line in file:
                line = line.strip()
                s = line.split()
                if "Initial Placement took" in line:
                    self.time_initial_place = float(s[s.index("took") + 1])
                if "Stroobandt-analysis of graph took" in line:
                    self.time_stroobandt_init = float(s[s.index("took") + 1])
                if "The entire flow of VPR took" in line:
                    self.time_total = float(s[s.index("took") + 1])

                if "Initial placement estimated Critical Path Delay" in line:
                    self.cpd_initial_place = float(s[s.index("(CPD):") + 1])
                if "Final critical path delay" in line:
                    self.cpd_total = float(s[s.index("slack):") + 1])

                if wirelength == False and "BB estimate of min-dist (placement)" in line:
                    self.wirelength_initial_place = int(s[s.index("length:") + 1])
                    wirelength = True
                if "Total wiring segments used" in line:
                    self.wirelength_total = int(s[s.index("used:") + 1].strip(','))

                if "Initial placement estimated setup Total Negative" in line:
                    self.slacktime_initial_place = float(s[s.index("(sTNS):") + 1])
                if "Final setup Total Negative Slack" in line:
                    self.slacktime_total = float(s[s.index("(sTNS):") + 1])

                if "## Placement Quench took" in line:
                    self.time_quench = float(s[s.index("took") + 1])

                if nonimportants > 2:
                    continue
                if "Tnum   Time       T Av Cost Av BB Cost Av TD Cost     CPD       sTNS     sWNS Ac Rate Std Dev  R lim Crit Exp Tot Moves  Alpha" in line:
                    start += 1
                    self.cpd_history = [self.cpd_initial_place]
                    continue
                elif start == -1 or start == 0:
                    start += 1
                    continue
                elif start > 0:
                    try:
                        t = int(s[0])
                        nonimportants = 0
                        if t != start:
                            nonimportants += 1
                            continue
                        start += 1
                        self.cpd_history.append(float(s[6]))
                    except:
                        nonimportants += 1
                        continue
        self.cpd_history.append(self.cpd_total)

files = find_and_order_files("./vprs", "vpr_output.log")

# Reading
readings = {}
for file in files:
    print(f"Processing File: {file}")
    cat = file.split("/")[-2][:-2]
    if cat not in readings:
        readings[cat] = []
    l = logInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    l.fillFromLog(file)
    readings[cat].append(l)

# Averaging
averages = {}
arch = files[0].split("/")[-2].split("_")[-2]
blocksizes = []
for cat, logs in readings.items():
    avg = logInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    blocksizes.append(int(cat.split("_")[1]))
    for log in logs:
        avg.time_initial_place += log.time_initial_place
        try:
            avg.time_stroobandt_init += log.time_stroobandt_init
        except:
            pass
        avg.time_total += log.time_total
        avg.cpd_initial_place += log.cpd_initial_place
        avg.cpd_total += log.cpd_total
        avg.wirelength_initial_place += log.wirelength_initial_place
        avg.wirelength_total += log.wirelength_total
        avg.slacktime_initial_place += log.slacktime_initial_place
        avg.slacktime_total += log.slacktime_total
    print(f"Category: {cat} - {len(logs)} logs")
    avg.time_initial_place /= len(logs)
    avg.time_stroobandt_init /= len(logs)
    avg.time_total /= len(logs)
    avg.cpd_initial_place /= len(logs)
    avg.cpd_total /= len(logs)
    avg.wirelength_initial_place /= len(logs)
    avg.wirelength_total /= len(logs)
    avg.slacktime_initial_place /= len(logs)
    avg.slacktime_total /= len(logs)
    averages[cat] = avg
blocksizes = list(set(blocksizes))
blocksizes.sort()

# Plotting
for x in logInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0).__annotations__.keys():
    if x == "cpd_history":
        continue
    plt.figure()
    title, scale = logInfo(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0).strFromEntry(x)
    plt.title(title)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Blocksize")
    plt.ylabel(f"Time ({scale})")
    plt.plot(blocksizes, [getattr(averages[f"original_{bs}_{arch}"], x) for bs in blocksizes], label="Original Method")
    plt.plot(blocksizes, [getattr(averages[f"new_{bs}_{arch}"], x) for bs in blocksizes], label="Stroobandt Method")
    plt.legend()
    plt.grid()
    plt.savefig(f"{title}.png")

plt.figure()
plt.title("CPD History")
plt.xlabel("Iteration")
plt.ylabel("CPD (ns)")
bs = 50000 # max(blocksizes)
idx = 2
plt.plot(range(0, len(readings[f"original_{bs}_{arch}"][idx].cpd_history)), readings[f"original_{bs}_{arch}"][idx].cpd_history, label="Original Method")
plt.plot(range(0, len(readings[f"new_{bs}_{arch}"][idx].cpd_history)), readings[f"new_{bs}_{arch}"][idx].cpd_history, label="Stroobandt Method")
plt.legend()
plt.grid()
plt.savefig("CPD History.png")
