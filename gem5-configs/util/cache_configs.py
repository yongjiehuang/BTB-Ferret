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
This file contains utilities to create a chache hierarchy
"""


from gem5.isas import ISA

from m5.objects import (
    MultiPrefetcher,
    FetchDirectedPrefetcher,
    TaggedPrefetcher,
    StridePrefetcher,
    L2XBar,
    Cache,
)
from m5.objects import *
from gem5.components.boards.abstract_board import AbstractBoard
# from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.mmu_cache import MMUCache
# from gem5.components.cachehierarchies.classic.private_l1_private_l2_walk_cache_hierarchy import PrivateL1PrivateL2WalkCacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy


class L1ICache(Cache):
    # size = "32KiB"
    # assoc = 8
    size = "64KiB"
    assoc = 16
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 12
    tgts_per_mshr = 20
    writeback_clean = True
    prefetcher = TaggedPrefetcher()


va = True
class L1DCache(Cache):
    size = "48KiB"
    # size = "64KiB"
    assoc = 12
    # assoc = 8
    tag_latency = 4
    data_latency = 4
    response_latency = 4
    # tag_latency = 0
    # data_latency = 0
    # response_latency = 0
    mshrs = 16
    tgts_per_mshr = 20
    writeback_clean = False
    # prefetcher = StridePrefetcher(use_virtual_addresses=va)
    # prefetcher = SignaturePathPrefetcherV2(use_virtual_addresses=va)
    # prefetcher = IrregularStreamBufferPrefetcher(use_virtual_addresses=va)
    prefetcher = BOPPrefetcher(
        use_virtual_addresses=va,
        # rr_size=16,
        # degree=2,
        )
    # prefetcher = SmsPrefetcher(use_virtual_addresses=va)
    # prefetcher = STeMSPrefetcher(use_virtual_addresses=va)
    # prefetcher = STeMSPrefetcher()

class L15DCache(Cache):
    size = "192KiB"
    # size = "64KiB"
    assoc = 12
    # assoc = 8
    tag_latency = 9
    data_latency = 9
    response_latency = 9
    # tag_latency = 0
    # data_latency = 0
    # response_latency = 0
    mshrs = 16
    tgts_per_mshr = 20
    writeback_clean = False
    prefetcher = StridePrefetcher(use_virtual_addresses=True)


class L2Cache(Cache):
    size = "3MiB"
    assoc = 12
    tag_latency = 17
    data_latency = 17
    response_latency = 17
    # tag_latency = 0
    # data_latency = 0
    # response_latency = 0
    mshrs = 256
    tgts_per_mshr = 16
    write_buffers = 256

class L3Cache(Cache):
    size = "8MiB"
    assoc = 16
    tag_latency = 51
    data_latency = 51
    response_latency = 51
    # tag_latency = 0
    # data_latency = 0
    # response_latency = 0
    mshrs = 256
    tgts_per_mshr = 16
    write_buffers = 256



class GNRCacheHierarchy(PrivateL1PrivateL2CacheHierarchy):
    """
    A three level cache hierarchy modelled roughly after Intel's Granit
    Rappid Xeon server CPU:
    - L1I: 64KiB, 16-way, private
    - L1D: 48KiB, 12-way, private
    - L2: 3MiB, 12-way, private
    - L3: 8MiB, 16-way, shared

    Setting `useL15D` adds another 195KiB LD cache between L1 and L2 hence L1.5D
    Setting `fdp` adds the FDP prefetcher to the L1I cache.
    """
    def __init__(self, fdp=True, useL15D=False):
        super().__init__("", "", "")
        self._fdp = fdp
        self._useL15D = useL15D


    def incorporate_cache(self, board: AbstractBoard) -> None:
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_memory().get_mem_ports():
            self.membus.mem_side_ports = port


        ## L1I cache with prefetchers
        self.l1icaches = [
            L1ICache()
            for i in range(board.get_processor().get_num_cores())
        ]
        for i, cpu in enumerate(board.get_processor().cores):

            self.l1icaches[i].prefetcher = MultiPrefetcher()
            if self._fdp:
               pf = FetchDirectedPrefetcher(use_virtual_addresses=True, cpu=cpu.core)
               pf.registerCache(self.l1icaches[i]) # <--- We need to register the cache to enable the probing before issuing
               self.l1icaches[i].prefetcher.prefetchers.append(pf)

            self.l1icaches[i].prefetcher.prefetchers.append(
                    TaggedPrefetcher(use_virtual_addresses=True)
                )

            for pf in self.l1icaches[i].prefetcher.prefetchers:
                pf.registerMMU(cpu.core.mmu)


        self.l1dcaches = [
            L1DCache()
            for i in range(board.get_processor().get_num_cores())
        ]
        for i, cpu in enumerate(board.get_processor().cores):
            self.l1dcaches[i].prefetcher.registerMMU(cpu.core.mmu)

        if self._useL15D:
            self.l15dcaches = [
                L15DCache()
                for i in range(board.get_processor().get_num_cores())
            ]
            self.l15buses = [
                L2XBar() for i in range(board.get_processor().get_num_cores())
            ]

        self.l2buses = [
            L2XBar() for i in range(board.get_processor().get_num_cores())
        ]
        self.l2caches = [
            L2Cache()
            for i in range(board.get_processor().get_num_cores())
        ]
        self.mmucaches = [
            MMUCache(size="8KiB")
            for _ in range(board.get_processor().get_num_cores())
        ]

        self.mmubuses = [
            L2XBar(width=64) for i in range(board.get_processor().get_num_cores())
        ]

        self.l3cache = L3Cache()
        self.l3bus = L2XBar()
        self.membus.cpu_side_ports = self.l3cache.mem_side
        self.l3bus.mem_side_ports = self.l3cache.cpu_side


        if board.has_coherent_io():
            self._setup_io_cache(board)

        for i, cpu in enumerate(board.get_processor().get_cores()):

            cpu.connect_icache(self.l1icaches[i].cpu_side)
            self.l1icaches[i].mem_side = self.l2buses[i].cpu_side_ports

            cpu.connect_dcache(self.l1dcaches[i].cpu_side)
            if self._useL15D:
                self.l1dcaches[i].mem_side = self.l15buses[i].cpu_side_ports
                self.l15dcaches[i].cpu_side = self.l15buses[i].mem_side_ports
                self.l15dcaches[i].mem_side = self.l2buses[i].cpu_side_ports
            else:
                self.l1dcaches[i].mem_side = self.l2buses[i].cpu_side_ports

            self.mmucaches[i].mem_side = self.l2buses[i].cpu_side_ports

            self.mmubuses[i].mem_side_ports = self.mmucaches[i].cpu_side
            self.l2buses[i].mem_side_ports = self.l2caches[i].cpu_side

            self.l3bus.cpu_side_ports = self.l2caches[i].mem_side

            cpu.connect_walker_ports(
                self.mmubuses[i].cpu_side_ports, self.mmubuses[i].cpu_side_ports
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()






##############################################################
# Giant Cache Hierarchy
##############################################################

class L1ICacheGiant(Cache):
    size = "32MiB"
    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 32
    tgts_per_mshr = 20
    writeback_clean = True


class L1DCacheGiant(Cache):
    size = "32MiB"
    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 32
    tgts_per_mshr = 20
    writeback_clean = True


class CacheHierarchyGiant(PrivateL1CacheHierarchy):
    def __init__(self):
        super().__init__(l1d_size="", l1i_size="")

    def incorporate_cache(self, board: AbstractBoard) -> None:
        board.connect_system_port(self.membus.cpu_side_ports)

        for _, port in board.get_mem_ports():
            self.membus.mem_side_ports = port

        self.l1icaches = [
            L1ICacheGiant()
            for i in range(board.get_processor().get_num_cores())
        ]

        self.l1dcaches = [
            L1DCacheGiant()
            for i in range(board.get_processor().get_num_cores())
        ]
        # ITLB Page walk caches
        self.iptw_caches = [
            MMUCache(size="8MiB")
            for _ in range(board.get_processor().get_num_cores())
        ]
        # DTLB Page walk caches
        self.dptw_caches = [
            MMUCache(size="8MiB")
            for _ in range(board.get_processor().get_num_cores())
        ]

        if board.has_coherent_io():
            self._setup_io_cache(board)

        for i, cpu in enumerate(board.get_processor().get_cores()):
            cpu.connect_icache(self.l1icaches[i].cpu_side)
            cpu.connect_dcache(self.l1dcaches[i].cpu_side)

            self.l1icaches[i].mem_side = self.membus.cpu_side_ports
            self.l1dcaches[i].mem_side = self.membus.cpu_side_ports

            self.iptw_caches[i].mem_side = self.membus.cpu_side_ports
            self.dptw_caches[i].mem_side = self.membus.cpu_side_ports

            cpu.connect_walker_ports(
                self.iptw_caches[i].cpu_side, self.dptw_caches[i].cpu_side
            )

            if board.get_processor().get_isa() == ISA.X86:
                int_req_port = self.membus.mem_side_ports
                int_resp_port = self.membus.cpu_side_ports
                cpu.connect_interrupt(int_req_port, int_resp_port)
            else:
                cpu.connect_interrupt()
