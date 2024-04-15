#!/usr/bin/env bash
LIB=$(dirname $(readlink -f -- "$0";));
PYTHONPATH=$PYTHONPATH:$LIB jupyter lab --no-browser
