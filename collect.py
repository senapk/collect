#!/usr/bin/env python3
import csv
import os
import yaml # type: ignore
import json
import argparse
import datetime

def load_csv(arquivo_csv) -> list[list[str]]:
    try:
        with open(arquivo_csv, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            sheet = list(reader)
            return sheet
    except FileNotFoundError:
        exit(f"Arquivo '{arquivo_csv}' não encontrado.")

# count how many characters are in common in the beginning of two strings
def calc_name_collision(one, two) -> int:
    count = 0
    for i in range(min(len(one), len(two))):
        if one[i] == two[i]:
            count += 1
        else:
            break
    return count

class Task:
    def __init__(self, name: str, coverage: int = 0, autonomy: int = 0, ability: int = 0, count: int = 0, minutes: int = 0):
        self.name = name
        self.coverage = coverage
        self.autonomy = autonomy
        self.ability = ability
        self.count = count
        self.minutes = 0

    @staticmethod
    def get_autonomy_symbol(autonomy: int) -> str:
        return ["x", "E", "D", "C", "B", "A"][autonomy]
    
    @staticmethod
    def get_ability_symbol(ability: int) -> str:
        return ["x", "e", "d", "c", "b", "a"][ability]

    def str_mini(self) -> str:
        coverage_str = str(self.coverage).rjust(3, "0")
        autonomy_str = Task.get_autonomy_symbol(self.autonomy)
        ability_str = Task.get_ability_symbol(self.ability)
        return f"{coverage_str}{autonomy_str}{ability_str}"


    def str_full(self) -> str:
        coverage_str = str(self.coverage).rjust(3, "0")
        count_str = str(self.count).rjust(3, "0")
        minutes_str = str(self.minutes).rjust(3, "0")
        autonomy_str = Task.get_autonomy_symbol(self.autonomy)
        ability_str = Task.get_ability_symbol(self.ability)
        return f"{coverage_str}{autonomy_str}{minutes_str}{ability_str}{count_str}"
    
    def __str__(self) -> str:
        return self.str_full()

def get_task_count_map(folder: str) -> dict[str, int]:
    path = os.path.join(folder, "poo", ".tko", "history.csv")
    task_count_map: dict[str, int] = {}
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
            for line in lines:
                parts = line.split(",")
                if len(parts) == 5:
                    hash = parts[0]
                    timestamp = parts[1]
                    action = parts[2]
                    task = parts[3]
                    payload = parts[4]
                    if action == "TEST" or action == "PROG":
                        if task not in task_count_map:
                            task_count_map[task] = 1
                        else:
                            task_count_map[task] = task_count_map[task] + 1

    return task_count_map

def get_task_timestamps(folder: str) -> dict[str, list[str]]:
    path = os.path.join(folder, "poo", ".tko", "history.csv")
    task_timestamp_list: dict[str, list[str]] = {}
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
            for line in lines:
                parts = line.split(",")
                if len(parts) == 5:
                    hash = parts[0]
                    timestamp = parts[1]
                    action = parts[2]
                    task = parts[3]
                    payload = parts[4]
                    if task != "":
                        if task not in task_timestamp_list:
                            task_timestamp_list[task] = [timestamp]
                        else:
                            task_timestamp_list[task].append(timestamp)

    return task_timestamp_list

def calc_time_usage(task_timestamps: dict[str, list[str]], minutes: int) -> dict[str, int]:
    task_usage: dict[str, datetime.timedelta] = {}

    # initialize task_usage
    for task in task_timestamps:
        task_usage[task] = datetime.timedelta(0)

    format = '%Y-%m-%d %H:%M:%S'
    for task in task_timestamps:
        array = [datetime.datetime.strptime(x, format) for x in task_timestamps[task]]
        last_timestamp = array[0]
        for i in range(1, len(array)):
            diff = array[i] - last_timestamp
            # check if difference is less than 20 minutes
            if diff.total_seconds() < minutes * 60:
                task_usage[task] += diff
            last_timestamp = array[i]
    # convert to minutes
    task_minutes: dict[str, int] = {}
    for task in task_usage:
        task_minutes[task] = int(task_usage[task].total_seconds() / 60)
    return task_minutes
    
def get_yaml_tasks(folder: str) -> dict[str, Task]:
    path = os.path.join(folder, "poo", ".tko", "repository.yaml")
    tasks: dict[str, Task] = {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for key in data["tasks"]:
                value = data["tasks"][key]
                parts = value.split(":")
                if len(parts) == 3:
                    coverage = int(parts[2])
                    opts = [(0, 0), (1, 1), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3), (4, 3), (3, 4), (4, 4)]
                    autonomy, ability = opts[int(parts[0])]
                    tasks[key] = Task(key, coverage, autonomy, ability)
                elif len(parts) == 4:
                    coverage = int(parts[0])
                    autonomy = int(parts[1])
                    ability = int(parts[2])
                    tasks[key] = Task(key, coverage, autonomy, ability)
    except FileNotFoundError:
        print(f"Arquivo '{path}' não encontrado.")
    return tasks

def load_header(user_tasks_map: dict[str, dict[str, Task]], arquivo_csv: str | None) -> list[str]:
    header: list[str] = []
    if arquivo_csv:
        sheet = load_csv(arquivo_csv)
        header = sheet[0]
        header = [x.strip() for x in header]

    else:
        tasks_key_set: set[str] = set()
        for folder in user_tasks_map:
            tasks_key_set.update(user_tasks_map[folder].keys())
        header = ["user"] + list(tasks_key_set)
    return header

def format_sheet(sheet: list[list[str]]) -> list[list[str]]:
    # discover the maximum length of each column and pad the strings
    max_len = [0] * len(sheet[0])
    for line in sheet:
        for i, cell in enumerate(line):
            max_len[i] = max(max_len[i], len(cell))
    for line in sheet:
        for i, cell in enumerate(line):
            line[i] = cell.ljust(max_len[i])
    return sheet

def load_history_and_yaml(folder: str):
    minutes_threshold = 30
    tasks_map: dict[str, Task] = get_yaml_tasks(folder)
    # update with count
    tasks_count = get_task_count_map(folder)
    for task in tasks_count:
        if task in tasks_map:
            tasks_map[task].count = tasks_count[task]
        else:
            tasks_map[task] = Task(task)
            tasks_map[task].count = tasks_count[task]

    # update with time usage
    task_timestamps = get_task_timestamps(folder)
    task_minutes = calc_time_usage(task_timestamps, minutes_threshold)
    for task in task_minutes:
        if task in tasks_map:
            tasks_map[task].minutes = task_minutes[task]
        else:
            tasks_map[task] = Task(task)
            tasks_map[task].minutes = task_minutes[task]

    return tasks_map

def load_line(folder: str, tasks: dict[str, Task], header: list[str], full_str: bool) -> list[str]:
    task_len = calc_task_len(full_str)
    student = os.path.basename(folder)
    line: list[str] = ["" for _ in range(len(header))]
    for i, key in enumerate(header):
        if i == 0:
            line[i] = student
        else:
            if key in tasks:
                line[i] = tasks[key].str_full() if full_str else tasks[key].str_mini()
            else:
                line[i] = "_" * task_len
    return line

def calc_task_len(full: bool) -> int:
    if full:
        return len(Task("x", 0, 0, 0).str_full())
    return len(Task("x", 0, 0, 0).str_mini())

def main():
    # Caminho do arquivo CSV
    parser = argparse.ArgumentParser(description="Coleta de dados de atividades de programação.")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("folders", nargs="*", help="Pastas dos projetos.")
    parser.add_argument("--csv", help="Caminho do arquivo CSV.")
    parser.add_argument("--full", action="store_true", help="Coleta de todos os dados")
    args = parser.parse_args()

    if args.version:
        print("1.0")
        return

    folders = [f for f in args.folders if os.path.isdir(f)]
    folders = sorted(args.folders)

    # map folder to dict[task_name, Task]
    # user_tasks_map: dict[str, dict[str, Task]] = load_history_and_yaml(folders)
    user_tasks_map: dict[str, dict[str, Task]] = {}
    for folder in folders:
        user_tasks_map[folder] = load_history_and_yaml(folder)
    minutes_threshold = 30
    header: list[str] = load_header(user_tasks_map, args.csv)
    sheet: list[list[str]] = [header]
    for folder in folders:
        tasks_map = user_tasks_map[folder]
        line = load_line(folder, tasks_map, header, args.full)
        sheet.append(line)
    sheet = format_sheet(sheet)
    
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet)
    else:
        for line in sheet:
            print(",".join(line))

if __name__ == "__main__":
    main()
