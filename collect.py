#!/usr/bin/env python3
import csv
import os
import yaml # type: ignore
import json
import argparse
import datetime
import subprocess

from util import load_csv, save_csv, Entry, load_entries, load_header

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
    
    def str_count(self) -> str:
        minutes_str = str(self.elapsed).rjust(3, "0")
        count_str = str(self.attempts).rjust(3, "0")
        return f"{minutes_str}m,{count_str}e"

    def str_full(self) -> str:
        coverage_str = str(self.coverage).rjust(3, "0")
        count_str = str(self.attempts).rjust(3, "0")
        minutes_str = str(self.elapsed).rjust(3, "0")
        autonomy_str = Task.get_autonomy_symbol(self.autonomy)
        ability_str = Task.get_ability_symbol(self.skill)
        return f"{coverage_str}{autonomy_str}{ability_str}{minutes_str}m{count_str}e"

def get_user_graph(folder: str) -> str:
    print(".." + folder)
    folder = os.path.join(folder, "poo")
    # run subprocess and capture output
    result = subprocess.run(["tko", "rep", "graph", folder], capture_output=True, text=True)
    output = result.stdout
    return output

def get_user_tasks(folder: str) -> dict[str, Task]:
    print(".." + folder)
    folder = os.path.join(folder, "poo")
    # run subprocess and capture output
    result = subprocess.run(["tko", "rep", "resume", folder], capture_output=True, text=True)
    output = result.stdout
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

def load_line(folder: str, tasks: dict[str, Task], header: list[Entry], mode: str) -> list[str]:
    task_len = calc_task_len(mode)
    student = os.path.basename(folder)
    line: list[str] = [student, "--?--"]
    header_keys = [entry.label for entry in header]
    for key in header_keys:
        if key in tasks:
            if mode == "count":
                line.append(tasks[key].str_count())
            elif mode == "full":
                line.append(tasks[key].str_full())
            else:
                line.append(tasks[key].str_mini())
        else:
            line.append("_" * task_len)
    return line

def calc_task_len(mode: str) -> int:
    if mode == "full":
        return len(Task("x", 0, 0, 0).str_full())
    if mode == "count":
        return len(Task("x", 0, 0, 0).str_count())
    return len(Task("x", 0, 0, 0).str_mini())

def main():
    # Caminho do arquivo CSV
    parser = argparse.ArgumentParser(description="Coleta de dados de atividades de programação.")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("folders", nargs="*", help="Pastas dos projetos.")
    parser.add_argument("--csv", help="Caminho do arquivo CSV.")
    parser.add_argument("--graph", type=str)
    args = parser.parse_args()

    if args.version:
        print("1.0")
        return
    
    if not args.csv:
        print("É necessário informar o caminho do arquivo CSV.")
        return

    folders = [f for f in args.folders if os.path.isdir(f)]
    folders = sorted(args.folders)

    if args.graph:
        with open(args.graph, "w", encoding="utf-8") as graphfile:
            for folder in folders:
                graph = get_user_graph(folder)
                graphfile.write("\n")
                graphfile.write(folder)
                graphfile.write(graph)
                graphfile.write("\n")


    # map folder to dict[task_name, Task]
    # user_tasks_map: dict[str, dict[str, Task]] = load_history_and_yaml(folders)
    user_tasks_map: dict[str, dict[str, Task]] = {}
    for folder in folders:
        user_tasks_map[folder] = get_user_tasks(folder)

    sheet = load_csv(args.csv) # carrega a planilha inteira a partir do csv
    entries = load_entries(sheet)

    sheet_notes: list[list[str]] = load_header(sheet)
    sheet_count: list[list[str]] = load_header(sheet)

    for folder in folders:
        tasks_map = user_tasks_map[folder]
        line_notes = load_line(folder, tasks_map, entries, "notes")
        line_count = load_line(folder, tasks_map, entries, "full")
        sheet_notes.append(line_notes)
        sheet_count.append(line_count)
    
    save_csv(args.csv, sheet_notes)
    save_csv(args.csv.replace(".csv", "_count.csv"), sheet_count)

if __name__ == "__main__":
    main()
