# LTE-Sampler-Residential
Sampler for residential


## Installation dans un ordinateur bur
setting (pour permettre l'installation de package): 

    "http.proxy": "http://bpbqvsg600.ireq.ca:8080"

s'assurer d'être connecté à artifactory

créer un fichier task.json dans un répertoire .vscode, contenant (adapter les chemins d'accès) :

    {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Create Python Environment with pip",
                "type": "shell",
                "group": {
                    "kind": "build",
                    "isDefault": true
                },
                "windows": {
                    "options":{
                        "shell": {
                            "executable": "c:\\Windows\\system32\\cmd.exe",//"C:\\Brice\\Python 3.11\\Winpython64-3.11.4.0\\WPy64-31140\\WinPython Command Prompt.exe",
                            "args": ["/d", "/c"]
                        },
                        "cwd": "${workspaceFolder}"
                    },
                    "command": "(if not exist C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv python -m venv C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv) && C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv\\Scripts\\activate.bat && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv\\Scripts\\deactivate C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv"
                },
                "problemMatcher": [],
            }
            
        ]
    }

Lancer la tache :

    Menu Terminal - Run Task - choisir la tâche 

## Lancer le tableau de bord
    python -m streamlit run "./ui/Dashboard.py"

## Mise à jour de la listes des packages requise dans un env situé dans un autre répertoire que le projet :
setting (pour permettre la connection à pypi): 

    "http.proxy": "http://bpbqvsg600.ireq.ca:8080"

Commandes à exécuter à partir de l'env, en se plaçant dans le répertoire du projet :

    activer l'environnement pathtoEnv/activate.bat
    python -m uv add openpyxl --active

Mettre à jour le fichier requirments.txt, en se plaçant dans le répertoire du projet :

    activer l'environnement pathtoEnv/activate.bat

    python -m uv export --no-hashes --format requirements-txt -o "N:\Mes Documents\Projets LTE\Projet archQc\code\GITHUB_Repo\LTE-Sampler-Residential\requirements.txt"
