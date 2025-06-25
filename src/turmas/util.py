#!/usr/bin/env python3
import csv
import argparse

class Entry:
    def __init__(self):
        self.category = ""
        self.label = ""
        self.weight = 0
        self.optional = False

    def __str__(self):
        return f"{self.category}:{self.weight}:{self.label}:{"+" if self.optional else "!"}"

def load_csv(arquivo_csv: str) -> list[list[str]]:
    try:
        with open(arquivo_csv, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            sheet = list(reader)
            return sheet
    except FileNotFoundError:
        exit(f"Arquivo '{arquivo_csv}' não encontrado.")

def save_csv(arquivo_csv: str, sheet: list[list[str]]):
    try:
        with open(arquivo_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sheet)
    except FileNotFoundError:
        exit(f"Arquivo '{arquivo_csv}' não encontrado.")

def load_opening_cols(sheet: list[list[str]]) -> list[list[str]]:
    header: list[list[str]] = [["XX", "label"], ["grade", "grade"]]
    for i in range(2, len(sheet)):
        header.append([sheet[i][0].strip(), sheet[i][1].strip()])
    return header

def load_entries(sheet: list[list[str]]) -> list[Entry]:
    entry_list: list[Entry] = []
    if not (sheet[1][0].strip() == "grade" and sheet[1][1].strip() == "grade"):
        print("Os dois primeiros elementos da segunda linha devem ser 'grade'.")
        exit(1)
    for i in range(2, len(sheet)):
        weight = sheet[i][0].strip()
        label = sheet[i][1].strip()
        entry = Entry()
        entry.category = weight[0]
        entry.label = label
        entry.weight = int(weight[1:])
        entry.optional = weight[1] == "+"
        entry_list.append(entry)
    return entry_list

    # else:
    #     tasks_key_set: set[str] = set()
    #     for folder in user_tasks_map:
    #         tasks_key_set.update(user_tasks_map[folder].keys())
    #     header = ["user"] + list(tasks_key_set)
    # return header

def transpose_sheet(csv_file: str) -> None:
    sheet = load_csv(csv_file)
    transposed_sheet: list[list[str]] = []
    for i in range(len(sheet[0])):
        transposed_row = [sheet[j][i] for j in range(len(sheet))]
        transposed_sheet.append(transposed_row)
    save_csv(csv_file, transposed_sheet)

def main():
    parser = argparse.ArgumentParser(description="Transpor arquivo CSV.")
    parser.add_argument("csv_file", help="Caminho do arquivo CSV.")
    args = parser.parse_args()
    transpose_sheet(args.csv_file)

if __name__ == "__main__":
    main()
