from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA

import argparse
from .specbms import spec_workloads as wlcfg



parser = argparse.ArgumentParser(
    description="gem5 configuration script to run a SPEC 2017 simulations"
)

parser.add_argument("--sid", type=int, required=True)
parser.add_argument("--checkpoint-dir", type=str, default="simpoint-checkpoint",)
parser.add_argument("--simpoint-dir", type=str, default="./",)
parser.add_argument("cmd", nargs=argparse.REMAINDER)
parser.add_argument(
    "--workload",
    type=str,
    required=True,
    choices=list(wlcfg.keys()),
    help="The workload to run",
)

cpu_types = {
    "atomic": CPUTypes.ATOMIC,
    "timing": CPUTypes.TIMING,
    "o3": CPUTypes.O3,
}

parser.add_argument(
    "--cpu-type",
    type=str,
    default="atomic",
    help="The CPU model to use.",
    choices=cpu_types.keys(),
)

parser.add_argument(
    "--fdp",
    action="store_true",
    default=False,
    help="Enable FDP",
)

parser.add_argument(
    "--trainBitsOnLookup",
    action="store_true",
    default=False,
    help="Train prefetch bits on lookup",
)

parser.add_argument(
    "--trainBitsOnCommit",
    action="store_true",
    default=False,
    help="Train prefetch bits on commit",
)

parser.add_argument(
    "--useCompressedTagFilter",
    action="store_true",
    default=False,
    help="Use compressed tag filter",
)

parser.add_argument(
    "--compressedTagBits",
    type=int,
    default=4,
    help="Number of bits for compressed tag array",
)

parser.add_argument(
    "--togetherArrive",
    action="store_true",
    default=False,
    help="2 prefetch arrive at the same time - 2-depth prefetch",
)

parser.add_argument(
    "--prefetchOnL1Hit",
    action="store_true",
    default=False,
    help="Prefetch on L1 hit",
)

parser.add_argument(
    "--prefetchOnPrefetchHit",
    action="store_true",
    default=False,
    help="Prefetch on prefetch hit",
)

parser.add_argument(
    "--pDepth",
    type=int,
    default=1,
    help="Prefetch depth for prefetch-bits prefetcher",
)

parser.add_argument(
    "--cleanBitsOnL1Promotion",
    action="store_true",
    default=False,
    help="Clean prefetch bits on L1 promotion",
)

parser.add_argument(
    "--prefetchOnlyCB",
    action="store_true",
    default=False,
    help="Prefetch only CB",
)

parser.add_argument(
    "--prefetchOnlyUB",
    action="store_true",
    default=False,
    help="Prefetch only UB",
)
parser.add_argument(
    "--noPrefetchLatency",
    action="store_true",
    default=False,
    help="No prefetch latency",
)

parser.add_argument(
    "--finalMarkov",
    action="store_true",
    default=False,
    help="Final markov prefetcher",
)

parser.add_argument(
    "--markovUseRecency",
    action="store_true",
    default=False,
    help="Use recency in markov prefetcher",
)

parser.add_argument(
    "--prefetchAllSuccessors",
    action="store_true",
    default=False,
    help="Prefetch all markov successors",
)

parser.add_argument(
    "--limitRet",
    action="store_true",
    default=False,
    help="Prefetch all markov successors, limit the successor num of RET to 2",
)

parser.add_argument(
    "--newPBits",
    action="store_true",
    default=False,
    help="New prefetch bits prefetcher",
)

parser.add_argument(
    "--enableL3",
    action="store_true",
    default=False,
    help="Enable L3 BTB",
)

parser.add_argument(
    "--onlyCall",
    action="store_true",
    default=False,
    help="New prefetch bits prefetcher",
)

parser.add_argument(
    "--onlyCallAndBackward",
    action="store_true",
    default=False,
    help="New prefetch bits prefetcher",
)

parser.add_argument(
    "--depthOnlyCall",
    action="store_true",
    default=False,
    help="Depth only for call",
)

parser.add_argument(
    "--forwardLoopExit",
    action="store_true",
    default=False,
    help="Prefetch on forward loop exit",
)

parser.add_argument(
    "--allConditional",
    action="store_true",
    default=True,
    help="Prefetch all conditional branches",
)


parser.add_argument(
    "--maxChainTrackerEntries",
    type=int,
    default=4,
    help="Max entries for chain tracker",
)

parser.add_argument(
    "--factor",
    type=int,
    default=1,
    help="Factor for ROB, IQ, LQ, and SQ sizes",
)

parser.add_argument(
    "--l1NumEntries",
    type=int,
    default=128,
    help="Size of L1-BTB",
)

parser.add_argument(
    "--l2NumEntries",
    type=int,
    default=16384,
    help="Size of L2-BTB",
)

parser.add_argument(
    "--l3NumEntries",
    type=int,
    default=32768,
    help="Size of L3-BTB",
)

parser.add_argument(
    "--l1Associativity",
    type=int,
    default=8,
    help="Associativity of L1-BTB",
)

parser.add_argument(
    "--l2Associativity",
    type=int,
    default=8,
    help="Associativity of L2-BTB",
)

parser.add_argument(
    "--l3Associativity",
    type=int,
    default=8,
    help="Associativity of L2-BTB",
)

parser.add_argument(
    "--numFTQEntries",
    type=int,
    default=16,
    help="Number of FTQ entries",
)

parser.add_argument(
    "--width",
    type=int,
    default=8,
    help="Width of the CPU",
)

parser.add_argument(
    "--maxTakenPredPerCycle",
    type=int,
    default=1,
    help="Maximum number of taken predictions per cycle",
)

parser.add_argument(
    "--pBufferSize",
    type=int,
    default=8,
    help="Size of the pBuffer in MultiLevelBTB",
)
parser.add_argument(
    "--TAGELatency",
    type=int,
    default=4,
    help="Latency of TAGE prediction",
)
parser.add_argument(
    "--l2Latency",
    type=int,
    default=4,
    help="Latency of L2 BTB",
)
parser.add_argument(
    "--l3Latency",
    type=int,
    default=8,
    help="Latency of L3 BTB",
)
parser.add_argument(
    "--pPolicy",
    type=int,
    default=0,
    help="l1BTB prefetch policy",
)
isa_choices = {
    "X86": ISA.X86,
    "Arm": ISA.ARM,
    "RiscV": ISA.RISCV,
}

parser.add_argument(
    "--isa",
    type=str,
    default="X86",
    help="The ISA to simulate.",
    choices=isa_choices.keys(),
)


parser.add_argument(
    "--ppc",
    type=int,
    default=1,
    help="The number of prediction per cycle to simulate."
)

parser.add_argument(
    "--data_point",
    type=int,
    default=10,
    help="The number of data points to simulate"
)


args = parser.parse_args()