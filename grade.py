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

def save_csv(arquivo_csv: str, sheet: list[list[str]]) -> None:
    with open(arquivo_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sheet)


def get_task_value(label: str) -> tuple[int, bool]:
    pieces = label.split(":")  # budega:5
    if len(pieces) == 1:
        return 0, False
    task_weight = int(pieces[1])
    extra = pieces[1].startswith("+")
    return task_weight, extra

def get_self_grade_value(choice: str) -> int:
    dict_values = { "a": 5, "b": 4, "c": 3, "d": 2, "e": 1, "x": 0, }
    return dict_values.get(choice.lower(), 0)

def get_user_task_grade(grade: str) -> float:
    if not grade[0].isdigit():
        return 0
    progress = grade[0:3] #numbers
    progress_value = int(progress) / 2 # 100 // 2 -> 50
    skill = get_self_grade_value(grade[3]) * 6 # 0 a 30
    autonomy = get_self_grade_value(grade[4]) * 6 # 0 a 30
    total = (progress_value + skill + autonomy) / 10
    return total

def update_grades(sheet: list[list[str]]) -> list[list[str]]:
    header = sheet[0]
    nc = len(header)
    nl = len(sheet)
    for l in range(1, nl):
        grade: float = 0
        total_task_value = 0
        for c in range(2, nc):
            weight, extra = get_task_value(header[c].strip())
            if weight == 0:
                continue
            grade += get_user_task_grade(sheet[l][c].strip()) * weight
            if not extra:
                total_task_value += weight
        sheet[l][1] = "{:.1f}".format(grade / total_task_value).rjust(5)
    return sheet

parser = argparse.ArgumentParser(description="Calcula a nota do aluno")
parser.add_argument("csv", help="Arquivo CSV com as notas")
args = parser.parse_args()

sheet = load_csv(args.csv)
sheet = update_grades(sheet)
save_csv(args.csv, sheet)
