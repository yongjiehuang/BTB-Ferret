#!/bin/bash -eux


# Install dependencies
sudo apt update && sudo apt install -y g++ zip unzip autoconf automake libtool zlib1g-dev

ARCH=$(dpkg --print-architecture)

# Install bazelisk
sudo wget -O /usr/local/bin/bazel "https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-${ARCH}"
sudo chmod +x /usr/local/bin/bazel


## Install fleetbench
git clone https://github.com/google/fleetbench.git


cd fleetbench
mkdir -p build

VERSION=cd20746b68b307b148a761c676d6400f2541082d

git checkout $VERSION



## Build fleetbench

BENCHMARKS=()
BENCHMARKS+=("proto:proto_benchmark")
BENCHMARKS+=("swissmap:swissmap_benchmark")
BENCHMARKS+=("libc:mem_benchmark")
BENCHMARKS+=("tcmalloc:empirical_driver")
BENCHMARKS+=("compression:compression_benchmark")
BENCHMARKS+=("hashing:hashing_benchmark")
BENCHMARKS+=("stl:cord_benchmark")




for BENCHMARK in "${BENCHMARKS[@]}"; do
  BENCHMARK_NAME=$(echo $BENCHMARK | cut -d':' -f1)
  BENCHMARK_TARGET=$(echo $BENCHMARK | cut -d':' -f2)
  bazel run --config=opt fleetbench/${BENCHMARK_NAME}:${BENCHMARK_TARGET}
done


