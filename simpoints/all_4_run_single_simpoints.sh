set -x

# GEM5=PathTo_BTB-Ferret/gem5/build/ARM/gem5.opt
GEM5=/home/yongjie/BTB-Ferret/gem5/build/ARM/gem5.opt


FACTOR=1
WIDTH=8
NUMFTQENTRIES=16
L1NUMENTRIES=128
L2NUMENTRIES=16384
L2LATENCY=3


L3NUMENTRIES=16384
L3LATENCY=3
L1ASSOC=8
L2ASSOC=8
L3ASSOC=8


MAXTAKENPREDPERCYCLE=1
TAGELATENCY=2
PBUFFER_SIZE=32


ARCH="arm64"
CPU_TYPE="o3"




# --- Select the experiment via command-line argument ---
# Usage: ./all_4_run_single_simpoints.sh --<experiment>
#   --baseline-2level       2-level BTB baseline (no prefetcher)
#   --BTB-Ferret            BTB-Ferret on 2-level BTB
#   --Ideal-BTB             Ideal BTB (L2 latency = 0)
#   --BTB-Ferret-3level     BTB-Ferret on 3-level BTB (enables L3, retunes L2)

EXPERIMENT=""
PPOLICY=""

if [ $# -lt 1 ]; then
    echo "Usage: $0 --<experiment>"
    echo "  --baseline-2level       2-level BTB baseline (no prefetcher)"
    echo "  --BTB-Ferret            BTB-Ferret on 2-level BTB"
    echo "  --Ideal-BTB             Ideal BTB (L2 latency = 0)"
    echo "  --BTB-Ferret-3level     BTB-Ferret on 3-level BTB (enables L3, retunes L2)"
    exit 1
fi

case "$1" in
    --baseline-2level)
        EXPERIMENT="baseline-2level"
        PPOLICY=""
        ;;
    --BTB-Ferret)
        EXPERIMENT="BTB-Ferret"
        PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --limitRet --newPBits --pDepth 14 --maxChainTrackerEntries 8"
        ;;
    --Ideal-BTB)
        EXPERIMENT="Ideal-BTB"
        PPOLICY=""
        L2LATENCY=0
        ;;
    --BTB-Ferret-3level)
        EXPERIMENT="BTB-Ferret-3level"
        PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --limitRet --newPBits --pDepth 14 --maxChainTrackerEntries 8 --enableL3"
        L2NUMENTRIES=6144
        L2LATENCY=1
        L3LATENCY=3
        L2ASSOC=6
        ;;
    *)
        echo "Unknown experiment: $1"
        echo "Usage: $0 --baseline-2level | --BTB-Ferret | --Ideal-BTB | --BTB-Ferret-3level"
        exit 1
        ;;
esac

echo "Selected experiment: $EXPERIMENT (PPOLICY: $PPOLICY)"


# --- Suite Configurations ---

# SPEC 2017
SPEC_BMS=()
SPEC_BMS+=("500.perlbench_r.checkspam")
SPEC_BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
SPEC_BMS+=("505.mcf_r.inp")
SPEC_BMS+=("523.xalancbmk_r.xalanc")
SPEC_BMS+=("525.x264_r.x264")
SPEC_BMS+=("531.deepsjeng_r.ref")
SPEC_BMS+=("541.leela_r.ref")
SPEC_BMS+=("557.xz_r.input")
SPEC_BMS+=("520.omnetpp_r.general")
SPEC_BMS+=("508.namd_r.apoa1")
SPEC_BMS+=("510.parest_r.ref")
SPEC_BMS+=("511.povray_r.ref")
SPEC_BMS+=("519.lbm_r.ref")
SPEC_BMS+=("526.blender_r.ref")
SPEC_BMS+=("538.imagick_r.ref")
SPEC_BMS+=("544.nab_r.ref")

SPEC_CONFIG="./gem5-configs/spec-simpoint-run.py"
SPEC_SIMPOINT_BASE="/share/david/spec/arm64/simpoints_200M_v2/"
SPEC_CHECKPOINT_BASE="/share/david/spec/arm64/checkpoints_200M_v2/"

# SVR
SVR_BMS=()
SVR_BMS+=("nodeapp")
SVR_BMS+=("mediawiki")
SVR_BMS+=("proto")
SVR_BMS+=("dacapo-lusearch")

SVR_BMS+=("tcmalloc")
SVR_BMS+=("benchbase-voter")
SVR_BMS+=("stl")
SVR_BMS+=("dacapo-h2")
SVR_BMS+=("dacapo-h2o")
SVR_BMS+=("dacapo-luindex")
SVR_BMS+=("dacapo-spring")
SVR_BMS+=("dacapo-tomcat")
SVR_BMS+=("renaissance-http")
SVR_BMS+=("benchbase-twitter")
SVR_BMS+=("benchbase-tatp")

