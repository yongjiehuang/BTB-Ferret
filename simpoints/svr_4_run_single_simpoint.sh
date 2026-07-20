

set -x


GEM5=/home/yongjie/gem5-fdp/build/ARM/gem5.opt
CONFIG=./gem5-configs/svr-simpoint-run.py

SIMPOINT_BASE=/share/david/svr/arm64/v2/simpoints_200M/
CHECKPOINT_BASE=/share/david/svr/arm64/v2/checkpoints_200M/
KERNEL=/share/david/svr/arm64/v2/kernel
DISK_IMAGE=/share/david/svr/arm64/v2/disk.img

ARCH="arm64"
CPU_TYPE="o3"



BMS=()



BMS+=("nodeapp")

BMS+=("mediawiki") 
BMS+=("proto")
# lusearch - voter not run for exploration
BMS+=("dacapo-lusearch")
BMS+=("swissmap")
BMS+=("benchbase-otmetrics")
# BMS+=("libc")  
BMS+=("tcmalloc")
BMS+=("benchbase-voter")
# BMS+=("compression") 
# BMS+=("hashing")
BMS+=("stl")

## Java BMS
# BMS+=("dacapo-cassandra") 
BMS+=("dacapo-h2")
BMS+=("dacapo-h2o")
BMS+=("dacapo-kafka")
BMS+=("dacapo-luindex")

BMS+=("dacapo-spring")
BMS+=("dacapo-tomcat")
BMS+=("renaissance-http")
# BMS+=("renaissance-chirper")


# BMS+=("benchbase-tpcc")
BMS+=("benchbase-twitter")
# BMS+=("benchbase-wikipedia")

BMS+=("benchbase-tatp")
BMS+=("benchbase-resourcestresser")
BMS+=("benchbase-epinions")
BMS+=("benchbase-ycsb") 
BMS+=("benchbase-seats")
# BMS+=("benchbase-auctionmark")
# BMS+=("benchbase-chbenchmark")

BMS+=("benchbase-sibench")
BMS+=("benchbase-noop")
BMS+=("benchbase-smallbank")
# BMS+=("benchbase-hyadapt")



# -----------------------


#------------------------


declare -A simpoints

simpoints["nodeapp"]=2
simpoints["hashing"]=3
simpoints["benchbase-tpcc"]=2
simpoints["benchbase-wikipedia"]=2
simpoints["benchbase-auctionmark"]=2

FACTOR=1
WIDTH=8
NUMFTQENTRIES=16
L1NUMENTRIES=128
L2NUMENTRIES=16384
L3NUMENTRIES=32768
L2ASSOC=8
MAXTAKENPREDPERCYCLE=1
L2LATENCY=4
L3LATENCY=8
TAGELATENCY=2
PBUFFER_SIZE=32
# PPOLICY=0
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --pDepth 2 --togetherArrive"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency --useCompressedTagFilter --compressedTagBits 3"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyCB"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyUB"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --noPrefetchLatency"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --pDepth 3"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --prefetchOnL1Hit --pDepth 2"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors"
# PPOLICY="--pPolicy 6 --noPrefetchLatency"
# PPOLICY="--pPolicy 4 --noPrefetchLatency"
# PPOLICY="--pPolicy 0"
# PPOLICY="--noPrefetchLatency --finalMarkov"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --limitRet"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --markovUseRecency"

# EXPERIMENT="B-BTB_2FT"
# EXPERIMENT="B-BTB_optimal_BTB_2FT"
# EXPERIMENT="B-BTB_32L1"
# EXPERIMENT="B-BTB_64L1"
# EXPERIMENT="B-BTB_256L1"
# EXPERIMENT="B-BTB_512L1"
# EXPERIMENT="B-BTB_optimal_BTB_32L1"
# EXPERIMENT="B-BTB_optimal_BTB_64L1"
# EXPERIMENT="B-BTB_optimal_BTB_256L1"
# EXPERIMENT="B-BTB_optimal_BTB_512L1"
# EXPERIMENT="Lookup-prefetchChain-cleanBit-noLat"
# EXPERIMENT="Lookup-prefetchChain-noLat"
# EXPERIMENT="Commit-prefetchChain-noLat"
# EXPERIMENT="Commit-prefetchChain-cleanBit-noLat"
# EXPERIMENT="Lookup-prefetchChain"
# EXPERIMENT="B-BTB_spatial_noLat"
# EXPERIMENT="B-BTB_markov_noLat"
# EXPERIMENT="Commit-prefetchChain-noLat-2depth"



