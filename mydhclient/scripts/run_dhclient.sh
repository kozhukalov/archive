#!/bin/bash

set -x

SCRIPTDIR=$(readlink -f $(dirname $0))
. ${SCRIPTDIR}/scriptrc

if [ -z ${WORKDIR} ]; then
    echo "WORKDIR is empty of unset"
    exit 1
fi
if [ -z ${CLIENT_INTERFACE_NAME} ]; then
    echo "CLIENT_INTERFACE_NAME is empty of unset"
    exit 1
fi

mkdir -p ${WORKDIR}
# It turned out that dhclient does not work with custom leases and script files
# When I try to run it with -lf and -sf options it says something like
# can't create ${WORKDIR}/dhclient.leases: Permission denied
# execve (${SCRIPTDIR}//dhclient-script, ...): Permission denied
# This is due to apparmor loaded and working
# The issue is described here https://help.ubuntu.com/community/isc-dhcp-server
# To check apparmor status just run the command
# sudo apparmor_status
${SUDO} ${DHCLIENT} -d --no-pid -lf ${WORKDIR}/dhclient.leases -sf ${SCRIPTDIR}/dhclient-script -cf ${SCRIPTDIR}/dhclient.conf ${CLIENT_INTERFACE_NAME}
