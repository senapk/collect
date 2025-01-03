#!/bin/bash
./pull_all.py a_dd
./collect.py a_dd/* --csv a_dd.csv --full

./pull_all.py b_dd
./collect.py b_dd/* --csv b_dd.csv --full

./pull_all.py ec
./collect.py ec/* --csv ec.csv --full

echo "Last updated: $(date)" > last_update.txt
git add .
git commit -m "Update on $(date)"
git push
