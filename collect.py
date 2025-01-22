#!/usr/bin/env python3
import csv
import os
import yaml # type: ignore
import json
import argparse
import datetime
import subprocess

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
    def __init__(self, name: str, coverage: int = 0, autonomy: int = 0, skill: int = 0, attempts: int = 0, elapsed: int = 0):
        self.name = name
        self.coverage = coverage
        self.autonomy = autonomy
        self.skill = skill
        self.attempts = attempts
        self.elapsed = elapsed

    @staticmethod
    def get_autonomy_symbol(autonomy: int) -> str:
        return ["x", "E", "D", "C", "B", "A"][autonomy]
    
    @staticmethod
    def get_ability_symbol(ability: int) -> str:
        return ["x", "e", "d", "c", "b", "a"][ability]

    def str_mini(self) -> str:
        coverage_str = str(self.coverage).rjust(3, "0")
        autonomy_str = Task.get_autonomy_symbol(self.autonomy)
        ability_str = Task.get_ability_symbol(self.skill)
        return f"{coverage_str}{autonomy_str}{ability_str}"


    def str_full(self) -> str:
        coverage_str = str(self.coverage).rjust(3, "0")
        count_str = str(self.attempts).rjust(3, "0")
        minutes_str = str(self.elapsed).rjust(3, "0")
        autonomy_str = Task.get_autonomy_symbol(self.autonomy)
        ability_str = Task.get_ability_symbol(self.skill)
        return f"{coverage_str}{autonomy_str}{minutes_str}{ability_str}{count_str}"
    
    def __str__(self) -> str:
        return self.str_full()

def get_user_tasks(folder: str) -> dict[str, Task]:
    print(folder)
    folder = os.path.join(folder, "poo")
    # run subprocess and capture output
    result = subprocess.run(["rota", "rep", "resume", folder], capture_output=True, text=True)
    output = result.stdout
    #print(output)
    #parse output yaml into a dict[str, dict[str, str]]
    data: dict[str, dict[str, str]] = yaml.safe_load(output)
    tasks: dict[str, Task] = {}
    if data is None:
        return tasks
    for key in data.keys():
        name     = key
        coverage = int(data[key]["coverage"])
        autonomy = int(data[key]["autonomy"])
        skill    = int(data[key]["skill"])
        elapsed  = int(data[key]["elapsed"])
        attempts = int(data[key]["attempts"])
        tasks[name] = Task(name, coverage, autonomy, skill, attempts, elapsed)
    
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
        user_tasks_map[folder] = get_user_tasks(folder)
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
