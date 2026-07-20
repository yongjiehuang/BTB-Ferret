

set -x

SIMPOINT_BIN=/scratch/david/g5/gem5-benchmarks/gem5-configs/01-simpoint/simpoint
SIMPOINT_BASE=/share/david/svr/arm64/v2/simpoints_200M/

## The directory containing the results from the ananlysis
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


for bm in "${BMS[@]}"; do
   mkdir -p ${SIMPOINT_BASE}/$bm/
   cp $RESBASE/$bm/simpoint.bb.gz ${SIMPOINT_BASE}/$bm/
   pushd ${SIMPOINT_BASE}/$bm
   ${SIMPOINT_BIN} -inputVectorsGzipped -loadFVFile simpoint.bb.gz -k 5 -saveSimpoints results.simpts -saveSimpointWeights results.weights &
   popd
done
