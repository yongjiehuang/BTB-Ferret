# Copyright (c) 2024 Technical University of Munich
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
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
#

"""
Simple gem5 configuration script to run a binary in syscall emulation mode.
Usage: ./build/<ISA>/gem5.opt se-imple.py <BINARY_PATH> <ARG1> <ARG2> ...

"""

import argparse

from gem5.isas import ISA
from gem5.utils.requires import requires
from gem5.resources.resource import obtain_resource, BinaryResource
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.boards.abstract_board import AbstractBoard
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.private_l1_private_l2_walk_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.simple_core import SimpleCore
from gem5.simulate.simulator import Simulator


isa_choices = {
    "X86": ISA.X86,
    "Arm": ISA.ARM,
    "RiscV": ISA.RISCV,
}

cpu_types = {
    "atomic": CPUTypes.ATOMIC,
    "timing": CPUTypes.TIMING,
    "o3": CPUTypes.O3,
}

parser = argparse.ArgumentParser(
    description="An example configuration script to run a binary in system call emulation"
)

# The only positional argument accepted is the benchmark name in this script.

parser.add_argument(
    "--isa",
    type=str,
    default="X86",
    help="The ISA to simulate.",
    choices=isa_choices.keys(),
)

parser.add_argument(
    "--cpu-type",
    type=str,
    default="atomic",
    help="The CPU model to use.",
    choices=cpu_types.keys(),
)

parser.add_argument("cmd", nargs=argparse.REMAINDER)

args = parser.parse_args()


# This check ensures the gem5 binary is compiled to the correct ISA target.
# If not, an exception will be thrown.
requires(isa_required=isa_choices[args.isa])

# We use a single channel DDR3_1600 memory system
memory = SingleChannelDDR3_1600(size="32MB")

# We use a PrivateL1PrivateL2CacheHierarchy with 32kB L1 caches and 256kB L2
cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32kB", l1i_size="32kB", l2_size="512kB"
)



# Create the processor with one core
processor = SimpleProcessor(
    cpu_type=cpu_types[args.cpu_type], isa=isa_choices[args.isa], num_cores=1
)

print(
    "Running {} on {} CPU: {}".format(
        args.isa, args.cpu_type, args.cmd
    )
)



# The gem5 library simble board which can be used to run simple SE-mode
# simulations.
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)


# Here we set the workload. In this case we want to run a simple "Hello World!"
# program compiled to the ARM ISA. The `Resource` class will automatically
# download the binary from the gem5 Resources cloud bucket if it's not already
# present.
board.set_se_binary_workload(

    binary=BinaryResource(args.cmd[0]),
    arguments=args.cmd[1:],

)


# Lastly we run the simulation.
simulator = Simulator(board=board)
simulator.run()

print(
    "Exiting @ tick {} because {}.".format(
        simulator.get_current_tick(), simulator.get_last_exit_event_cause()
    )
)
