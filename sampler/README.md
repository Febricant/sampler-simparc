# LTE-Sampler-Residential
Sampler for residential


## Installation on a corporate workstation
setting (to allow installing packages):

    "http.proxy": "http://bpbqvsg600.ireq.ca:8080"

Make sure you are connected to Artifactory.

Create a `task.json` file in a `.vscode` directory containing the following (adjust the paths as needed):

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
                    "command": "(if not exist C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv python -m venv C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv) && C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv\\Scripts\\activate.bat && python -m pip install --upgrade pip && python -m pip install -r requirements.txt && C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv\\Scripts\\deactivate.bat C:\\Brice\\Environnement_python\\LTE-Sampler-Residential\\py311\\.venv"
                },
                "problemMatcher": [],
            }
            
        ]
    }

Run the task:

    Terminal menu → Run Task → select the task

## Launch the dashboard
    1 - activate the environment (e.g., cmd inside VS Code)

    2 - run the script:
        without D-Tale links (remove them in the .py): python -m streamlit run "./ui/Dashboard.py"
        with D-Tale links: dtale-streamlit run "ui/Dashboard.py"

## Update the required packages list (env located outside the project directory)
setting (to allow connecting to PyPI):

    "http.proxy": "http://bpbqvsg600.ireq.ca:8080"

Commands to run from the environment while in the project directory:

    activate the environment pathtoEnv/activate.bat
    python -m uv add openpyxl --active

Update the `requirements.txt` file while in the project directory:

    activate the environment pathtoEnv/activate.bat

    python -m uv export --no-hashes --format requirements-txt -o "N:\Mes Documents\Projets LTE\Projet archQc\code\GITHUB_Repo\LTE-Sampler-Residential\requirements.txt"

## Generate HTML documentation
    HTML with pdoc3:
        python -m pdoc --html --output-dir "N:\Mes Documents\Projets LTE\Projet archQc\code\GITHUB_Repo\LTE-Sampler-Residential\documentation\html" "N:\Mes Documents\Projets LTE\Projet archQc\code\GITHUB_Repo\LTE-Sampler-Residential"
    Markdown with pdoc3:
        python -m pdoc --output-dir "N:\Mes Documents\Projets LTE\Projet archQc\code\GITHUB_Repo\LTE-Sampler-Residential\documentation\markdown" "N:\Mes Documents\Projets LTE\Projet archQc\code\GITHUB_Repo\LTE-Sampler-Residential"
