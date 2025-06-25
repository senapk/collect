#!/usr/bin/env python3
import os
import argparse
import subprocess
import json

class Target:
    def __init__(self, folder: str, rep: str):
        self.folder = folder
        self.rep = rep

    def __str__(self):
        return f"{self.folder} {self.rep}"

    def __repr__(self):
        return f"Target({self.folder}, {self.rep})"

def get_user_graph(target: Target):
    folder = target.folder
    rep = target.rep
    print(".." + folder)
    folder_name = os.path.basename(folder)
    basedir = os.path.dirname(folder)
    rep_folder = os.path.join(folder, rep)
    if not os.path.isdir(rep_folder):
        return
    result = subprocess.run(["tko", "rep", "graph", "-f", rep_folder, "-W", "100", "-H", "15"], capture_output=True, text=True)
    output = result.stdout
    with open(os.path.join(basedir, folder_name + "_graph.txt"), "w", encoding="utf-8") as graph_file:
        graph_file.write(output)

def get_user_tasks(target: Target):
    folder = target.folder
    rep_name = target.rep
    print(".." + folder + ".." + rep_name)
    folder = os.path.abspath(folder)
    basedir = os.path.dirname(folder)
    folder_name = os.path.basename(folder)
    rep_folder = os.path.join(folder, rep_name)
    if not os.path.isdir(rep_folder):
        return
    result = subprocess.run(["tko", "rep", "resume", "-f", rep_folder], capture_output=True, text=True)
    output = result.stdout
    with open(os.path.join(basedir, folder_name + "_tasks.yaml"), "w", encoding="utf-8") as tasks_file:
        tasks_file.write(output)

def load_folders_from_jsons(jsons: list[str]) -> list[Target]:
    folders: list[Target] = []
    for file in jsons:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            class_folders: str = data["folder"]
            rep: str = data["rep"]
            if "folder" in data:
                student_list: list[str] = os.listdir(class_folders)
                student_target = [Target(os.path.join(class_folders, student), rep) for student in student_list]
                folders.extend(student_target)
    return folders

def main():
    # Caminho do arquivo CSV
    parser = argparse.ArgumentParser(description="Coleta de dados de atividades de programação.")
    parser.add_argument("jsons", nargs="*", type=str, help="Json files")
    parser.add_argument("-f", "--folders", nargs="*", type=str, help="Pastas dos projetos.")
    parser.add_argument("-r", "--rep", type=str, help="Nome do repositório.")
    parser.add_argument("-g", "--graph", action="store_true")
    parser.add_argument("-i", "--info", action="store_true")
    args = parser.parse_args()

    if args.folders and not args.rep:
        print("É necessário informar o nome do repositório com --rep [fup|ed|poo].")
        exit(1)
        return
    
    if not args.info and not args.graph:
        print("É necessário informar --graph ou --info.")
        exit(1)
        return
    
    targets: list[Target] = []
    if args.jsons:
        targets.extend(load_folders_from_jsons(args.jsons))

    if args.folders:
        for folder in args.folders:
            if not os.path.isdir(folder):
                print(f"Folder {folder} does not exist.")
                continue
            targets.append(Target(folder, args.rep))

    targets = sorted(targets, key=lambda x: x.folder)

    if args.graph:
        for target in targets:
            get_user_graph(target)

    if args.info:
        for target in targets:
            get_user_tasks(target)

if __name__ == "__main__":
    main()
