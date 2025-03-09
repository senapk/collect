#!/usr/bin/env python3
import csv

class Entry:
    def __init__(self):
        self.category = ""
        self.label = ""
        self.weight = 0
        self.optional = False

    def __str__(self):
        return f"{self.category}:{self.weight}:{self.label}:{"+" if self.optional else "!"}"

def load_csv(arquivo_csv) -> list[list[str]]:
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

# load the first 2 lines of the CSV file
# A8B2               ,grade ,A1     ,A1     ,A1    ,A1          ,A1     ,A1    ,A2      ,A2     ,A3       ,A3      ,A3     ,A3        ,A+2       ,A+2       ,A3     ,A3       ,A3        ,A+2     ,A2      ,A3     ,A2     ,B2    ,B2    ,B+2   ,B+2
# username           ,grade ,toalha ,animal ,carro ,calculadora ,camisa ,roupa ,relogio ,motoca ,motouber ,charger ,budega ,lapiseira ,tabuleiro ,pula-pula ,cinema ,junkfood ,porquinho ,tarifas ,contato ,agenda ,agiota, shapes, estacionamento, cofre, cadastro
def load_header(sheet: list[list[str]]) -> list[list[str]]:
    header: list[list[str]] = []
    header = [[x.strip() for x in sheet[0]], [x.strip() for x in sheet[1]]]
    return header

def load_entries(sheet: list[list[str]]) -> list[Entry]:
    entry_list: list[Entry] = []
    if not (sheet[0][1].strip() == "grade" and sheet[1][1].strip() == "grade"):
        print("O item 2 da primeira linha e segunda linha do arquivo CSV deve ser 'grade'.")
        exit(1)
    for i in range(2, len(sheet[0])):
        weight = sheet[0][i].strip()
        label = sheet[1][i].strip()
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
