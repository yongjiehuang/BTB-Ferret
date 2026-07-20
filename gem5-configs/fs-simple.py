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
This script further shows an example of booting a full system Ubuntu
disk image. The script boots a full system Ubuntu image and starts the function container.
The function is invoked using a test client.

The workflow has two steps
1. Use the "setup" mode to boot the full system from scratch using the KVM core. The
   script will perform functional warming and then take a checkpoint of the system.
2. Use the "eval" mode to start from the previously taken checkpoint and perform
   the actual measurements using a detailed core model.

Usage
-----

```
scons build/ALL/gem5.opt -j<NUM_CPUS>
./build/ALL/gem5.opt fs-simple.py
    --mode <setup/eval> --workload <benchmark>
    --kernel <path-to-vmlinux> --disk <path-to-disk-image>
    [--cpu <cpu-type>]
```

"""
from pathlib import Path
from typing import Iterator

import m5
from gem5.resources.resource import obtain_resource,KernelResource,DiskImageResource
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.memory import DualChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor


from util.workloads import *
from util.arguments import *

# This check ensures the gem5 binary is compiled to the correct ISA target.
# If not, an exception will be thrown.
requires(isa_required=isa_choices[args.isa])

arch = isa_to_arch(args.isa)

# Path to the checkpoint directory
checkpoint_dir = f"wkdir/{arch}/checkpoints"
if args.mode == "setup":
    Path("{}/{}".format(checkpoint_dir, args.workload)).mkdir(parents=True, exist_ok=True)


# Here we setup the processor. For booting we take the KVM core and
# for the evaluation we can take ATOMIC, TIMING or O3

processor = SimpleProcessor(
    cpu_type=CPUTypes.KVM if args.mode=="setup" else cpu_types[args.cpu_type],
    isa=isa_choices[args.isa],
    num_cores=2,
)
cpu = processor.cores[-1].core

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32KiB", l1i_size="32KiB", l2_size="1MiB"
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
    if args.mode == "setup":
        print("Setup done")
    else:
        print("Simulation done")

    m5.stats.dump()
    yield True



def executeFail() -> Iterator[bool]:

    while True:
        fc = simulator.get_last_exit_event_code()
        print("Fail code: ", fc)
        if fc == 4:
            if args.mode == "setup":
                m5.checkpoint("{}/{}".format(checkpoint_dir, args.workload))
                m5.stats.dump()
                m5.stats.reset()

        yield False



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
    checkpoint=Path("{}/{}".format(checkpoint_dir, args.workload)) if args.mode=="eval" else None,
)

class MySimulator(Simulator):
    def get_last_exit_event_code(self):
        return self._last_exit_event.getCode()


# We define the system with the aforementioned system defined.
simulator = MySimulator(
    board=board,
    on_exit_event={
        ExitEvent.EXIT: executeExit(),
        ExitEvent.FAIL: executeFail(),
        ExitEvent.MAX_INSTS: maxInsts(),
    },
)



if args.mode == "eval":
    processor.cores[-1]._set_inst_stop_any_thread(delta, False)

simulator.run()
