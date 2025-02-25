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
    nl = len(sheet)
    nc = len(sheet[0])

    for c in range(nc):
        for l in range(nl):
            sheet[l][c] = sheet[l][c].strip()

    for c in range(nc):
        max_len = 0
        for l in range(nl):
            max_len = max(max_len, len(sheet[l][c]))
        for l in range(nl):
            if c == 0:
                sheet[l][c] = sheet[l][c].ljust(max_len)
            else:
                sheet[l][c] = sheet[l][c].rjust(max_len)

    # for line in sheet:
    #     for i, cell in enumerate(line):
    #         line[i] = cell.ljust(max_len[i])
    return sheet

def load_line(folder: str, tasks: dict[str, Task], header: list[str], mode: str) -> list[str]:
    task_len = calc_task_len(mode)
    student = os.path.basename(folder)
    line: list[str] = ["" for _ in range(len(header))]
    for i, key in enumerate(header):
        if i == 0:
            line[i] = student
        else:
            if key in tasks:
                if mode == "count":
                    line[i] = tasks[key].str_count()
                elif mode == "full":
                    line[i] = tasks[key].str_full()
                else:
                    line[i] = tasks[key].str_mini()
            else:
                line[i] = "_" * task_len
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

    if args.csv:
        # map folder to dict[task_name, Task]
        # user_tasks_map: dict[str, dict[str, Task]] = load_history_and_yaml(folders)
        user_tasks_map: dict[str, dict[str, Task]] = {}
        for folder in folders:
            user_tasks_map[folder] = get_user_tasks(folder)

        header: list[str] = load_header(user_tasks_map, args.csv)
        header_notes = [x for x in header]
        header_count = [x for x in header]
        sheet_notes: list[list[str]] = [header_notes]
        sheet_count: list[list[str]] = [header_count]
        for folder in folders:
            tasks_map = user_tasks_map[folder]
            line_notes = load_line(folder, tasks_map, header, "notes")
            line_count = load_line(folder, tasks_map, header, "full")
            sheet_notes.append(line_notes)
            sheet_count.append(line_count)
        sheet_notes = format_sheet(sheet_notes)
        sheet_count = format_sheet(sheet_count)
        
        with open(args.csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet_notes)
        
        with open(args.csv.replace(".csv", "_count.csv"), "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet_count)

if __name__ == "__main__":
    main()
