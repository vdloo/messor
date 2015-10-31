#!/usr/bin/env bash
set -e

function clear_pyc {
    find . -type f -name *.pyc -delete
}

clear_pyc
nosetests tests/
clear_pyc
