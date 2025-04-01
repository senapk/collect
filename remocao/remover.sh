#!/bin/bash

ORG="qxcode-course"

# Lê os repositórios do arquivo, removendo espaços extras
REPOS=($(cat filtrado.txt))

for REPO in "${REPOS[@]}"; do
    echo "Excluindo repositório: $ORG/$REPO"
    gh repo delete "$ORG/$REPO" --yes
done
