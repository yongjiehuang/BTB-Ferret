# Copyright (c) 2025 Technical University of Munich
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

"""
This script sets up a full system Ubuntu disk image with optional Fetch-Directed Prefetching.
The script boots a full system Ubuntu image and starts the function container.
The function is invoked using a test client.

Please create the checkpoints first by running the fd-simple.py configuration.

Usage
-----

```
scons build/ALL/gem5.opt -j<NUM_CPUS>
./build/ALL/gem5.opt fs-fdp.py
    --workload <benchmark>
    --kernel <path-to-vmlinux> --disk <path-to-disk-image>
    [--cpu <cpu-type>] [--fdp]
```

"""
from pathlib import Path
from typing import Iterator

import m5

from m5.objects import (
    SimpleBTB,
    LTAGE,
    TAGE_SC_L_64KB,
    ITTAGE,
    MultiPrefetcher,
    TaggedPrefetcher,
    FetchDirectedPrefetcher,
    L2XBar,
)
from gem5.resources.resource import obtain_resource,KernelResource,DiskImageResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor


from util.workloads import *
from util.arguments import *

# This check ensures the gem5 binary is compiled to the correct ISA target.
# If not, an exception will be thrown.
requires(isa_required=isa_choices[args.isa])
assert(args.mode == "eval", "This script is only for evaluation mode")

arch = isa_to_arch(args.isa)

# Path to the checkpoint directory
checkpoint_dir = f"wkdir/{arch}/checkpoints"

processor = SimpleProcessor(
    cpu_type=cpu_types[args.cpu_type],
    isa=isa_choices[args.isa],
    num_cores=2,
)
cpu = processor.cores[-1].core


class BTB(SimpleBTB):
    numEntries = 16*1024
    associativity = 8


class BPLTage(LTAGE):
    instShiftAmt = 0
    btb = BTB()
    indirectBranchPred=ITTAGE()
    requiresBTBHit = True


class BPTageSCL(TAGE_SC_L_64KB):
    instShiftAmt = 0
    btb = BTB()
    indirectBranchPred=ITTAGE()
    requiresBTBHit = True


cpu.numROBEntries=576
cpu.LQEntries=190
cpu.SQEntries=120
cpu.numIQEntries=128*2
cpu.fetchBufferSize = 32

# Configure the branch predictor
cpu.branchPred = BPTageSCL()

if args.fdp:
    # We need to configure the decoupled front-end with some specific parameters.
    # First the fetch buffer and fetch target size. We want double the size of
    # the fetch buffer to be able to run ahead of fetch
    cpu.fetchTargetWidth = 64
    cpu.numFTQEntries = 24
    cpu.minInstSize = 1 if args.isa == "X86" else 4
    cpu.decoupledFrontEnd = True
    cpu.bacBranchPredictDelay = 3
    # cpu.fetchQueueSize = 16
    cpu.branchPred.takenOnlyHistory=True



# 2. Instruction prefetcher ---------------------------------------------
# The decoupled front-end is only the first part.
# Now we also need the instruction prefetcher which listens to the
# insertions into the fetch target queue (FTQ) to issue prefetches.


