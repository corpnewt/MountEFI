#!/bin/bash

# Turn on case-insensitive matching
shopt -s nocasematch
# turn on extended globbing
shopt -s extglob

py_path="python3"
bot="MountEFI.py"
name="MountEFI"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function check_py () {
    if [ -x "$(command -v python3)" ]; then
        py_path="$(which python3)"
    else
        if [ -x "$(command -v python)" ]; then
            py_path="$(which python)"
        else
            echo
            exit 1
        fi
    fi
    echo $py_path
}

function main () {
    echo \#\#\# Starting "$name" \#\#\#
    cd "$DIR"
    py_path="$(check_py)"
    if [[ "$py_path" == "" ]]; then
        echo
        echo "Python is not installed!"
        echo
        exit 1
    fi
    "$py_path" "$bot"
}

function silent () {
    cd "$DIR"
    py_path="$(check_py)"
    if [[ "$py_path" == "" ]]; then
        exit 1
    fi
    "$py_path" "$bot" "$1"
}

if [[ "$1" == "" ]]; then
    main
else
    silent $1
fi