# l2btb access + atSquash
# EXPERIMENT="baseline-latest"
# EXPERIMENT="optimal_BTB-latest"
# EXPERIMENT="Commit-prefetchChain-latest"
# EXPERIMENT="Commit-prefetchChain-2depth-latest"
# EXPERIMENT="markov_onMiss-latest"
# EXPERIMENT="spatial-latest"
# EXPERIMENT="spatial-noLat-latest"
# EXPERIMENT="Commit-prefetchChain-noLat-latest"
# EXPERIMENT="finalMarkov-noLat"
# EXPERIMENT="finalMarkov-noLat-all"
# EXPERIMENT="Commit-prefetchChain-bothForCall-latest"
# EXPERIMENT="markov_onMiss-noLat-latest"
# EXPERIMENT="Commit-prefetchChain-2together-latest"

# EXPERIMENT="Commit-prefetchChain-bothForCall-cls"
# EXPERIMENT="finalMarkov-noLat-all-cls"
# EXPERIMENT="Commit-prefetchChain-cls"
# EXPERIMENT="finalMarkov-noLat-recency-cls"

#single simpoint 
EXPERIMENT="Commit-prefetchChain-onlyCB"
EXPERIMENT="Commit-prefetchChain-onlyUB"
EXPERIMENT="baseline-24FT-single"
EXPERIMENT="PBits_noPlat-24FT-single"
EXPERIMENT="finalMarkov-noLat-24FT-single"
EXPERIMENT="optimal_BTB-24FT-single"

# EXPERIMENT="baseline-24FT-noFDP-single"
# EXPERIMENT="PBits_noPlat-24FT-noFDP-single"
# EXPERIMENT="finalMarkov-noLat-24FT-noFDP-single"
# EXPERIMENT="optimal_BTB-24FT-noFDP-single"

# EXPERIMENT="baseline-2FT-single"
# EXPERIMENT="PBits_noPlat-2FT-single"
# EXPERIMENT="finalMarkov-noLat-2FT-single"
# EXPERIMENT="optimal_BTB-2FT-single"

EXPERIMENT="baseline-16FT-single"
EXPERIMENT="optimal_BTB-16FT-single"
EXPERIMENT="PBits_noLat-16FT-single"
EXPERIMENT="finalMarkov-noLat-16FT-single"

EXPERIMENT="baseline-2FT-single"
# EXPERIMENT="optimal_BTB-2FT-single"
# EXPERIMENT="PBits_noLat-2FT-single"
# EXPERIMENT="finalMarkov-noLat-2FT-single"


# EXPERIMENT="baseline-2FT-noFDP-single"
# EXPERIMENT="PBits_noPlat-2FT-noFDP-single"
# EXPERIMENT="finalMarkov-noLat-2FT-noFDP-single"
# EXPERIMENT="optimal_BTB-2FT-noFDP-single"

EXPERIMENT="baseline-1FT-noFDP-single"
EXPERIMENT="PBits_noLat-1FT-noFDP-single"
EXPERIMENT="finalMarkov-noLat-1FT-noFDP-single"
# EXPERIMENT="optimal_BTB-1FT-noFDP-single"


EXPERIMENT="baseline-16FT-update"
EXPERIMENT="baseline-16FT-graph"
# EXPERIMENT="optimal_Both-16FT-update"
# EXPERIMENT="optimal_BTB-16FT-update"
# EXPERIMENT="PBits_noLat-16FT-update"
# EXPERIMENT="PBits-16FT-update"
# EXPERIMENT="PBits-16FT-bothCall-update"
# EXPERIMENT="PBits_noLat-16FT-bothCall-update"
# EXPERIMENT="PBits_noLat-16FT-bothCall-limitRet-update"
# EXPERIMENT="finalMarkov-noLat-16FT-update"
# EXPERIMENT="finalMarkovAll-noLat-16FT-update"
# EXPERIMENT="finalMarkovRec-noLat-16FT-update"
# EXPERIMENT="spatial-noLat-16FT-update"
# EXPERIMENT="PBits_noLat-16FT-dump"
# EXPERIMENT="finalMarkovAll-noLat-16FT-limitRet-l1hit"
# EXPERIMENT="finalMarkovAll-noLat-16FT-l1hit"
# EXPERIMENT="finalMarkov-noLat-16FT-l1hit"
# EXPERIMENT="oldMarkov-noLat-16FT"

