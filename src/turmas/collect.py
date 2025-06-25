#!/usr/bin/env python3
import os
import argparse
import subprocess
import json

class JsonTask:
    def __init__(self):
        self.path = ""
        self.folder = ""
        self.rep = ""

    def __str__(self):
        return f"{self.folder} {self.rep}"

    def __repr__(self):
        return f"JsonTask({self.folder}, {self.rep})"
    
    def load_from_json(self, json_data: dict[str, str]):
        self.folder = json_data.get("folder", self.folder)
        self.rep = json_data.get("rep", self.rep)

class Target:
    def __init__(self, folder: str, rep: str):
        self.folder = folder
        self.rep = rep

    def __str__(self):
        return f"{self.folder} {self.rep}"

    def __repr__(self):
        return f"Target({self.folder}, {self.rep})"

def get_user_graph(target: Target) -> str:
    folder = target.folder
    rep = target.rep
    print(".." + folder)
    # folder_name = os.path.basename(folder)
    # basedir = os.path.dirname(folder)
    rep_folder = os.path.join(folder, rep)
    if not os.path.isdir(rep_folder):
        return ""
    result = subprocess.run(["tko", "rep", "graph", "--mono", "-f", rep_folder, "-W", "100", "-H", "15"], capture_output=True, text=True)
    output = result.stdout
    # with open(os.path.join(basedir, folder_name + "_graph.txt"), "w", encoding="utf-8") as graph_file:
    #     graph_file.write(output)
    return output

def get_user_resume(target: Target):
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

def load_folders_from_jsons(file: str) -> list[Target]:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        task: JsonTask = JsonTask()
        task.load_from_json(data)
        task.path = file
        class_folders: str = task.folder
        rep: str = task.rep
        student_list: list[str] = os.listdir(class_folders)
        student_target = [Target(os.path.join(class_folders, student), rep) for student in student_list]
        return student_target
        
 
def process_task_jsons(args: argparse.Namespace):
    jsons: list[str] = args.jsons
    
    for json_file in jsons:
        repo_list: list[Target] = load_folders_from_jsons(json_file)

        if args.graph:
            output_file = os.path.splitext(json_file)[0] + "_graph.txt"
            with open(output_file, "w", encoding="utf-8") as graph_file:
                for repo in repo_list:
                    graph_file.write("-" * 120 + "\n")
                    graph_file.write(repo.folder + "\n")
                    graph = get_user_graph(repo)
                    graph_file.write(graph + "\n")


        if args.info:
            for repo in repo_list:
                get_user_resume(repo)

def process_task_folders(args: argparse.Namespace):
    repo_list: list[Target] = []
    for folder in args.folders:
        if not os.path.isdir(folder):
            print(f"Folder {folder} does not exist.")
            continue
        repo_list.append(Target(folder, args.rep))

    repo_list = sorted(repo_list, key=lambda x: x.folder)
    if args.graph:
        for repo in repo_list:
            get_user_graph(repo)

    if args.info:
        for repo in repo_list:
            get_user_resume(repo)


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
    
    if args.jsons:
        process_task_jsons(args)

    if args.folders:
        process_task_folders(args)




if __name__ == "__main__":
    main()
