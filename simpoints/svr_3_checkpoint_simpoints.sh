

set -x



GEM5=/scratch/david/g5/tmp/gem5-llbp-x/build/ARM/gem5.opt
CONFIG=./gem5-configs/svr-simpoint-gen.py

SIMPOINT_BASE=/share/david/svr/arm64/v2/simpoints_200M/
CHECKPOINT_BASE=/share/david/svr/arm64/v2/checkpoints_200M/
KERNEL=/share/david/svr/arm64/v2/kernel
DISK_IMAGE=/share/david/svr/arm64/v2/disk.img

RESBASE=./results_svr/IV200M_cptkvm/

BMS=()

BMS+=("nodeapp")

# BMS+=("nodeapp")
BMS+=("nodeapp-nginx")
BMS+=("mediawiki")
BMS+=("mediawiki-nginx")
BMS+=("proto")
BMS+=("swissmap")
BMS+=("libc")
BMS+=("tcmalloc")
BMS+=("compression")
BMS+=("hashing")
BMS+=("stl")

## Java BMS
# WORKLOADS="cassandra h2 h2o kafka luindex lusearch spring tomcat"
BMS+=("dacapo-cassandra")
BMS+=("dacapo-h2")
BMS+=("dacapo-h2o")
BMS+=("dacapo-kafka")
BMS+=("dacapo-luindex")
BMS+=("dacapo-lusearch")
BMS+=("dacapo-spring")
BMS+=("dacapo-tomcat")
BMS+=("renaissance-http")
BMS+=("renaissance-chirper")


BMS+=("benchbase-tpcc")
BMS+=("benchbase-twitter")
BMS+=("benchbase-wikipedia")

BMS+=("benchbase-tpch")
BMS+=("benchbase-tatp")
BMS+=("benchbase-resourcestresser")
BMS+=("benchbase-epinions")
BMS+=("benchbase-ycsb")
BMS+=("benchbase-seats")
BMS+=("benchbase-auctionmark")
BMS+=("benchbase-chbenchmark")
BMS+=("benchbase-voter")
BMS+=("benchbase-sibench")
BMS+=("benchbase-noop")
BMS+=("benchbase-smallbank")
BMS+=("benchbase-hyadapt")
BMS+=("benchbase-otmetrics")
BMS+=("benchbase-templated")



for bm in "${BMS[@]}"; do
   RESDIR=${RESBASE}/$bm
   mkdir -p $RESDIR
   mkdir -p $CHECKPOINT_BASE/$bm
   ${GEM5}  --outdir=$RESDIR \
      ${CONFIG} --workload $bm \
      --kernel $KERNEL --disk $DISK_IMAGE --isa=Arm \
      --checkpoint-dir $CHECKPOINT_BASE \
      --simpoint-dir $SIMPOINT_BASE \
      --simpoint-mode=analysis \
      > $RESDIR/gem5.log 2>&1 &
done
