#!/bin/bash

set -x

SCRIPTDIR=$(readlink -f $(dirname $0))
. ${SCRIPTDIR}/scriptrc

if [ -z ${CLIENT_INTERFACE_NAME} ]; then
    echo "CLIENT_INTERFACE_NAME is empty of unset"
    exit 1
fi
if [ -z ${CLIENT_INTERFACE_MAC} ]; then
    echo "CLIENT_INTERFACE_MAC is empty of unset"
    exit 1
fi
if [ -z ${SERVER_INTERFACE_NAME} ]; then
    echo "SERVER_INTERFACE_NAME is empty of unset"
    exit 1
fi
if [ -z ${SERVER_INTERFACE_IP} ]; then
    echo "SERVER_INTERFACE_IP is empty of unset"
    exit 1
fi
if [ -z ${SERVER_INTERFACE_CIDR} ]; then
    echo "SERVER_INTERFACE_CIDR is empty of unset"
    exit 1
fi

${SUDO} ip link add name ${SERVER_INTERFACE_NAME} type veth peer name ${CLIENT_INTERFACE_NAME} address ${CLIENT_INTERFACE_MAC}
sleep 1
${SUDO} ip link set ${SERVER_INTERFACE_NAME} up
${SUDO} ip link set ${CLIENT_INTERFACE_NAME} up
${SUDO} ip address add ${SERVER_INTERFACE_IP}/${SERVER_INTERFACE_CIDR} dev ${SERVER_INTERFACE_NAME}
