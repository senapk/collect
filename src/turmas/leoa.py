#!/usr/bin/env python3
from __future__ import annotations
import os
import argparse
import re
import json
from typing import Any
from turmas.paths import Paths
from turmas.student_repo import StudentRepo
from turmas.collected_data import CollectedData
from turmas.class_task import ClassTask
from turmas.collect import Collect
from turmas.pull import pull_class_task

def clear_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    ansi_escape = re.compile(r'\x1B\[[0-?9;]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


                
def join_student_daily_graph(user_info_map: dict[str, CollectedData]) -> str:
    lines: list[str] = []
    for folder, info in user_info_map.items():
        lines.append("─" * 120)
        lines.append(folder)
        lines.append(info.graph)
        lines.append("\n")
    return "\n".join(lines)



def decode_student_info_file(file: str) -> dict[str, CollectedData]:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        user_info_map: dict[str, CollectedData] = {}
        for folder, text in data.items():
            collected_data = CollectedData().load_from_dict(json.loads(text))
            user_info_map[folder] = collected_data
    return user_info_map

class Join:
    @staticmethod
    def main(args: argparse.Namespace) -> None:
        class_task = ClassTask().load_from_file(args.target)
        collected_path = Paths.get_default_collected(class_task)
        if not os.path.isfile(collected_path):
            print(f"Collected data file not found: {collected_path}")
            return
        user_info_map = decode_student_info_file(collected_path)
        class_graph = join_student_daily_graph(user_info_map)
        graph_color, graph_mono = Paths.get_default_graph_joined(class_task)
        with open(graph_color, "w", encoding="utf-8") as f:
            f.write(class_graph)
        with open(graph_mono, "w", encoding="utf-8") as f:
            f.write(clear_ansi_codes(class_graph))

def pull(args: argparse.Namespace) -> None:
    pull_class_task(args.target, args.threads)

def main():
    # Caminho do arquivo CSV
    parser = argparse.ArgumentParser(description="Ferramenta para lidar com tarefas do classroom usando o tko.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    pull_cmd = subcommands.add_parser("pull", help="Pull data from the specified target.")
    pull_cmd.add_argument("target", type=str, help="Json class task file")
    pull_cmd.add_argument("-t", "--threads", type=int, default=5, help="Number of threads to use for pulling data.")
    pull_cmd.set_defaults(func=pull)

    collect_cmd = subcommands.add_parser("collect", help="Collect data from the specified target.")
    collect_cmd.add_argument("target", type=str, help="Json class task file")
    collect_cmd.set_defaults(func=Collect.main)

    join_cmd = subcommands.add_parser("join", help="Join collected data from the specified target.")
    join_cmd.add_argument("target", type=str, help="Json class task file")
    join_cmd.set_defaults(func=Join.main)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
