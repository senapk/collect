#!/bin/bash

if [[ " $* " == *" --all "* ]]; then
    set -- "$@" --pull --collect --push
fi

if [[ " $* " == *" --pull "* ]]; then
    echo "Pulling data..."
    ./pull_all.py a_dd
    ./pull_all.py b_dd
    ./pull_all.py ec
fi

if [[ " $* " == *" --collect "* ]]; then
    echo "Collecting data from repositories"
    ./collect.py a_dd/* --csv a_dd.csv --full
    ./collect.py b_dd/* --csv b_dd.csv --full
    ./collect.py ec/* --csv ec.csv --full
fi

if [[ " $* " == *" --push "* ]]; then
    echo "Last updated: $(date)" > last_update.txt
    git add .
    git commit -m "Update on $(date)"
    git push
fi
