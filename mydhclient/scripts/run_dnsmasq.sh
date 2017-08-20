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
${SUDO} /usr/sbin/dnsmasq -d --conf-file=${SCRIPTDIR}/dnsmasq.conf --log-facility=${WORKDIR}/dnsmasq.log --dhcp-leasefile=${WORKDIR}/dnsmasq.leases --interface=${SERVER_INTERFACE_NAME}
