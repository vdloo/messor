#!/usr/bin/env bash

function clear_pyc {
    find . -type f -name *.pyc -delete
}

clear_pyc
nosetests tests/
clear_pyc
