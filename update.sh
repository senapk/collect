#!/bin/bash

if [[ " $* " == *" --all "* ]]; then
    set -- "$@" --pull --collect --grade --format --push
fi


if [[ " $* " == *" --headers "* ]]; then
    echo "Updating header files..."
    head -2 a_dd.csv > b_dd.csv
    head -2 a_dd.csv > ec.csv
fi


if [[ " $* " == *" --pull "* ]]; then
    echo "Pulling data..."
    ./pull_all.py a_dd
    ./pull_all.py b_dd
    ./pull_all.py ec
fi

if [[ " $* " == *" --collect "* ]]; then
    echo "Collecting data from repositories"
    ./collect.py a_dd/* --csv a_dd.csv --graph graph_a_dd.txt
    ./collect.py b_dd/* --csv b_dd.csv --graph graph_b_dd.txt
    ./collect.py ec/*   --csv ec.csv   --graph graph_ec.txt
fi


if [[ " $* " == *" --grade "* ]]; then
    echo "Updating grades"
    ./grade.py a_dd.csv
    ./grade.py b_dd.csv
    ./grade.py ec.csv
    ./grade.py a_dd_count.csv
    ./grade.py b_dd_count.csv
    ./grade.py ec_count.csv
fi

if [[ " $* " == *" --format "* ]]; then
    echo "Formatting data"
    ./format.py *.csv
fi

if [[ " $* " == *" --push "* ]]; then
    echo "Last updated: $(date)" > last_update.txt
    git add .
    git commit -m "Update on $(date)"
    git push
fi
