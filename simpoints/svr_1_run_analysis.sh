

set -x



GEM5=/scratch/david/g5/tmp/gem5-llbp-x/build/ARM/gem5.opt
CONFIG=./gem5-configs/svr-simpoint-gen.py

CHECKPOINT_BASE=/share/david/svr/arm64/v2/checkpoints/
KERNEL=/share/david/svr/arm64/v2/kernel
DISK_IMAGE=/share/david/svr/arm64/v2/disk.img

RESBASE=./results_svr/IV200M/


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


# BMS+=("dcperf-django")



# # Arm Ubench
# BMS+=("armub-branch_direct_workload")
# BMS+=("armub-branch_indirect_workload")
# BMS+=("armub-call_return_workload")
# BMS+=("armub-div32_workload")
# BMS+=("armub-div64_workload")
# BMS+=("armub-double2int_workload")
# BMS+=("armub-fpmul_workload")
# BMS+=("armub-fpdiv_workload")
# BMS+=("armub-fpmac_workload")
# BMS+=("armub-fpsqrt_workload")
# BMS+=("armub-int2double_workload")
# BMS+=("armub-l1d_cache_workload")
# BMS+=("armub-l1d_tlb_workload")
# BMS+=("armub-l1i_cache_workload")
# BMS+=("armub-l2d_cache_workload")
# BMS+=("armub-load_after_store_workload")
# BMS+=("armub-mac32_workload")
# BMS+=("armub-mac64_workload")
# BMS+=("armub-mul32_workload")
# BMS+=("armub-mul64_workload")
# BMS+=("armub-memcpy_workload")
# BMS+=("armub-store_buffer_full_workload")


for bm in "${BMS[@]}"; do
   RESDIR=${RESBASE}/$bm
   mkdir -p $RESDIR
   ${GEM5}  --outdir=$RESDIR \
      ${CONFIG} --workload $bm \
      --kernel $KERNEL --disk $DISK_IMAGE --isa=Arm \
      --checkpoint-dir $CHECKPOINT_BASE \
      --simpoint-mode=analysis \
      > $RESDIR/gem5.log 2>&1 &
done
