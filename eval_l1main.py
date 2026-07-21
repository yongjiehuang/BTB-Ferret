#!/usr/bin/env python3
"""
eval_l1main.py – Converted from eval-l1main.ipynb
Produces two PDF figures:
  1. opportunity.pdf      – Grouped bar chart of normalized IPC (Speedup)
  2. btb_successors.pdf   – Stacked bar chart of L1 BTB miss predecessors
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as mlp
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import re
import glob

# ── Global matplotlib settings ──────────────────────────────────────────────
mlp.rcParams['font.family'] = 'serif'
mlp.rcParams['font.serif'] = ['Times New Roman'] + mlp.rcParams['font.serif']
mlp.rcParams['pdf.fonttype'] = 42
mlp.rcParams['hatch.linewidth'] = 0.6

APATH = "."
RES_DIR = "./results"


# ── Utility functions ────────────────────────────────────────────────────────

def name(cfg):
    n = "Scale "
    match = re.search(r'_f(\d+)_', cfg)
    s = match.group(1) if match else ""
    n += s + "x"
    if "_infp1_" in cfg:
        n += "\n+ Inf Pred"
    return n


def fmtBytes(size):
    # 2**10 = 1024
    tmp = -size if size < 0 else size
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while tmp >= power:
        tmp /= power
        n += 1
    return "%s%d%s" % ("-" if size < 0 else "", tmp, power_labels[n])


def geo_mean(iterable):
    a = np.array(iterable)
    return np.prod(a, where=a > 0)**(1.0 / len(a))


def fmtByte(value, unit="B"):
    for unit in ["", "k", "M", "G", "T", "P"]:
        if value < 1024:
            return f"{value:.0f}{unit}"
        value /= 1024


def renameBms(bm):
    m = {
        "nodeapp": "NodeApp",
        "mediawiki": "PHPWiki",
        "compression": "Compression",
        "proto": "Proto",

        # "swissmap": "SwissMap",
        "tcmalloc": "TCMalloc",
        "stl": "STL",

        "dacapo-h2": "H2",
        "dacapo-h2o": "H2O",
        # "dacapo-kafka": "Kafka",
        "dacapo-luindex": "Luindex",
        "dacapo-spring": "Spring",
        "dacapo-tomcat": "Tomcat",
        "dacapo-lusearch": "Lusearch",
        "benchbase-otmetrics": "OTMetrics",
        "benchbase-voter": "Voter",
        "benchbase-twitter": "Twitter",
        "benchbase-tatp": "TATP",
        # "benchbase-resourcestresser": "Stresser",
        "benchbase-epinions": "Epinions",
        "benchbase-ycsb": "YCSB",
        "benchbase-seats": "Seats",
        "benchbase-sibench": "SiBench",
        "benchbase-noop": "Noop",
        "benchbase-smallbank": "SmallBank",
        "renaissance-http": "HTTP",
        "renaissance-chirper": "Chirper",

        # "dacapo-spring": "Spring",
        # "dacapo-luindex": "Luindex",
        # "dacapo-lusearch": "Lusearch",
        # "renaissance-http": "HTTP",
        # "renaissance-chirper": "Chirper",
        # "benchbase-tpcc": "TPCC",
        # "benchbase-twitter": "Twitter",
        # "benchbase-wikipedia": "Wikipedia",
        # "dacapo-kafka": "Kafka",
        # "dacapo-tomcat": "Tomcat",
        "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000": "502.gcc",
        # "505.mcf_r.inp": "505.mcf",
        "520.omnetpp_r.inp": "520.omnetpp",
        "523.xalancbmk_r.inp": "523.xalancbmk",
        "523.xalancbmk_r.xalanc": "523.xalancbmk",
        "525.x264_r.inp": "525.x264",
        "525.x264_r.x264": "525.x264",
        "538.imagick_r.inp": "538.imagick",
        "541.leela_r.ref": "541.leela",
        "544.nab_r.inp": "544.nab",
        "557.xz_r.input": "557.xz",
        "500.perlbench_r.inp": "500.perlbench",
        "500.perlbench_r.checkspam": "500.perlbench",
        "500.perlbench_r.diffmail": "500.perlbench",
        "502.gcc_r.inp": "502.gcc",
        "505.mcf_r.inp": "505.mcf",
        "520.omnetpp_r.general": "520.omnetpp",
        "531.deepsjeng_r.ref": "531.deepsjeng",
        "508.namd_r.apoa1": "508.namd",
        "510.parest_r.ref": "510.parest",
        "511.povray_r.ref": "511.povray",
        "519.lbm_r.ref": "519.lbm",
        "526.blender_r.ref": "526.blender",
        "538.imagick_r.ref": "538.imagick",
        "544.nab_r.ref": "544.nab",

    # "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000",
    # "505.mcf_r.inp",
    # "523.xalancbmk_r.xalanc",
    # "531.deepsjeng_r.ref",
    # "541.leela_r.ref",

    # "500.perlbench_r.checkspam",
    # "500.perlbench_r.diffmail",
    # "557.xz_r.cpu2006docs",
    # # "520.omnetpp_r.general",
    # "525.x264_r.x264",

    }
    return m.get(bm, bm) if bm else bm


# ── Benchmark lists ──────────────────────────────────────────────────────────

small_bms = [
    "nodeapp",
    "mediawiki",
    "compression",
    "dacapo-spring",
    "dacapo-luindex",
    "dacapo-lusearch",
    "renaissance-http",
    "renaissance-chirper",

    "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000",
    "505.mcf_r.inp",
    "523.xalancbmk_r.xalanc",
    "531.deepsjeng_r.ref",
    "541.leela_r.ref",
]

all_bms = [
    "nodeapp",
    "mediawiki",

    "proto",
    # "swissmap",
    "tcmalloc",
    "stl",

    "dacapo-h2",
    "dacapo-h2o",
    # "dacapo-kafka",
    "dacapo-luindex",
    "dacapo-spring",
    "dacapo-tomcat",
    "dacapo-lusearch",


    # "benchbase-otmetrics",
    "benchbase-voter",
    "benchbase-twitter",
    "benchbase-tatp",
    # "benchbase-resourcestresser",
    "benchbase-epinions",
    "benchbase-ycsb",
    "benchbase-seats",
    "benchbase-sibench",
    "benchbase-noop",
    "benchbase-smallbank",


    # "dacapo-spring",
    # "dacapo-luindex",
    # "dacapo-lusearch",
    # "renaissance-http",
    # "renaissance-chirper",

    "renaissance-http",

    "500.perlbench_r.checkspam",
    "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000",
    "505.mcf_r.inp",
    "508.namd_r.apoa1",
    "510.parest_r.ref",
    "511.povray_r.ref",
    "519.lbm_r.ref",
    "520.omnetpp_r.general",
    "523.xalancbmk_r.xalanc",
    "525.x264_r.x264",
    "526.blender_r.ref",
    "531.deepsjeng_r.ref",
    "538.imagick_r.ref",
    "541.leela_r.ref",
    "544.nab_r.ref",

    # "500.perlbench_r.diffmail",
    # "557.xz_r.cpu2006docs",
    # "557.xz_r.cld",
    "557.xz_r.input",


]



# ── Shared Line Plot Configurations ──────────────────────────────────────────
# These are used by plot_meanLine, plot_meanCovered, plot_meanLooseCovered, 
# and plot_meanOverprefetch to avoid manual duplication.

SHARED_BASELINE_CFG = "baseline-128-16K"

SHARED_SERIES_LIST = [
    # {
    #     "name": "64-entry PB",
    #     "configs": [
    #         (1, "64pb-8sz-dep1"),
    #         (2, "64pb-8sz-dep2"),
    #         (4, "64pb-8sz-dep4"),
    #         (6, "64pb-8sz-dep6"),
    #         (8, "64pb-8sz-dep8"),
    #         (10, "64pb-8sz-dep10"),
    #         (12, "64pb-8sz-dep12"),
    #         (14, "64pb-8sz-dep14"),
    #         (16, "64pb-8sz-dep16"),
    #         (18, "64pb-8sz-dep18"),
    #         (20, "64pb-8sz-dep20"),
    #         (22, "64pb-8sz-dep22"),
    #     ],
    #     "color": "#f39c12" # 
    # },
    # {
    #     "name": "32-entry PB",
    #     "configs": [
    #         (1, "32pb-8sz-dep1"),
    #         (2, "32pb-8sz-dep2"),
    #         (4, "32pb-8sz-dep4"),
    #         (6, "32pb-8sz-dep6"),
    #         (8, "32pb-8sz-dep8"),
    #         (10, "32pb-8sz-dep10"),
    #         (12, "32pb-8sz-dep12"),
    #         (14, "32pb-8sz-dep14"),
    #         (18, "32pb-8sz-dep18"),
    #         (20, "32pb-8sz-dep20"),
    #         (22, "32pb-8sz-dep22"),
    #     ],
    #     "color": "#4fc3f7" # 
    # },
    
    # {
    #     "name": "16-entry PB",
    #     "configs": [
    #         (1, "16pb-8sz-dep1"),
    #         (2, "16pb-8sz-dep2"),
    #         (4,  "16pb-8sz-dep4"),
    #         (6, "16pb-8sz-dep6"),
    #         (8,  "16pb-8sz-dep8"),
    #         (10, "16pb-8sz-dep10"),
    #         (12, "16pb-8sz-dep12"),
    #         (14, "16pb-8sz-dep14"),
    #         (18, "16pb-8sz-dep18"),
    #         (20, "16pb-8sz-dep20"),
    #         (22, "16pb-8sz-dep22"),
    #     ],
    #     "color": "#3498db" # Blue
    # },
    # {
    #     "name": "8-entry PB",
    #     "configs": [
    #         (1, "8pb-8sz-dep1"),
    #         (2, "8pb-8sz-dep2"),
    #         (4,  "8pb-8sz-dep4"),
    #         (6, "8pb-8sz-dep6"),
    #         (8,  "8pb-8sz-dep8"),
    #         (10, "8pb-8sz-dep10"),
    #         (12, "8pb-8sz-dep12"),
    #         (14, "8pb-8sz-dep14"),
    #         (18, "8pb-8sz-dep18"),
    #         (20, "8pb-8sz-dep20"),
    #         (22, "8pb-8sz-dep22"),
    #     ],
    #     "color": "#e74c3c" # Red
    # },
    ## sweep of table
    {
        "name": "64-entry PB",
        "configs": [
            (10, "64pb-10sz-dep14"),
            (8, "64pb-8sz-dep14"),
            (5, "64pb-5sz-dep14"),
            (4, "64pb-4sz-dep14"),
            (3, "64pb-3sz-dep14"),
            (2, "64pb-2sz-dep14"),
            (1, "64pb-1sz-dep14"),
        ],
        "color": "#f39c12" # 
    },
    {
        "name": "32-entry PB",
        "configs": [
            (10, "32pb-10sz-dep14"),
            (8, "32pb-8sz-dep14"),
            (5, "32pb-5sz-dep14"),
            (4, "32pb-4sz-dep14"),
            (3, "32pb-3sz-dep14"),
            (2, "32pb-2sz-dep14"),
            (1, "32pb-1sz-dep14"),
        ],
        "color": "#4fc3f7" # 
    },
    
    {
        "name": "16-entry PB",
        "configs": [
            (10, "16pb-10sz-dep6"),
            (8, "16pb-8sz-dep6"),
            (5, "16pb-5sz-dep6"),
            (4, "16pb-4sz-dep6"),
            (3, "16pb-3sz-dep6"),
            (2, "16pb-2sz-dep6"),
            (1, "16pb-1sz-dep6"),
        ],
        "color": "#3498db" # Blue
    },
    {
        "name": "8-entry PB",
        "configs": [
            (10, "8pb-10sz-dep6"),
            (8, "8pb-8sz-dep6"),
            (5, "8pb-5sz-dep6"),
            (4, "8pb-4sz-dep6"),
            (3, "8pb-3sz-dep6"),
            (2, "8pb-2sz-dep6"),
            (1, "8pb-1sz-dep6"),
        ],
        "color": "#e74c3c" # Red
    },
]


# ── Helper: read a stats.txt file ────────────────────────────────────────────

def read_stats(path):
    stats = {}
    with open(path, "r") as f:
        for line in f:
            try:
                parts = line.split()
                stat_name = parts[0]
                stat_value = parts[1]
                stats[stat_name] = float(stat_value)
            except:
                continue
    return stats


def resolve_metric(metric, bm):
    """Format a metric template based on whether the benchmark is SPEC (starts with '5')."""
    spec = bm.startswith("5")
    return metric.format(
        core="board.processor.cores.core" if spec else "board.processor.cores1.core",
        nc="" if spec else "1"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 1: Opportunity  (opportunity.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_opportunity():
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
    }

    bms = all_bms

    configs = [
        # ("optimal_BTB", "Ideal BTB"),
        # ("pf-8sz-20", "8sz 20 dep prefetcher"),
        # ("baseline-144L1", "144L1 Baseline"),
        # ("baseline-160L1", "166L1 Baseline"),
        # ("baseline", "2-Level Baseline")
        
        ("pf-8pb-4sz-16", "8pb-4sz-16dep"),
        ("pf-8pb-2sz-16", "8pb-2sz-16dep"),
        ("l1hit-baseline", "2-Level Baseline")
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    df = pd.DataFrame(columns=["Config", "Benchmark", "Metric", "Value"])

    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                print(f"Warning: No stats file found for {cfg}/{bm} at {path_pattern}")
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm not in data[cfg][bm]:
                    print(f"Warning: Metric {mm} not found in {cfg}/{bm}")
                else:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]

            ## Compute derived metrics
            data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]

            cfgref = configs[0][0]
            data[cfg][bm]["Speedup"] = data[cfg][bm]["IPC"] / data[cfgref][bm]["IPC"]

    # ── Colors ───────────────────────────────────────────────────────────────
    colors = ["#07163d", "#01739e", "#4fc3f7", "#cc0000", "#888888"]

    metrics = [
        ("Baseline", "#cc0000", ""),
        # ("L2Hit NT", "#cc0000", "...."),
        ("Ideal BTB", "#005e8a", ""),
        # ("L1Hit NT", "#005e8a", "...."),
        ("Ideal BPU", "#0f0f0f", ""),
        # ("No Entry", "#B4B4B4", ""),
    ]

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 12.5
    fs = 13
    NG = 1
    fig, ax = mlp.subplots(1, NG, figsize=(NG * cw, cw * 0.165), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    _labels = [renameBms(bm) for bm in bms] + ["Mean"]

    vals = {}

    bottoms = np.zeros(len(bms) + 1)
    x = np.arange(len(bms) + 1, dtype=float)  # the label locations, including mean
    x[-1] = x[-1] + 0.4
    x = [xi + 0.2 if "5" in l else xi for xi, l in zip(x, _labels)]
    x = np.array(x)
    print(x)
    xi = 0
    for i, l in enumerate(_labels):
        if "5" in l:
            xi = i
            break
    print(xi)

    width = 0.8 / len(configs)  # the width of the bars

    # Filter bms to only those that have data in ALL configs
    valid_bms = []
    for bm in bms:
        if all(bm in data[cfg] for (cfg, cfgn) in configs):
            valid_bms.append(bm)
    
    bms = valid_bms

    for i, (cfg, cfgn) in enumerate(configs):
        y = [data[cfg][bm]["Speedup"] for bm in bms]
        y += [np.mean(y)]
        y = np.array(y)

        ax.bar(x=x + width * i - width, height=y, width=width, label=cfgn, bottom=bottoms, zorder=3, color=colors[i], edgecolor="k")
        # bottoms += np.array(y)

    print(y)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_ylabel("Norm. IPC", fontsize=fs - 1)

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=0)

    _labels = [renameBms(bm) for bm in bms] + ["Mean"]
    ax.set_xticklabels(_labels, rotation=25, horizontalalignment="right", fontsize=fs - 4, rotation_mode="anchor")

    ax.set_xlim(xmin=-0.6, xmax=max(x) + 0.6)

    ax.set_ylim(bottom=0.73, top=1.02)

    # Calculate vertical lines dynamically
    spec_start = -1
    for i, bm in enumerate(bms):
        if bm.startswith("5"):
            spec_start = i
            break
    
    if spec_start != -1:
        # Find where MEAN starts (it's at the end)
        mean_pos = len(bms)
        xx = [x[spec_start] - 0.5, x[mean_pos] - 0.7]
        print(f"Dynamic xx: {xx}")
        ax.vlines(xx, ymin=0, ymax=1.02, color="k", linestyle="--", zorder=2, linewidth=0.7)
        ax.fill_between(x=[xx[0], xx[1]], y1=0, y2=1.02, color="k", alpha=0.1, zorder=1, hatch="////")

    fig.tight_layout(pad=0.4)

    handles, labels = ax.get_legend_handles_labels()

    ax.legend(handles, labels, loc='lower left', fontsize=fs - 3, ncols=6, bbox_to_anchor=(0.01, 0),
              labelspacing=0.05, columnspacing=0.7, handletextpad=0.3, borderpad=0.3,
              framealpha=1, edgecolor="k",
              frameon=True)

    fig.savefig(f"{APATH}/opportunity.pdf", dpi=300, bbox_inches='tight', pad_inches=0, facecolor="w")
    print(f"Saved {APATH}/opportunity.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 2: BTB Successors  (btb_successors.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_btb_successors():
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
        "{core}.fetchStats0.fetchRate": "fetchRate",

        "{core}.branchPred.mispredictDueToBTBMiss_0::total": "BTB Misses",
        "{core}.branchPred.mispredicted_0::total": "BPU Misses",
        "{core}.branchPred.mispredictDueToPredictor_0::DirectCond": "CBP Misses",
        "{core}.commit.fetchAccessDepth::0": "Committed inst access (L1I)",
        "{core}.commit.fetchAccessDepth::1": "Committed inst access (L2)",
        "{core}.commit.fetchAccessDepth::2": "Committed inst access (L3)",
        "{core}.commit.fetchAccessDepth::3": "Committed inst access (Mem)",
        "{core}.commit.firstFTfetchAccessDepth::0": "Committed FT access (L1I)",
        "{core}.commit.firstFTfetchAccessDepth::1": "Committed FT access (L2)",
        "{core}.commit.firstFTfetchAccessDepth::2": "Committed FT access (L3)",
        "{core}.commit.firstFTfetchAccessDepth::3": "Committed FT access (Mem)",
        "{core}.commit.numCommittedFTs": "Committed FTs",
        "{core}.bac.fetchTargets": "Created FTs",

        ### BTB
        "{core}.branchPred.l1btbHits": "L1 BTB Hits",
        "{core}.branchPred.l2btbHits": "L2 BTB Hits",
        "{core}.bac.fetchBlockCycles::total": "Fetch Block Cycles",
        "{core}.branchPred.L2Hit": "L2Hit",
        "{core}.branchPred.Succ_L1Hit_Taken": "L1Hit T",
        "{core}.branchPred.Succ_L1Hit_NotTaken": "L1Hit NT",
        "{core}.branchPred.Succ_L2Hit_Taken": "L2Hit T",
        "{core}.branchPred.Succ_L2Hit_NotTaken": "L2Hit NT",
        "{core}.branchPred.Succ_L2Miss": "L2Miss",
        "{core}.branchPred.Succ_NoBtbEntry": "No Entry",
    }

    mpkis = [k.strip(" Misses") for k in stats_keys.values() if "Misses" in k]

    bms = all_bms

    configs = [
        "baseline-single",
    ]

    metrics_plot = [
        ("L2Hit T", "#cc0000", ""),
        ("L2Hit NT", "#cc0000", "...."),
        ("L1Hit T", "#005e8a", ""),
        ("L1Hit NT", "#005e8a", "...."),
        ("L2Miss", "#0f0f0f", ""),
        ("No Entry", "#B4B4B4", ""),
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}

    for cfg in configs:
        data[cfg] = {}
        for bm in bms:
            print(cfg, bm)
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                print(f"Warning: No stats file found for {cfg}/{bm} at {path_pattern}")
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm not in data[cfg][bm]:
                    print(f"Warning: Metric {mm} not found in {cfg}/{bm}")
                else:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]

            ## Compute derived metrics
            data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]
            data[cfg][bm]["CPI"] = data[cfg][bm]["cycles"] / data[cfg][bm]["insts"]
            for mpki in mpkis:
                data[cfg][bm][f"{mpki} MPKI"] = 1000 * data[cfg][bm][f"{mpki} Misses"] / data[cfg][bm]["insts"]
            data[cfg][bm]["Committed FT ration"] = data[cfg][bm]["Committed FTs"] / data[cfg][bm]["Created FTs"]

            cfgref = configs[0]
            data[cfg][bm]["Speedup"] = data[cfg][bm]["IPC"] / data[cfgref][bm]["IPC"]

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 7.5
    fs = 13
    NG = 1
    fig, ax = mlp.subplots(1, NG, figsize=(NG * cw, cw * 0.2), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    cfg = configs[0]
    vals = {}

    # Filter bms to only those that have data in ALL configs
    valid_bms = []
    for bm in bms:
        if all(bm in data[cfg] for cfg in configs):
            valid_bms.append(bm)
    
    bms = valid_bms

    ref = [data[cfg][bm]["L2Hit"] for bm in bms]
    ref = np.array(ref + [np.mean(ref)])

    for i, (m, color, pattern) in enumerate(metrics_plot):
        y = [data[cfg][bm][m] for bm in bms]
        y += [np.mean(y)]
        y = np.array(y)
        y = y / ref

        ax.bar(x=x, height=y, width=0.8, label=m, bottom=bottoms, zorder=3, color=color, edgecolor="k", hatch=pattern)
        bottoms += np.array(y)

    print(y)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_ylabel("Predecessor of\nL1 BTB misses", fontsize=fs - 2)

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=0)

    _labels = [renameBms(bm) for bm in bms] + ["Mean"]
    _labels = [""] * (len(bms) + 1)
    ax.set_xticklabels(_labels, rotation=35, horizontalalignment="center", fontsize=fs - 4)

    ax.set_xlim(xmin=-0.7, xmax=max(x) + 0.7)

    ax.set_xlabel("Benchmarks")

    fig.tight_layout()

    handles, labels = ax.get_legend_handles_labels()
    handles = [h for h in handles if "NT" not in h.get_label()]
    labels = [l.strip(" T") for l in labels if "NT" not in l]
    handles, labels = handles[::-1], labels[::-1]

    handles += [mpatches.Patch(facecolor="w", edgecolor="k", hatch=""), mpatches.Patch(facecolor="w", edgecolor="k", hatch="....")]
    labels += ["Taken", "Not Taken"]

    ax.legend(handles, labels, loc='lower center', fontsize=fs - 4, ncols=6, bbox_to_anchor=(0.5, 0.93),
              labelspacing=0.05, columnspacing=0.7, handletextpad=0.2, borderpad=0.2,
              framealpha=1, edgecolor="k",
              frameon=True)

    fig.savefig(f"{APATH}/btb_successors.pdf", dpi=300, bbox_inches='tight', pad_inches=0, facecolor="w")
    print(f"Saved {APATH}/btb_successors.pdf")


def plot_cycleCovered():
    stats_keys = {
        "{core}.branchPred.btb.latePrefetchByL2Hit::1": "partialCoveredByL21",
        "{core}.branchPred.btb.latePrefetchByPBHit::1": "partialCoveredByPBHit1",
        "{core}.branchPred.btb.latePrefetchByL2Hit::2": "partialCoveredByL22",
        "{core}.branchPred.btb.latePrefetchByPBHit::2": "partialCoveredByPBHit2",
        "{core}.branchPred.btb.latePrefetchByL2Hit::4": "fullCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::4": "fullCoveredByPBHit",
    }

    bms = all_bms

    configs = [
        ("32pb-8sz-dep14", "BTB-Ferret"),
    ]

    metrics_plot = [
        ("1 Cycle", "#deebf7", ""),
        ("2 Cycles", "#9ecae1", ""),
        ("3 Cycles", "#3182bd", ""),
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}

    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            ## Compute segments
            data[cfg][bm]["1 Cycle"] = data[cfg][bm]["partialCoveredByL21"] + data[cfg][bm]["partialCoveredByPBHit1"]
            data[cfg][bm]["2 Cycles"] = data[cfg][bm]["partialCoveredByL22"] + data[cfg][bm]["partialCoveredByPBHit2"]
            data[cfg][bm]["3 Cycles"] = data[cfg][bm]["fullCoveredByL2"] + data[cfg][bm]["fullCoveredByPBHit"]

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 14.0
    fs = 24
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.26))
    fig.patch.set_facecolor('white')

    cfg, cfgn = configs[0]
    
    # Filter bms to only those that have data
    valid_bms = [bm for bm in bms if bm in data[cfg]]
    bms = valid_bms

    # Setup the x locations
    _labels_bms = [renameBms(bm) for bm in bms] + ["Mean"]
    x = np.arange(len(bms) + 1, dtype=float)
    x[-1] = x[-1] + 0.4 # Offset for mean
    x = np.array([xi + 0.2 if "5" in l else xi for xi, l in zip(x, _labels_bms)])
    
    bottoms = np.zeros(len(bms) + 1)

    cc = {}
    for i, (m, color, pattern) in enumerate(metrics_plot):
        y = [data[cfg][bm][m] for bm in bms]
        y_mean = np.mean(y)
        
        # Calculate group means
        server_y = [data[cfg][bm][m] for bm in bms if not bm.startswith("5")]
        spec_y = [data[cfg][bm][m] for bm in bms if bm.startswith("5")]

        y_plot = np.array(y + [y_mean])
        
        # Calculate reference (sum of all segments) for normalization
        ref = np.zeros(len(bms) + 1)
        ref_server = 0
        ref_spec = 0
        for m_all, _, _ in metrics_plot:
            vals = [data[cfg][bm][m_all] for bm in bms]
            ref += np.array(vals + [np.mean(vals)])
            ref_server += np.mean([data[cfg][bm][m_all] for bm in bms if not bm.startswith("5")]) if server_y else 0
            ref_spec += np.mean([data[cfg][bm][m_all] for bm in bms if bm.startswith("5")]) if spec_y else 0
            
        # Avoid division by zero
        y_norm = np.divide(y_plot, ref, out=np.zeros_like(y_plot), where=ref!=0)

        ax.bar(x=x, height=y_norm, width=0.8, label=m, bottom=bottoms, zorder=3, color=color, edgecolor="k", hatch=pattern)
        bottoms += y_norm

        # Store for printing
        cc[m] = {renameBms(bm): v / r if r != 0 else 0 for bm, v, r in zip(bms, y, ref[:-1])}
        cc[m]["Mean"] = y_mean / ref[-1] if ref[-1] != 0 else 0
        cc[m]["Server Mean"] = (np.mean(server_y) / ref_server) if (server_y and ref_server != 0) else np.nan
        cc[m]["SPEC Mean"] = (np.mean(spec_y) / ref_spec) if (spec_y and ref_spec != 0) else np.nan

    ## Grid
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax.grid(True, which='major', axis='y', linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)

    ax.set_ylabel("Ratio", fontsize=fs)
    ax.tick_params(axis='y', labelsize=fs - 2)

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=-2, length=0.1)
    ax.set_xticklabels([])

    ax.set_xlim(xmin=-0.7, xmax=max(x) + 0.7)
    
    top = 1.0
    ax.set_ylim(bottom=0, top=top)

    # Shading and category labels (matching plot_Coverage)
    nspec = sum([1 for b in bms if "5" in b])
    xx = [len(bms)-nspec-1+0.6, len(bms)-1+0.8]
    
    ax.vlines(xx, ymin=-10, ymax=top, color="k", linestyle="--", zorder=2, linewidth=0.7, alpha=0.3)
    ax.fill_between(x=[xx[0], xx[1]], y1=0, y2=top, color="k", alpha=0.1, zorder=1, hatch="////")

    ax.text(xx[0]/2, 0-top*0.05, "Server", size=fs-1, rotation=0.,
             ha="center", va="top")
    ax.text(xx[0]+(xx[1]-xx[0])/2, 0-top*0.05, "SPEC", size=fs-1, rotation=0.,
             ha="center", va="top")
    ax.text(x[-1], 0-top*0.05, "Mean", size=fs-1, rotation=0.,
             ha="center", va="top")

    fig.tight_layout()

    ax.legend(loc='upper center', fontsize=fs - 5, ncols=3, bbox_to_anchor=(0.5, 0.98),
               labelspacing=0.05, columnspacing=0.8, handletextpad=0.3, borderpad=0.3,
               framealpha=0.8, edgecolor="k", frameon=True)

    fig.savefig(f"{APATH}/cycleCovered.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/cycleCovered.pdf")

    # Print data
    print("\n" + "="*80)
    print(f"{'Benchmark':<25}", end="")
    for m, _, _ in metrics_plot:
        print(f"{m:>15}", end="")
    print("\n" + "-"*80)
    
    print_labels = [renameBms(bm) for bm in bms] + ["Server Mean", "SPEC Mean", "Mean"]
    for label in print_labels:
        print(f"{label:<25}", end="")
        for m, _, _ in metrics_plot:
            val = cc[m].get(label, np.nan)
            print(f"{val:>15.4f}", end="")
        print()
    print("="*80 + "\n")


def plot_endReason():
    stats_keys = {
        "{core}.branchPred.btb.chainEndDepthExhaust": "Chain Exhaust",
        "{core}.branchPred.btb.chainEndRetFilter": "Return",
        "{core}.branchPred.btb.chainEndL2Miss": "L2 Miss",
        "{core}.branchPred.btb.chainEndPresence": "L1/PB Presence",
        "{core}.branchPred.btb.chainEndDemand": "Demand Access",
        "{core}.branchPred.btb.chainEndEvicted": "Evicted",
        "{core}.branchPred.btb.chainEndNonEntry": "Non Entry",
    }

    metrics_plot = [
        ("Chain Exhaust", "#2ecc71", ""),
        ("Return", "#3498db", ""),
        ("L2 Miss", "#9b59b6", ""),
        ("L1/PB Presence", "#f1c40f", ""),
        ("Demand Access", "#e67e22", ""),
        ("Evicted", "#e74c3c", ""),
        ("Non Entry", "#7f8c8d", ""),
    ]

    bms = all_bms

    configs = [
        ("8sz-14", "8sz-14"),
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}

    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 10.0
    fs = 15
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.35))
    fig.patch.set_facecolor('white')

    cfg, cfgn = configs[0]
    
    # Filter bms to only those that have data
    valid_bms = [bm for bm in bms if bm in data[cfg]]
    bms = valid_bms

    # Setup the x locations
    _labels_bms = [renameBms(bm) for bm in bms] + ["Mean"]
    x = np.arange(len(bms) + 1, dtype=float)
    x[-1] = x[-1] + 0.4 # Offset for mean
    x = np.array([xi + 0.2 if "5" in l else xi for xi, l in zip(x, _labels_bms)])
    
    bottoms = np.zeros(len(bms) + 1)

    res = {}
    for i, (m, color, pattern) in enumerate(metrics_plot):
        y = [data[cfg][bm][m] for bm in bms]
        y_mean = np.mean(y)
        
        # Calculate group means
        server_y = [data[cfg][bm][m] for bm in bms if not bm.startswith("5")]
        spec_y = [data[cfg][bm][m] for bm in bms if bm.startswith("5")]

        y_plot = np.array(y + [y_mean])
        
        # Calculate reference (sum of all segments) for normalization
        ref = np.zeros(len(bms) + 1)
        ref_server = 0
        ref_spec = 0
        for m_all, _, _ in metrics_plot:
            vals = [data[cfg][bm][m_all] for bm in bms]
            ref += np.array(vals + [np.mean(vals)])
            ref_server += np.mean([data[cfg][bm][m_all] for bm in bms if not bm.startswith("5")]) if server_y else 0
            ref_spec += np.mean([data[cfg][bm][m_all] for bm in bms if bm.startswith("5")]) if spec_y else 0
            
        # Avoid division by zero
        y_norm = np.divide(y_plot, ref, out=np.zeros_like(y_plot), where=ref!=0)

        ax.bar(x=x, height=y_norm, width=0.8, label=m, bottom=bottoms, zorder=3, color=color, edgecolor="k", hatch=pattern)
        bottoms += y_norm

        # Store for printing
        res[m] = {renameBms(bm): v / r if r != 0 else 0 for bm, v, r in zip(bms, y, ref[:-1])}
        res[m]["Mean"] = y_mean / ref[-1] if ref[-1] != 0 else 0
        res[m]["Server Mean"] = (np.mean(server_y) / ref_server) if (server_y and ref_server != 0) else np.nan
        res[m]["SPEC Mean"] = (np.mean(spec_y) / ref_spec) if (spec_y and ref_spec != 0) else np.nan

    ## Grid
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.grid(True, which='major', axis='y', linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)

    ax.set_ylabel("Termination Reason Ratio", fontsize=fs)
    ax.tick_params(axis='y', labelsize=fs - 2)

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=0, length=0.1)
    ax.set_xticklabels([renameBms(bm) for bm in bms] + ["Mean"], rotation=45, ha="right", fontsize=fs - 4)

    ax.set_xlim(xmin=-0.7, xmax=max(x) + 0.7)
    
    top = 1.0
    ax.set_ylim(bottom=0, top=top)

    # Shading and category labels
    nspec = sum([1 for b in bms if "5" in b])
    xx = [len(bms)-nspec-1+0.6, len(bms)-1+0.8]
    
    ax.vlines(xx, ymin=-10, ymax=top, color="k", linestyle="--", zorder=2, linewidth=0.7, alpha=0.3)
    ax.fill_between(x=[xx[0], xx[1]], y1=0, y2=top, color="k", alpha=0.1, zorder=1, hatch="////")

    ax.text(xx[0]/2, 1.02, "Server", size=fs-1, rotation=0.,
             ha="center", va="bottom")
    ax.text(xx[0]+(xx[1]-xx[0])/2, 1.02, "SPEC", size=fs-1, rotation=0.,
             ha="center", va="bottom")

    fig.tight_layout()

    fig.subplots_adjust(top=0.78)

    ax.legend(loc='lower center', fontsize=fs - 4, ncols=4, bbox_to_anchor=(0.5, 1.12),
               labelspacing=0.2, columnspacing=0.8, handletextpad=0.3, borderpad=0.3,
               framealpha=0.8, edgecolor="k", frameon=True)

    fig.savefig(f"{APATH}/endReason.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/endReason.pdf")

    # Print data
    print("\n" + "="*110)
    print(f"{'Benchmark':<25}", end="")
    for m, _, _ in metrics_plot:
        print(f"{m:>13}", end="")
    print("\n" + "-"*110)
    
    print_labels = [renameBms(bm) for bm in bms] + ["Server Mean", "SPEC Mean", "Mean"]
    for label in print_labels:
        print(f"{label:<25}", end="")
        for m, _, _ in metrics_plot:
            val = res[m].get(label, np.nan)
            print(f"{val:>13.4f}", end="")
        print()
    print("="*110 + "\n")


def plot_committedBTBHit():
    stats_keys = {
        "{core}.commit.committedInst": "insts",
        "{core}.branchPred.l2btbHits": "l2Hit",
        "{core}.branchPred.l3btbHits": "l3Hit",
        "{core}.branchPred.mispredictDueToBTBMiss_0::total": "Miss",
    }

    metrics_plot = [
        ("l2Hit", "#3498db", ""),
        ("l3Hit", "#9b59b6", ""),
        ("Miss", "#e74c3c", ""),
    ]

    bms = all_bms
    configs = [
        ("baseline-3level", "3level Baseline"),
        # ("baseline", "2level Baseline"),
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            # Convert each committed BTB component into MPKI (per 1K committed instructions).
            insts = data[cfg][bm].get("insts", 0)
            for m, _, _ in metrics_plot:
                count_val = data[cfg][bm].get(m, 0)
                data[cfg][bm][f"{m} MPKI"] = (1000.0 * count_val / insts) if insts > 0 else 0.0

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 10.0
    fs = 15
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.35))
    fig.patch.set_facecolor('white')

    cfg, cfgn = configs[0]

    valid_bms = [bm for bm in bms if bm in data[cfg]]
    bms = valid_bms

    _labels_bms = [renameBms(bm) for bm in bms] + ["Mean"]
    x = np.arange(len(bms) + 1, dtype=float)
    x[-1] = x[-1] + 0.4
    x = np.array([xi + 0.2 if "5" in l else xi for xi, l in zip(x, _labels_bms)])

    bottoms = np.zeros(len(bms) + 1)

    # Only keep segments that have at least one non-zero value.
    active_metrics_plot = []
    for m, color, pattern in metrics_plot:
        vals = [data[cfg][bm][f"{m} MPKI"] for bm in bms]
        if np.any(np.array(vals) > 0):
            active_metrics_plot.append((m, color, pattern))

    res = {}
    global_max = 0.0
    for i, (m, color, pattern) in enumerate(active_metrics_plot):
        y = [data[cfg][bm][f"{m} MPKI"] for bm in bms]
        y_mean = np.mean(y)

        server_y = [data[cfg][bm][f"{m} MPKI"] for bm in bms if not bm.startswith("5")]
        spec_y = [data[cfg][bm][f"{m} MPKI"] for bm in bms if bm.startswith("5")]

        y_plot = np.array(y + [y_mean])
        ax.bar(x=x, height=y_plot, width=0.8, label=m, bottom=bottoms, zorder=3,
               color=color, edgecolor="k", hatch=pattern)
        bottoms += y_plot
        global_max = max(global_max, np.max(bottoms))

        res[m] = {renameBms(bm): v for bm, v in zip(bms, y)}
        res[m]["Mean"] = y_mean
        res[m]["Server Mean"] = np.mean(server_y) if server_y else np.nan
        res[m]["SPEC Mean"] = np.mean(spec_y) if spec_y else np.nan

    ## Grid
    ax.grid(True, which='major', axis='y', linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)

    ax.set_ylabel("Committed BTB MPKI", fontsize=fs)
    ax.tick_params(axis='y', labelsize=fs - 2)

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=0, length=0.1)
    ax.set_xticklabels([renameBms(bm) for bm in bms] + ["Mean"], rotation=45, ha="right", fontsize=fs - 4)

    ax.set_xlim(xmin=-0.7, xmax=max(x) + 0.7)
    top = global_max * 1.05 if global_max > 0 else 1.0
    ax.set_ylim(bottom=0, top=top)

    nspec = sum([1 for b in bms if "5" in b])
    xx = [len(bms) - nspec - 1 + 0.6, len(bms) - 1 + 0.8]

    ax.vlines(xx, ymin=-10, ymax=top, color="k", linestyle="--", zorder=2, linewidth=0.7, alpha=0.3)
    ax.fill_between(x=[xx[0], xx[1]], y1=0, y2=top, color="k", alpha=0.1, zorder=1, hatch="////")

    # ax.text(xx[0] / 2, 1.02, "Server", size=fs - 1, rotation=0., ha="center", va="bottom")
    # ax.text(xx[0] + (xx[1] - xx[0]) / 2, 1.02, "SPEC", size=fs - 1, rotation=0., ha="center", va="bottom")

    fig.tight_layout()
    fig.subplots_adjust(top=0.78)

    if active_metrics_plot:
        ax.legend(loc='lower center', fontsize=fs - 4, ncols=4, bbox_to_anchor=(0.5, 1.12),
                  labelspacing=0.2, columnspacing=0.8, handletextpad=0.3, borderpad=0.3,
                  framealpha=0.8, edgecolor="k", frameon=True)

    fig.savefig(f"{APATH}/committedBTBHit.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/committedBTBHit.pdf")

    # Print data
    print("\n" + "=" * 90)
    print(f"{'Benchmark':<25}", end="")
    for m, _, _ in active_metrics_plot:
        print(f"{m:>13}", end="")
    print("\n" + "-" * 90)

    print_labels = [renameBms(bm) for bm in bms] + ["Server Mean", "SPEC Mean", "Mean"]
    for label in print_labels:
        print(f"{label:<25}", end="")
        for m, _, _ in active_metrics_plot:
            val = res[m].get(label, np.nan)
            print(f"{val:>13.4f}", end="")
        print()
    print("=" * 90 + "\n")


def plot_accessNum():
    stats_keys = {
        "{core}.bac.fetchTargets": "fetchTargets",
        "{core}.fetch.ftqStallCycles": "ftqStallCycles",
        "{core}.branchPred.btb.l1Hits": "l1Hits",
        "{core}.branchPred.btb.l1HitInOverriding": "l1HitInOverriding",
        "{core}.branchPred.l1btbHitBpLatency": "l1btbHitBpLatency",
        "{core}.branchPred.btb.l1MissInOverriding": "l1MissInOverriding",
        "{core}.branchPred.btb.totalPrefetches": "totalPrefetches",
        "{core}.branchPred.btb.uselessPrefetches::total": "uselessPrefetches",
        "{core}.branchPred.btb.l1Accesses": "l1Accesses",
        "{core}.branchPred.btb.l2Accesses": "l2Accesses",
    }

    bms = all_bms
    configs = [
        ("power-baseline", "Baseline"),
        ("power-ferret", "BTB-Ferret"),
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    for (cfg, _) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            for metric, alias in stats_keys.items():
                mm = resolve_metric(metric, bm)
                data[cfg][bm][alias] = data[cfg][bm].get(mm, 0.0)

    # Keep only benchmarks with both bars available.
    bms = [bm for bm in bms if all(bm in data[cfg] for cfg, _ in configs)]

    # ── Compute stacked segments ─────────────────────────────────────────────
    bar_segments = {
        "power-baseline": {},
        "power-ferret": {},
    }
    for bm in bms:
        # Baseline
        # b_fetchTargets = data["power-baseline"][bm]["fetchTargets"]
        # b_overriding = data["power-baseline"][bm]["l1HitInOverriding"] 
        # b_l1btbHitBpLatency = data["power-baseline"][bm]["l1btbHitBpLatency"]
        # # b_l1_hits = data["power-baseline"][bm]["l1Hits"] - b_l1btbHitBpLatency
        # b_l1_hits = data["power-baseline"][bm]["ftqStallCycles"]
        
        # # b_l1 = b_fetchTargets
        # b_l1 = b_l1_hits
        # b_l2 = b_fetchTargets - b_l1_hits - b_overriding
        
        b_l1 = data["power-baseline"][bm]["l1Accesses"]
        b_l2 = data["power-baseline"][bm]["l2Accesses"]
        bar_segments["power-baseline"][bm] = {
            "L1 accesses": b_l1,
            "L2 accesses": b_l2,
        }

        # BTB-Ferret
        # f_fetchTargets = data["power-ferret"][bm]["fetchTargets"]
        # # f_overriding = data["power-ferret"][bm]["l1HitInOverriding"] + data["power-ferret"][bm]["l1MissInOverriding"]
        # f_overriding = data["power-ferret"][bm]["l1HitInOverriding"] 
        # f_l1btbHitBpLatency = data["power-ferret"][bm]["l1btbHitBpLatency"]
        # # f_l1_hits = data["power-ferret"][bm]["l1Hits"] - f_l1btbHitBpLatency
        # f_l1_hits = data["power-ferret"][bm]["ftqStallCycles"]
        # f_total_prefetches = data["power-ferret"][bm]["totalPrefetches"]
        # f_useless_prefetches = data["power-ferret"][bm]["uselessPrefetches"]
        # # f_l1 = f_fetchTargets
        # f_l1 = f_l1_hits
        # f_pb = f_l1
        # f_l2 = f_fetchTargets - f_l1_hits + f_useless_prefetches - f_overriding
        f_l1 = data["power-ferret"][bm]["l1Accesses"]
        f_pb = f_l1
        f_l2 = data["power-ferret"][bm]["l2Accesses"]
        bar_segments["power-ferret"][bm] = {
            "L1 accesses": f_l1,
            "PB accesses": f_pb,
            "L2 accesses": f_l2,
        }

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 10.0
    fs = 15
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.35))
    fig.patch.set_facecolor('white')

    labels = [renameBms(bm) for bm in bms] + ["Mean"]
    x = np.arange(len(bms) + 1, dtype=float)
    x[-1] = x[-1] + 0.4
    x = np.array([xi + 0.2 if "5" in l else xi for xi, l in zip(x, labels)])

    width = 0.36
    offsets = {
        "power-baseline": -width / 2,
        "power-ferret": width / 2,
    }
    cfg_hatch = {
        "power-baseline": "///",
        "power-ferret": "\\\\\\",
    }
    segment_colors = {
        "L1 accesses": "#3498db",
        "PB accesses": "#f39c12",
        "L2 accesses": "#e74c3c",
    }
    segment_order = ["L1 accesses", "PB accesses", "L2 accesses"]

    # Draw one stacked bar per config for each benchmark (+mean).
    global_max = 0.0
    for cfg, cfgn in configs:
        bottoms = np.zeros(len(bms) + 1)
        for seg in segment_order:
            vals = [bar_segments[cfg][bm].get(seg, 0.0) for bm in bms]
            seg_mean = np.mean(vals) if vals else 0.0
            y_plot = np.array(vals + [seg_mean])

            if np.any(y_plot != 0):
                ax.bar(
                    x=x + offsets[cfg],
                    height=y_plot,
                    width=width,
                    bottom=bottoms,
                    zorder=3,
                    color=segment_colors[seg],
                    edgecolor="k",
                    hatch=cfg_hatch[cfg],
                    label=f"{cfgn} - {seg}",
                )
            bottoms += y_plot
        global_max = max(global_max, np.max(bottoms))

    # Grid and axes
    ax.grid(True, which='major', axis='y', linestyle='-', alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_ylabel("Access Number", fontsize=fs)
    ax.tick_params(axis='y', labelsize=fs - 2)

    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=0, length=0.1)
    ax.set_xticklabels([renameBms(bm) for bm in bms] + ["Mean"], rotation=45, ha="right", fontsize=fs - 4)

    ax.set_xlim(xmin=-0.7, xmax=max(x) + 0.7)
    top = global_max * 1.05 if global_max > 0 else 1.0
    ax.set_ylim(bottom=0, top=top)

    nspec = sum([1 for b in bms if "5" in b])
    xx = [len(bms) - nspec - 1 + 0.6, len(bms) - 1 + 0.8]
    ax.vlines(xx, ymin=-10, ymax=top, color="k", linestyle="--", zorder=2, linewidth=0.7, alpha=0.3)
    ax.fill_between(x=[xx[0], xx[1]], y1=0, y2=top, color="k", alpha=0.1, zorder=1, hatch="////")

    fig.tight_layout()
    fig.subplots_adjust(top=0.78)

    # Legend: use patches to avoid duplicate labels.
    legend_handles = [
        mpatches.Patch(facecolor=segment_colors["L1 accesses"], edgecolor="k", label="L1 accesses"),
        mpatches.Patch(facecolor=segment_colors["PB accesses"], edgecolor="k", label="PB accesses"),
        mpatches.Patch(facecolor=segment_colors["L2 accesses"], edgecolor="k", label="L2 accesses"),
        mpatches.Patch(facecolor="white", edgecolor="k", hatch=cfg_hatch["power-baseline"], label="Baseline"),
        mpatches.Patch(facecolor="white", edgecolor="k", hatch=cfg_hatch["power-ferret"], label="BTB-Ferret"),
    ]
    ax.legend(
        handles=legend_handles,
        loc='lower center',
        fontsize=fs - 4,
        ncols=5,
        bbox_to_anchor=(0.5, 1.12),
        labelspacing=0.2,
        columnspacing=0.8,
        handletextpad=0.3,
        borderpad=0.3,
        framealpha=0.8,
        edgecolor="k",
        frameon=True,
    )

    fig.savefig(f"{APATH}/accessNum.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/accessNum.pdf")

    # Print each benchmark's two bars and all their segments.
    print("\n" + "=" * 140)
    print(
        f"{'Benchmark':<25}"
        f"{'Baseline L1':>18}{'Baseline L2':>18}"
        f"{'Ferret L1':>18}{'Ferret PB':>18}{'Ferret L2':>18}"
    )
    print("-" * 140)

    for bm in bms:
        b_seg = bar_segments["power-baseline"][bm]
        f_seg = bar_segments["power-ferret"][bm]
        print(
            f"{renameBms(bm):<25}"
            f"{b_seg['L1 accesses']:>18.0f}{b_seg['L2 accesses']:>18.0f}"
            f"{f_seg['L1 accesses']:>18.0f}{f_seg['PB accesses']:>18.0f}{f_seg['L2 accesses']:>18.0f}"
        )

    # Also print means for quick comparison.
    b_l1_mean = np.mean([bar_segments["power-baseline"][bm]["L1 accesses"] for bm in bms]) if bms else np.nan
    b_l2_mean = np.mean([bar_segments["power-baseline"][bm]["L2 accesses"] for bm in bms]) if bms else np.nan
    f_l1_mean = np.mean([bar_segments["power-ferret"][bm]["L1 accesses"] for bm in bms]) if bms else np.nan
    f_pb_mean = np.mean([bar_segments["power-ferret"][bm]["PB accesses"] for bm in bms]) if bms else np.nan
    f_l2_mean = np.mean([bar_segments["power-ferret"][bm]["L2 accesses"] for bm in bms]) if bms else np.nan
    print("-" * 140)
    print(
        f"{'Mean':<25}"
        f"{b_l1_mean:>18.2f}{b_l2_mean:>18.2f}"
        f"{f_l1_mean:>18.2f}{f_pb_mean:>18.2f}{f_l2_mean:>18.2f}"
    )
    print("=" * 140 + "\n")


def plot_stackedBar(
    configs=None,
    bms=None,
    filename="stackedBar_bac_status.pdf",
    metrics=None,
    segments=None,
):
    """
    Plot two stacked bars per benchmark (one bar per config).

    metrics can be:
      - dict: {"{core}.metric.name": "Segment Label", ...}
      - list of (metric, label) tuples
      - list of metric strings, using the metric suffix as the segment label

    Up to six metrics/segments are supported. If metrics is not provided, the
    plot defaults to the four BAC status metrics. segments is kept as a shortcut
    for BAC status names, e.g. segments=["Running", "FTQFull"].
    """
    if configs is None:
        configs = [
            ("power-baseline-breakdown", "Baseline"),
            ("power-ferret-breakdown", "BTB-Ferret"),
        ]
    if bms is None:
        bms = all_bms
    if len(configs) != 2:
        raise ValueError("plot_stackedBar currently expects exactly 2 configs")

    def metric_label(metric):
        if "::" in metric:
            return metric.rsplit("::", 1)[1]
        return metric.rsplit(".", 1)[-1]

    if metrics is not None and segments is not None:
        raise ValueError("plot_stackedBar expects either metrics or segments, not both")
    if metrics is None:
        if segments is None:
            segments = ["Running", "Squashing", "Overriding", "FTQFull"]
        metrics = [(f"{{core}}.bac.status::{seg}", seg) for seg in segments]
    elif isinstance(metrics, dict):
        metrics = list(metrics.items())
    else:
        metrics = [
            (metric, metric_label(metric)) if isinstance(metric, str) else metric
            for metric in metrics
        ]

    if not 1 <= len(metrics) <= 6:
        raise ValueError("plot_stackedBar supports between 1 and 6 segments")

    stats_keys = dict(metrics)
    segment_order = list(stats_keys.values())
    if len(set(segment_order)) != len(segment_order):
        raise ValueError("plot_stackedBar segment labels must be unique")
    color_palette = [
        "#4c78a8",
        "#f58518",
        "#54a24b",
        "#e45756",
        "#72b7b2",
        "#b279a2",
    ]
    segment_colors = {
        seg: color_palette[idx] for idx, seg in enumerate(segment_order)
    }

    # Load stats for all available benchmark/config pairs.
    data = {}
    for cfg, _ in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            stat = read_stats(stats_files[0])
            for metric, alias in stats_keys.items():
                mm = resolve_metric(metric, bm)
                stat[alias] = stat.get(mm, 0.0)
            data[cfg][bm] = stat

    # Keep benchmarks that exist in all configs.
    valid_bms = [bm for bm in bms if all(bm in data[cfg] for cfg, _ in configs)]
    if not valid_bms:
        print("No common benchmarks found across all configs for plot_stackedBar().")
        return

    # Per-benchmark segments for each config.
    bar_segments = {cfg: {} for cfg, _ in configs}
    for cfg, _ in configs:
        for bm in valid_bms:
            bar_segments[cfg][bm] = {
                seg: float(data[cfg][bm][seg]) for seg in segment_order
            }
        bar_segments[cfg]["__MEAN__"] = {
            seg: float(np.mean([bar_segments[cfg][bm][seg] for bm in valid_bms])) for seg in segment_order
        }

    # Plot.
    cw = 12.0
    fs = 14
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.33))
    fig.patch.set_facecolor("white")

    plot_bms = valid_bms + ["__MEAN__"]
    labels = [renameBms(bm) for bm in valid_bms] + ["Mean"]
    x = np.arange(len(plot_bms), dtype=float)
    x[-1] = x[-1] + 0.4
    x = np.array([xi + 0.2 if "5" in l else xi for xi, l in zip(x, labels)])
    width = 0.36
    offsets = {
        configs[0][0]: -width / 2,
        configs[1][0]: width / 2,
    }
    cfg_hatch = {
        configs[0][0]: "///",
        configs[1][0]: "\\\\\\",
    }

    global_max = 0.0
    for cfg_idx, (cfg, _) in enumerate(configs):
        bottoms = np.zeros(len(plot_bms), dtype=float)
        for seg in segment_order:
            heights = np.array([bar_segments[cfg][bm][seg] for bm in plot_bms], dtype=float)
            ax.bar(
                x=x + offsets[cfg],
                height=heights,
                width=width,
                bottom=bottoms,
                color=segment_colors[seg],
                edgecolor="k",
                linewidth=0.7,
                hatch=cfg_hatch[cfg],
                zorder=3,
                label=seg if cfg_idx == 0 else None,
            )
            bottoms += heights
        global_max = max(global_max, float(np.max(bottoms)))

    ax.grid(True, which="major", axis="y", linestyle="-", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=fs - 4)
    ax.set_xlim(xmin=-0.7, xmax=max(x) + 0.7 if len(x) else 1.0)
    ax.set_ylabel("Count", fontsize=fs)
    ax.tick_params(axis="y", labelsize=fs - 1)
    ax.set_ylim(bottom=0, top=(global_max * 1.08 if global_max > 0 else 1.0))

    legend_handles = [
        mpatches.Patch(facecolor=segment_colors[seg], edgecolor="k", label=seg)
        for seg in segment_order
    ] + [
        mpatches.Patch(
            facecolor="white",
            edgecolor="k",
            hatch=cfg_hatch[configs[0][0]],
            label=configs[0][1],
        ),
        mpatches.Patch(
            facecolor="white",
            edgecolor="k",
            hatch=cfg_hatch[configs[1][0]],
            label=configs[1][1],
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center",
        fontsize=fs - 4,
        ncols=len(legend_handles),
        bbox_to_anchor=(0.5, 1.02),
        framealpha=0.85,
        edgecolor="k",
        frameon=True,
    )

    fig.tight_layout()
    fig.savefig(f"{APATH}/{filename}", dpi=300, bbox_inches="tight", pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/{filename}")

    # Text dump for quick checking.
    print("\n" + "=" * 140)
    print(
        f"{'Benchmark':<26}{'Config':<14}"
        + "".join(f"{seg:>14}" for seg in segment_order)
        + f"{'Total':>14}"
    )
    print("-" * 140)
    for bm in plot_bms:
        first = True
        for cfg, cfgn in configs:
            segs = bar_segments[cfg][bm]
            total = sum(segs[s] for s in segment_order)
            bm_label = ("Mean" if bm == "__MEAN__" else renameBms(bm)) if first else ""
            first = False
            print(
                f"{bm_label:<26}{cfgn:<14}"
                + "".join(f"{segs[seg]:>14.0f}" for seg in segment_order)
                + f"{total:>14.0f}"
            )
    print("=" * 140)
    print(f"Benchmarks used ({len(valid_bms)}): {', '.join(renameBms(bm) for bm in valid_bms)}\n")


def plot_horizontalStackedBar(
    configs=None,   
    bms=None,
    filename="L1_L2 accesses.pdf",
):
    """
    Plot mean-only horizontal stacked bars with fixed metric composition.

    For each config, draw two bars:
      - L1 accesses
      - L2 accesses
    Mean is computed across benchmarks common to all configs.
    """
    if configs is None:
        configs = [
            ("power-baseline", "Baseline"),
            ("power-ferret", "BTB-Ferret"),
        ]
    if bms is None:
        bms = all_bms
    if len(configs) < 1:
        raise ValueError("plot_horizontalStackedBar expects at least 1 config")

    # Fixed raw metrics.
    m_btb_miss = "{core}.branchPred.btb.l2AccessesByReason::BTBMiss"
    m_non_entry = "{core}.branchPred.btb.l2AccessesByReason::NonEntry"
    m_override_l1_miss = "{core}.branchPred.btb.l2AccessesByReason::OverrideL1Miss"
    m_normal_l2_hit = "{core}.branchPred.btb.l2AccessesByReason::NormalL2Hit"
    m_l1_hit_in_overriding = "{core}.branchPred.btb.l1HitInOverriding"
    m_prefetch = "{core}.branchPred.btb.l2AccessesByReason::Prefetch"
    m_l1_hits = "{core}.branchPred.btb.l1Hits"
    m_l1btb_hit_bp_latency = "{core}.branchPred.l1btbHitBpLatency"
    m_normalL1Hits = "{core}.branchPred.btb.normalL1Hits"
    m_skip_due_to_presence = "{core}.branchPred.btb.skipDuetoPresence"

    # Segment definitions as requested.
    l1_segment_order = [
        "NonEntry",
        "Override",
        "Normal",
    ]
    l2_segment_order = [
        "NonEntry",
        "Override",
        "Normal",
        "Prefetch",
    ]
    all_segment_order = [
        "NonEntry",
        "Override",
        "Normal",
        "Prefetch",
    ]
    color_palette = [
        "#4c78a8",
        "#f58518",
        "#54a24b",
        "#e45756",
        "#72b7b2",
        "#b279a2",
    ]
    segment_colors = {seg: color_palette[idx] for idx, seg in enumerate(all_segment_order)}
    segment_colors["Prefetch"] = "#9ecbff"

    # Load stats for all available benchmark/config pairs.
    data = {}
    for cfg, _ in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            stat = read_stats(stats_files[0])
            data[cfg][bm] = stat

    # Keep benchmarks that exist in all configs.
    valid_bms = [bm for bm in bms if all(bm in data[cfg] for cfg, _ in configs)]
    if not valid_bms:
        print("No common benchmarks found across all configs for plot_horizontalStackedBar().")
        return

    # Per-benchmark segment values for each config and each bar type.
    bar_segments = {cfg: {"L1 accesses": {}, "L2 accesses": {}} for cfg, _ in configs}
    prefetch_with_skip = {cfg: {} for cfg, _ in configs}
    for cfg, _ in configs:
        for bm in valid_bms:
            stat = data[cfg][bm]

            def gv(metric):
                return float(stat.get(resolve_metric(metric, bm), 0.0))

            btb_non_entry = gv(m_btb_miss) + gv(m_non_entry)
            override_l1_miss = gv(m_override_l1_miss)
            normal_l2_hit = gv(m_normal_l2_hit)
            l1_hit_overriding = gv(m_l1_hit_in_overriding)
            prefetch = gv(m_prefetch)
            skip_due_to_presence = gv(m_skip_due_to_presence)
            # l1_hits_no_bp_latency = gv(m_l1_hits) - gv(m_l1btb_hit_bp_latency)
            l1_hits_no_bp_latency = gv(m_normalL1Hits) - gv(m_l1_hit_in_overriding)
            prefetch_with_skip[cfg][bm] = prefetch + skip_due_to_presence

            bar_segments[cfg]["L1 accesses"][bm] = {
                "NonEntry": btb_non_entry,
                "Override": override_l1_miss + l1_hit_overriding,
                "Normal": normal_l2_hit + l1_hits_no_bp_latency,
            }
            bar_segments[cfg]["L2 accesses"][bm] = {
                "NonEntry": btb_non_entry,
                # Keep underlying metrics unchanged; only labels are renamed.
                "Override": override_l1_miss,
                "Normal": normal_l2_hit,
                "Prefetch": prefetch,
            }

    # Mean segments for plotting.
    mean_segments = {cfg: {"L1 accesses": {}, "L2 accesses": {}} for cfg, _ in configs}
    for cfg, _ in configs:
        for seg in l1_segment_order:
            mean_segments[cfg]["L1 accesses"][seg] = float(
                np.mean([bar_segments[cfg]["L1 accesses"][bm][seg] for bm in valid_bms])
            )
        for seg in l2_segment_order:
            mean_segments[cfg]["L2 accesses"][seg] = float(
                np.mean([bar_segments[cfg]["L2 accesses"][bm][seg] for bm in valid_bms])
            )
    mean_prefetch_with_skip = {
        cfg: float(np.mean([prefetch_with_skip[cfg][bm] for bm in valid_bms]))
        for cfg, _ in configs
    }

    if len(configs) != 2:
        raise ValueError("plot_horizontalStackedBar currently expects exactly 2 configs (Baseline and Ferret)")

    cw = 10.0
    fs = 16
    fig_h = 2.5
    fig, ax = mlp.subplots(figsize=(cw, fig_h))
    fig.patch.set_facecolor("white")

    group_keys = ["L1 accesses", "L2 accesses"]
    group_labels = ["L1", "L2"]
    group_spacing = 0.2
    group_centers = np.arange(len(group_keys), dtype=float) * group_spacing
    bar_height = 0.075
    # Use exactly half-height offsets so bars in the same group touch each other.
    cfg_offsets = [-bar_height / 2, bar_height / 2]
    # Baseline: no hatch, BTB-Ferret: keep hatch texture.
    cfg_hatch = {cfg: ("" if idx == 0 else "\\\\\\") for idx, (cfg, _) in enumerate(configs)}

    global_max = 0.0
    for group_idx, bar_type in enumerate(group_keys):
        y_center = group_centers[group_idx]
        segment_order = l1_segment_order if bar_type == "L1 accesses" else l2_segment_order
        for cfg_idx, (cfg, _) in enumerate(configs):
            y_pos = y_center + cfg_offsets[cfg_idx]
            left = 0.0
            for seg in segment_order:
                width = float(mean_segments[cfg][bar_type][seg])
                ax.barh(
                    y=y_pos,
                    width=width,
                    height=bar_height,
                    left=left,
                    color=segment_colors[seg],
                    edgecolor="k",
                    linewidth=0.7,
                    hatch=cfg_hatch[cfg],
                    zorder=3,
                )
                left += width
            global_max = max(global_max, left)

    ax.grid(True, which="major", axis="x", linestyle="-", alpha=0.3)
    ax.set_axisbelow(True)
    ax.set_yticks(group_centers)
    ax.set_yticklabels(group_labels, fontsize=fs)
    ax.invert_yaxis()
    ax.margins(y=0.04)
    ax.set_xlabel("Accesses", fontsize=fs)
    ax.tick_params(axis="x", labelsize=fs)
    ax.set_xlim(left=0, right=(global_max * 1.08 if global_max > 0 else 1.0))

    segment_legend_handles = [
        mpatches.Patch(facecolor=segment_colors[seg], edgecolor="k", label=seg)
        for seg in all_segment_order
    ]
    config_legend_handles = [
        mpatches.Patch(facecolor="white", edgecolor="k", hatch=cfg_hatch[cfg], label=cfgn)
        for cfg, cfgn in configs
    ]
    config_legend = ax.legend(
        handles=config_legend_handles,
        loc="lower right",
        fontsize=fs - 4,
        ncols=1,
        bbox_to_anchor=(0.98, 0.04),
        borderaxespad=0.2,
        columnspacing=1.0,
        handlelength=1.4,
        framealpha=0.85,
        edgecolor="k",
        frameon=True,
    )
    ax.add_artist(config_legend)
    ax.legend(
        handles=segment_legend_handles,
        loc="lower center",
        fontsize=fs - 1,
        ncols=len(segment_legend_handles),
        bbox_to_anchor=(0.5, 1.02),
        borderaxespad=0.0,
        columnspacing=1.0,
        handlelength=1.4,
        framealpha=0.85,
        edgecolor="k",
        frameon=True,
    )

    fig.tight_layout()
    fig.savefig(f"{APATH}/{filename}", dpi=300, bbox_inches="tight", pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/{filename}")

    print("\nMean segment values (common benchmarks only):")
    for cfg, cfgn in configs:
        l1_msg = ", ".join([f"{seg}={mean_segments[cfg]['L1 accesses'][seg]:.2f}" for seg in l1_segment_order])
        l2_msg = ", ".join([f"{seg}={mean_segments[cfg]['L2 accesses'][seg]:.2f}" for seg in l2_segment_order])
        l1_total = sum(mean_segments[cfg]["L1 accesses"][seg] for seg in l1_segment_order)
        l2_total = sum(mean_segments[cfg]["L2 accesses"][seg] for seg in l2_segment_order)
        print(f"{cfgn:20} | L1 accesses: {l1_msg}")
        print(f"{'':20} | L1 total: {l1_total:.2f}")
        print(f"{'':20} | L2 accesses: {l2_msg}")
        print(f"{'':20} | L2 total: {l2_total:.2f}")
        if cfgn == "BTB-Ferret":
            print(f"{'':20} | Prefetch + skipDuetoPresence: {mean_prefetch_with_skip[cfg]:.2f}")


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 3: IPC Improvement  (speedup.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_speedup():
    stats_keys = {
        "{core}.commitStats0.numInsts" : "insts",
        "{core}.numCycles" : "cycles",
    }

    bms = all_bms

    configs = [
        ("baseline-2level", "2-Level Baseline"),
        # ("baseline-144L1", "144-entry L1"),
        # ("baseline-160L1", "160-entry L1"),
        
        ("BTB-Ferret", "BTB-Ferret"),
        
        ("Ideal-BTB", "Ideal BTB")
    ]
    # Keep baseline for normalization, but do not render it as a bar.
    plot_configs = configs[1:]

    data = {}
    
    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                # print(f"Warning: No stats file found for {cfg}/{bm} at {path_pattern}")
                continue
            path = stats_files[0]
            
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm not in data[cfg][bm]:
                    # print(f"Warning: Metric {mm} not found in {cfg}/{bm}")
                    pass
                else:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]

            ## Compute derived metrics
            data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]

            cfgref = configs[0][0]
            data[cfg][bm]["Speedup"] = data[cfg][bm]["IPC"] / data[cfgref][bm]["IPC"]

    colors = ["#07163d","#005e8a","#cc0000","#94bf73", "#888888"]

    cw = 12.5
    fs = 13
    NG = 1
    fig, ax = mlp.subplots(1, NG, figsize=(NG * cw, cw * 0.165), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    _labels = [renameBms(bm) for bm in bms] + ["Mean"]
    bottoms = np.zeros(len(bms) + 1)
    x = np.arange(len(bms) + 1, dtype=float)  # the label locations, including mean
    x[-1] = x[-1] + 0.4
    x = [xi + 0.2 if "5" in l else xi for xi, l in zip(x, _labels)]
    x = np.array(x)

    # Filter bms to only those that have data in ALL configs
    valid_bms = []
    for bm in bms:
        if all(bm in data[cfg] for (cfg, cfgn) in configs):
            valid_bms.append(bm)
    bms = valid_bms

    width = 0.7 / len(plot_configs)  # the width of the bars

    cc = {}
    for i, (cfg, cfgn) in enumerate(plot_configs):
        y_vals = [data[cfg][bm]["Speedup"] - 1 for bm in bms]
        y_plot = np.array(y_vals + [np.mean(y_vals)])

        # Calculate group means
        server_y = [data[cfg][bm]["Speedup"] - 1 for bm in bms if not bm.startswith("5")]
        spec_y = [data[cfg][bm]["Speedup"] - 1 for bm in bms if bm.startswith("5")]
        
        cc[cfgn] = {renameBms(bm): v for bm, v in zip(bms, y_vals)}
        cc[cfgn]["Mean"] = np.mean(y_vals)
        cc[cfgn]["Server Mean"] = np.mean(server_y) if server_y else np.nan
        cc[cfgn]["SPEC Mean"] = np.mean(spec_y) if spec_y else np.nan

        # Keep the original color mapping from the 3-config plot:
        # BTB-Ferret -> colors[1], Ideal BTB -> colors[2]
        ax.bar(x=x + width * i - width / 2, height=y_plot, width=width, label=cfgn, bottom=bottoms, zorder=3, color=colors[i + 1], edgecolor="k", hatch="")

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_ylabel("IPC Gain [%]", fontsize=fs - 1)
    ax.set_yticks([0.0, 0.05, 0.10])
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=0)

    ax.set_xticklabels(_labels, rotation=25, horizontalalignment="right", fontsize=fs - 4, rotation_mode="anchor")

    ax.set_xlim(xmin=-0.6, xmax=max(x) + 0.6)

    top = 0.145

    nspec = sum([1 for b in bms if "5" in b])
    xx = [len(bms) - nspec - 1 + 0.7, len(bms) - 1 + 0.9]
    ax.vlines(xx, ymin=-1.0, ymax=top, color="k", linestyle="--", zorder=2, linewidth=0.7)
    ax.fill_between(x=[xx[0], xx[1]], y1=-1.0, y2=top, color="k", alpha=0.1, zorder=1, hatch="////")

    ax.text(xx[0] / 2 + 5, top * 0.99, "Server", size=fs - 4, rotation=0.,
             ha="center", va="top")
    ax.text(xx[0] + (xx[1] - xx[0]) / 2, top * 0.99, "SPEC", size=fs - 4, rotation=0.,
             ha="center", va="top")

    # Important: annotation for perlbench
    try:
        # 紧贴在 'Ideal BTB' 柱子的左侧边缘
        ax.text(20.90, top - 0.006, f"{cc['Ideal BTB']['500.perlbench']*100:.1f}%", size=fs - 6, rotation=90.,
                 ha="left", va="top")
    except KeyError:
        pass

    ax.set_ylim(bottom=-0.003, top=top)

    fig.tight_layout()

    handles, labels = ax.get_legend_handles_labels()

    ax.legend(handles, labels, fontsize=fs - 3, ncols=6,
              loc='upper left', bbox_to_anchor=(0.01, 1),
              labelspacing=0.05, columnspacing=0.7, handletextpad=0.3, borderpad=0.3,
              framealpha=1, edgecolor="k",
              frameon=True)

    fig.savefig(f"{APATH}/performance_Ferret.pdf", dpi=300, bbox_inches='tight', pad_inches=0.08, facecolor="w")
    print(f"Saved {APATH}/performance_Ferret.pdf")

    # Print data
    print("\n" + "="*80)
    print(f"{'Benchmark':<25}", end="")
    for _, cfgn in plot_configs:
        print(f"{cfgn:>20}", end="")
    print("\n" + "-"*80)
    
    print_labels = [renameBms(bm) for bm in bms] + ["Server Mean", "SPEC Mean", "Mean"]
    for label in print_labels:
        print(f"{label:<25}", end="")
        for _, cfgn in plot_configs:
            val = cc[cfgn].get(label, np.nan)
            if not np.isnan(val):
                print(f"{val*100:>19.2f}%", end="")
            else:
                print(f"{'NaN':>20}", end="")
        print()
    print("="*80 + "\n")


def plot_config_summary(configs_to_plot, data, bms, ylabel="Norm. IPC", filename="summary.pdf", ylim=(0.9, 1.01), yticks=None, decimals=0, start_idx=0):
    """
    Generic bar chart plotter for configuration summaries.
    Plots the mean of 'Speedup' across all specified benchmarks for each config.
    Uses the "paired" style: 2 bars share a color, but use different hatches.
    """
    import numpy as np # Ensure np is available locally if not global
    cw = 8
    fs = 13
    NG = 1
    fig, ax = mlp.subplots(1, NG, figsize=(NG * cw, cw * 0.27), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    # Colors as defined in your snippet
    colors = ["#07163d", "#01739e", "#cc0000", "#94bf73", "#f39c12"]

    vals = {}
    is_gain = "Gain" in ylabel
    for i, (cfg, cfgn) in enumerate(configs_to_plot):
        # Use an effective index for coloring and hatching to maintain pairings
        idx = i + start_idx
        
        # Extract values for the benchmarks that exist in this config
        y_vals = [data[cfg][bm]["Speedup"] for bm in bms if bm in data[cfg]]
        if not y_vals:
            print(f"Warning: No data for config {cfg}")
            continue
        
        # Calculate mean (as in your snippet)
        if is_gain:
            y_vals = [y - 1 for y in y_vals]

        mean_val = np.mean(y_vals)
        vals[cfgn] = mean_val
        print(f"{cfgn:20}: {mean_val:.4f}")

        # Apply the paired coloring and hatching style
        color_idx = (idx // 2) % len(colors)
        hatch = "" if idx % 2 == 0 else "////"
        
        ax.bar(i, mean_val, zorder=3, color=colors[color_idx], edgecolor="k", hatch=hatch)

    ## Grid and Axis Styling
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_ylabel(ylabel, fontsize=fs - 2)
    if is_gain:
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=decimals))

    labels = [c[1] for c in configs_to_plot]
    x = np.arange(len(labels))

    ## Format x-axis
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, horizontalalignment="center", fontsize=fs - 3)

    ax.set_ylim(ylim[0], ylim[1])
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.set_xlim(xmin=-0.6, xmax=max(x) + 0.6 if len(x) > 0 else 0.6)

    fig.tight_layout()
    
    output_path = f"{APATH}/{filename}"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0, facecolor="w")
    print(f"Saved {output_path}")


def plot_pb_size():
    """
    Example usage of plot_config_summary.
    Modify the 'configs' list below to change what is plotted.
    """
    # 1. Define your configurations
    configs = [
        ("baseline-128-16K", "2-Level Baseline"),
        ("8pb-8sz-dep6", "8-entry PB"),
        ("16pb-8sz-dep6", "16-entry PB"),
        ("baseline-144-16K", "144-entry\nL1-BTB"),
        ("32pb-8sz-dep14", "32-entry PB"),
        ("baseline-160-16K", "160-entry\nL1-BTB"),
        ("64pb-8sz-dep14", "64-entry PB"),
        ("baseline-192-16K", "192-entry\nL1-BTB"),
    ]

    # 2. Load data (Reusing the common script logic)
    bms = all_bms
    data = {}
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
    }

    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            
            data[cfg][bm] = read_stats(stats_files[0])
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
            
            # Compute IPC and Speedup (W.R.T the first config in the list)
            if "insts" in data[cfg][bm] and "cycles" in data[cfg][bm]:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]
                cfgref = configs[0][0]
                # Pre-calculate speedup if reference IPC is available
                if bm in data.get(cfgref, {}):
                    data[cfg][bm]["Speedup"] = data[cfg][bm]["IPC"] / data[cfgref][bm]["IPC"]

    # 3. Call the summary plotting tool
    plot_config_summary(
        configs_to_plot=configs[1:],
        data=data,
        bms=bms,
        ylabel="IPC Gain [%]",
        filename="pb_size.pdf",
        ylim=(0, 0.02),
        yticks=np.arange(0, 0.021, 0.005),
        decimals=1,
        start_idx=1
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 4: Mean Speedup Line (mean_speedup_line.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_meanLine(baseline_cfg=SHARED_BASELINE_CFG, series_list=SHARED_SERIES_LIST):
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
    }

    bms = all_bms

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    
    # Collect all unique configs to load
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]

            ## Compute IPC
            if "insts" in data[cfg][bm] and "cycles" in data[cfg][bm]:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 7.0
    fs = 13
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.6))
    fig.patch.set_facecolor('white')

    all_y_vals = []
    print("\nMean IPC Improvement by Series and Depth:")
    for series in series_list:
        depths = []
        mean_imprs = []
        
        print(f"  Series: {series['name']}")
        for depth, cfg in series["configs"]:
            y_vals = []
            for bm in bms:
                if bm in data[cfg] and bm in data[baseline_cfg] and "IPC" in data[cfg][bm] and "IPC" in data[baseline_cfg][bm]:
                    impr = (data[cfg][bm]["IPC"] - data[baseline_cfg][bm]["IPC"]) / data[baseline_cfg][bm]["IPC"]
                    y_vals.append(impr)
            
            if y_vals:
                mean_val = np.mean(y_vals)
                depths.append(depth)
                mean_imprs.append(mean_val)
                all_y_vals.append(mean_val)
                print(f"    Variable {depth}: {mean_val*100:6.2f}%")

        if depths:
            ax.plot(depths, mean_imprs, marker='o', markersize=6, linewidth=1.5, 
                    color=series["color"], label=series["name"], zorder=3)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_xlabel("depth", fontsize=fs - 1)
    ax.set_ylabel("Speedup w.r.t. 2-level baseline", fontsize=fs - 1)

    # ── Format y-axis as percentage ─────────────────────────────────────────
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

    # ── Format x-axis ───────────────────────────────────────────────────────
    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    ax.set_xticks(sorted(list(all_depths)))
    
    # ── Auto-adjust axis ranges ───────────────────────────────────────────
    if all_depths:
        ax.set_xlim(left=min(all_depths), right=max(all_depths))

    if all_y_vals:
        y_max = max(all_y_vals)
        # Provide some headroom (e.g., 20% above max) to avoid "squeezing" at the top
        # but keep it sensitive to the actual values.
        ax.set_ylim(bottom=0, top=max(y_max * 1.3, 0.01))
        
        # Control tick granularity dynamically based on the range
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=10, steps=[1, 2, 2.5, 5, 10]))


    ax.legend(fontsize=fs - 4, frameon=True, edgecolor="k", framealpha=1, loc='lower right')

    fig.tight_layout()

    fig.savefig(f"{APATH}/mean_speedup_line.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/mean_speedup_line.pdf")


def plot_combineMeanSpeedup(
    baseline_cfg="baseline-128-16K",
    ideal_cfg="optimal-128-16K",
):
    """
    Plot two side-by-side mean speedup figures:
      1) L1-BTB size sweep
      2) Hierarchy depth sweep

    Mean speedup is computed as IPC_cfg / IPC_baseline.
    Y-axis shows mean IPC improvement percentage:
      (mean_speedup - 1) * 100%
    """
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
    }
    bms = all_bms

    left_panel = {
        "title": "L1-BTB size",
        "x_labels": ["128", "256", "512", "1K"],
        "ferret_cfgs": [
            "32pb-8sz-dep14",
            "32pb-8sz-dep14-256L1",
            "32pb-8sz-dep14-512L1",
            "32pb-8sz-dep14-1KL1",
        ],
        "noferret_cfgs": [
            "baseline-128-16K",
            "baseline-256-16K",
            "baseline-512-16K",
            "baseline-1K-16K",
        ],
    }

    right_panel = {
        "title": "Hierarchy Depth",
        "x_labels": ["2-level", "3-level"],
        "ferret_cfgs": ["32pb-8sz-dep14", "Ferret-test-3level2"],
        "noferret_cfgs": ["baseline-128-16K", "baseline-128-6K-16K-incl"],
    }

    panel_defs = [left_panel, right_panel]

    # Collect all required configs
    required_cfgs = {baseline_cfg, ideal_cfg}
    for panel in panel_defs:
        required_cfgs.update(panel["ferret_cfgs"])
        required_cfgs.update(panel["noferret_cfgs"])

    # Load data for all required configs
    data = {}
    for cfg in required_cfgs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue

            data[cfg][bm] = read_stats(stats_files[0])
            for metric, alias in stats_keys.items():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][alias] = data[cfg][bm][mm]

            if "insts" in data[cfg][bm] and "cycles" in data[cfg][bm] and data[cfg][bm]["cycles"] > 0:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]

    def _mean_speedup_ratio(cfg_name):
        raw_speedups = []

        for bm in bms:
            if bm not in data.get(cfg_name, {}) or bm not in data.get(baseline_cfg, {}):
                continue

            ipc_cfg = data[cfg_name][bm].get("IPC")
            ipc_base = data[baseline_cfg][bm].get("IPC")
            if ipc_cfg is None or ipc_base is None or ipc_base <= 0:
                continue

            raw_speedups.append(ipc_cfg / ipc_base)

        if not raw_speedups:
            return None

        return np.mean(raw_speedups)

    # Style: keep close to plot_meanCombined
    cw = 4.4
    fs = 15
    fig, axes = mlp.subplots(1, 2, figsize=(2 * cw, cw * 0.67), sharey=True)
    fig.patch.set_facecolor("white")

    ferret_color = "#0066cc"
    noferret_color = "#ff7f0e"
    marker_style = "."
    line_width = 2.1
    global_y_vals = []

    ideal_ratio = _mean_speedup_ratio(ideal_cfg)
    ideal_impr = None if ideal_ratio is None else (ideal_ratio - 1.0)
    print("\nL1 Sweep point values (y-axis):")
    if ideal_impr is None:
        print("  Ideal: N/A")
    else:
        print(f"  Ideal: {ideal_impr:.6f} ({ideal_impr * 100:.2f}%)")

    for idx, panel in enumerate(panel_defs):
        ax = axes[idx]
        x = np.arange(len(panel["x_labels"]))

        ferret_y = []
        noferret_y = []
        for cfg in panel["ferret_cfgs"]:
            ratio = _mean_speedup_ratio(cfg)
            ferret_y.append(None if ratio is None else (ratio - 1.0))
        for cfg in panel["noferret_cfgs"]:
            ratio = _mean_speedup_ratio(cfg)
            noferret_y.append(None if ratio is None else (ratio - 1.0))

        print(f"  Panel {idx + 1}: {panel['title']}")
        for x_label, ferret_cfg, noferret_cfg, fy, ny in zip(
            panel["x_labels"],
            panel["ferret_cfgs"],
            panel["noferret_cfgs"],
            ferret_y,
            noferret_y,
        ):
            fy_str = "N/A" if fy is None else f"{fy:.6f} ({fy * 100:.2f}%)"
            ny_str = "N/A" if ny is None else f"{ny:.6f} ({ny * 100:.2f}%)"
            print(
                f"    {x_label}: "
                f"Ferret[{ferret_cfg}]={fy_str}, "
                f"NoFerret[{noferret_cfg}]={ny_str}"
            )

        if any(v is not None for v in ferret_y):
            ax.plot(
                x,
                [np.nan if v is None else v for v in ferret_y],
                marker=marker_style,
                markersize=12,
                linewidth=line_width,
                color=ferret_color,
                label="Ferret",
                zorder=4,
            )
        if any(v is not None for v in noferret_y):
            ax.plot(
                x,
                [np.nan if v is None else v for v in noferret_y],
                marker=marker_style,
                markersize=12,
                linewidth=line_width,
                color=noferret_color,
                linestyle="--",
                label="No Ferret",
                zorder=4,
            )

        if ideal_impr is not None:
            ax.axhline(
                y=ideal_impr,
                color="#d62728",
                linestyle=(0, (4.0, 4.0)),
                linewidth=1.3,
                alpha=0.95,
                zorder=2,
            )
            if idx == 0:
                ax.annotate("Ideal", (x[0] - 0.18, ideal_impr), xytext=(0, 2), textcoords="offset points",
                            fontsize=fs - 2, va="bottom", ha="left", clip_on=False)
            global_y_vals.append(ideal_impr)
        ax.axhline(y=0.0, color="k", linewidth=0.9, alpha=0.9, zorder=2)

        global_y_vals.extend([v for v in ferret_y if v is not None])
        global_y_vals.extend([v for v in noferret_y if v is not None])

        ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
        ax.grid(True, which="both")
        ax.grid(True, which="minor", linestyle=":")

        ax.set_xticks(x)
        ax.set_xticklabels(panel["x_labels"], fontsize=fs + 1)
        ax.set_xlabel(panel["title"], fontsize=fs + 4)
        ax.tick_params(axis="y", labelsize=fs + 1)
        ax.set_xlim(-0.25, len(panel["x_labels"]) - 0.55)

    axes[0].set_ylabel("Speedup", fontsize=fs + 4)
    axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

    # Fixed y-axis scale for readability: 0.0% to 5.0%, step 1.0%.
    axes[0].set_ylim(0.0, 0.05)
    axes[0].set_yticks(np.arange(0.0, 0.051, 0.01))

    # Remove center touching spines and use one vertical dashed separator.
    axes[0].spines["right"].set_visible(False)
    axes[1].spines["left"].set_visible(False)
    axes[1].tick_params(labelleft=False)

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.subplots_adjust(wspace=0.0)

    # Add figure-level vertical solid separator between the two subplots.
    bbox_left = axes[0].get_position()
    x_sep = bbox_left.x1
    y0 = min(axes[0].get_position().y0, axes[1].get_position().y0)
    y1 = max(axes[0].get_position().y1, axes[1].get_position().y1)
    sep = mlp.Line2D([x_sep, x_sep], [y0, y1], transform=fig.transFigure,
                     linestyle="-", color="k", linewidth=1.0, alpha=0.8)
    fig.add_artist(sep)

    # Top legend: slimmer box and centered to the two-panel separator.
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(x_sep, 0.975),
        ncols=2,
        fontsize=fs - 1,
        frameon=True,
        edgecolor="k",
        framealpha=1.0,
        borderpad=0.25,
        labelspacing=0.25,
        columnspacing=0.8,
        handletextpad=0.35,
        handlelength=1.9,
    )

    fig.savefig(f"{APATH}/sweep_L1_level.pdf", dpi=300, bbox_inches="tight", pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/sweep_L1_level.pdf")


def plot_L1sweep(
    baseline_cfg="baseline-128-16K",
    ideal_cfg="optimal-128-16K",
    left_panel=None,
    right_panel=None,
    output_name="sweep_L1_mid.pdf",
):
    """
    Plot two side-by-side L1-BTB size sweep figures with the same style
    as plot_combineMeanSpeedup().

    Each panel can specify its own cfg groups via:
      {
        "title": "panel title",
        "x_labels": [...],
        "ferret_cfgs": [...],
        "noferret_cfgs": [...],
      }

    Mean speedup is computed as IPC_cfg / IPC_baseline.
    Y-axis shows mean IPC improvement percentage:
      (mean_speedup - 1) * 100%
    """
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
    }
    bms = all_bms

    default_left = {
        "title": "2-level BTB",
        "x_labels": ["128", "256", "512", "1K"],
        "ferret_cfgs": [
            "32pb-8sz-dep14",
            "32pb-8sz-dep14-256L1",
            "32pb-8sz-dep14-512L1",
            "32pb-8sz-dep14-1KL1",
        ],
        "noferret_cfgs": [
            "baseline-128-16K",
            "baseline-256-16K",
            "baseline-512-16K",
            "baseline-1K-16K",
        ],
    }
    # default_right = {
    #     "title": "3-level BTB",
    #     "x_labels": ["64","128", "256", "512", "1K"],
    #     "ferret_cfgs": [
            
    #         "32pb-8sz-dep14-64-6K-16K",
    #         "32pb-8sz-dep14-128-6K-16K",
    #         "32pb-8sz-dep14-256-6K-16K",
    #         "32pb-8sz-dep14-512-6K-16K",
    #         "32pb-8sz-dep14-1K-6K-16K",
    #     ],
    #     "noferret_cfgs": [
    #         "baseline-64-6K-16K",
    #         "baseline-128-6K-16K-incl",
    #         "baseline-256-6K-16K",
    #         "baseline-512-6K-16K",
    #         "baseline-1K-6K-16K",
    #     ],
    # }
    default_right = {
        "title": "3-level BTB",
        "x_labels": ["2K","4K", "6K", "8K"],
        "ferret_cfgs": [
            
            "32pb-8sz-dep14-128-2K-16K",
            "32pb-8sz-dep14-128-4K-16K",
            "32pb-8sz-dep14-128-6K-16K",
            "32pb-8sz-dep14-128-8K-16K",
            
        ],
        "noferret_cfgs": [
            "baseline-128-2K-16K",
            "baseline-128-4K-16K",
            "baseline-128-6K-16K",
            "baseline-128-8K-16K",
        ],
    }

    left_panel = default_left if left_panel is None else left_panel
    right_panel = default_right if right_panel is None else right_panel
    panel_defs = [left_panel, right_panel]

    # Basic consistency checks for safer plotting.
    for panel in panel_defs:
        if len(panel["x_labels"]) != len(panel["ferret_cfgs"]) or len(panel["x_labels"]) != len(panel["noferret_cfgs"]):
            raise ValueError(
                f"Panel '{panel['title']}' has mismatched lengths: "
                f"x_labels={len(panel['x_labels'])}, "
                f"ferret_cfgs={len(panel['ferret_cfgs'])}, "
                f"noferret_cfgs={len(panel['noferret_cfgs'])}"
            )

    # Collect all required configs
    required_cfgs = {baseline_cfg, ideal_cfg}
    for panel in panel_defs:
        required_cfgs.update(panel["ferret_cfgs"])
        required_cfgs.update(panel["noferret_cfgs"])

    # Load data for all required configs
    data = {}
    for cfg in required_cfgs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue

            data[cfg][bm] = read_stats(stats_files[0])
            for metric, alias in stats_keys.items():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][alias] = data[cfg][bm][mm]

            if "insts" in data[cfg][bm] and "cycles" in data[cfg][bm] and data[cfg][bm]["cycles"] > 0:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]

    def _mean_speedup_ratio(cfg_name):
        raw_speedups = []

        for bm in bms:
            if bm not in data.get(cfg_name, {}) or bm not in data.get(baseline_cfg, {}):
                continue

            ipc_cfg = data[cfg_name][bm].get("IPC")
            ipc_base = data[baseline_cfg][bm].get("IPC")
            if ipc_cfg is None or ipc_base is None or ipc_base <= 0:
                continue

            raw_speedups.append(ipc_cfg / ipc_base)

        if not raw_speedups:
            return None

        return np.mean(raw_speedups)

    # Style: keep exactly aligned with plot_combineMeanSpeedup
    cw = 4.4
    fs = 15
    fig, axes = mlp.subplots(1, 2, figsize=(2 * cw, cw * 0.67), sharey=True)
    fig.patch.set_facecolor("white")

    ferret_color = "#0066cc"
    noferret_color = "#ff7f0e"
    marker_style = "."
    line_width = 2.1
    global_y_vals = []

    ideal_ratio = _mean_speedup_ratio(ideal_cfg)
    ideal_impr = None if ideal_ratio is None else (ideal_ratio - 1.0)
    print("\nL1 Sweep point values (y-axis):")
    if ideal_impr is None:
        print("  Ideal BTB: N/A")
    else:
        print(f"  Ideal BTB: {ideal_impr:.6f} ({ideal_impr * 100:.2f}%)")

    for idx, panel in enumerate(panel_defs):
        ax = axes[idx]
        x = np.arange(len(panel["x_labels"]))

        ferret_y = []
        noferret_y = []
        for cfg in panel["ferret_cfgs"]:
            ratio = _mean_speedup_ratio(cfg)
            ferret_y.append(None if ratio is None else (ratio - 1.0))
        for cfg in panel["noferret_cfgs"]:
            ratio = _mean_speedup_ratio(cfg)
            noferret_y.append(None if ratio is None else (ratio - 1.0))

        print(f"  Panel {idx + 1}: {panel['title']}")
        for x_label, ferret_cfg, noferret_cfg, fy, ny in zip(
            panel["x_labels"],
            panel["ferret_cfgs"],
            panel["noferret_cfgs"],
            ferret_y,
            noferret_y,
        ):
            fy_str = "N/A" if fy is None else f"{fy:.6f} ({fy * 100:.2f}%)"
            ny_str = "N/A" if ny is None else f"{ny:.6f} ({ny * 100:.2f}%)"
            print(
                f"    {x_label}: "
                f"Ferret[{ferret_cfg}]={fy_str}, "
                f"NoFerret[{noferret_cfg}]={ny_str}"
            )

        if any(v is not None for v in ferret_y):
            ax.plot(
                x,
                [np.nan if v is None else v for v in ferret_y],
                marker=marker_style,
                markersize=12,
                linewidth=line_width,
                color=ferret_color,
                label="Ferret",
                zorder=4,
            )
        if any(v is not None for v in noferret_y):
            ax.plot(
                x,
                [np.nan if v is None else v for v in noferret_y],
                marker=marker_style,
                markersize=12,
                linewidth=line_width,
                color=noferret_color,
                linestyle="--",
                label="No Ferret",
                zorder=4,
            )

        if ideal_impr is not None:
            ax.axhline(
                y=ideal_impr,
                color="#d62728",
                linestyle=(0, (4.0, 4.0)),
                linewidth=1.3,
                alpha=0.95,
                zorder=2,
            )
            if idx == 0:
                ax.annotate("Ideal BTB", (x[0] - 0.18, ideal_impr), xytext=(0, 2), textcoords="offset points",
                            fontsize=fs - 2, va="bottom", ha="left", clip_on=False)
            global_y_vals.append(ideal_impr)
        ax.axhline(y=0.0, color="k", linewidth=0.9, alpha=0.9, zorder=2)

        global_y_vals.extend([v for v in ferret_y if v is not None])
        global_y_vals.extend([v for v in noferret_y if v is not None])

        ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
        ax.grid(True, which="both")
        ax.grid(True, which="minor", linestyle=":")

        ax.set_xticks(x)
        ax.set_xticklabels(panel["x_labels"], fontsize=fs + 1)
        ax.set_xlabel(panel["title"], fontsize=fs + 4)
        ax.tick_params(axis="y", labelsize=fs + 1)
        ax.set_xlim(-0.25, len(panel["x_labels"]) - 0.55)

    axes[0].set_ylabel("Speedup", fontsize=fs + 4)
    axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))

    # Fixed y-axis scale for readability: 0.0% to 5.0%, step 1.0%.
    axes[0].set_ylim(0.0, 0.040)
    axes[0].set_yticks(np.arange(0.0, 0.041, 0.01))

    # Remove center touching spines and use one vertical separator.
    axes[0].spines["right"].set_visible(False)
    axes[1].spines["left"].set_visible(False)
    axes[1].tick_params(labelleft=False)

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.subplots_adjust(wspace=0.0)

    # Add figure-level vertical solid separator between the two subplots.
    bbox_left = axes[0].get_position()
    x_sep = bbox_left.x1
    y0 = min(axes[0].get_position().y0, axes[1].get_position().y0)
    y1 = max(axes[0].get_position().y1, axes[1].get_position().y1)
    sep = mlp.Line2D([x_sep, x_sep], [y0, y1], transform=fig.transFigure,
                    linestyle="-", color="k", linewidth=1.0, alpha=0.8)
    fig.add_artist(sep)

    # Top legend: slimmer box and centered to the two-panel separator.
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(x_sep, 0.975),
        ncols=2,
        fontsize=fs - 1,
        frameon=True,
        edgecolor="k",
        framealpha=1.0,
        borderpad=0.25,
        labelspacing=0.25,
        columnspacing=0.8,
        handletextpad=0.35,
        handlelength=1.9,
    )

    fig.savefig(f"{APATH}/{output_name}", dpi=300, bbox_inches="tight", pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/{output_name}")


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 6: Mean Coverage Line (mean_coverage_line.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_meanCovered(baseline_cfg=SHARED_BASELINE_CFG, series_list=SHARED_SERIES_LIST):
    stats_keys = {
        "{core}.branchPred.btb.l1MissL2Hits": "l1MissL2Hits",
        "{core}.branchPred.btb.latePrefetchByL2Hit::total": "partialCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::total": "partialCoveredByPBHit",
        "{core}.branchPred.btb.latePrefetchByL2Hit::4": "fullCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::4": "fullCoveredByPBHit",
    }

    bms = all_bms

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            ## Compute coverage
            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                     data[cfg][bm].get("partialCoveredByPBHit", 0)
            
            if l2_acc > 0:
                data[cfg][bm]["Covered"] = (data[cfg][bm].get("fullCoveredByL2", 0) + data[cfg][bm].get("fullCoveredByPBHit", 0)) / l2_acc
            else:
                data[cfg][bm]["Covered"] = 0

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 7.0
    fs = 13
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.6))
    fig.patch.set_facecolor('white')

    all_y_vals = []
    print("\nMean Coverage by Series and Depth:")
    for series in series_list:
        depths = []
        mean_covs = []
        
        print(f"  Series: {series['name']}")
        for depth, cfg in series["configs"]:
            y_vals = [data[cfg][bm]["Covered"] for bm in bms if bm in data[cfg]]
            
            if y_vals:
                mean_val = np.mean(y_vals)
                depths.append(depth)
                mean_covs.append(mean_val)
                all_y_vals.append(mean_val)
                print(f"    Depth {depth}: {mean_val*100:6.2f}%")

        if depths:
            ax.plot(depths, mean_covs, marker='o', markersize=6, linewidth=1.5, 
                    color=series["color"], label=series["name"], zorder=3)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_xlabel("Depth", fontsize=fs - 1)
    ax.set_ylabel("Mean Coverage", fontsize=fs - 1)

    # ── Format y-axis as percentage ─────────────────────────────────────────
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

    # ── Format x-axis ───────────────────────────────────────────────────────
    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    ax.set_xticks(sorted(list(all_depths)))
    
    # ── Auto-adjust axis ranges ───────────────────────────────────────────
    if all_depths:
        ax.set_xlim(left=min(all_depths), right=max(all_depths))

    if all_y_vals:
        y_max = max(all_y_vals)
        # Ensure 30% headroom to keep lines from being squeezed at the top
        ax.set_ylim(bottom=0, top=max(y_max * 1.3, 0.01))
        
        # Improve tick granularity based on values
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=10, steps=[1, 2, 2.5, 5, 10]))

    ax.legend(fontsize=fs - 4, frameon=True, edgecolor="k", framealpha=1, loc='lower right')

    fig.tight_layout()

    fig.savefig(f"{APATH}/mean_coverage_line.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/mean_coverage_line.pdf")


def plot_meanLooseCovered(baseline_cfg=SHARED_BASELINE_CFG, series_list=SHARED_SERIES_LIST):
    stats_keys = {
        "{core}.branchPred.btb.l1MissL2Hits": "l1MissL2Hits",
        "{core}.branchPred.btb.latePrefetchByL2Hit::total": "partialCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::total": "partialCoveredByPBHit",
        "{core}.branchPred.btb.latePrefetchByL2Hit::1": "paritalCoveredByL21",
        "{core}.branchPred.btb.latePrefetchByPBHit::1": "partialCoveredByPBHit1",
        "{core}.branchPred.btb.latePrefetchByL2Hit::2": "paritalCoveredByL22",
        "{core}.branchPred.btb.latePrefetchByPBHit::2": "partialCoveredByPBHit2",
        "{core}.branchPred.btb.latePrefetchByL2Hit::3": "paritalCoveredByL23",
        "{core}.branchPred.btb.latePrefetchByPBHit::3": "partialCoveredByPBHit3",
        "{core}.branchPred.btb.latePrefetchByL2Hit::4": "fullCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::4": "fullCoveredByPBHit",
    }

    bms = all_bms

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            ## Compute loose coverage
            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                     data[cfg][bm].get("partialCoveredByPBHit", 0)
            
            full = data[cfg][bm].get("fullCoveredByL2", 0) + \
                   data[cfg][bm].get("fullCoveredByPBHit", 0)
            
            partial = data[cfg][bm].get("paritalCoveredByL21", 0) + \
                      data[cfg][bm].get("paritalCoveredByL22", 0) + \
                      data[cfg][bm].get("paritalCoveredByL23", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit1", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit2", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit3", 0)
            
            if l2_acc > 0:
                data[cfg][bm]["LooseCovered"] = (full + partial) / l2_acc
            else:
                data[cfg][bm]["LooseCovered"] = 0

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 7.0
    fs = 13
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.6))
    fig.patch.set_facecolor('white')

    all_y_vals = []
    print("\nMean Loose Coverage by Series and Depth:")
    for series in series_list:
        depths = []
        mean_covs = []
        
        print(f"  Series: {series['name']}")
        for depth, cfg in series["configs"]:
            y_vals = [data[cfg][bm]["LooseCovered"] for bm in bms if bm in data[cfg]]
            
            if y_vals:
                mean_val = np.mean(y_vals)
                depths.append(depth)
                mean_covs.append(mean_val)
                all_y_vals.append(mean_val)
                print(f"    Var {depth}: {mean_val*100:6.2f}%")

        if depths:
            ax.plot(depths, mean_covs, marker='o', markersize=6, linewidth=1.5, 
                    color=series["color"], label=series["name"], zorder=3)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_xlabel("depth", fontsize=fs - 1)
    ax.set_ylabel("Mean Coverage", fontsize=fs - 1)

    # ── Format y-axis as percentage ─────────────────────────────────────────
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

    # ── Format x-axis ───────────────────────────────────────────────────────
    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    ax.set_xticks(sorted(list(all_depths)))
    
    # ── Auto-adjust axis ranges ───────────────────────────────────────────
    if all_depths:
        ax.set_xlim(left=min(all_depths), right=max(all_depths))

    if all_y_vals:
        y_max = max(all_y_vals)
        # Ensure 30% headroom to keep lines from being squeezed at the top
        ax.set_ylim(bottom=0, top=max(y_max * 1.3, 0.01))
        
        # Improve tick granularity based on values
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=10, steps=[1, 2, 2.5, 5, 10]))

    ax.legend(fontsize=fs - 4, frameon=True, edgecolor="k", framealpha=1, loc='lower right')

    fig.tight_layout()

    fig.savefig(f"{APATH}/mean_loose_coverage_line.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/mean_loose_coverage_line.pdf")



# ═══════════════════════════════════════════════════════════════════════════════
# Plot 7: Mean Overprefetch Line (mean_overprefetch_line.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_meanOverprefetch(baseline_cfg=SHARED_BASELINE_CFG, series_list=SHARED_SERIES_LIST):
    stats_keys = {
        "{core}.branchPred.btb.l1MissL2Hits": "l1MissL2Hits",
        "{core}.branchPred.btb.latePrefetchByL2Hit::total": "partialCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::total": "partialCoveredByPBHit",
        "{core}.branchPred.btb.uselessPrefetches::total": "uselessPrefetches"
    }

    bms = all_bms

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            ## Compute overprediction ratio
            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                     data[cfg][bm].get("partialCoveredByPBHit", 0)
            
            if l2_acc > 0:
                data[cfg][bm]["Overpredicted"] = data[cfg][bm].get("uselessPrefetches", 0) / l2_acc
            else:
                data[cfg][bm]["Overpredicted"] = 0

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 7.0
    fs = 13
    fig, ax = mlp.subplots(figsize=(cw, cw * 0.6))
    fig.patch.set_facecolor('white')

    all_y_vals = []
    print("\nMean Overprefetch Ratio by Series and Depth:")
    for series in series_list:
        depths = []
        mean_ovps = []
        
        print(f"  Series: {series['name']}")
        for depth, cfg in series["configs"]:
            y_vals = [data[cfg][bm]["Overpredicted"] for bm in bms if bm in data[cfg]]
            
            if y_vals:
                mean_val = np.mean(y_vals)
                depths.append(depth)
                mean_ovps.append(mean_val)
                all_y_vals.append(mean_val)
                print(f"    Var {depth}: {mean_val*100:6.2f}%")

        if depths:
            ax.plot(depths, mean_ovps, marker='o', markersize=6, linewidth=1.5, 
                    color=series["color"], label=series["name"], zorder=3)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_xlabel("depth", fontsize=fs - 1)
    ax.set_ylabel("Mean Overprediction Ratio", fontsize=fs - 1)

    # ── Format y-axis as percentage ─────────────────────────────────────────
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

    # ── Format x-axis ───────────────────────────────────────────────────────
    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    ax.set_xticks(sorted(list(all_depths)))
    
    # ── Auto-adjust axis ranges ───────────────────────────────────────────
    if all_depths:
        ax.set_xlim(left=min(all_depths), right=max(all_depths))

    if all_y_vals:
        y_max = max(all_y_vals)
        # Ensure 30% headroom to keep lines from being squeezed at the top
        ax.set_ylim(bottom=0, top=max(y_max * 1.3, 0.01))
        
        # Improve tick granularity based on values
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=10, steps=[1, 2, 2.5, 5, 10]))

    ax.legend(fontsize=fs - 4, frameon=True, edgecolor="k", framealpha=1, loc='best')

    fig.tight_layout()

    fig.savefig(f"{APATH}/mean_overprefetch_line.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/mean_overprefetch_line.pdf")


def plot_meanCombined(baseline_cfg=SHARED_BASELINE_CFG, series_list=SHARED_SERIES_LIST):
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
        "{core}.branchPred.btb.l1MissL2Hits": "l1MissL2Hits",
        "{core}.branchPred.btb.latePrefetchByL2Hit::total": "partialCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::total": "partialCoveredByPBHit",
        "{core}.branchPred.btb.latePrefetchByL2Hit::1": "paritalCoveredByL21",
        "{core}.branchPred.btb.latePrefetchByPBHit::1": "partialCoveredByPBHit1",
        "{core}.branchPred.btb.latePrefetchByL2Hit::2": "paritalCoveredByL22",
        "{core}.branchPred.btb.latePrefetchByPBHit::2": "partialCoveredByPBHit2",
        "{core}.branchPred.btb.latePrefetchByL2Hit::3": "paritalCoveredByL23",
        "{core}.branchPred.btb.latePrefetchByPBHit::3": "partialCoveredByPBHit3",
        "{core}.branchPred.btb.latePrefetchByL2Hit::4": "fullCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::4": "fullCoveredByPBHit",
        "{core}.branchPred.btb.uselessPrefetches::total": "uselessPrefetches"
    }

    bms = all_bms
    data = {}
    
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files: continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)
            for metric, key in stats_keys.items():
                mm = resolve_metric(metric, bm)
                data[cfg][bm][key] = data[cfg][bm].get(mm, 0)
            
            if data[cfg][bm].get("cycles", 0) > 0:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]
            
            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                     data[cfg][bm].get("partialCoveredByPBHit", 0)
            
            full = data[cfg][bm].get("fullCoveredByL2", 0) + \
                   data[cfg][bm].get("fullCoveredByPBHit", 0)
            
            partial = data[cfg][bm].get("paritalCoveredByL21", 0) + \
                      data[cfg][bm].get("paritalCoveredByL22", 0) + \
                      data[cfg][bm].get("paritalCoveredByL23", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit1", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit2", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit3", 0)
            
            if l2_acc > 0:
                data[cfg][bm]["LooseCovered"] = (full + partial) / l2_acc
                data[cfg][bm]["Overpredicted"] = data[cfg][bm].get("uselessPrefetches", 0) / l2_acc
            else:
                data[cfg][bm]["LooseCovered"] = 0
                data[cfg][bm]["Overpredicted"] = 0

    cw = 3.5
    fs = 15
    NG = 3
    fig, axes = mlp.subplots(1, NG, figsize=(NG * cw, cw * 1), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    metrics = [
        ("IPC Improvement", "Speedup"),
        ("LooseCovered", "Coverage"),
        ("Overpredicted", "Overfetched")
    ]

    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    sorted_depths = sorted(list(all_depths))
    linestyles = ['-', '--', '-.', ':']

    for i, (metric_key, y_label) in enumerate(metrics):
        ax = axes[i]
        all_y_vals = []
        # ax.set_title(y_label, fontsize=fs, fontweight='bold')
        for j, series in enumerate(series_list):
            plot_depths, mean_vals = [], []
            for depth, cfg in series["configs"]:
                y_vals = []
                for bm in bms:
                    if bm in data[cfg]:
                        if metric_key == "IPC Improvement":
                            if bm in data[baseline_cfg] and "IPC" in data[cfg][bm] and "IPC" in data[baseline_cfg][bm]:
                                val = (data[cfg][bm]["IPC"] - data[baseline_cfg][bm]["IPC"]) / data[baseline_cfg][bm]["IPC"]
                                y_vals.append(val)
                        else:
                            # For Coverage/Overfetched, skip benchmarks with no
                            # L2 BTB accesses (l2_acc == 0): their values are
                            # undefined (set to 0 by the else branch) and would
                            # drag down the mean.
                            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                                     data[cfg][bm].get("partialCoveredByPBHit", 0)
                            if l2_acc > 0:
                                y_vals.append(data[cfg][bm].get(metric_key, 0))
                if y_vals:
                    mv = np.mean(y_vals)
                    plot_depths.append(depth)
                    mean_vals.append(mv)
                    all_y_vals.append(mv)
            if plot_depths:
                ax.plot(plot_depths, mean_vals, marker='.', markersize=12, linewidth=2.1, color=series["color"], 
                        label=series["name"], zorder=3, linestyle=linestyles[j % len(linestyles)])

        ## Grid
        ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
        ax.grid(True, which='both')
        ax.grid(True, which='minor', linestyle=':')

        ax.set_xlabel("# max chains", fontsize=fs + 4)
        ax.set_ylabel(y_label, fontsize=fs + 4)

        # ── Format y-axis as percentage ─────────────────────────────────────────
        if i == 0:
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))
        else:
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))

        # ── Format x-axis ───────────────────────────────────────────────────────
        ax.set_xticks(sorted_depths)
        ax.tick_params(axis='x', which='major', pad=0)
        ax.set_xticklabels(sorted_depths, rotation=0, horizontalalignment="center", fontsize=fs + 1)
        ax.tick_params(axis='y', labelsize=fs + 1)

        if sorted_depths:
            ax.set_xlim(left=min(sorted_depths) - 0.5, right=max(sorted_depths) + 0.5)

        if all_y_vals:
            if i == 0:      # Speedup: ticks 0–2%, small top clearance for legend
                ax.set_ylim(bottom=0, top=0.024)
                ax.set_yticks(np.arange(0, 0.0201, 0.005))
            elif i == 1:    # Coverage: ticks 0–40%, small top clearance for legend
                ax.set_ylim(bottom=0, top=0.44)
                ax.set_yticks(np.arange(0, 0.401, 0.10))
            else:           # Overfetched: ticks 0–50%, small top clearance for legend
                ax.set_ylim(bottom=0, top=0.54)
                ax.set_yticks(np.arange(0, 0.501, 0.10))

    # Add single figure legend at the top (centered)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.73),
               ncols=len(series_list), fontsize=fs - 1, frameon=True, edgecolor="k",
               columnspacing=1.0, handletextpad=0.4)

    fig.tight_layout(rect=[0, 0, 1, 0.80])
    fig.savefig(f"{APATH}/Sweep_chains.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/Sweep_chains.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 9: Speedup & False Positive Rate (speedup_fpr.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_sweepPrefetches(baseline_cfg=SHARED_BASELINE_CFG, series_list=SHARED_SERIES_LIST):
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
        "{core}.branchPred.btb.l1MissL2Hits": "l1MissL2Hits",
        "{core}.branchPred.btb.latePrefetchByL2Hit::total": "partialCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::total": "partialCoveredByPBHit",
        "{core}.branchPred.btb.latePrefetchByL2Hit::1": "paritalCoveredByL21",
        "{core}.branchPred.btb.latePrefetchByPBHit::1": "partialCoveredByPBHit1",
        "{core}.branchPred.btb.latePrefetchByL2Hit::2": "paritalCoveredByL22",
        "{core}.branchPred.btb.latePrefetchByPBHit::2": "partialCoveredByPBHit2",
        "{core}.branchPred.btb.latePrefetchByL2Hit::3": "paritalCoveredByL23",
        "{core}.branchPred.btb.latePrefetchByPBHit::3": "partialCoveredByPBHit3",
        "{core}.branchPred.btb.latePrefetchByL2Hit::4": "fullCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::4": "fullCoveredByPBHit",
        "{core}.branchPred.btb.uselessPrefetches::total": "uselessPrefetches"
    }

    bms = all_bms
    data = {}
    
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files: continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)
            for metric, key in stats_keys.items():
                mm = resolve_metric(metric, bm)
                data[cfg][bm][key] = data[cfg][bm].get(mm, 0)
            
            if data[cfg][bm].get("cycles", 0) > 0:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]
            
            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                     data[cfg][bm].get("partialCoveredByPBHit", 0)
            
            full = data[cfg][bm].get("fullCoveredByL2", 0) + \
                   data[cfg][bm].get("fullCoveredByPBHit", 0)
            
            partial = data[cfg][bm].get("paritalCoveredByL21", 0) + \
                      data[cfg][bm].get("paritalCoveredByL22", 0) + \
                      data[cfg][bm].get("paritalCoveredByL23", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit1", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit2", 0) + \
                      data[cfg][bm].get("partialCoveredByPBHit3", 0)
            
            if l2_acc > 0:
                data[cfg][bm]["LooseCovered"] = (full + partial) / l2_acc
                data[cfg][bm]["Overpredicted"] = data[cfg][bm].get("uselessPrefetches", 0) / l2_acc
            else:
                data[cfg][bm]["LooseCovered"] = 0
                data[cfg][bm]["Overpredicted"] = 0

    cw = 3.5
    fs = 15
    NG = 3
    fig, axes = mlp.subplots(1, NG, figsize=(NG * cw, cw * 1), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    metrics = [
        ("IPC Improvement", "Speedup"),
        ("LooseCovered", "Coverage"),
        ("Overpredicted", "Overfetched")
    ]

    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    sorted_depths = sorted(list(all_depths))
    linestyles = ['-', '--', '-.', ':']

    for i, (metric_key, y_label) in enumerate(metrics):
        ax = axes[i]
        all_y_vals = []
        # ax.set_title(y_label, fontsize=fs, fontweight='bold')
        for j, series in enumerate(series_list):
            plot_depths, mean_vals = [], []
            for depth, cfg in series["configs"]:
                y_vals = []
                for bm in bms:
                    if bm in data[cfg]:
                        if metric_key == "IPC Improvement":
                            if bm in data[baseline_cfg] and "IPC" in data[cfg][bm] and "IPC" in data[baseline_cfg][bm]:
                                val = (data[cfg][bm]["IPC"] - data[baseline_cfg][bm]["IPC"]) / data[baseline_cfg][bm]["IPC"]
                                y_vals.append(val)
                        else:
                            # For Coverage/Overfetched, skip benchmarks with no
                            # L2 BTB accesses (l2_acc == 0): their values are
                            # undefined (set to 0 by the else branch) and would
                            # drag down the mean.
                            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                                     data[cfg][bm].get("partialCoveredByPBHit", 0)
                            if l2_acc > 0:
                                y_vals.append(data[cfg][bm].get(metric_key, 0))
                if y_vals:
                    mv = np.mean(y_vals)
                    plot_depths.append(depth)
                    mean_vals.append(mv)
                    all_y_vals.append(mv)
            if plot_depths:
                ax.plot(plot_depths, mean_vals, marker='.', markersize=8, linewidth=2.1, color=series["color"], 
                        label=series["name"], zorder=3, linestyle=linestyles[j % len(linestyles)])

        ## Grid
        ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
        ax.grid(True, which='both')
        ax.grid(True, which='minor', linestyle=':')

        ax.set_xlabel("# max prefetches", fontsize=fs + 6)
        ax.set_ylabel(y_label, fontsize=fs + 7)

        # ── Format y-axis as percentage ─────────────────────────────────────────
        if i == 0:
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))
        else:
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))

        # ── Format x-axis ───────────────────────────────────────────────────────
        ax.set_xticks(sorted_depths)
        ax.tick_params(axis='x', which='major', pad=0)
        ax.set_xticklabels(sorted_depths, rotation=0, horizontalalignment="center", fontsize=fs-5)
        ax.tick_params(axis='y', labelsize=fs-1)

        if sorted_depths:
            ax.set_xlim(left=min(sorted_depths) - 0.5, right=max(sorted_depths) + 0.5)

        if all_y_vals:
            y_max = max(all_y_vals)
            ax.set_ylim(bottom=0, top=max(y_max * 1.08, 0.01))
            if i == 0:
                # Speedup: 0.5% major tick interval
                ax.yaxis.set_major_locator(mticker.MultipleLocator(0.005))
            elif i == 1:
                # Coverage: 10% major tick interval
                ax.yaxis.set_major_locator(mticker.MultipleLocator(0.10))
            else:
                # Overfetched: leave more headroom up to 110%, but ticks end at 100%.
                ax.set_ylim(bottom=0, top=1.10)
                ax.set_yticks(np.arange(0.0, 1.01, 0.2))

    # Add single figure legend at the top (centered)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.73),
               ncols=len(series_list), fontsize=fs - 1, frameon=True, edgecolor="k",
               columnspacing=1.0, handletextpad=0.4)

    fig.tight_layout(rect=[0, 0, 1, 0.80])
    fig.savefig(f"{APATH}/Sweep_prefetches.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/Sweep_prefetches.pdf")

def plot_speedup_falsePositiveRate():
    stats_keys = {
        "{core}.commitStats0.numInsts": "insts",
        "{core}.numCycles": "cycles",
        "{core}.branchPred.btb.compressedTagFalsePositiveRate": "fpr"
    }

    bms = all_bms
    baseline_cfg = "l1hit-baseline"

    # Define multiple series. (Reused from plot_meanLine)
    series_list = [
        {
            "name": "newDesign_l1hit-5depth",
            "configs": [
                (5, "l1hit-5b"),
                (6, "l1hit-6b"),
                (7, "l1hit-7b"),
                (8, "l1hit-8b"),
                (9, "l1hit-9b"),
                (10, "l1hit-10b"),
                (11, "l1hit-11b"),
                (12, "l1hit-12b"),
                (13, "l1hit-13b"),
                (16, "l1hit-16b"),
            ],
            "color": "#3498db" # Blue
        },
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    all_cfg_names = set([baseline_cfg])
    for series in series_list:
        for _, cfg in series["configs"]:
            all_cfg_names.add(cfg)

    for cfg in all_cfg_names:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            ## Compute IPC
            if "insts" in data[cfg][bm] and "cycles" in data[cfg][bm] and data[cfg][bm]["cycles"] > 0:
                data[cfg][bm]["IPC"] = data[cfg][bm]["insts"] / data[cfg][bm]["cycles"]

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 7.0
    fs = 13
    fig, ax1 = mlp.subplots(figsize=(cw, cw * 0.6))
    fig.patch.set_facecolor('white')

    ax2 = ax1.twinx()  # Create secondary axis

    all_y_vals_speedup = []
    all_y_vals_fpr = []
    
    print("\nMean Speedup and False Positive Rate by Series and Depth:")
    for series in series_list:
        depths = []
        mean_speedups = []
        mean_fprs = []
        
        print(f"  Series: {series['name']}")
        for depth, cfg in series["configs"]:
            # Speedup calculation
            speedup_vals = []
            for bm in bms:
                if bm in data[cfg] and bm in data[baseline_cfg] and "IPC" in data[cfg][bm] and "IPC" in data[baseline_cfg][bm]:
                    impr = (data[cfg][bm]["IPC"] - data[baseline_cfg][bm]["IPC"]) / data[baseline_cfg][bm]["IPC"]
                    speedup_vals.append(impr)
            
            # FPR calculation (no baseline needed)
            fpr_vals = [data[cfg][bm]["fpr"] for bm in bms if bm in data[cfg] and "fpr" in data[cfg][bm]]
            
            if speedup_vals and fpr_vals:
                m_speedup = np.mean(speedup_vals)
                m_fpr = np.mean(fpr_vals)
                
                depths.append(depth)
                mean_speedups.append(m_speedup)
                mean_fprs.append(m_fpr)
                
                all_y_vals_speedup.append(m_speedup)
                all_y_vals_fpr.append(m_fpr)
                
                print(f"    num TagBits {depth:2d}: Speedup {m_speedup*100:6.2f}%, FPR {m_fpr*100:6.2f}%")

        if depths:
            # Plot Speedup as Line Chart on ax1
            ax1.plot(depths, mean_speedups, marker='o', markersize=6, linewidth=1.5, 
                    color=series["color"], label=f"{series['name']} (Speedup)", zorder=5)
            
            # Plot FPR as Bar Chart on ax2
            # Use alpha and a slightly different width/color to distinguish
            ax2.bar(depths, mean_fprs, width=0.8, alpha=0.3, color=series["color"], 
                    edgecolor=series["color"], label=f"{series['name']} (FPR)", zorder=3)

    ## Grid and labels
    ax1.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax1.grid(True, which='both')
    ax1.grid(True, which='minor', linestyle=':')

    ax1.set_xlabel("presence tagArray bits", fontsize=fs - 1)
    ax1.set_ylabel("IPC Improvement", fontsize=fs - 1, color=series_list[0]['color'])
    ax2.set_ylabel("False Positive Rate", fontsize=fs - 1, color='gray')

    # ── Format axes ─────────────────────────────────────────────────────────
    ax1.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=1))

    # ── Format x-axis ───────────────────────────────────────────────────────
    all_depths = set()
    for series in series_list:
        for d, _ in series["configs"]:
            all_depths.add(d)
    ax1.set_xticks(sorted(list(all_depths)))
    
    if all_depths:
        ax1.set_xlim(left=min(all_depths)-1, right=max(all_depths)+1)

    # Auto-adjust y-axis ranges
    if all_y_vals_speedup:
        y_min, y_max = min(all_y_vals_speedup), max(all_y_vals_speedup)
        y_range = y_max - y_min
        if y_range > 0:
            ax1.set_ylim(bottom=y_min - y_range * 0.2, top=y_max + y_range * 0.4)
        else:
            ax1.set_ylim(bottom=y_min - 0.01, top=y_max + 0.02)

    if all_y_vals_fpr:
        y_max_fpr = max(all_y_vals_fpr)
        ax2.set_ylim(bottom=0, top=max(y_max_fpr * 1.5, 0.01))

    # Combined Legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=fs - 4, frameon=True, edgecolor="k", framealpha=1, loc='upper left')

    fig.tight_layout()
    fig.savefig(f"{APATH}/speedup_fpr.pdf", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor="w")
    print(f"Saved {APATH}/speedup_fpr.pdf")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# Plot 3: IPC Improvement  (speedup.pdf)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_Coverage():
    stats_keys = {
        "{core}.branchPred.btb.l1MissL2Hits": "l1MissL2Hits",
        "{core}.branchPred.btb.latePrefetchByL2Hit::total": "partialCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::total": "partialCoveredByPBHit",
        "{core}.branchPred.btb.latePrefetchByL2Hit::2": "partialCoveredByL22",
        "{core}.branchPred.btb.latePrefetchByPBHit::2": "partialCoveredByPBHit2",
        "{core}.branchPred.btb.latePrefetchByL2Hit::1": "partialCoveredByL21",
        "{core}.branchPred.btb.latePrefetchByPBHit::1": "partialCoveredByPBHit1",
        "{core}.branchPred.btb.latePrefetchByL2Hit::4": "fullCoveredByL2",
        "{core}.branchPred.btb.latePrefetchByPBHit::4": "fullCoveredByPBHit",

        "{core}.branchPred.btb.uselessPrefetches::total": "uselessPrefetches",
       
    }

    bms = all_bms

    configs = [
        ("BTB-Ferret", "BTB-Ferret"),
    ]

    # ── Load data ────────────────────────────────────────────────────────────
    data = {}
    for (cfg, cfgn) in configs:
        data[cfg] = {}
        for bm in bms:
            path_pattern = f"{RES_DIR}/{cfg}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if not stats_files:
                continue
            path = stats_files[0]
            data[cfg][bm] = read_stats(path)

            ## Map metrics
            for metric in stats_keys.keys():
                mm = resolve_metric(metric, bm)
                if mm in data[cfg][bm]:
                    data[cfg][bm][stats_keys[metric]] = data[cfg][bm][mm]
                else:
                    data[cfg][bm][stats_keys[metric]] = 0

            ## Compute derived metrics
            # L2_accesses = l1MissL2Hits + partialCoveredByL2 + partialCoveredByPBHit
            l2_acc = data[cfg][bm].get("l1MissL2Hits", 0) + \
                     data[cfg][bm].get("partialCoveredByL2", 0) + \
                     data[cfg][bm].get("partialCoveredByPBHit", 0)
            
            data[cfg][bm]["l2_acc"] = l2_acc
            if l2_acc > 0:
                # Covered = (fullCoveredByL2 + fullCoveredByPBHit) / L2_accesses
                partial = data[cfg][bm].get("partialCoveredByL22", 0) + data[cfg][bm].get("partialCoveredByPBHit2", 0) + \
                          data[cfg][bm].get("partialCoveredByL21", 0) + data[cfg][bm].get("partialCoveredByPBHit1", 0)
                covered = ( partial + data[cfg][bm].get("fullCoveredByL2", 0) + data[cfg][bm].get("fullCoveredByPBHit", 0)) / l2_acc
                data[cfg][bm]["Covered"] = covered
                data[cfg][bm]["Uncovered"] = 1.0 - covered
                # Overpredicted = uselessPrefetches / L2_accesses

                data[cfg][bm]["Overpredicted"] = data[cfg][bm].get("uselessPrefetches", 0) / l2_acc
            else:
                data[cfg][bm]["Covered"] = 0
                data[cfg][bm]["Uncovered"] = 0
                data[cfg][bm]["Overpredicted"] = 0

    # ── Plot ─────────────────────────────────────────────────────────────────
    cw = 8
    fs = 15
    NG = 1
    fig, ax = mlp.subplots(1, NG, figsize=(NG * cw, cw * 0.27), sharex=True, sharey=False)
    fig.patch.set_facecolor('white')

    valid_bms = [bm for bm in bms if all(bm in data[cfg] for (cfg, _) in configs)]
    bms_filtered = valid_bms

    _labels = [renameBms(bm) for bm in bms_filtered] + ["Mean"]
    x = np.arange(len(bms_filtered) + 1, dtype=float)
    x[-1] = x[-1] + 0.4
    x = np.array([xi + 0.2 if "5" in l else xi for xi, l in zip(x, _labels)])

    width = 0.8 / len(configs)
    
    # Segment definitions
    colors_seg = ["#005e8a", "#B4B4B4", "#cc0000"]
    labels_seg = ["Covered", "Uncovered", "Overfetched"]
    hatches = ["", "", "////"]

    for i, (cfg, cfgn) in enumerate(configs):
        y_cov_raw = [data[cfg][bm]["Covered"] for bm in bms_filtered]
        y_unc_raw = [data[cfg][bm]["Uncovered"] for bm in bms_filtered]
        y_ovp_raw = [data[cfg][bm]["Overpredicted"] for bm in bms_filtered]

        # Mean excludes benchmarks with no L2 BTB accesses (l2_acc == 0),
        # since their Covered/Uncovered are undefined (set to 0 by the else branch).
        bms_with_l2 = [bm for bm in bms_filtered if data[cfg][bm].get("l2_acc", 0) > 0]
        m_cov = np.mean([data[cfg][bm]["Covered"] for bm in bms_with_l2]) if bms_with_l2 else 0.0
        m_unc = np.mean([data[cfg][bm]["Uncovered"] for bm in bms_with_l2]) if bms_with_l2 else 0.0
        m_ovp = np.mean([data[cfg][bm]["Overpredicted"] for bm in bms_with_l2]) if bms_with_l2 else 0.0

        y_cov = np.array(y_cov_raw + [m_cov])
        y_unc = np.array(y_unc_raw + [m_unc])
        y_ovp = np.array(y_ovp_raw + [m_ovp])
        
        # Print the data
        print(f"\nData for config: {cfgn} ({cfg})")
        print(f"{'Benchmark':<40} {'Covered':>12} {'Uncovered':>12} {'Overfetched':>12}")
        print("-" * 80)
        for j, bm in enumerate(bms_filtered):
            print(f"{renameBms(bm):<40} {y_cov_raw[j]:>12.4f} {y_unc_raw[j]:>12.4f} {y_ovp_raw[j]:>12.4f}")
        print("-" * 80)
        print(f"{'Mean':<40} {m_cov:>12.4f} {m_unc:>12.4f} {m_ovp:>12.4f}")

        # Position logic to center groups around x
        pos = x + width * i - (width * (len(configs)-1) / 2)
        
        c_hatch = "" if i == 0 else "..."

        # Plot stacked bars
        ax.bar(pos, y_cov, width=width*0.85, color=colors_seg[0], edgecolor="k", zorder=3, 
               hatch=c_hatch, label=labels_seg[0] if i == 0 else None)
        ax.bar(pos, y_unc, width=width*0.85, bottom=y_cov, color=colors_seg[1], edgecolor="k", zorder=3, 
               hatch=c_hatch, label=labels_seg[1] if i == 0 else None)
        ax.bar(pos, y_ovp, width=width*0.85, bottom=y_cov+y_unc, color=colors_seg[2], edgecolor="k", zorder=3, 
               hatch=hatches[2] + c_hatch, label=labels_seg[2] if i == 0 else None)

        ## Add outlier labels
        for idx in range(len(pos)):
            total_h = y_cov[idx] + y_unc[idx] + y_ovp[idx]
            if total_h > 2.5: # 2.5 is the current top cap
                ax.text(pos[idx] - width*0.4, 2.5 - 0.02, f"{total_h*100:.0f}%",
                         size=fs - 6, rotation=90., ha="right", va="top", zorder=5)

    ## Grid
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(True, which='both')
    ax.grid(True, which='minor', linestyle=':')

    ax.set_ylabel("L2-BTB hits[%]", fontsize=fs - 2)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))

    ## Format x-axis
    ax.set_xticks(x)
    ax.tick_params(axis='x', which='major', pad=-2, length=0.1)
    ax.set_xticklabels([])

    ax.set_xlim(xmin=-0.6, xmax=max(x) + 0.6)
    
    # Auto-adjust ylim - capped at 250%
    all_heights = []
    for (cfg, _) in configs:
        for bm in bms_filtered:
            # So total height = 1.0 + overpredicted
            ovp = data[cfg][bm].get("Overpredicted", 0)
            all_heights.append(1.0 + ovp)
    
    max_h = max(all_heights) if all_heights else 1.0
    top = 2.5 # Capped at 250%
    ax.set_ylim(bottom=0, top=top) 

    # Calculate vertical lines dynamically
    bms = bms_filtered
    nspec = sum([1 for b in bms if "5" in b])
    xx = [len(bms)-nspec-1+0.6, len(bms)-1+0.8]
    
    ax.vlines(xx, ymin=-10, ymax=top, color="k", linestyle="--", zorder=2, linewidth=0.7, alpha=0.3)
    ax.fill_between(x=[xx[0], xx[1]], y1=0, y2=top, color="k", alpha=0.1, zorder=1, hatch="////")

    ax.text(xx[0]/2, 0-top*0.05, "Server", size=fs-2, rotation=0.,
             ha="center", va="top")
    ax.text(xx[0]+(xx[1]-xx[0])/2, 0-top*0.05, "SPEC", size=fs-2, rotation=0.,
             ha="center", va="top")
    ax.text(x[-1], 0-top*0.05, "Mean", size=fs-2, rotation=0.,
             ha="center", va="top")

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.2, left=0.1)

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    # Add dummy legend entries for Configs
    # for i, (cfg, cfgn) in enumerate(configs):
    #     h = "" if i == 0 else "..."
    #     handles.append(mpatches.Patch(facecolor='white', edgecolor='k', hatch=h, label=cfgn))
    #     labels.append(cfgn)
    
    ax.legend(handles, labels, loc='lower center', fontsize=fs -3, ncols=len(handles), bbox_to_anchor=(0.5, 0.95),
              labelspacing=0.05, columnspacing=0.8, handletextpad=0.3, borderpad=0.1,
              framealpha=1, edgecolor="k", frameon=True)

    fig.savefig(f"{APATH}/coverage.pdf", dpi=300, bbox_inches='tight', pad_inches=0, facecolor="w")
    print(f"Saved {APATH}/coverage.pdf")

def plot_cdf_histogram():
    cfg_dir = "pf-8sz-20-stats4"
    metrics_templates = ["{core}.branchPred.btb.parallelChains", "{core}.branchPred.btb.prefetchesPerTrigger"]
    for metric_template in metrics_templates:
        fig, ax = mlp.subplots(figsize=(10, 6))
        global_max_bin = 0
        
        # Filter bms to only those that have data
        valid_bms = []
        for bm in all_bms:
            full_metric = resolve_metric(metric_template, bm)
            path_pattern = f"{RES_DIR}/{cfg_dir}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            if stats_files:
                valid_bms.append(bm)
        
        valid_bms.sort()
        
        # Use a high-resolution colormap to ensure unique colors for many benchmarks
        num_bms = len(valid_bms)
        colors = [mlp.get_cmap('nipy_spectral')(i / num_bms) if num_bms > 0 else 'blue' for i in range(num_bms)]
        
        for i, bm in enumerate(valid_bms):
            full_metric = resolve_metric(metric_template, bm)
            path_pattern = f"{RES_DIR}/{cfg_dir}/{bm}/sid*/stats.txt"
            stats_files = glob.glob(path_pattern)
            path = stats_files[0]
            stats = read_stats(path)
            
            bins = []
            counts = []
            prefix = full_metric + "::"
            for stat_name, val in stats.items():
                if stat_name.startswith(prefix):
                    bin_str = stat_name[len(prefix):]
                    if bin_str.isdigit():
                        bin_idx = int(bin_str)
                        if val > 0:
                            bins.append(bin_idx)
                            counts.append(val)
            
            if not bins:
                continue
                
            sorted_indices = np.argsort(bins)
            bins = np.array(bins)[sorted_indices]
            counts = np.array(counts)[sorted_indices]
            
            cumsum = np.cumsum(counts)
            cdf = cumsum / cumsum[-1]
            
            # Smooth line plot for CDF, starting from (0, xxx) where xxx is value at 0.
            if bins[0] > 0:
                plot_bins = np.concatenate(([0], bins))
                plot_cdf = np.concatenate(([0], cdf))
            else:
                plot_bins = bins
                plot_cdf = cdf
            
            ax.plot(plot_bins, plot_cdf, label=renameBms(bm), 
                    color=colors[i], linewidth=1.5)
            
            global_max_bin = max(global_max_bin, np.max(bins))
            
        metric_name = metric_template.split('.')[-1]
        ax.set_title(f"CDF of {metric_name}", fontsize=16)
        ax.set_xlabel("Value", fontsize=14)
        ax.set_ylabel("Cumulative Distribution", fontsize=14)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
        if global_max_bin > 0:
            ax.set_xlim(0, global_max_bin + 1)
        ax.set_ylim(0, 1.05)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Place legend outside to the right
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='x-small', ncol=1)
        
        fig.savefig(f"{APATH}/cdf_{metric_name}.pdf", bbox_inches='tight')
        mlp.close(fig)
        print(f"Saved {APATH}/cdf_{metric_name}.pdf")


if __name__ == "__main__":

    plot_speedup()
    
    plot_Coverage()

    
    
