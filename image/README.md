---
title: Building the base x86-ubuntu and arm-ubuntu image for Ubuntu 22.04 and 24.04
authors:
    - Harshil Patel
---


> [!NOTE]
> The disk image build process is inherited from [gem5-resources](https://github.com/gem5/gem5-resources/tree/stable/src/ubuntu-generic-diskimages). See this documentation for further details.


This document provides instructions to create the "x86-ubuntu" image and "arm-ubuntu" image.

The disk images are based on Ubuntu and support both x86 and ARM architectures, specifically Ubuntu 22.04 and 24.04. These images have their .bashrc files modified to execute a script passed from the gem5 configuration files (using the m5 readfile instruction). The boot-exit test passes a script that causes the guest OS to terminate the simulation (using the m5 exit instruction) as soon as the system boots.

## What's on the disk?

- username: gem5
- password: 12345

- The `gem5-bridge`(m5) utility is installed in `/usr/local/bin/gem5-bridge`.
- `libm5` is installed in `/usr/local/lib/`.
- The headers for `libm5` are installed in `/usr/local/include/`.

### Installed packages

- `build-essential`
- `git`
- `scons`
- `vim`

## Directory map

- `files`: Files that are copied to the disk image.
- `scripts`: Scripts run on the disk image after installation.
- `http`: cloud-init Ubuntu autoinstall files for different versions of Ubuntu for Arm and x86.
  - `arm-22-04`: cloud-init Ubuntu autoinstall files for arm ubuntu 22.04 image.
  - `arm-24-04`: cloud-init Ubuntu autoinstall files for arm ubuntu 24.04 image.
  - `x86`: cloud-init Ubuntu autoinstall files for x86 ubuntu 22.04 and 24.04 images.


## Disk Image

Run `build-x86.sh` or `build-arm.sh` with the argument `22.04` or `24.04` to build the respective x86 or arm disk image in the `image` directory.
Building the arm image assume that we are on an ARM machine as we use kvm to build the image.
You can also run the packer file by adding the "use_kvm=false" in `build-arm.sh` in the `./packer build` command to build the disk image without KVM.
This will download the packer binary, initialize packer, and build the disk image.

## Arm image specific requirements

We need a EFI file to boot the arm image. We use the file named `flash0.img` in the packer file.

To get the `flash0.img` run the following commands in the `files` directory

```bash
dd if=/dev/zero of=flash0.img bs=1M count=64
dd if=/usr/share/qemu-efi-aarch64/QEMU_EFI.fd of=flash0.img conv=notrunc
```

**Note**: The `build-arm.sh` will make this file for you.

Note: Building the image can take a while to run.
You will see `qemu.initialize: Waiting for SSH to become available...` while the installation is running.
You can watch the installation with a VNC viewer.
See [Troubleshooting](#troubleshooting) for more information.


## Changes from the base Ubuntu image

- The default user is `gem5` with password `12345`.
- The `m5` utility is renamed to `gem5-bridge`.
  - `gem5-bridge` utility is installed in `/usr/local/bin/gem5-bridge`.
  - `gem5-bridge` has a symlink to `m5` for backwards compatibility.
  - `libm5` is installed in `/usr/local/lib/` and the headers for `libm5` are installed in `/usr/local/include/m5`.
- The `.bashrc` file checks to see if there is anything in the `gem5-bridge readfile` command and executes the script if there is.
- The init process is modified to provide better annotations and more exit event. For more details see the [Init Process and Exit events](README.md#init-process-and-exit-events).
  - The `gem5-bridge exit` command is run after the linux kernel initialization by default.
  - If the `no_systemd` boot option is passed, systemd is not run and the user is dropped to a terminal.
  - If the `interactive` boot option is passed, the `gem5-bridge exit` command is not run after the linux kernel initialization.


### Customization of the boot Processes

- **`gem5_init.sh` replaces /sbin/init**: This script is what executes as the Linux init process (pid=0) immediately after Linux boot. This script adds an `gem5-bridge exit` when the file is executed. It also checks the `no_systemd` kernel arg to redirect to the user or boot with systemd.

### Details of the After-Boot Script

- **Persistent Execution of `after-boot.sh`**: The `after-boot.sh` script executes at first login.
To avoid its infinite execution, we incorporated a conditional check in `post-installation.sh` similar to the following:

```sh
echo -e "\nif [ -z \"\$AFTER_BOOT_EXECUTED\" ]; then\n   export AFTER_BOOT_EXECUTED=1\n    /home/gem5/after_boot.sh\nfi\n" >> /home/gem5/.bashrc
```

This ensures `after-boot.sh` runs only once per session by setting an environment variable.

### Adjusting File Permissions

- **Setting Permissions for `gem5-bridge`**: Since the default user is not root, `gem5-bridge` requires root permissions. Apply setuid to grant these permissions:

  ```sh
  chmod u+s /path/to/gem5-bridge
  ```

## Extending the disk image with custom files and scripts

- You can add more packages to the disk image by updating the `post-installation.sh` script.
- To add files from host to the disk image you can add a file provisioner with source as path in host and destination as path in the image.

```hcl
provisioner "file" {
    destination = "/home/gem5/"
    source      = "path/to/files"
  }
```

### Extending Disk Image Size

If you need to increase the size of the disk image when adding more libraries and files, follow these steps:

1. **Update the Partition Size in `user-data`:**
   - Modify the `size` of the partition in the relevant `http/*/user-data` file. The size in `user-data` is specified in **bytes**.

2. **Update the `disk_size` Parameter in Packer:**
   - Adjust the `disk_size` parameter in the Packer script to be at least **1 MB more** than the total size specified in the `user-data` file. Note that `disk_size` in Packer is specified in **megabytes**.

#### Example: Setting the Main Partition Size to 10 GB

To ensure that the **main partition** is exactly **10 GB**, follow these steps:

1. **Calculate the Total Disk Size:**
   - The total disk size needs to account for the main partition, boot partition, and additional space required by Packer.
   - Add the respective boot partition size and Packer’s required space to **10 GB (10,000,000,000 bytes)**:
     - **x86 boot partition:** `1,048,576 bytes` (1 MB).
     - **ARM boot partition:** `564,133,888 bytes`.
     - Additional space required: `1,048,576 bytes` (1 MB).
   - Compute the total disk size:
     - **x86 disk image:** `10,000,000,000 + 1,048,576 + 1,048,576 = 10,002,097,152 bytes`.
     - **ARM disk image:** `10,000,000,000 + 564,133,888 + 1,048,576 = 10,565,182,464 bytes`.

2. **Update the Packer `disk_size`:**
   - Set `disk_size` to `10,003` MB for **x86**.
   - Set `disk_size` to `10,566` MB for **ARM**.


To take a pre-built image and add new files or packages, take a look at the following [documentation](https://www.gem5.org/documentation/gem5-stdlib/extending-disk-images).

## Creating a Disk Image from Scratch

### Automated Ubuntu Installation

- **Ubuntu Autoinstall**: We leveraged Ubuntu's autoinstall feature for an automated setup process.
- **Acquire `user-data` File**: To get the `user-data` file, install your desired Ubuntu version on a machine or VM. Post-installation, retrieve the `autoinstall-user-data` from `/var/log/installer/autoinstall-user-data` after the system's first reboot.
The `user-data` file in this repo, is made by selecting all default options except a minimal server installation.

### Configuration and Directory Structure

- **Determine QEMU Arguments**: Identify the QEMU arguments required for booting the system. These vary by ISA and mirror the arguments used for booting a disk image in QEMU.
- **Directory Organization**: Arrange your source directory to include the `user-data` file and any additional content. Utilize the `provisioner` section for transferring extra files into the disk image, ensuring all necessary resources are embedded within your custom disk image.

## Troubleshooting

To see what `packer` is doing, you can use the environment variable `PACKER_LOG=INFO` when running `./build.sh`.

Packer seems to have a bug that aborts the VM build after 2-5 minutes regardless of the ssh_timeout setting.
As a workaround, set ssh_handshake_attempts to a high value.
Thus, I have `ssh_handshake_attempts = 1000`.
From <https://github.com/rlaun/packer-ubuntu-22.04>

To see what is happening while packer is running, you can connect with a vnc viewer.
The port for the vnc viewer is shown in the terminal while packer is running.

You can mount the disk image to see what is inside.
Use the following command to mount the disk image:
(note `norecovery` is needed if you get the error "cannot mount ... read-only")

```sh
mkdir x86-ubuntu/mount
sudo mount -o loop,offset=2097152,norecovery x86-ubuntu/x86-ubuntu-image/x86-ubuntu x86-ubuntu/mount
```

Useful documentation: <https://ubuntu.com/server/docs/install/autoinstall>
