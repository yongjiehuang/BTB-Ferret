

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
# BMS+=("benchbase-otmetrics")
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
TAGELATENCY=4
PBUFFER_SIZE=32
# PPOLICY=0
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --pDepth 2 --togetherArrive"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency --useCompressedTagFilter --compressedTagBits 3"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyCB"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchOnlyUB"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit"
PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --noPrefetchLatency"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --noPrefetchLatency"
# PPOLICY="--trainBitsOnCommit --prefetchOnPrefetchHit --prefetchBothForCall --limitRet --pDepth 2"
PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors"
# PPOLICY="--pPolicy 6 --noPrefetchLatency"
# PPOLICY="--pPolicy 4 --noPrefetchLatency"
# PPOLICY="--pPolicy 0"
# PPOLICY="--noPrefetchLatency --finalMarkov"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --limitRet"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchAllSuccessors --prefetchOnL1Hit"
# PPOLICY="--noPrefetchLatency --finalMarkov --prefetchOnL1Hit"

EXPERIMENT="baseline"
EXPERIMENT="PBits_noLat"
EXPERIMENT="markovAll_noLat"



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


pueue group add -p 25 "$PGROUP" || true
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

    # pueue add -g "$PGROUP" -l "$EXPERIMENT-$bm-sid$sid" -- "$GEM5 \
    nohup $GEM5 --outdir=$RESDIR \
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
done