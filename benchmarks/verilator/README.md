# Verilator Benchmark

This benchmark runs a [Verilator](https://github.com/verilator/verilator) simulation of the [CVA6](https://github.com/openhwgroup/cva6) RISC-V core running a drystone workload.

The benchmark features a large number of static conditional branches. Thus its particularly interesting to study BTB pressure. The branches itself are simple to predict.

> [!NOTE]
> The benchmark needs 3GiB of memory. With less the application will crash with OOM.


## Compile the verilator object (optional)

> See also the instructions on the [GitHub page](https://github.com/openhwgroup/cva6)

TODO

## Running the workload

Once the simulation object is compiled you can execute it with
```bash
./Variane_testharness dhrystone.riscv
```

