#!/bin/bash

rm -rf a_dd b_dd ec

gh classroom clone student-repos -a 701141
mv tko-rep-submissions b_dd
./rename_folders.py b_dd usernames/b_dd_usernames.csv

gh classroom clone student-repos -a 701146
mv tko-rep-base-submissions a_dd
./rename_folders.py a_dd usernames/a_dd_usernames.csv

gh classroom clone student-repos -a 696117
mv tko-base-rep-submissions ec
./rename_folders.py ec usernames/ec_usernames.csv
