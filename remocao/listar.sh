#!/bin/sh
gh repo list qxcode-course --limit 1000 --json name --jq '.[].name' > todos.txt
