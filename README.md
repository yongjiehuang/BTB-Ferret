# BTB-Ferret: Prefetching for Hierarchical Branch Target Buffers Artifact

<p align="left">
    <a href="https://github.com/dhschall/LLBP-X/blob/main/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>

</p>

> [!INFO]
> This repository based on the [gem5 FDIP](https://github.com/dhschall/gem5-fdp) repository and contains extension of hierarchical BTBs and BTB-Ferret.

BTB-Ferret is a metadata-free L1-BTB prefetcher that improves the performance 
of hierarchical branch target buffers. L1-BTB misses often occur in 
back-to-back miss chains during transitions to new code regions, which are 
commonly led by loop exit and function returns. The key insight is that the 
"alternate" path of a branch, e.g., loop exit diretion and the fall-through of
a call, tends to trigger future BTB misses. Prefetching those paths makes a
stateless prefetcher feasible with trivial timeliness challenge. This enables
BTB-Ferret to leverage existing BTB metadata to identify bidirectional branches
and call, and prefetches an N-deep chain of BTB entries from the lower-level
BTB into a small prefetch buffer nearby the L1-BTB, avoiding the storage
overhead of stateful prefetchers.

BTB-Ferret will be presented at MICRO 2026.

This repository contains the modified gem5 simulator and the
infrastructure to evaluate the performance of BTB-Ferret.

The artifact is a gem5 implementation of hierarchical BTBs and BTB-Ferret for
detailed microarchitectural simulation.

# gem5 Simulation

## Prerequisites

* **OS**: Ubuntu 22.04 LTS
* **Compiler**: GCC 11.4.0
* **Python**: 3.10+
* **SCons**: 4.0+

The BTB-Ferret implementation has been tested with gem5 version v25.1.0.0.

## Benchmark Dependencies

The artifact evaluates two workload suites:

* **SPEC CPU 2017** — the SPEC CPU 2017 benchmark suite must be installed
  on the host. Refer to the [SPEC CPU 2017](https://www.spec.org/cpu2017/).
* **Server benchmarks** — the server workload infrastructure (disk-image
  build scripts, benchmark install scripts, gem5 full-system
  configurations, and the client/driver programs) in this repository is
  derived from the
  [gem5-svr-bench](https://github.com/dhschall/gem5-svr-bench) framework.
  This repository ships a snapshot of that infrastructure; for a
  detailed description of how the server workloads are built, kernel and disk image, and SimPoint checkpointing for gem5, please refer to
  [gem5-svr-bench README](https://github.com/dhschall/gem5-svr-bench).

## Setting up the Environment

Two supported ways of preparing the build and plotting dependencies are
provided below. Using Nix is recommended as it reproduces the exact
environment used to develop the artifact.

### Option A: Nix (recommended)

A `default.nix` file is provided at the repository. It declares all the build dependencies required to
compile gem5 with SCons, as well as the Python packages used by the
plotting and analysis scripts.

From the repository root, simply enter the Nix shell:

```bash
nix-shell default.nix
```

Once inside the shell, gem5 can be built directly with SCons and the plotting script `eval_l1main.py` should
be executed without any extra installation step.

### Option B: Manual installation

If you prefer not to use Nix, you need to install the gem5 build
prerequisites yourself. Please refer to the official
[gem5 documentation](https://www.gem5.org/documentation/).

To plot the graphs used by the paper with (`eval_l1main.py`), additionally
install the following Python packages with `pip`:

```bash
pip install pandas numpy matplotlib
```

## Build gem5

Clone the repository:

```bash
git clone https://github.com/yongjiehuang/BTB-Ferret.git
cd BTB-Ferret
```

Build the modified gem5 simulator for the Arm ISA:

```bash
cd gem5
scons build/ARM/gem5.opt -j"$(nproc)"
cd ..
```

The resulting simulator binary is located at:

```text
gem5/build/ARM/gem5.opt
```

### BTB-Ferret Implementation

The BTB-Ferret implementation is integrated into the branch prediction
infrastructure:

```text
gem5/src/cpu/pred/multilevel_btb.cc
```

The gem5 configuration scripts used for the experiments are located
under `gem5-configs/`, with the main SimPoint configurations being
`gem5-configs/spec-simpoint-run.py` and `gem5-configs/svr-simpoint-run.py`.

### SimPoint and Checkpoint Inputs

The experiments restore the most representative SimPoint checkpoints for each
workload. We assume the SimPoint checkpoints for both the SPEC CPU 2017
and the server suites have already been generated in your host. Point the following
variables at the top of `simpoints/all_4_run_single_simpoints.sh` to
their local paths (the server suite additionally needs an Arm Linux
kernel and a full-system disk image for gem5 full-system simulation):

```bash
GEM5=<path-to-BTB-Ferret>/gem5/build/ARM/gem5.opt

SPEC_SIMPOINT_BASE=<path-to-spec-simpoints>
SPEC_CHECKPOINT_BASE=<path-to-spec-checkpoints>

SVR_SIMPOINT_BASE=<path-to-server-simpoints>
SVR_CHECKPOINT_BASE=<path-to-server-checkpoints>
SVR_KERNEL=<path-to-server-kernel>
SVR_DISK_IMAGE=<path-to-server-disk-image>
```

### Configure the Experiment

The primary experiment script is:

```text
simpoints/all_4_run_single_simpoints.sh
```

The script contains the architectural parameters, the BTB hierarchy
configuration, the workload lists, and a set of pre-defined experiment
groups. The experiment group is selected via a command-line argument spefifying different configurations.
The available options are:

| Argument               | `EXPERIMENT`        | Description                            |
|------------------------|---------------------|----------------------------------------|
| `--baseline-2level`    | `baseline-2level`   | 2-level BTB baseline (no prefetcher)   |
| `--BTB-Ferret`         | `BTB-Ferret`        | BTB-Ferret on the 2-level BTB hierarchy|
| `--Ideal-BTB`          | `Ideal-BTB`         | Ideal BTB (opportunity for Prefetching)|

`EXPERIMENT` is the directory name under which the simulation results
are stored, so each group writes to a separate directory and they do not
overwrite each other. Run the script with no argument to see the usage
summary.

The workload suites can be enabled or disabled with:

```bash
RUN_SPEC=1
RUN_SVR=1
```

Set either variable to `0` to skip that workload suite.

Individual workloads can be selected by editing the `SPEC_BMS` and
`SVR_BMS` arrays in the script.

### Run the Experiments

Make the experiment script executable:

```bash
chmod +x simpoints/all_4_run_single_simpoints.sh
```

Run the selected configuration, passing the specific experiment as an
argument:

```bash
./simpoints/all_4_run_single_simpoints.sh --BTB-Ferret
```

For each enabled workload, the script selects the SimPoint with the largest weight.
It then restores the corresponding checkpoint and runs the detailed
gem5 O3 simulation.

The simulations are launched in the background. The progress of an
individual simulation can be inspected through its `gem5.log` file.

For example:

```bash
tail -f results/<experiment>/<workload>/sid<simpoint-id>/gem5.log
```

### Simulation Results

The experiment outputs are stored under:

```text
results/<experiment>/<workload>/sid<simpoint-id>/
```

### Reproducing the Paper Figures (Figure 15 & Figure 16)

The IPC speedup and BTB-Ferret coverage results reported in the paper
(Figure 15 and Figure 16) are produced by the plotting script
`eval_l1main.py`. Running

```bash
python eval_l1main.py
```

invokes `plot_speedup()` and `plot_Coverage()`, which read the gem5
`stats.txt` files produced by the SimPoint experiments and write two
PDFs:

| Function          | Paper figure | Output PDF                       | Configs read from `RES_DIR`                                          |
|-------------------|--------------|----------------------------------|----------------------------------------------------------------------|
| `plot_speedup()`  | Figure 15    | `<APATH>/performance_Ferret.pdf` | `baseline-2level`, `BTB-Ferret`, `Ideal-BTB`              |
| `plot_Coverage()` | Figure 16    | `<APATH>/coverage.pdf`           | `BTB-Ferret`                                                     |

Before running the script, configure the two path variables at the top
of `eval_l1main.py`:

```python
APATH = "<path-to-output-dir>"          # where the PDFs are written
RES_DIR = "<path-to-results>"           # parent of the experiment result dirs
```

The script expects the results laid out as:

```text
<RES_DIR>/<experiment>/<workload>/sid<simpoint-id>/stats.txt
```

Each `<experiment>` directory name must match the corresponding config
name listed in the table above (i.e. the `EXPERIMENT` variable in
`simpoints/all_4_run_single_simpoints.sh` must be set to
`baseline-2level`, `BTB-Ferret`, and `Idea-BTB` for the three
runs consumed by `plot_speedup()`). The workload names under each
experiment directory must match the entries in the `all_bms` list
defined in `eval_l1main.py` (SPEC workloads are the ones whose name
starts with `5`, e.g. `500.perlbench_r.checkspam`; the rest are server
workloads, e.g. `nodeapp`, `mediawiki`).

Once the three experiments have been simulated and their `stats.txt`
files are in place under `RES_DIR`, `python eval_l1main.py` will produce
`performance_Ferret.pdf` (Figure 15) and `coverage.pdf` (Figure 16) in
`APATH`.
## Citation

If you use our work, please cite the paper:

```bibtex
@inproceedings{huang2026btbferret,
  title     = {Prefetching for Hierarchical Branch Target Buffers},
  author    = {Huang, Yongjie and
               Ďuračková, Mária and
               Grot, Boris and
               Schall, David},
  booktitle = {2026 59th IEEE/ACM International Symposium on Microarchitecture (MICRO)},
  year      = {2026}
}
```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Yongjie Huang —
[GitHub](https://github.com/yongjiehuang),
[Mail](mailto:yongjie.huang@ed.ac.uk)