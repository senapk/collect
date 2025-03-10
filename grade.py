#!/usr/bin/env python3
import csv
import os
import yaml # type: ignore
import json
import argparse
import datetime
import subprocess

from util import load_csv, save_csv, Entry, load_entries, load_header

def get_self_grade_value(choice: str) -> int:
    dict_values = { "a": 5, "b": 4, "c": 3, "d": 2, "e": 1, "x": 0, }
    return dict_values.get(choice.lower(), 0)

def get_user_task_grade(grade: str) -> float:
    grade = grade.strip()
    if not grade[0].isdigit():
        return 0
    progress = grade[0:3] #numbers
    progress_value = int(progress) / 2 # 100 // 2 -> 50
    skill = get_self_grade_value(grade[3]) * 6 # 0 a 30
    autonomy = get_self_grade_value(grade[4]) * 5 # 0 a 25
    total = (progress_value + skill + autonomy) / 10
    return total

def calc_grade(entry_list: list[Entry], notes: list[str], categories: dict[str, int]) -> float:
    received_dict: dict[str, float] = {} # total received for each category
    expected_dict: dict[str, float] = {} # total expected for each category
    
    for cat in categories:
        received_dict[cat] = 0
        expected_dict[cat] = 0

    for note, entry in zip(notes, entry_list):
        weight: float = float(entry.weight)
        extra = entry.optional
        if weight == 0:
            continue
        received_dict[entry.category] += get_user_task_grade(note) * weight
        if not extra:
            expected_dict[entry.category] += weight

    total_grade = 0.0
    for cat in categories:
        if expected_dict[cat] == 0:
            continue
        total_grade += (received_dict[cat] / expected_dict[cat]) * categories[cat]
    return total_grade / sum(categories.values())


def decode_categories(categories: str) -> dict[str, int]:
    cat_map = {}
    for c in categories.split("_"):
        cat_map[c[0]] = int(c[1:])
    return cat_map

def update_grades(sheet: list[list[str]]) -> list[list[str]]:
    header = sheet[0]
    nl = len(sheet)
    entry_list = load_entries(sheet)
    categories = decode_categories(sheet[0][0])
    for l in range(2, nl):
        notes = sheet[l][2:]
        grade = calc_grade(entry_list, notes, categories)
        sheet[l][1] = "{:.1f}".format(grade).rjust(5)
    return sheet

parser = argparse.ArgumentParser(description="Calcula a nota do aluno")
parser.add_argument("csv", help="Arquivo CSV com as notas")
args = parser.parse_args()

sheet = load_csv(args.csv)
sheet = update_grades(sheet)
save_csv(args.csv, sheet)
