# Copyright (c) 2024 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This script is used to run simpoints taken from full-system worloads.
It assumes that checkpoints for each simpoint are already taken. See
`./scripts/simpoint/README`

Usage
-----

gem5 fs-simpoint-run.py --sid=[sid] --workload <workload>

"""

import argparse
from pathlib import Path

from gem5.resources.resource import obtain_resource,KernelResource,DiskImageResource
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.boards.arm_board import ArmBoard
from gem5.components.memory import DualChannelDDR4_2400
from gem5.simulate.exit_event import ExitEvent
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource, SimpointDirectoryResource
from gem5.utils.requires import requires
import m5
from m5.objects import (
    ArmDefaultRelease,
    VExpress_GEM5_V1,
)
from util.workloads import svr_workloads as wlcfg
from util.arguments import *
from util.cpu_configs import *
from util.cache_configs import GNRCacheHierarchy

# requires(isa_required=ISA.X86)
requires(isa_required=ISA.ARM)


memory = DualChannelDDR4_2400(size="3GB")

processor = SimpleProcessor(
    cpu_type=CPUTypes.O3,
    isa=ISA.ARM,
    num_cores=2,
)
cpu = processor.get_cores()[-1].core

config_GNR(cpu, fdp=args.fdp, factor=args.factor, width=args.width, maxTakenPredPerCycle=args.maxTakenPredPerCycle, numFTQEntries=args.numFTQEntries)

#set branch predictor
cpu.branchPred = BPTageSCL(TAGELatency=args.TAGELatency)
cpu.branchPred.btb = BTB(l1NumEntries=args.l1NumEntries,l2NumEntries=args.l2NumEntries,l3NumEntries=args.l3NumEntries,l1Associativity=args.l1Associativity,l2Associativity=args.l2Associativity,l3Associativity=args.l3Associativity,pBufferSize=args.pBufferSize,l2Latency=args.l2Latency,l3Latency=args.l3Latency,
    enableL3=args.enableL3,
    trainBitsOnLookup=args.trainBitsOnLookup,
    trainBitsOnCommit=args.trainBitsOnCommit,
    prefetchOnPrefetchHit=args.prefetchOnPrefetchHit,
    cleanBitsOnL1Promotion=args.cleanBitsOnL1Promotion,
    noPrefetchLatency=args.noPrefetchLatency,
    pDepth=args.pDepth,
    markovUseRecency=args.markovUseRecency,
    limitRet=args.limitRet,
    newPBits=args.newPBits,
    onlyCall=args.onlyCall,
    onlyCallAndBackward=args.onlyCallAndBackward,
    depthOnlyCall=args.depthOnlyCall,
    useCompressedTagFilter=args.useCompressedTagFilter,
    compressedTagBits=args.compressedTagBits,
    forwardLoopExit=args.forwardLoopExit,
    allConditional=args.allConditional,
    maxChainTrackerEntries=args.maxChainTrackerEntries
    )


simpoint_info = SimpointDirectoryResource(
    local_path=Path(f"{args.simpoint_dir}/{args.workload}"),
    simpoint_file="results.simpts",
    weight_file="results.weights",
    simpoint_interval=200_000_000,
    warmup_interval=100_000_000
)

processor.get_cores()[-1]._set_simpoint(
    inst_starts=simpoint_info.get_simpoint_start_insts(),
    board_initialized=False,
)


#  The ArmBoard allows for Full-System ARM simulations.
board = ArmBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=GNRCacheHierarchy(),
    # # The ArmBoard requires a `release` to be specified. This adds all the
    #     # extensions or features to the system. We are setting this to Armv8
    #     # (ArmDefaultRelease) in this example config script.
    release = ArmDefaultRelease.for_kvm(),
    # The platform sets up the memory ranges of all the on-chip and
    # off-chip devices present on the ARM system. ARM KVM only works with
    # VExpress_GEM5_V1 on the ArmBoard at the moment.
    platform = VExpress_GEM5_V1(),
)



kernel_args = [
    'isolcpus=1',
    'cloud-init=disabled',
    'mitigations=off',
    "console=ttyAMA0",
    "lpj=19988480", "norandmaps",
    "root=/dev/vda2",
]

# Here we set a full system workload.
board.set_kernel_disk_workload(
    kernel=KernelResource(args.kernel),
    disk_image=DiskImageResource(args.disk),
    bootloader=obtain_resource("arm64-bootloader"),
    readfile_contents=wlcfg[args.workload]["runscript"](wlcfg[args.workload], 1),
    kernel_args=kernel_args,
    checkpoint=Path("{}/{}/cpt.SimPoint{}".format(args.checkpoint_dir, args.workload, args.sid)),
)

def workitems(start):
    cnt = 1
    while True:
        if start:
            print("Begin Invocation ", cnt)
        else:
            print("End Invocation ", cnt)
            # m5.stats.dump()
            # m5.stats.reset()
            cnt += 1
        yield False

def max_inst():
    warmed_up = False
    while True:
        if warmed_up:
            print("end of SimPoint interval")
            yield True
        else:
            print("end of warmup, starting to simulate SimPoint")
            warmed_up = True
            # Schedule a MAX_INSTS exit event during the simulation
            processor.cores[-1]._set_inst_stop_any_thread(
                simpoint_info.get_simpoint_interval(),
                True
            )
            m5.stats.dump()
            m5.stats.reset()
            yield False


simulator = Simulator(
    board=board,
    on_exit_event={
        ExitEvent.MAX_INSTS: max_inst(),
        ExitEvent.WORKBEGIN: workitems(True),
        ExitEvent.WORKEND: workitems(False),
    },
)

warmup_interval = simpoint_info.get_warmup_list()[args.sid]
if warmup_interval == 0:
    warmup_interval = 1

print(f"Starting simulating SimPoint {args.sid} with weight {simpoint_info.get_weight_list()[args.sid]}")
print(f"Starting warmup interval {warmup_interval}")
processor.cores[-1]._set_inst_stop_any_thread(warmup_interval, False)
simulator.run()

print("Simulation Done")
print(f"Ran SimPoint {args.sid} with weight {simpoint_info.get_weight_list()[args.sid]}")
