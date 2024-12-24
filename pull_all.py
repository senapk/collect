#!/bin/env python

import os
import argparse
import subprocess
from typing import Any, Tuple


parser = argparse.ArgumentParser(description='Pull all git repositories in a directory')
parser.add_argument('directory', type=str, help='Directory to pull all git repositories in')

args = parser.parse_args()
directory = args.directory

folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
outputs: list[str] = []
processes: list[Tuple[str, Any]] = []

root = os.getcwd()
# create a child process for each folder and wait for it to finish after the for loop
for folder in folders:
    # Check if the folder is a git repository
    if not os.path.exists(os.path.join(directory, folder, '.git')):
        continue
    os.chdir(os.path.join(directory, folder))
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processes.append((folder, process))
    os.chdir(root)

# Espera todos os subprocessos terminarem
for folder, process in processes:
    stdout, stderr = process.communicate()
    # print(f"Comando terminou com código {process.returncode}")
    output: str = stdout.decode().strip()
    error : str = stderr.decode().strip()
    if not output.startswith("Already up to date."):
        print(folder)
        if error != "":
            # print in red
            print(f"\033[91m{error}\033[0m")
    
