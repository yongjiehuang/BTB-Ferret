

set -x

RESBASE=./results_spec/IV200M_cptkvm/

GEM5=/scratch/david/g5/tmp/gem5-llbp-x/build/ARM/gem5.opt
CONFIG=/scratch/david/g5/gem5-benchmarks/gem5-configs/01-simpoint/spec-simpint-gen.py

SIMPOINT_BASE=/share/david/spec/arm64/simpoints_200M_v2/
CHECKPOINT_BASE=/share/david/spec/arm64/checkpoints_200M_v2/


BMS=()
BMS+=("500.perlbench_r.checkspam")
BMS+=("500.perlbench_r.diffmail")
# BMS+=("500.perlbench_r.splitmail")
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_0")
BMS+=("502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000")
BMS+=("502.gcc_r.gcc-smaller.c-O3_-fipa-pta")
BMS+=("502.gcc_r.ref32.c_-O5")
BMS+=("502.gcc_r.ref32.c_-O3")
BMS+=("505.mcf_r.inp")
# BMS+=("520.omnetpp_r.general")
BMS+=("523.xalancbmk_r.xalanc")
BMS+=("525.x264_r.x264_pass1")
# BMS+=("525.x264_r.x264_pass2")
BMS+=("525.x264_r.x264")
BMS+=("531.deepsjeng_r.ref")
BMS+=("541.leela_r.ref")
# BMS+=("548.exchange2_r.general")
BMS+=("557.xz_r.cld")
BMS+=("557.xz_r.cpu2006docs")
BMS+=("557.xz_r.input")
BMS+=("999.specrand_ir.rand")


for bm in "${BMS[@]}"; do
   RESDIR=${RESBASE}/$bm
   mkdir -p $RESDIR
   mkdir -p $CHECKPOINT_BASE/$bm
   ${GEM5}  --outdir=$RESDIR  ${CONFIG} \
      --checkpoint-dir $CHECKPOINT_BASE --simpoint-dir $SIMPOINT_BASE \
      --workload $bm --simpoint-mode=analyze > $RESDIR/gem5.log 2>&1 &
done
