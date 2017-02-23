#!/usr/bin/env bash

set -e  # exit on errors

if ! which coverage > /dev/null; then
    pip install coverage
fi

coverage run -m unittest discover -v
coverage report
