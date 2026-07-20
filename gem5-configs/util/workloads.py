# Copyright (c) 2024-2025 Technical University of Munich
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


svr_workloads = {}

### Own Benchmarks ###################################################################


def writeRunScript(cfg, cpu=1):
    urlfile = cfg["urlfile"]
    dcfile = cfg["dcfile"]
    container = cfg["container"]
    test_ip = "0.0.0.0"
    conc = 2
    # home = "root"
    home = "home/gem5"
    n_invocations=cfg["invocations"]
    n_warming=cfg["warming"]
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

m5 --addr=0x10010000 exit ## 1: BOOTING complete

## Spin up Container
echo "Start the container..."
sudo docker compose -f /{home}/{dcfile} up -d
sudo docker compose -f /{home}/{dcfile} up -d
m5 --addr=0x10010000 exit ## 2: Started container

echo "Pin {container} container to core {cpu}"
sudo docker update {container} --cpuset-cpus {cpu}
sleep 30

sleep 5
m5 --addr=0x10010000 exit ## 3: Pinned container


# # The client will perform some functional warming
# and then send a fail code before invoking the
# function again for the actual measurement.
sudo GOGC=1000 /{home}/http-client -f /{home}/{urlfile} -url {test_ip} -c {conc} -n {n_invocations} -w {n_warming} -m5ops -v



m5 --addr=0x10010000 exit ## 4: Stop client
# -------------------------------------------


## Stop container
sudo docker compose -f /{home}/{dcfile} down
m5 --addr=0x10010000 exit ## 5: Container stop


## exit the simulations
m5 --addr=0x10010000 exit ## 6: Test done

"""



svr_workloads |= {
    "nodeapp": {
        "runscript": writeRunScript,
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nodeapp",
        "invocations": 200,
        "warming": 5000,
    },
    "nodeapp-nginx": {
        "runscript": writeRunScript,
        "urlfile": "nodeapp.urls.tmpl",
        "dcfile": "dc-nodeapp.yaml",
        "container": "nginx",
        "invocations": 200,
        "warming": 5000,
    },
    "mediawiki": {
        "runscript": writeRunScript,
        "urlfile": "mediawiki.urls.tmpl",
        "dcfile": "dc-mediawiki.yaml",
        "container": "wiki",
        "invocations": 200,
        "warming": 5000,
    },
    "mediawiki-nginx": {
        "runscript": writeRunScript,
        "urlfile": "mediawiki.urls.tmpl",
        "dcfile": "dc-mediawiki.yaml",
        "container": "nginx",
        "invocations": 200,
        "warming": 5000,
    },
}







### Fleetbench ###################################################################


def writeFleetbenchRunScript(cfg, cpu=1):
    workload = cfg["cmd"]
    options = cfg["options"]
    conc = 2
    # home = "root"
    home = "home/gem5"
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

m5 exit ## 1: BOOTING complete

sleep 3

taskset -c {cpu} {workload} {options} &
PID=$!

sleep 1
m5 fail 4 ## take checkpoint


wait $PID


sleep 5

## exit the simulations
m5 exit ## 6: Test done

"""

FLEETBENCH_BUILD_BASE="/home/gem5/fleetbench/build/execroot/com_google_fleetbench/bazel-out/k8-opt/bin/fleetbench"

svr_workloads |= {

    "proto": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/proto/proto_benchmark.runfiles/com_google_fleetbench/fleetbench/proto/proto_benchmark",
        "options" : "--benchmark_min_time=30s",
    },
    "swissmap": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/swissmap/swissmap_benchmark.runfiles/com_google_fleetbench/fleetbench/swissmap/swissmap_benchmark",
        "options" : "--benchmark_min_time=30s",
    },
    "libc": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/libc/mem_benchmark.runfiles/com_google_fleetbench/fleetbench/libc/mem_benchmark",
        "options" : f"--benchmark_min_time=1s --L1_data_size={32*1024} --L2_size={512*1024} --L3_size {512*1024}",
    },
    "tcmalloc": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/tcmalloc/empirical_driver.runfiles/com_google_fleetbench/fleetbench/tcmalloc/empirical_driver",
        "options" : "--benchmark_min_time=1s",
    },
    "compression": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/compression/compression_benchmark.runfiles/com_google_fleetbench/fleetbench/compression/compression_benchmark",
        "options" : "--benchmark_min_time=1s",
    },
    "compression-weird": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/compression/compression_benchmark.runfiles/com_google_fleetbench/fleetbench/compression/compression_benchmark",
        "options" : "--benchmark_min_time=1s",
    },
    "hashing": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/hashing/hashing_benchmark.runfiles/com_google_fleetbench/fleetbench/hashing/hashing_benchmark",
        "options" : f"--benchmark_min_time=1s --L1_data_size {32*1024} --L2_size {512*1024} --L3_size {512*1024}",
    },
    "stl": {
        "runscript": writeFleetbenchRunScript,
        "cmd" : f"{FLEETBENCH_BUILD_BASE}/stl/cord_benchmark.runfiles/com_google_fleetbench/fleetbench/stl/cord_benchmark",
        "options" : "--benchmark_min_time=30s",
    },

}



