packer {
  required_plugins {
    qemu = {
      source  = "github.com/hashicorp/qemu"
      version = "~> 1"
    }
  }
}

locals {
  rootdir = "${path.root}/../../"
}


variable "image_name" {
  type    = string
  default = "arm-ubuntu"
}

variable "ssh_password" {
  type    = string
  default = "12345"
}

variable "ssh_username" {
  type    = string
  default = "gem5"
}

variable "ubuntu_version" {
  type    = string
  default = "24.04"
  validation {
    condition     = contains(["22.04", "24.04"], var.ubuntu_version)
    error_message = "Ubuntu version must be either 22.04 or 24.04."
  }
}

locals {
  iso_data = {
    "22.04" = {
      iso_url       = "https://old-releases.ubuntu.com/releases/jammy/ubuntu-22.04-live-server-arm64.iso"
      iso_checksum  = "sha256:c209ab013280d3cd26a344def60b7b19fbb427de904ea285057d94ca6ac82dd5"
      output_dir    = "arm-disk-image-22-04"
      http_directory = "http/arm-22-04"
    }
    "24.04" = {
      iso_url       = "https://cdimage.ubuntu.com/releases/24.04/release/ubuntu-24.04.2-live-server-arm64.iso"
      iso_checksum  = "sha256:9fd122eedff09dc57d66e1c29acb8d7a207e2a877e762bdf30d2c913f95f03a4"
      output_dir    = "arm-disk-image-24-04"
      http_directory = "http/arm-24-04"
    }
  }
}

variable "use_kvm" {
  type    = string
  default = "true"
  validation {
    condition     = contains(["true", "false"], var.use_kvm)
    error_message = "KVM option must be either 'true' or 'false'."
  }
}

locals {
  qemuargs_base = [
    ["-boot", "order=dc"],
    ["-bios", "./files/flash0.img"],
    ["-machine", "virt"],
    ["-machine", "gic-version=max"],
    ["-serial", "mon:stdio"],
    ["-device", "virtio-gpu-pci"],
    ["-device", "qemu-xhci"],
    ["-device", "usb-kbd"],
    ["-nographic"],
  ]

  qemuargs_kvm = concat(local.qemuargs_base,[
    ["-cpu", "host"],
    ["-enable-kvm"]
  ])

  qemuargs_no_kvm = concat(local.qemuargs_base,[
    ["-cpu", "cortex-a57"]
  ])

  qemuargs = var.use_kvm == "true" ? local.qemuargs_kvm : local.qemuargs_no_kvm
}

source "qemu" "initialize" {
  boot_command     = [
                      "c<wait>",
                      "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{.HTTPIP}}:{{.HTTPPort}}/ --- ",
                      "<enter><wait>",
                      "initrd /casper/initrd",
                      "<enter><wait>",
                      "boot",
                      "<enter>",
                      "<wait>"
                      ]
  cpus             = "16"
  disk_size        = "16G"   # 15G + Boot partition + 1MB reserve
  format           = "raw"
  headless         = "true"
  http_directory   = local.iso_data[var.ubuntu_version].http_directory
  iso_checksum     = local.iso_data[var.ubuntu_version].iso_checksum
  iso_urls         = [local.iso_data[var.ubuntu_version].iso_url]
  memory           = "8192"
  output_directory = local.iso_data[var.ubuntu_version].output_dir
  qemu_binary      = "/usr/bin/qemu-system-aarch64"
  qemuargs         = local.qemuargs
  shutdown_command = "echo '${var.ssh_password}'|sudo -S shutdown -P now"
  ssh_password     = "${var.ssh_password}"
  ssh_username     = "${var.ssh_username}"
  ssh_wait_timeout = "60m"
  vm_name          = "${var.image_name}"
  ssh_handshake_attempts = "1000"
}

build {
  sources = ["source.qemu.initialize"]

  provisioner "file" {
    destination = "/home/gem5/"
    source      = "${local.rootdir}/image/files/exit.sh"
  }

  provisioner "file" {
    destination = "/home/gem5/"
    source      = "${local.rootdir}/image/files/gem5_init.sh"
  }

  provisioner "file" {
    destination = "/home/gem5/"
    source      = "${local.rootdir}/image/files/after_boot.sh"
  }

  provisioner "file" {
    destination = "/home/gem5/"
    source      = "${local.rootdir}/image/files/serial-getty@.service"
  }

  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    scripts         = ["${local.rootdir}/image/scripts/post-installation.sh"]
    environment_vars = ["ISA=arm64"]
    expect_disconnect = true
  }
}
