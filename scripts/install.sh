
set -xue

sudo apt update

# Install qemu and others
sudo apt install -y \
        qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virtinst libvirt-daemon \
        pip python3-matplotlib python3-pandas python3-numpy python3-scipy


# Check system architecture

ARCH="amd64"

if [ $(uname -m) == "aarch64" ]; then
        ARCH="arm64"
fi

# Install go

wget https://go.dev/dl/go1.23.3.linux-$ARCH.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.23.3.linux-$ARCH.tar.gz
rm go1.23.3.linux-$ARCH.tar.gz
export PATH=$PATH:/usr/local/go/bin
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc

go version


ARCH="$(uname -m)"

wget https://github.com/Nukesor/pueue/releases/download/v4.0.0/pueue-$ARCH-unknown-linux-musl
wget https://github.com/Nukesor/pueue/releases/download/v4.0.0/pueued-$ARCH-unknown-linux-musl

mv pueue-$ARCH-unknown-linux-musl /usr/local/bin/pueue
mv pueued-$ARCH-unknown-linux-musl /usr/local/bin/pueued

chmod +x /usr/local/bin/pueue
chmod +x /usr/local/bin/pueued