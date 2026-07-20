#!/bin/bash

# MIT License
#
# Copyright (c) 2022 David Schall and EASE lab
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

MKFILE 		:= $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT 		:= $(abspath $(dir $(MKFILE))/../)
ARCH = $(shell dpkg --print-architecture)

## User specific inputs
WORKING_DIR ?= $(ROOT)/wkdir/$(ARCH)


## Machine parameter
MEMORY 	:= 64G
CPUS    := 16
CPU 	?= host -enable-kvm


## Required artifacts
TMP_DIR := $(ROOT)/image/tmp


CLIENT 			:= $(TMP_DIR)/http-client
DOWNLOAD_KERNEL := $(TMP_DIR)/vendored-kernel
BUILD_KERNEL 	:= $(TMP_DIR)/kernel

ifeq ($(ARCH), arm64)
    DISK := $(ROOT)/image/arm-disk-image-24-04/arm-ubuntu
else
    DISK := $(ROOT)/image/x86-disk-image-22-04/x86-ubuntu
endif


## Dependencies -------------------------------------------------
$(TMP_DIR):
	mkdir -p $@
	

$(CLIENT): $(TMP_DIR)
	cd $(ROOT)/client && \
	ARCH=$(ARCH) make all
	cp $(ROOT)/client/output/$(ARCH)/http-client $@
	

$(DOWNLOAD_KERNEL): $(TMP_DIR)
	wget -O $@ https://github.com/dhschall/gem5-svr-bench/releases/latest/download/vmlinux-v5.15.59-${ARCH} 

$(BUILD_KERNEL): $(TMP_DIR)
	cd $(ROOT)/kernel && \
	ARCH=$(ARCH) make all
	cp $(ROOT)/kernel/linux/vmlinux $@


##################################################################
## Build the working directory ----------------------------
#
WK_KERNEL 	:= $(WORKING_DIR)/kernel
WK_DISK 	:= $(WORKING_DIR)/disk.img
WK_CLIENT	:= $(WORKING_DIR)/http-client

build-wkdir: $(WORKING_DIR) $(TMP_DIR) \
	$(WK_DISK) $(WK_KERNEL) $(WK_CLIENT)


$(WORKING_DIR):
	@echo "Create folder: $(WORKING_DIR)"
	mkdir -p $@

# Change this to BUILD_KERNEL to build the kernel yourself
$(WK_KERNEL): $(DOWNLOAD_KERNEL)
	cp $< $@

$(WK_CLIENT): $(CLIENT)
	cp $< $@


# Create the disk image from the base image
$(WK_DISK): $(DISK)
	qemu-img convert $< $@



## Run Emulator -------------------------------------------------


FLASH0 := $(WORKING_DIR)/flash0.img
FLASH1 := $(WORKING_DIR)/flash1.img

$(FLASH0):
	cp /usr/share/qemu-efi-aarch64/QEMU_EFI.fd $@
	truncate -s 64M $@

$(FLASH1):
	truncate -s 64M $@


run-arm: $(FLASH0) $(FLASH1)
	sudo qemu-system-aarch64 \
		-nographic \
		-M virt \
		-machine gic-version=max \
		-cpu host -enable-kvm \
		-smp ${CPUS} -m ${MEMORY} \
		-device e1000,netdev=net0 \
    	-netdev type=user,id=net0,hostfwd=tcp:127.0.0.1:8888-:22  \
		-drive file=$(WK_DISK),format=raw \
		-drive file=$(FLASH0),format=raw,if=pflash -drive file=$(FLASH1),format=raw,if=pflash 



run-x86:
	sudo qemu-system-x86_64 \
		-nographic -serial mon:stdio \
		-cpu "qemu64" -enable-kvm \
		-smp ${CPUS} -m ${MEMORY} \
		-drive file=$(WK_DISK),format=raw \
		-device e1000,netdev=net0 \
    	-netdev type=user,id=net0,hostfwd=tcp:127.0.0.1:8888-:22 




run-arm64: run-arm
run-amd64: run-x86
