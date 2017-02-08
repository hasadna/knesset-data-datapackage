#!/usr/bin/env bash

set -e  # exit on errors

[ -f .travis/.env ] && source .travis/.env

pip install --upgrade pip
pip install git+https://github.com/turnkeylinux/octohub.git
pip install .

if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ] && [ "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
    echo "creating ssh socks tunnel"
    echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
    chmod 400 sshproxy.key
    ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
fi