class CacheHierarchy(PrivateL1PrivateL2CacheHierarchy):
    def __init__(self, l1i_size, l1d_size, l2_size):
        super().__init__(l1i_size, l1d_size, l2_size)

    def incorporate_cache(self, board: AbstractBoard) -> None:
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_memory().get_mem_ports():
            self.membus.mem_side_ports = port

        self.l1icaches = [
            L1ICache(size=self._l1i_size)
            for i in range(board.get_processor().get_num_cores())
        ]
        cpu1 = board.get_processor().cores[-1].core

        self.l1icaches[-1].prefetcher = MultiPrefetcher()
        if args.fdp:
            self.l1icaches[-1].prefetcher.prefetchers.append(
                FetchDirectedPrefetcher(use_virtual_addresses=True, cpu=cpu1)
            )
        self.l1icaches[-1].prefetcher.prefetchers.append(
                TaggedPrefetcher(use_virtual_addresses=True)
            )

        for pf in self.l1icaches[-1].prefetcher.prefetchers:
            pf.registerMMU(cpu1.mmu)

        self.l1dcaches = [
            L1DCache(size=self._l1d_size)
            for i in range(board.get_processor().get_num_cores())
        ]
        self.l2buses = [
            L2XBar() for i in range(board.get_processor().get_num_cores())
        ]
        self.l2caches = [
            L2Cache(size=self._l2_size)
            for i in range(board.get_processor().get_num_cores())
        ]
        self.mmucaches = [
            MMUCache(size="8KiB")
            for _ in range(board.get_processor().get_num_cores())
        ]

        self.mmubuses = [
            L2XBar(width=64) for i in range(board.get_processor().get_num_cores())
        ]


        if board.has_coherent_io():
            self._setup_io_cache(board)

        for i, cpu in enumerate(board.get_processor().get_cores()):

            cpu.connect_icache(self.l1icaches[i].cpu_side)
            cpu.connect_dcache(self.l1dcaches[i].cpu_side)

            self.l1icaches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.l1dcaches[i].mem_side = self.l2buses[i].cpu_side_ports
            self.mmucaches[i].mem_side = self.l2buses[i].cpu_side_ports

            self.mmubuses[i].mem_side_ports = self.mmucaches[i].cpu_side
            self.l2buses[i].mem_side_ports = self.l2caches[i].cpu_side

            self.membus.cpu_side_ports = self.l2caches[i].mem_side

            cpu.connect_walker_ports(
                self.mmubuses[i].cpu_side_ports, self.mmubuses[i].cpu_side_ports
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()


cache_hierarchy = CacheHierarchy(
    l1i_size="32KiB", l1d_size="32KiB", l2_size="1MB"
)


memory = DualChannelDDR4_2400(size="3GiB")


# Here we setup the board.
if args.isa == "Arm":
    #  The ArmBoard allows for Full-System ARM simulations.
    from gem5.components.boards.arm_board import ArmBoard
    from m5.objects import (
        ArmDefaultRelease,
        VExpress_GEM5_V1,
    )

    board = ArmBoard(
        clk_freq="3GHz",
        processor=processor,
        memory=memory,
        cache_hierarchy=cache_hierarchy,
        # The ArmBoard requires a `release` to be specified. This adds all the
        # extensions or features to the system. We are setting this to Armv8
        # (ArmDefaultRelease) in this example config script.
        release = ArmDefaultRelease.for_kvm(),
        # The platform sets up the memory ranges of all the on-chip and
        # off-chip devices present on the ARM system. ARM KVM only works with
        # VExpress_GEM5_V1 on the ArmBoard at the moment.
        platform = VExpress_GEM5_V1(),
    )

elif args.isa == "X86":
    # The X86Board allows for Full-System X86 simulations.
    from gem5.components.boards.x86_board import X86Board
    board = X86Board(
        clk_freq="3GHz",
        processor=processor,
        memory=memory,
        cache_hierarchy=cache_hierarchy,
    )
else:
    raise ValueError("ISA not supported")


def executeExit() -> Iterator[bool]:
    print("Simulation done")
    m5.stats.dump()
    yield True


delta = 50_000_000

def maxInsts() -> Iterator[bool]:
    sim_instr = 0
    max_instr = 1_000_000_000

    while True:
        m5.stats.dump()
        m5.stats.reset()
        sim_instr += delta
        print("Simulated Instructions: ", sim_instr)
        processor.cores[-1]._set_inst_stop_any_thread(delta, True)
        if sim_instr >= max_instr:
            yield True
        yield False


kernel_args = [
    'isolcpus=1',
    'cloud-init=disabled',
    'mitigations=off',
]
if args.isa == "Arm":
    kernel_args += [
        "console=ttyAMA0",
        "lpj=19988480", "norandmaps",
        "root=/dev/vda2",
    ]
elif args.isa == "X86":
    kernel_args += [
        "console=ttyS0",
        "lpj=7999923",
        "root=/dev/sda2",
    ]

# Here we set a full system workload.
board.set_kernel_disk_workload(
    kernel=KernelResource(args.kernel),
    disk_image=DiskImageResource(args.disk),
    bootloader=obtain_resource("arm64-bootloader") if args.isa == "Arm" else None,
    readfile_contents=wlcfg[args.workload]["runscript"](wlcfg[args.workload], 1),
    kernel_args=kernel_args,
    checkpoint=Path("{}/{}".format(checkpoint_dir, args.workload)),
)

class MySimulator(Simulator):
    def get_last_exit_event_code(self):
        return self._last_exit_event.getCode()


# We define the system with the aforementioned system defined.
simulator = MySimulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: executeExit(),
        ExitEvent.MAX_INSTS: maxInsts(),
    },
)


if args.mode == "eval":
    processor.cores[-1]._set_inst_stop_any_thread(delta, False)


simulator.run()
