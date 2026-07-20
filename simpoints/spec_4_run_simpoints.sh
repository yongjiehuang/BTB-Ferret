

set -x

GEM5=/home/yongjie/gem5-fdp/build/ARM/gem5.opt
CONFIG=./gem5-configs/spec-simpoint-run.py

SIMPOINT_BASE=/share/david/spec/arm64/simpoints_200M_v2/
CHECKPOINT_BASE=/share/david/spec/arm64/checkpoints_200M_v2/


ARCH="arm64"
CPU_TYPE="o3"


# ------------Benchmarks---------------

BMS=()
BMS+=("500.perlbench_r.checkspam")
BMS+=("500.perlbench_r.diffmail")
# BMS+=("500.perlbench_r.splitmail")
# BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_0")
# BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
# BMS+=("502.gcc_r.gcc-smaller.c-O3_-fipa-pta")
# BMS+=("502.gcc_r.ref32.c_-O3")
# BMS+=("502.gcc_r.ref32.c_-O5")
# BMS+=("505.mcf_r.inp")
#BMS+=("520.omnetpp_r.general")
BMS+=("523.xalancbmk_r.xalanc")
#BMS+=("525.x264_r.x264_pass1")
# BMS+=("525.x264_r.x264_pass2")
BMS+=("525.x264_r.x264")
BMS+=("531.deepsjeng_r.ref")
BMS+=("541.leela_r.ref")
# BMS+=("548.exchange2_r.general")
# BMS+=("557.xz_r.cld")
# BMS+=("557.xz_r.cpu2006docs")
# BMS+=("557.xz_r.input")
# BMS+=("999.specrand_ir.rand")



#------------------------


declare -A simpoints

simpoints["999.specrand_ir.rand"]=2


FACTOR=1
WIDTH=8
NUMFTQENTRIES=24
L1NUMENTRIES=128
L2NUMENTRIES=16384
L3NUMENTRIES=32768
L2ASSOC=8
MAXTAKENPREDPERCYCLE=1
L2LATENCY=4
L3LATENCY=8
TAGELATENCY=4
PBUFFER_SIZE=32
# PPOLICY=0
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --pDepth 2 --togetherArrive"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyCB"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyUB"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit"
# PPOLICY="--pPolicy 6 --noPrefetchLatency"
# PPOLICY="--pPolicy 4 --noPrefetchLatency"
# PPOLICY="--pPolicy 0"
# PPOLICY="--noPrefetchLatency --finalMarkov"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors"
PPOLICY="--noPrefetchLatency --finalMarkov --markovUseRecency"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall"

EXPERIMENT="L1_Prefetch_3"

# ---------------------

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


# Define the output file of your run
RESULTS_DIR="./results/$EXPERIMENT"


if ! pgrep -x "pueued" > /dev/null
then
    pueued -d
fi

PGROUP="$ARCH-$EXPERIMENT"


pueue group add -p 100 "$PGROUP" || true
sudo chown $(id -u) /dev/kvm


for bm in "${BMS[@]}"; do

    # Check if the key exists
    max_sid=4
    if [[ -v simpoints["$bm"] ]]; then
        max_sid=${simpoints["$bm"]}
    fi

    for sid in $(seq 0 $max_sid); do
        RESDIR=${RESULTS_DIR}/$bm/sid$sid

        mkdir -p $RESDIR

        pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
            --outdir=$RESDIR \
            ${CONFIG} \
            --workload $bm \
            --sid $sid \
            --fdp --l1NumEntries $L1NUMENTRIES --l2NumEntries $L2NUMENTRIES --l3NumEntries $L3NUMENTRIES --l2Associativity $L2ASSOC --numFTQEntries $NUMFTQENTRIES \
            --l2Latency $L2LATENCY --l3Latency $L3LATENCY --TAGELatency $TAGELATENCY --factor $FACTOR --width $WIDTH --maxTakenPredPerCycle $MAXTAKENPREDPERCYCLE \
            --pBufferSize $PBUFFER_SIZE $PPOLICY \
            --checkpoint-dir $CHECKPOINT_BASE \
            --simpoint-dir $SIMPOINT_BASE \
            > $RESDIR/gem5.log 2>&1"

    done
done
