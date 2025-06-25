#!/bin/bash

if [[ " $* " == *" --all "* ]]; then
    set -- "$@" --pull --collect --grade --format
fi


if [[ " $* " == *" --headers "* ]]; then
    echo "Updating header files..."
    head -2 ed_m.csv > ed_t.csv
fi


if [[ " $* " == *" --pull "* ]]; then
    echo "Pulling data..."
    ./pull_all.py fup
    ./pull_all.py ed_m
    ./pull_all.py ed_t
fi

if [[ " $* " == *" --collect "* ]]; then
    echo "Collecting data from repositories"
    ./collect.py fup/* --csv fup.csv --graph graph_fup.txt --rep fup
    ./collect.py ed_m/* --csv ed_m.csv --graph graph_ed_m.txt --rep ed
    ./collect.py ed_t/* --csv ed_t.csv --graph graph_ed_t.txt --rep ed
fi


if [[ " $* " == *" --grade "* ]]; then
    echo "Updating grades"
    ./grade.py fup.csv
    ./grade.py ed_m.csv
    ./grade.py ed_t.csv
    ./grade.py fup_count.csv
    ./grade.py ed_m_count.csv
    ./grade.py ed_t_count.csv
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
