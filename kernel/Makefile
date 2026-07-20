#!/bin/bash

# MIT License
#
# Copyright (c) 2022 EASE lab, University of Edinburgh
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
#
# Authors: David Schall


mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
ROOT 		:= $(abspath $(dir $(mkfile_path))/../)


LINUX_DIR 	:= linux/
OUTPUT		?=

KVERSION	?= v5.15.59
ARCH		?= $(shell dpkg --print-architecture)
KERNEL_CONFIG_GEM5 := $(ROOT)/kernel/configs/$(KVERSION)-$(ARCH).config
KERNEL_CONFIG := $(LINUX_DIR)/.config
KERNEL_PATCH_GEM5 := $(ROOT)/kernel/m5struct-$(KVERSION).patch


BUILD_OBJ 	:= $(LINUX_DIR)/vmlinux

.PHONY: all config

all: build

## Dependencies -------------------------------------------------
## Install all dependencies to build linux kernel
##
dep_install:
	sudo apt-get update \
  	&& sudo apt-get install -y \
        git build-essential ncurses-dev xz-utils libssl-dev bc \
    	flex libelf-dev bison \
		gcc-arm-linux-gnueabihf gcc-aarch64-linux-gnu device-tree-compiler

## Get sources --
$(LINUX_DIR):
	git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git $@

get_sources: $(LINUX_DIR)
	cd $(LINUX_DIR); \
	git checkout $(KVERSION)


## Make config
config: $(LINUX_DIR)
	cd $(LINUX_DIR); \
	git checkout $(KVERSION)
	cp $(KERNEL_CONFIG_GEM5) $(KERNEL_CONFIG)


## Add patches to the kernel
patch: $(LINUX_DIR)
	-cd $(LINUX_DIR); \
	git apply --ignore-space-change $(KERNEL_PATCH_GEM5)


## Build
build-amd64: $(LINUX_DIR) config patch
	@$(call print_config)
	cd $(LINUX_DIR); \
	make ARCH=x86_64 -j $$(nproc)

build-arm64: $(LINUX_DIR) config patch
	@$(call print_config)
	cd $(LINUX_DIR); \
	make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j $$(nproc)


ifeq ($(ARCH), arm64)
build: build-arm64
else
build: build-amd64
endif

clean:
	rm -rf $(LINUX_DIR)

clean_all: clean
	rm $(KERNEL)

RED=\033[0;31m
GREEN=\033[0;32m
NC=\033[0m # No Color

define print_config
	printf "\n=============================\n"; \
	printf "${GREEN} Build Linux kernel for gem5 ${NC}\n"; \
	printf " ---\n"; \
	printf "kernel version: $(KVERSION)\n"; \
	printf "Output: $(KERNEL)\n"; \
	printf "=============================\n\n";
endef