#!/bin/bash

set -x

SCRIPTDIR=$(readlink -f $(dirname $0))
. ${SCRIPTDIR}/scriptrc

if [ -z ${CLIENT_INTERFACE_NAME} ]; then
    echo "CLIENT_INTERFACE_NAME is empty of unset"
    exit 1
fi
if [ -z ${SERVER_INTERFACE_NAME} ]; then
    echo "SERVER_INTERFACE_NAME is empty of unset"
    exit 1
fi

# Since we use veth interfaces which are always paired
# thus destroying one of them also destroys paired one
${SUDO} ip link del ${SERVER_INTERFACE_NAME}
