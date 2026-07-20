# Generating Simpoints

Simpoints are useful to reduce the simulation time of gem5 for long running applications by simulating only the most representative snippets of the program.
The end goal is to have a set of gem5 checkpoints that start at these most representative regions (minus some warm-up interval).

Three steps are needed to generate simpoint checkpoints:
1. Profile application
2. Run the simpoint analysis
3. Rerun the application to take checkpoints at the correct time stamps
4. Perform experiments

This folder contains for each step an example script to perform the specific step and the `gem5-config` folder contains the configuration scripts.
Step 1-3 can take a long time (multiple days) but need to be done only once.


## Server workload checkpoints

Our server workloads are mostly full-system workloads and take quite some time to boot and setup, including the JIT warm up. Those parts we do not want to be part of the analysis and it would also take quite some time to do the booting with the atomic core. However, we can start the analysis from a checkpoint that was taken with the KVM core after the booting. See the [setup instructions](../README.md#automated-setup).


### 1. Profile application

The first step is to collect statistics about the basic blocks executed in the program. We can do this with the `atomic` core in gem5.
There faster alternatives [using QEMU](https://mircomannino.github.io/posts/simulation/1_gem5_simpoints.html) but I was not yet able to get it working yet.

See the `svr-simpoint-gen.py` config file for more details (`simpoint-mode=analysis`).

To run start the analyzis step for all server workloads (or comment the once you want) run
```bash
./simpoints/svr_1_run_analysis.sh
```
The statistics are collected in the `simpoint.bb.gz` file which is placed in the output directory. We use a profiling interval of 200M instructions.

### 2. Run simpoint analysis

Once the analysis has completed the next step is to run the analysis of the basic block vectors (`simpoint.bb.gz`) using the [SimPoint tool](https://cseweb.ucsd.edu/~calder/simpoint/index.htm).

> Note: this folder contains a precompiled binary for x86-64

Run the analysis with:
```bash
./simpoints/svr_2_run_analysis.sh
```

The script will copy the `simpoint.bb.gz` file into a new directory and the run the analysis. Adapt the paths as needed.


### 3. Create checkpoints for simpoints

The SimPoint tool will output a `results.simpts` and a `results.weights` file which contains start indices and the weights for each simpoint (In our case five). The indices are in *profiling interval* from the beginning of the program. E.g. in our case we use a profiling interval of 200M instructions, thus a start index of 124 means the simpoint starts at 124*200M = 24.8B instructions.

To avoid running every time all the way to the simpoint start we do another full run and take checkpoints before each simpoint interval. Note that we have to take the checkpoint a bit further to allow sufficient warm-up of the caches. In our case we use 100M instruction warming and 200M measurement. Thus for the above example the checkpoint will be taken at 124*200M-100M instructions.

The checkpoint taking step can be done with

```bash
./simpoints/svr_3_checkpoint_simpoints.sh
```


### 4. Doing the actual experiments

Once all checkpoints are taken we are ready to perform the actual analysis.
The `svr-simpoint-run.py` script provides a basic setup to run the checkpoints with the O3 core. It expects the path the the checkpoints, the workload to run and the simpoint ID (sid).

Refer to `./simpoints/svr_4_run_simpoints.sh` as example how to run all checkpoints.

After the experiments the results of each simpoint need to be weighted according the the simpoint weight and added together with the other results. 



## SPEC simpoints

This repo also contains scripts to generate simpoints for SPEC workloads. They assume that the spec benchmarks are already compiled and available as executables.
Unlike the server workloads they assume SE mode and can be run right from the start.