EXPERIMENT="baseline-16FT-bb"
EXPERIMENT="optimal_BTB-16FT-bb"
EXPERIMENT="optimal_Both-16FT-bb"



EXPERIMENT="baseline-16FT-override"
EXPERIMENT="optimal_BTB-16FT-override"
EXPERIMENT="optimal_Both-16FT-override"
EXPERIMENT="PBits_noLat-16FT-override"
# EXPERIMENT="PBits_noLat-16FT-test"
# EXPERIMENT="optimal_Both-16FT-test"
EXPERIMENT="markovAll-noLat-16FT-override"
EXPERIMENT="markovAll-noLat-limitRet-16FT-override"

# EXPERIMENT="PBits-16FT-override"


EXPERIMENT="PBits-bothCall-16FT-single"
EXPERIMENT="PBits-bothCall-limitRet-16FT-single"
# EXPERIMENT="PBits-bothCall-limitRet-16FT-override"
EXPERIMENT="PBits-bothCall-limitRet-16FT-2dep-single"
EXPERIMENT="optimal_BTB-single"
# EXPERIMENT="PBits-bothCall-16FT-override"
EXPERIMENT="baseline-single"
EXPERIMENT="PBits-noLat-single"
EXPERIMENT="Markov-noLat-single"
EXPERIMENT="PBits-single"
EXPERIMENT="PBits-callRet-2dep-single"
EXPERIMENT="PBits-callRet-l1hit-single"
EXPERIMENT="PBits-bothCall-limitRet-16FT-3dep-single"
EXPERIMENT="PBits-callRet-l1hit-2dep-single"
# EXPERIMENT="PBits-bothCall-limitRet-noLat-16FT-override"

# EXPERIMENT="PBits-16FT-l1hit-override"
# EXPERIMENT="PBits-16FT-l1hit-2dep-override"


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


pueue group add -p 70 "$PGROUP" || true
sudo chown $(id -u) /dev/kvm


for bm in "${BMS[@]}"; do

   #find sid with the max weight
   WEIGHT_FILE="${SIMPOINT_BASE}${bm}/results.weights"

   SIMPTS_FILE="${SIMPOINT_BASE}${bm}/results.simpts"

   # results.simpts: <phase> <index>
   # results.weights: <weight> <index>
   max_phase=$(join -1 2 -2 2 <(sort -k2,2 "$SIMPTS_FILE") <(sort -k2,2 "$WEIGHT_FILE") | sort -k3,3nr | head -n 1 | awk '{print $2}')

   sid=$(awk '{print $1}' "$SIMPTS_FILE" | sort -n | grep -nx "$max_phase" | cut -d: -f1)
   sid=$((sid - 1))
   

   RESDIR=${RESULTS_DIR}/$bm/sid$sid

   mkdir -p $RESDIR

   # pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
   nohup    $GEM5 --outdir=$RESDIR \
            ${CONFIG} \
            --workload $bm \
            --sid $sid \
            --fdp --l1NumEntries $L1NUMENTRIES --l2NumEntries $L2NUMENTRIES --l3NumEntries $L3NUMENTRIES --l2Associativity $L2ASSOC --numFTQEntries $NUMFTQENTRIES \
            --l2Latency $L2LATENCY --l3Latency $L3LATENCY --TAGELatency $TAGELATENCY --factor $FACTOR --width $WIDTH --maxTakenPredPerCycle $MAXTAKENPREDPERCYCLE \
            --pBufferSize $PBUFFER_SIZE $PPOLICY \
            --kernel $KERNEL --disk $DISK_IMAGE --isa=Arm \
            --checkpoint-dir $CHECKPOINT_BASE \
            --simpoint-dir $SIMPOINT_BASE \
            > $RESDIR/gem5.log 2>&1 &
done