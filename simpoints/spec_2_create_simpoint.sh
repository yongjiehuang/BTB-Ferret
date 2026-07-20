

set -x

SIMPOINT_BIN=./simpoints/simpoint
RESBASE=./results_spec/IV200M/
SIMPOINT_BASE=/share/david/spec/arm64/simpoints_200M_v2/


BMS=()
BMS+=("500.perlbench_r.checkspam")
BMS+=("500.perlbench_r.diffmail")
BMS+=("500.perlbench_r.splitmail")
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_0")
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
BMS+=("502.gcc_r.gcc-smaller.c-O3_-fipa-pta")
BMS+=("502.gcc_r.ref32.c_-O5")
BMS+=("502.gcc_r.ref32.c_-O3")
BMS+=("505.mcf_r.inp")
BMS+=("520.omnetpp_r.general")
BMS+=("523.xalancbmk_r.xalanc")
BMS+=("525.x264_r.x264_pass1")
BMS+=("525.x264_r.x264_pass2")
BMS+=("525.x264_r.x264")
BMS+=("531.deepsjeng_r.ref")
BMS+=("541.leela_r.ref")
BMS+=("548.exchange2_r.general")
BMS+=("557.xz_r.cld")
BMS+=("557.xz_r.cpu2006docs")
BMS+=("557.xz_r.input")
BMS+=("999.specrand_ir.rand")


for bm in "${BMS[@]}"; do
   mkdir -p ${SIMPOINT_BASE}/$bm/
   cp $RESBASE/$bm/simpoint.bb.gz ${SIMPOINT_BASE}/$bm/
   pushd ${SIMPOINT_BASE}/$bm
   ${SIMPOINT_BIN} -inputVectorsGzipped -loadFVFile simpoint.bb.gz -k 5 -saveSimpoints results.simpts -saveSimpointWeights results.weights &
   popd
done