### Verilator ###################################################################


def writeVerilatorRunScript(cfg, cpu=1):
    # home = "root"
    home = "home/gem5"
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

m5 exit ## 1: BOOTING complete

sleep 3

taskset -c {cpu} /{home}/Variane_testharness /{home}/dhrystone.riscv &
PID=$!

sleep 20
m5 fail 4 ## take checkpoint


wait $PID

## exit the simulations
m5 exit ## 6: Test done

"""


svr_workloads |= {

    "verilator": {
        "runscript": writeVerilatorRunScript,
    },
}









### Java Apps ###################################################################


def writeJavaAppRunScript(cfg, cpu=1):
    # home = "root"
    home = cfg["wkdir"] if "wkdir" in cfg else "/home/gem5"
    wl = cfg["workload"]
    wlarg = f"{cfg['workload-arg']} {wl}" if "workload-arg" in cfg else wl
    java_home = cfg["java_home"] if "java_home" in cfg else "/usr/bim/java"
    return f"""
#!/bin/bash

## Define the image name of your function.

# We use the 'm5 exit' magic instruction to indicate the
# python script where in workflow the system currently is.

## 1: BOOTING complete
set -x

sleep 3

cd {home}

CMD="{java_home} -jar {cfg["jarfile"]} {wlarg} {cfg["args"]}"

taskset --cpu-list {cpu} $CMD > /tmp/{wl}.log 2>&1 &
BMPID=$!


i=0
while true; do
    if grep -q '{cfg["match_string"]}' /tmp/{wl}.log; then
        echo "Found the match string in the log file."
        break
    fi
    sleep 1
    i=$((i+1))
    if [ $i -gt 10 ]; then
        cat /tmp/{wl}.log
        i=0
    fi
done

sleep 5
m5 fail 4 ## take checkpoint

wait $BMPID

m5 writefile /tmp/{wl}.log workload.log

## exit the simulations
m5 exit ## 6: Test done

"""


## Dacapo BMs
DACAPO_BMS = [
    "cassandra",
    "h2",
    "h2o",
    "kafka",
    "luindex",
    "lusearch",
    "spring",
    "tomcat",
]


svr_workloads |= {
    f"dacapo-{bm}": {
        "runscript": writeJavaAppRunScript,
        "workload": bm,
        "jarfile": "dacapo.jar",
        "args": "-n 5",
        "match_string": f"{bm} starting =====",
        "java_home": "/usr/lib/jvm/java-11-openjdk-arm64/bin/java",
    } for bm in DACAPO_BMS
}



## Renaissance BMs -------------
RENAISSANCE_BMS = [
    "chirper",
    "http",
]

svr_workloads |= {
    f"renaissance-{bm}": {
        "runscript": writeJavaAppRunScript,
        "workload": f"finagle-{bm}",
        "jarfile": "renaissance.jar",
        "args": "-r 10",
        "match_string": "iteration 7 started ======",
        "java_home": "/usr/lib/jvm/java-11-openjdk-arm64/bin/java",
    } for bm in RENAISSANCE_BMS
}



## Benchbase BMs
BENCHBASE_BMS = [
    "tpcc",
    "tpch",
    "tatp",
    "wikipedia",
    "resourcestresser",
    "twitter",
    "epinions",
    "ycsb",
    "seats",
    "auctionmark",
    "chbenchmark",
    "voter",
    "sibench",
    "noop",
    "smallbank",
    "hyadapt",
    "otmetrics",
    "templated",
]


svr_workloads |= {
    f"benchbase-{bm}": {
        "runscript": writeJavaAppRunScript,
        "wkdir" : "/home/gem5/benchbase-mariadb",
        "workload": bm,
        "workload-arg" : "-b",
        "jarfile": "benchbase.jar",
        "args": f"-c config/mariadb/sample_{bm}_config.xml --create=true --load=true --execute=true",
        "match_string": "Warmup complete, starting measurements.",
        "java_home": "/usr/lib/jvm/java-21-openjdk-arm64/bin/java",
    } for bm in BENCHBASE_BMS
}


