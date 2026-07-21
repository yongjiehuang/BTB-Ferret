{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/refs/tags/24.05.tar.gz") {} }:
let
  aarch64Platform = pkgs.pkgsCross.aarch64-multiplatform;
  buildInputs = with pkgs; [
    python3
    protobuf
    zlib
    boost
    gperftools
    ncurses
    libpng
    hdf5
    mpfr
    gmp
    libmpc
    isl
    zstd
    ninja
    libxml2
    xorg.libX11
    xorg.libXext
    xorg.xorgproto
    mesa
    libGLU
    xorg.libXi
    xorg.libXmu
    tbb
    mold-wrapped
    cmake
    # Compiler GCC per x86
    gcc13
    clang
    llvmPackages_14.clang-unwrapped.python
    # # Cross-compiler per ARM (AArch64)
    # aarch64Platform.buildPackages.gcc
    # aarch64Platform.buildPackages.binutils
    # aarch64Platform.glibc.static
  ];
  # moz_overlay = import (builtins.fetchTarball https://github.com/mozilla/nixpkgs-mozilla/archive/master.tar.gz);
  # rustpkgs = import <nixpkgs> { overlays = [ moz_overlay ]; };
  # rustBuild = (
  #   rustpkgs.rustChannelOf (
  #     let
  #       rustToolchain = builtins.replaceStrings ["\n" "\r" " " "\t"] ["" "" "" ""] (
  #         builtins.readFile ./rust-toolchain
  #       );
  #     in
  #       {
  #         channel = pkgs.lib.head (pkgs.lib.splitString "-" rustToolchain);
  #         date = pkgs.lib.concatStringsSep "-" (pkgs.lib.tail (pkgs.lib.splitString "-" rustToolchain));
  #       }
  #   )
  # ).rust.override {
  #   extensions = [
  #     "rust-src"
  #     "llvm-tools-preview"
  #     "rust-analyzer-preview"
  #     "rustfmt-preview"
  #   ];
  # };
  # byaccBuild = pkgs.stdenv.mkDerivation {
  #   pname = "byacc";
  #   version = "20210808";
  #   dontPatchELF = true;
  #   src = pkgs.fetchurl {
  #     urls = [
  #       "ftp://ftp.invisible-island.net/byacc/byacc-20210808.tgz"
  #       "https://invisible-mirror.net/archives/byacc/byacc-20210808.tgz"
  #     ];
  #     sha256 = "sha256-8VhSm+nQWUJjx/Eah2FqSeoj5VrGNpElKiME+7x9OoM=";
  #   };
  #   configureFlags = [
  #     "--program-transform-name='s,^,b,'"
  #     "--enable-btyacc"
  #   ];
  #   doCheck = true;
  #   postInstall = ''
  #     ln -s $out/bin/byacc $out/bin/yacc
  #   '';
  # };
  ld = pkgs.writeShellScriptBin "ld" ''
     exec ${pkgs.gcc13Stdenv.cc}/bin/ld ${pkgs.lib.concatMapStringsSep " " (l: "-L${pkgs.lib.getLib l}/lib -rpath ${pkgs.lib.getLib l}/lib" ) buildInputs} "$@"
  '';
  args = pkgs.lib.concatMapStringsSep " " (l: "-I${pkgs.lib.getDev l}/include -L${pkgs.lib.getLib l}/lib -Wl,-rpath,${pkgs.lib.getLib l}/lib" ) buildInputs;
  cc = pkgs.writeShellScriptBin "cc" ''
    exec ${pkgs.gcc13Stdenv.cc}/bin/cc ${args} "$@"
  '';
  cxx = pkgs.writeShellScriptBin "c++" ''
    exec ${pkgs.gcc13Stdenv.cc}/bin/c++ ${args} "$@"
  '';
in pkgs.gcc13Stdenv.mkDerivation rec {
  name = "env";
  EDITOR = "vim";
  M4 = "m4";
  inherit buildInputs;
# shellHook = ''
#     export CC=cc CXX=c++ LD=ld
#     export PATH=${ld}/bin:${cxx}/bin:${cc}/bin:$PATH
#     export CROSS_COMPILE=aarch64-unknown-linux-gnu-
#     export PATH=${pkgs.pkgsCross.aarch64-multiplatform.buildPackages.gcc}/bin:${pkgs.pkgsCross.aarch64-multiplatform.buildPackages.binutils}/bin:$PATH
#     # Aggiungi il path per le librerie statiche
#     export LIBRARY_PATH="${aarch64Platform.glibc.static}/lib:$LIBRARY_PATH"
# '';
# shellHook = ''
#     export PYTHONPATH="$PYTHONPATH:/run/current-system/sw/bin/python"
# '';
  hardeningDisable = [ "format" ];
  nativeBuildInputs = with pkgs; [
    python3.pkgs.pyyaml
    python3.pkgs.pandas
    python3.pkgs.seaborn
    python3.pkgs.matplotlib
    python3.pkgs.scipy
    pkgs.python3Packages.colorama
    pkgs.python3Packages.tabulate
    pkgs.python3Packages.graphviz
    pkgs.python3Packages.networkx
    pkgs.python3Packages.psutil
    git
    git-lfs
    gdb
    scons
    swig
    m4
    pkg-config
    tree
    # rustBuild
    # byaccBuild
    texinfoInteractive
    gnumake
    pre-commit
    go
    valgrind
    diffsitter
    jdk11
    zip
    unzip
    pueue
    parallel
    bazelisk
    autoconf
    automake
    libtool
    zfs
    # # Cross-compiler per ARM
    # pkgsCross.aarch64-multiplatform.buildPackages.gcc
    # pkgsCross.aarch64-multiplatform.buildPackages.binutils
  ];
}

