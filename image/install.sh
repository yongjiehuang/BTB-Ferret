
set -x

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ARCH=$(dpkg --print-architecture)

PACKER_VERSION="1.11.2"

if [ ! -f /usr/local/bin/packer ]; then
    wget https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_${ARCH}.zip;
    unzip packer_${PACKER_VERSION}_linux_${ARCH}.zip;
    rm packer_${PACKER_VERSION}_linux_${ARCH}.zip;
    rm LICENSE.txt
    mv packer /usr/local/bin/packer
    chmod +x /usr/local/bin/packer
fi



# Store the configuration file name from the command line argument
config_file=$SCRIPTPATH/packer-scripts/benchmarks.pkr.hcl


make -f $SCRIPTPATH/Makefile build-wkdir

make -f $SCRIPTPATH/Makefile run-$ARCH 1> qemu.log 2>&1 &

QEMU_PID=$!
echo "QEMU PID: $QEMU_PID"





# Wait for the QEMU process to finish
sleep 1s


# Check if the specified configuration file exists
if [ -f "$config_file" ]; then
    # Install the needed plugins
    /usr/local/bin/packer init "$config_file"
    # Build the image
    /usr/local/bin/packer build -var "architecture=$ARCH" "$config_file" 
else
    echo "Error: Configuration file '$config_file' not found."
    exit 1
fi


# Wait for the QEMU process to finish
wait $QEMU_PID

rm -rf $SCRIPTPATH/tmp