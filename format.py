#!/usr/bin/env python3
import argparse

from util import load_csv, save_csv

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
    return sheet

parser = argparse.ArgumentParser(description='format all csv files')
parser.add_argument('lista_arquivos_csv', type=str, nargs='+', help='Lista de arquivos csv para formatar')
args = parser.parse_args()

for arquivo_csv in args.lista_arquivos_csv:
    sheet = load_csv(arquivo_csv)
    sheet = format_sheet(sheet)
    save_csv(arquivo_csv, sheet)
