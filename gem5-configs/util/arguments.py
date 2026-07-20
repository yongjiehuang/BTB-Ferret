# Copyright (c) 2024 Technical University of Munich
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# Install dependencies

from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA

from .workloads import *
from .workloads import svr_workloads as wlcfg
import argparse


parser = argparse.ArgumentParser(
    description="gem5 configuration script to run a full system simulation"
)

parser.add_argument(
    "--checkpoint-dir",
    type=str,
    default="simpoint-checkpoint",
)

parser.add_argument(
    "--simpoint-dir",
    type=str,
    default="./",
)

parser.add_argument(
    "--simpoint-mode",
    type=str,
    default="",
    choices=["", "analysis", "checkpoint"]
)

parser.add_argument("--sid", type=int)

parser.add_argument(
    "--kernel",
    type=str,
    default="wkdir4/kernel",
    help="The kernel image to boot the system.",
)

parser.add_argument(
    "--disk",
    type=str,
    default="wkdir4/disk.img",
    help="The disk image to boot the system.",
)

parser.add_argument(
    "-w","--workload",
    action="store",
    type=str,
    default="nodeapp",
    choices=wlcfg.keys(),
    help="""Specify a workload that should run in the simulator.""",
)

parser.add_argument(
    "--mode",
    type=str,
    default="setup",
    choices=["setup", "eval",],
    help="""Setup mode: Will boot linux using the kvm core, perform functional
            warming and then take a snapshot.
            Evaluation mode: Will start from a previously taken checkpoint and
            run the actual measurements using the specified core.""",
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
    default=True,
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
    help="Associativity of L3-BTB",
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

args = parser.parse_args()


def isa_to_arch(isa: str) -> str:
    match isa:
        case "X86": return "amd64"
        case "Arm": return "arm64"
        case "RiscV": return "riscv"
        case _: raise ValueError(f"Unsupported ISA: {isa}")