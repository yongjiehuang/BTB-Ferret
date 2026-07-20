
locals {
  rootdir = "${path.root}/../../"
}

variable "ssh_password" {
  type    = string
  default = "12345"
}

variable "ssh_username" {
  type    = string
  default = "gem5"
}

variable "architecture" {
  type    = string
  default = "arm64"
}


source "null" "remote" {
  ssh_host = "localhost"
  ssh_port = "8888"
  ssh_password     = "${var.ssh_password}"
  ssh_username     = "${var.ssh_username}"
  ssh_handshake_attempts = "30"
  # shutdown_command = "echo '${var.ssh_password}'|sudo -S shutdown -P now"
  communicator = "ssh"
}




build {
  sources = ["sources.null.remote"]
  # sources = ["sources.qemu.boot"]


  # Install Docker --------------------------
  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    scripts         = ["${local.rootdir}/image/scripts/install_docker.sh"]
  }




  ### Move the client to the VM
  provisioner "file" {
    destination = "http-client"
    source      = "${local.rootdir}/wkdir/${var.architecture}/http-client"
  }

  provisioner "shell" {
    inline = [
      "chmod +x http-client",
    ]
  }

  ## Nodeapp provisioning --------------------------
  provisioner "file" {
    destination = "nodeapp.urls.tmpl"
    source      = "${local.rootdir}/benchmarks/nodeapp/urls.tmpl"
  }

  provisioner "file" {
    destination = "dc-nodeapp.yaml"
    source      = "${local.rootdir}/benchmarks/nodeapp/docker-compose.yaml"
  }


  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    inline = [
      "sudo docker compose -f dc-nodeapp.yaml pull",
      "sudo docker compose -f dc-nodeapp.yaml up -d",
      "sleep 10",
      "curl 0.0.0.0:9999/",
      "sudo docker compose -f dc-nodeapp.yaml down",
    ]
  }

  ## Mediawiki provisioning --------------------------
  provisioner "file" {
    destination = "mediawiki.urls.tmpl"
    source      = "${local.rootdir}/benchmarks/mediawiki/urls.tmpl"
  }

  provisioner "file" {
    destination = "dc-mediawiki.yaml"
    source      = "${local.rootdir}/benchmarks/mediawiki/docker-compose.yaml"
  }


  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    inline = [
      "sudo docker compose -f dc-mediawiki.yaml pull",
      "sudo docker compose -f dc-mediawiki.yaml up -d",
      "sleep 10",
      "curl 0.0.0.0:9999/",
      "sudo docker compose -f dc-mediawiki.yaml down",
    ]
  }


  ## Fleetbench provisioning --------------------------

  # 
  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} bash '{{ .Path }}'"
    scripts         = ["${local.rootdir}/benchmarks/fleetbench/install_fleetbench.sh"]
  }


  ## Verilator provisioning --------------------------
  provisioner "file" {
    destination = "Variane_testharness"
    source      = "${local.rootdir}/benchmarks/verilator/Variane_testharness"
  }

  provisioner "file" {
    destination = "dhrystone.riscv"
    source      = "${local.rootdir}/benchmarks/verilator/dhrystone.riscv"
  }

  provisioner "shell" {
    inline = [
      "chmod +x Variane_testharness",
    ]
  }


  #### Shutdown the VM ###########
  provisioner "shell" {
    inline = [
      "sudo shutdown -h now",
    ]
    valid_exit_codes = [ 0, 2300218 ]
  }

}
