spec_workloads = {}



SPECDIR="/share/david/spec/arm64/benchspec/CPU/"
TEST="run/run_base_refrate_mytestst-64.0000"
BIN="mytestst-64"



# 500.perlbench --------------
rundir = f"{SPECDIR}/500.perlbench_r/{TEST}"
spec_workloads |= {
    "500.perlbench_r.checkspam": {
        "rundir": rundir,
        "cmd": f"{rundir}/perlbench_r_base.{BIN}",
        "args": f"-I{rundir}/lib {rundir}/checkspam.pl 2500 5 25 11 150 1 1 1 1".split(),
    },
    "500.perlbench_r.diffmail": {
        "rundir": rundir,
        "cmd": f"{rundir}/perlbench_r_base.{BIN}",
        "args": f"-I{rundir}/lib {rundir}/diffmail.pl 4 800 10 17 19 300".split(),
    },
    "500.perlbench_r.splitmail": {
        "rundir": rundir,
        "cmd": f"{rundir}/perlbench_r_base.{BIN}",
        "args": f"-I{rundir}/lib {rundir}/splitmail.pl 6400 12 26 16 100 0".split(),
    }
}


# 502.gcc ------------------
rundir = f"{SPECDIR}/502.gcc_r/{TEST}"
spec_workloads |= {
    "502.gcc_r.gcc-pp.opts-O3_-finline-limit_0": {
        "rundir": rundir,
        "cmd": f"{rundir}/cpugcc_r_base.{BIN}",
        "args": f"{rundir}/gcc-pp.c -O3 -finline-limit=0 -fif-conversion -fif-conversion2".split(),
    },
    "502.gcc_r.gcc-pp.opts-O3_-finline-limit_36000": {
        "rundir": rundir,
        "cmd": f"{rundir}/cpugcc_r_base.{BIN}",
        "args": f"{rundir}/gcc-pp.c -O2 -finline-limit=36000 -fpic".split(),
    },
    "502.gcc_r.gcc-smaller.c-O3_-fipa-pta": {
        "rundir": rundir,
        "cmd": f"{rundir}/cpugcc_r_base.{BIN}",
        "args": f"{rundir}/gcc-smaller.c -O3 -fipa-pta -o {rundir}/gcc-smaller.opts-O3_-fipa-pta.s".split(),
    },
    "502.gcc_r.ref32.c_-O5": {
        "rundir": rundir,
        "cmd": f"{rundir}/cpugcc_r_base.{BIN}",
        "args": f"{rundir}/ref32.c -O5".split(),
    },
    "502.gcc_r.ref32.c_-O3": {
        "rundir": rundir,
        "cmd": f"{rundir}/cpugcc_r_base.{BIN}",
        "args": f"{rundir}/ref32.c -O3 -fselective-scheduling -fselective-scheduling2".split(),
    }
}


## 505.mcf ------------------
rundir = f"{SPECDIR}/505.mcf_r/{TEST}"
spec_workloads |= {
    "505.mcf_r.inp": {
        "rundir": rundir,
        "cmd": f"{rundir}/mcf_r_base.{BIN}",
        "args": f"{rundir}/inp.in".split(),
    }
}


## 520.omnetpp_r ------------------
rundir = f"{SPECDIR}/520.omnetpp_r/{TEST}"
spec_workloads |= {
    "520.omnetpp_r.general": {
        "rundir": rundir,
        "cmd": f"{rundir}/omnetpp_r_base.{BIN}",
        "args": f"-c General -r 0".split(),
    }
}

## 523.xalancbmk_r ------------------
rundir = f"{SPECDIR}/523.xalancbmk_r/{TEST}"
spec_workloads |= {
    "523.xalancbmk_r.xalanc": {
        "rundir": rundir,
        "cmd": f"{rundir}/cpuxalan_r_base.{BIN}",
        "args": f"-v {rundir}/t5.xml {rundir}/xalanc.xsl".split(),
    }
}

## 525.x264_r ------------------
rundir = f"{SPECDIR}/525.x264_r/{TEST}"
spec_workloads |= {
    "525.x264_r.x264_pass1": {
        "rundir": rundir,
        "cmd": f"{rundir}/x264_r_base.{BIN}",
        "args": f"--pass 1 --stats {rundir}/x264_stats.log --bitrate 1000 --frames 1000 -o {rundir}/BuckBunny_New.264 {rundir}/BuckBunny.yuv 1280x720".split(),
    },
    "525.x264_r.x264_pass2": {
        "rundir": rundir,
        "cmd": f"{rundir}/x264_r_base.{BIN}",
        "args": f"--pass 2 --stats {rundir}/x264_stats.log --bitrate 1000 --dumpyuv 200 --frames 1000 -o {rundir}/BuckBunny_New.264 {rundir}/BuckBunny.yuv 1280x720".split(),
    },
    "525.x264_r.x264": {
        "rundir": rundir,
        "cmd": f"{rundir}/x264_r_base.{BIN}",
        "args": f"--seek 500 --dumpyuv 200 --frames 1250 -o {rundir}/BuckBunny_New.264 {rundir}/BuckBunny.yuv 1280x720".split(),
    }
}

