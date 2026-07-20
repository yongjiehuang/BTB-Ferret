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
This file contains utility functions for configuring the CPU core
"""

from m5.objects import (
    SimpleBTB,
    MultiLevelBTB,
    LocalBP,
    TAGE_SC_L_64KB,
    TAGE_SC_L_TAGE_64KB,
    ITTAGE,
    BranchPredictor,
)
from m5.objects.FuncUnit import *
from m5.objects.FuncUnitConfig import *
from m5.objects.FUPool import *


#############################################################
######################### Functions #########################
############################################################


#This function rounds the number to the closet power of 2
def RTCPO2(n):
    if n < 1:
        return 1
    lower = 1 << (n.bit_length() - 1)
    upper = lower << 1
    return lower if (n - lower) < (upper - n) else upper

def scale_registers(cpu_, factor):

    cpu_.numPhysIntRegs = 500 * factor
    cpu_.numPhysFloatRegs = 400 * factor
    cpu_.numPhysVecRegs = min(256 * factor, 512)
    cpu_.numPhysVecPredRegs = 32 * factor
    cpu_.numPhysMatRegs = 2 * factor
    cpu_.numPhysCCRegs = 5*cpu_.numPhysIntRegs
    return

def set_width(cpu_, width):
    cpu_.fetchWidth = width
    cpu_.decodeWidth = width
    cpu_.renameWidth = width
    cpu_.issueWidth = width
    cpu_.wbWidth = width
    cpu_.commitWidth = width
    cpu_.squashWidth = 5*width
    cpu_.dispatchWidth = width

# Configure the CPU with the specified arguments
def configure_cpu_multi_ppc(cpu, args):
    if not args.fdp:
        exit("This script is meant to be used with FDP enabled for mutiple branch prediction. Please use the --fdp flag.")

    #Enable the decoupled front-end
    cpu.decoupledFrontEnd = True
    #set branch predictor
    cpu.branchPred = BPTageSCL(args.inf_tage)
    cpu.branchPred.btb = BTB(args.factor)
    #configure frontend
    cpu.fetchBufferSize = 64
    cpu.fetchQueueSize = 128 * args.factor
    cpu.fetchTargetWidth = 64
    cpu.minInstSize = 1 if args.isa == "X86" else 4

        # Set size of relevant buffers
    cpu.numFTQEntries = 50 * args.factor
    cpu.numROBEntries = 576 * args.factor
    cpu.numIQEntries = 300 * 2 * args.factor
    cpu.LQEntries = 200 * args.factor
    cpu.SQEntries = 200 * args.factor

    # configure multiple branch prediction
    if args.ppc > 0:
        cpu.maxPrefetchesPerCycle= 2* args.ppc
        cpu.maxOutstandingTranslations=8 * args.ppc
        cpu.maxOutstandingPrefetches=8 * args.ppc
        cpu.numPredPerCycle = args.ppc

    # Enable the Fetch target queue to store the fetch block information
    if args.fbInFTQ:
        cpu.enableFBinFTQ = True

    # Custom functional unit configuration
    cpu.fuPool = S_FUPool(args.factor)

    # Return address stack size
    cpu.branchPred.ras.numEntries=128

    # Scaling the number of registers used for renaming
    scale_registers(cpu, args.factor)


    #Setting the width of the different stages
    set_width (cpu, args.width)

    if args.big_squash:
        cpu.squashWidth = cpu.numROBEntries

    #tuning phast
    if args.inf_phast:
        cpu.phast_num_rows = 256
        cpu.phast_associativity = 16
        cpu.phast_tag_bits = 20
        cpu.phast_max_counter = 100
        cpu.LSQDepCheckShift = 0

    #tune mmu
    cpu.mmu.l2_shared.size = RTCPO2(3840 * args.factor)
    cpu.mmu.l2_shared.assoc = 8
    cpu.mmu.itb.size = RTCPO2(256 * args.factor)
    cpu.mmu.dtb.size = RTCPO2(256 * args.factor)
    cpu.mmu.stage2_itb.size = RTCPO2(256 * args.factor)
    cpu.mmu.stage2_dtb.size = RTCPO2(256 * args.factor)





def config_GNR(cpu, fdp=True, factor=2, width=16, maxTakenPredPerCycle=1, numFTQEntries=16):
    """
    Configuration for Intel Xeon Granit Rapid
    8-wide, 576-entry ROB
    """

    # Pipeline delays
    cpu.fetchToDecodeDelay = 8
    cpu.decodeToFetchDelay = 2
    cpu.decodeToRenameDelay = 2
    cpu.renameToIEWDelay = 3
    cpu.issueToExecuteDelay = 1
    cpu.iewToCommitDelay = 2

    cpu.forwardComSize = 19
    cpu.backComSize = 19

    # Pipeline widths
    cpu.fetchWidth = width
    cpu.decodeWidth = width
    cpu.renameWidth = width
    cpu.issueWidth = 2*width
    # cpu.issueWidth = 12
    cpu.dispatchWidth = width
    cpu.wbWidth = 2*width
    cpu.commitWidth = 2*width
    # cpu.commitWidth = 12
    # cpu.squashWidth = 3 * width * factor
    # cpu.squashWidth = 12

    cpu.fuPool = S_FUPool()


    cpu.fetchBufferSize = 64
    cpu.fetchQueueSize = 128 * factor
    cpu.fetchTargetWidth = 64
    cpu.minInstSize = 2

    # Set size if relevant buffers
    cpu.numFTQEntries = 16 * factor
    # Modified
    cpu.maxTakenPredPerCycle = maxTakenPredPerCycle
    cpu.numROBEntries = 576 * factor
    cpu.numIQEntries = 576 * factor
    cpu.LQEntries = 189 * factor
    cpu.SQEntries = 120 * factor
    cpu.LFSTSize = 1024 * factor
    cpu.SSITSize = "1024"


    #tune mmu
    cpu.mmu.l2_shared.size = 2048 * factor
    cpu.mmu.l2_shared.assoc = 8
    cpu.mmu.itb.size = 256 * factor
    cpu.mmu.itb.assoc = 8
    cpu.mmu.dtb.size = 128 * factor
    cpu.mmu.dtb.size = 16
    cpu.mmu.stage2_itb.size = 256 * factor
    cpu.mmu.stage2_dtb.size = 128 * factor


    cpu.numPhysIntRegs = 512 * factor
    cpu.numPhysFloatRegs = 406 * factor
    cpu.numPhysVecRegs = min(256 * factor, 512)
    cpu.numPhysVecPredRegs = 32 * factor
    cpu.numPhysMatRegs = 2 * factor
    cpu.numPhysCCRegs = 5*cpu.numPhysIntRegs



    if fdp:
        #Enable the decoupled front-end
        cpu.decoupledFrontEnd = True
        cpu.fetchTargetWidth = 64
        cpu.minInstSize = 4

        # Set size of relevant buffers
        cpu.numFTQEntries = numFTQEntries





#############################################################
########### Classes for the different components ###########
############################################################
# class BTB(SimpleBTB):
#     numEntries = 16 * 1024
#     tagBits = 16
#     associativity = 8

class BTB(MultiLevelBTB):
    def __init__(self, l1NumEntries=128, l2NumEntries=16384, l3NumEntries=32768, l1Associativity=8, l2Associativity=8, l3Associativity=8, pBufferSize=8, l2Latency=4, l3Latency=8,
        enableL3=False,
        trainBitsOnLookup=False,
        trainBitsOnCommit=False,
        togetherArrive=False,
        prefetchOnPrefetchHit=False,
        cleanBitsOnL1Promotion=False,
        noPrefetchLatency=False,
        pDepth=1,
        finalMarkov=False,
        markovUseRecency=False,
        prefetchAllSuccessors=False,
        limitRet=False,
        newPBits=False,
        onlyCall=False,
        onlyCallAndBackward=False,
        depthOnlyCall=False,
        prefetchOnlyCB=False,
        prefetchOnlyUB=False,
        useCompressedTagFilter=False,
        compressedTagBits=4,
        forwardLoopExit=False,
        allConditional=False,
        maxChainTrackerEntries=4,
        ):
        super().__init__()
        self.l1NumEntries = l1NumEntries
        self.l1Associativity = l1Associativity
        self.l1Latency = 0
        self.l2NumEntries = l2NumEntries
        self.l2Associativity = l2Associativity
        self.l2Latency = l2Latency
        self.l3NumEntries = l3NumEntries
        self.l3Associativity = l3Associativity
        self.l3Latency = l3Latency
        self.enableL3 = enableL3
        self.pBufferSize = pBufferSize
        self.trainBitsOnLookup = trainBitsOnLookup
        self.trainBitsOnCommit = trainBitsOnCommit
        self.prefetchOnPrefetchHit = prefetchOnPrefetchHit
        self.cleanBitsOnL1Promotion = cleanBitsOnL1Promotion
        self.noPrefetchLatency = noPrefetchLatency
        self.prefetchDepth = pDepth
        self.markovUseRecency = markovUseRecency
        self.limitRet = limitRet
        self.newPBits = newPBits
        self.onlyCall = onlyCall
        self.onlyCallAndBackward = onlyCallAndBackward
        self.depthOnlyCall = depthOnlyCall
        self.useCompressedTagFilter = useCompressedTagFilter
        self.compressedTagBits = compressedTagBits
        self.forwardLoopExit = forwardLoopExit
        self.allConditional = allConditional
        self.maxChainTrackerEntries = maxChainTrackerEntries

class TAGE_Inf_N(TAGE_SC_L_64KB):
    tage = TAGE_SC_L_TAGE_64KB(
        logTagTableSize = 20,
        shortTagsSize = 20,
        longTagsSize = 20,
    )


class BPTageSCL(BranchPredictor):
    def __init__(self, inf_tage :bool = False, TAGELatency=4):
        super().__init__()
        if inf_tage:
            self.indirectBranchPred.itage.tagTableTagWidths = [
                0,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                ]
            self.indirectBranchPred.itage.logTagTableSizes = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
            self.conditionalBranchPred = TAGE_Inf_N()
        else:
            self.conditionalBranchPred = TAGE_SC_L_64KB()
            self.conditionalBranchPred.latency = TAGELatency
            # self.conditionalBranchPred = LocalBP(
            #     latency = 0,
            #     localPredictorSize = 16 * 1024,
            #     localCtrBits = 2
            # )

            # self.overridingBranchPred = TAGE_SC_L_64KB(
            #     latency = 4
            # )
            

    instShiftAmt = 2
    indirectBranchPred = ITTAGE()
    requiresBTBHit = True
    updateBTBAtSquash = True


# -------------- Backend Configutation --------- #
#-----------------------------------------------
class S_IntALU(IntALU):
    def __init__(self, factor):
        super().__init__()
        self.count = 12 * factor

class S_IntMultDiv(IntMultDiv):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_FP_ALU(FP_ALU):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_FP_MultDiv(FP_MultDiv):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_SIMD_Unit(SIMD_Unit):
    def __init__(self, factor):
        super().__init__()
        self.count = 6 * factor

class S_Matrix_Unit(Matrix_Unit):
    def __init__(self, factor):
        super().__init__()
        self.count = 1 * factor

class S_PredALU(PredALU):
    def __init__(self, factor):
        super().__init__()
        self.count = 1 * factor

class S_ReadPort(ReadPort):
    def __init__(self, factor):
        super().__init__()
        self.count = 4 * factor

class S_WritePort(WritePort):
    def __init__(self, factor):
        super().__init__()
        self.count = 4 * factor

class S_RdWrPort(RdWrPort):
    def __init__(self, factor):
        super().__init__()
        self.count = 8 * factor

class S_System_Unit(System_Unit):
    def __init__(self, factor):
        super().__init__()
        self.count = 1 * factor

class S_FUPool(FUPool):
    def __init__(self, factor=1):
        super().__init__()
        self.FUList = [
            S_IntALU(factor=factor),
            S_IntMultDiv(factor=factor),
            S_FP_ALU(factor=factor),
            S_FP_MultDiv(factor=factor),
            S_ReadPort(factor=factor),
            S_SIMD_Unit(factor=factor),
            S_Matrix_Unit(factor=factor),
            S_PredALU(factor=factor),
            S_WritePort(factor=factor),
            S_RdWrPort(factor=factor),
            S_System_Unit(factor=factor),
        ]
#-----------------------------------------------
#-----------------------------------------------#

