
# Build Linux Kernel

Gem5 requires a binary that is executed on the simulated hardware system. In our case this is the linux kernel. To build a custom kernel configured for gem5 you can follow the setup steps [here](https://gem5.googlesource.com/public/gem5-resources/+/refs/heads/stable/src/linux-kernel/). From this site you also get kernel configs with all required modules enabled that gem5 can execute it.

Since some of the server workloads use docker as paravirtualization the kernel has to be configured with the necessary kernel moduls to for docker to work. Important is that kernel modules **can not** be loaded dynmaically but must be compiled into the binary.

## Use precompiled kernel

We provide a pre-compiled kernel version `5.15.59` for downloading at [TODO](TODO).


## Building the kernel

To build the kernel yourself
```bash
# will create a `linux` directory and download the initial kernel files into it.
git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

cd linux
# replace version with any of the above listed version numbers
git checkout v[version]

# copy the appropriate Linux kernel configuration file from configs/
# E.g. v5.15.59-arm64.config
cp ../configs/v[version]-[arch] .config

make -j`nproc`
```

Alternatively use the Makefile in this repo.
```bash
# Install all build tools
make dep_install
# Build the kernel
make build
```

After compiling copy the `vmlinux` binary into your working directory.


## Customize linux kernel
If you need to enable additional modules you may want to customize the kernel config. For this the easiest way is to start from one of the existing pre-configurations. For this overwrite the good `.config` file in the linux repo with the config you want and start the configuration process as usual with `make oldconfig`.
> Note: Gem5 cannot load modules at runtime therefore all modules need to be build into the binary.

## Check kernel config for container workloads
To find out if your kernel is ready to run container workloads the developers from the moby project provide a neat [script](https://github.com/moby/moby/raw/master/contrib/check-config.sh).
This [blog post](https://blog.hypriot.com/post/verify-kernel-container-compatibility/) explains nicely how to use this script in detail to check your kernel config for compatibility with containers.

This folder contains a copy of this scripts and can be used by:
```bash
./check-config.sh <path/to/your/kernel.config>
```