## 531.deepsjeng_r ------------------
rundir = f"{SPECDIR}/531.deepsjeng_r/{TEST}"
spec_workloads |= {
    "531.deepsjeng_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/deepsjeng_r_base.{BIN}",
        "args": f"{rundir}/ref.txt".split(),
    }
}

## 541.leela_r ------------------
rundir = f"{SPECDIR}/541.leela_r/{TEST}"
spec_workloads |= {
    "541.leela_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/leela_r_base.{BIN}",
        "args": f"{rundir}/ref.sgf".split(),
    }
}

## 548.exchange2_r ------------------
rundir = f"{SPECDIR}/548.exchange2_r/{TEST}"
spec_workloads |= {
    "548.exchange2_r.general": {
        "rundir": rundir,
        "cmd": f"{rundir}/exchange2_r_base.{BIN}",
        "args": f"6 > {rundir}/exchange2.txt".split(),
    }
}

## 557.xz_r ------------------
rundir = f"{SPECDIR}/557.xz_r/{TEST}"
spec_workloads |= {
    "557.xz_r.cld": {
        "rundir": rundir,
        "cmd": f"{rundir}/xz_r_base.{BIN}",
        "args": f"{rundir}/cld.tar.xz 160 19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474 59796407 61004416 6".split(),
    },
    "557.xz_r.cpu2006docs": {
        "rundir": rundir,
        "cmd": f"{rundir}/xz_r_base.{BIN}",
        "args": f"{rundir}/cpu2006docs.tar.xz 250 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 23047774 23513385 6e".split(),
    },
    "557.xz_r.input": {
        "rundir": rundir,
        "cmd": f"{rundir}/xz_r_base.{BIN}",
        "args": f"{rundir}/input.combined.xz 250 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 40401484 41217675 7".split(),
    }
}

# 999.specrand_ir ------------------
rundir = f"{SPECDIR}/999.specrand_ir/{TEST}"
spec_workloads |= {
    "999.specrand_ir.rand": {
        "rundir": rundir,
        "cmd": f"{rundir}/specrand_ir_base.{BIN}",
        "args": f"1255432124 234923".split(),
    }
}

## 508.namd_r ------------------
rundir = f"{SPECDIR}/508.namd_r/{TEST}"
spec_workloads |= {
    "508.namd_r.apoa1": {
        "rundir": rundir,
        "cmd": f"{rundir}/namd_r_base.{BIN}",
        "args": f"--input {rundir}/apoa1.input --output apoa1.ref.output --iterations 65".split(),
    }
}

## 510.parest_r ------------------
rundir = f"{SPECDIR}/510.parest_r/{TEST}"
spec_workloads |= {
    "510.parest_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/parest_r_base.{BIN}",
        "args": f"{rundir}/ref.prm".split(),
    }
}

## 511.povray_r ------------------
# Copy content of run directory to wkdir
rundir = f"{SPECDIR}/511.povray_r/{TEST}"
spec_workloads |= {
    "511.povray_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/povray_r_base.{BIN}",
        "args": f"SPEC-benchmark-ref.ini".split(),
        # "args": f"--help".split(),
    }
}

## 519.lbm_r ------------------
rundir = f"{SPECDIR}/519.lbm_r/{TEST}"
spec_workloads |= {
    "519.lbm_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/lbm_r_base.{BIN}",
        "args": f"3000 {rundir}/reference.dat 0 0 {rundir}/100_100_130_ldc.of".split(),
    }
}

## 526.blender_r ------------------
rundir = f"{SPECDIR}/526.blender_r/{TEST}"
spec_workloads |= {
    "526.blender_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/blender_r_base.{BIN}",
        "args": f"{rundir}/sh3_no_char.blend --render-output sh3_no_char_ --threads 1 -b -F RAWTGA -s 849 -e 849 -a".split(),
    }
}


## 538.imagick_r ------------------
rundir = f"{SPECDIR}/538.imagick_r/{TEST}"
spec_workloads |= {
    "538.imagick_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/imagick_r_base.{BIN}",
        "args": f"-limit disk 0 {rundir}/refrate_input.tga -edge 41 -resample 181% -emboss 31 -colorspace YUV -mean-shift 19x19+15% -resize 30% refrate_output.tga".split(),
    }
}

## 544.nab_r ------------------
## Need to copy 1am0 into the run folder
rundir = f"{SPECDIR}/544.nab_r/{TEST}"
spec_workloads |= {
    "544.nab_r.ref": {
        "rundir": rundir,
        "cmd": f"{rundir}/nab_r_base.{BIN}",
        "args": f"1am0 1122214447 122".split(),
    }
}