SVR_BMS+=("benchbase-epinions")
SVR_BMS+=("benchbase-ycsb")
SVR_BMS+=("benchbase-seats")
SVR_BMS+=("benchbase-sibench")
SVR_BMS+=("benchbase-noop")
SVR_BMS+=("benchbase-smallbank")



SVR_CONFIG="./gem5-configs/svr-simpoint-run.py"
SVR_SIMPOINT_BASE="/share/david/svr/arm64/v2/simpoints_200M/"
SVR_CHECKPOINT_BASE="/share/david/svr/arm64/v2/checkpoints_200M/"
SVR_KERNEL="/share/david/svr/arm64/v2/kernel"
SVR_DISK_IMAGE="/share/david/svr/arm64/v2/disk.img"

# --- Selection ---

# Set to 1 to enable, 0 to disable
RUN_SPEC=1
RUN_SVR=1

# -----------------

# Architecture to ISA mapping
if [ "$ARCH" == "amd64" ]; then
    ISA="X86"
elif [ "$ARCH" == "arm64" ]; then
    ISA="Arm"
elif [ "$ARCH" == "risc" ]; then
    ISA="RiscV"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

RESULTS_DIR="./results/$EXPERIMENT"

# if ! pgrep -x "pueued" > /dev/null; then
#     pueued -d
# fi

PGROUP="$ARCH-$EXPERIMENT"
# pueue group add -p 100 "$PGROUP" || true
sudo chown $(id -u) /dev/kvm

# Execution Loop
for suite in "spec" "svr"; do
    if [ "$suite" == "spec" ] && [ $RUN_SPEC -eq 0 ]; then continue; fi
    if [ "$suite" == "svr" ] && [ $RUN_SVR -eq 0 ]; then continue; fi

    if [ "$suite" == "spec" ]; then
        BMS=("${SPEC_BMS[@]}")
        CONFIG=$SPEC_CONFIG
        SIMPOINT_BASE=$SPEC_SIMPOINT_BASE
        CHECKPOINT_BASE=$SPEC_CHECKPOINT_BASE
        EXTRA_FLAGS=""
    else
        BMS=("${SVR_BMS[@]}")
        CONFIG=$SVR_CONFIG
        SIMPOINT_BASE=$SVR_SIMPOINT_BASE
        CHECKPOINT_BASE=$SVR_CHECKPOINT_BASE
        EXTRA_FLAGS="--kernel $SVR_KERNEL --disk $SVR_DISK_IMAGE --isa=Arm"
    fi

    echo "Starting suite: $suite"

    for bm in "${BMS[@]}"; do
        WEIGHT_FILE="${SIMPOINT_BASE}${bm}/results.weights"
        SIMPTS_FILE="${SIMPOINT_BASE}${bm}/results.simpts"

        if [ -f "$WEIGHT_FILE" ] && [ -f "$SIMPTS_FILE" ]; then
            max_phase=$(join -1 2 -2 2 <(sort -k2,2 "$SIMPTS_FILE") <(sort -k2,2 "$WEIGHT_FILE") | sort -k3,3nr | head -n 1 | awk '{print $2}')
            sid=$(awk '{print $1}' "$SIMPTS_FILE" | sort -n | grep -nx "$max_phase" | cut -d: -f1)
            sid=$((sid - 1))
        else
            echo "Warning: Weight file $WEIGHT_FILE or $SIMPTS_FILE not found for $bm. Skipping."
            continue
        fi

        RESDIR=${RESULTS_DIR}/$bm/sid$sid
        if [ -d "$RESDIR" ]; then
            echo "Skipping $bm (SID: $sid) - Result directory already exists."
            continue
        fi
        mkdir -p $RESDIR

        echo "Enqueuing $suite:$bm (SID: $sid)"

        if [ "$bm" == "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000" ] || [ "$bm" == "511.povray_r.ref" ]; then
            SUDO="sudo"
        else
            SUDO=""
        fi

        $SUDO nohup $GEM5 --outdir=$RESDIR \
            ${CONFIG} \
            --workload $bm \
            --sid $sid \
            --fdp --l1NumEntries $L1NUMENTRIES --l2NumEntries $L2NUMENTRIES --l3NumEntries $L3NUMENTRIES --l1Associativity $L1ASSOC --l2Associativity $L2ASSOC --l3Associativity $L3ASSOC --numFTQEntries $NUMFTQENTRIES \
            --l2Latency $L2LATENCY --l3Latency $L3LATENCY --TAGELatency $TAGELATENCY --factor $FACTOR --width $WIDTH --maxTakenPredPerCycle $MAXTAKENPREDPERCYCLE \
            --pBufferSize $PBUFFER_SIZE $PPOLICY \
            --checkpoint-dir $CHECKPOINT_BASE \
            --simpoint-dir $SIMPOINT_BASE \
            $EXTRA_FLAGS \
            > $RESDIR/gem5.log 2>&1 &
    done
done

echo "All jobs submitted."
