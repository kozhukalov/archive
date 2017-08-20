#!/bin/bash

set -x

SCRIPTDIR=$(readlink -f $(dirname $0))
. ${SCRIPTDIR}/scriptrc

if [ -z ${WORKDIR} ]; then
    echo "WORKDIR is empty of unset"
    exit 1
fi
if [ -z ${SERVER_INTERFACE_NAME} ]; then
    echo "SERVER_INTERFACE_NAME is empty of unset"
    exit 1
fi

mkdir -p ${WORKDIR}

# Please note that if you run this command on Ubuntu
# There could be permission issues with leases and configuration files
# The issue is described here https://help.ubuntu.com/community/isc-dhcp-server
# To check apparmor status use the following command
# sudo apparmor_status
${SUDO} touch ${WORKDIR}/dhcpd.leases
${SUDO} ${DHCPD} -f --no-pid -lf ${WORKDIR}/dhcpd.leases -cf ${SCRIPTDIR}/dhcpd.conf ${SERVER_INTERFACE_NAME}
