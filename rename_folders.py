#!/bin/env python3

import os
import argparse

def load_user_map(usernames_path: str) -> dict[str, str]:
    user_map: dict[str, str] = {}
    with open(usernames_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            parts = line.split(",")
            username = parts[0].strip()
            name = parts[1].strip().lower().replace(" ", "_")
            user_map[username] = name
    return user_map

calc_name_collision = lambda one, two: sum([1 for i in range(min(len(one), len(two))) if one[i] == two[i]])

def identify_prefix(folders: list[str]) -> int:
    if not folders:
        return 0
    prefix = folders[0]
    for folder in folders[1:]:
        prefix = prefix[:calc_name_collision(prefix, folder)]
    return len(prefix)

def main():
    parser = argparse.ArgumentParser(description="Rename folders based on usernames")
    parser.add_argument("root", type=str, help="Root folder")
    parser.add_argument("usernames", type=str, help="usernames csv file")

    args = parser.parse_args()
    usernames_path = args.usernames
    user_map = load_user_map(usernames_path)

    files: list[str] = os.listdir(args.root)
    folders: list[str] = [f for f in files if os.path.isdir(os.path.join(args.root, f))]
    prefix = identify_prefix(folders)

    for folder in folders:
        folder_username = folder[prefix:]
        folder_path = os.path.join(args.root, folder)
        if folder_username in user_map:
            name = user_map[folder_username]
            new_folder_path = os.path.join(args.root, name)
            os.rename(folder_path, new_folder_path)
            print(f"{folder} -> {name}")

main()