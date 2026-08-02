English is following.  

# Avertissement  
## Statut du projet et limitation de responsabilité  
Ce dépôt contient du code, des données et de la documentation qui sont toujours en cours de développement. Le contenu est fourni "tel quel", sans aucune garantie d’aucune sorte, expresse ou implicite, y compris, sans s’y limiter, les garanties de qualité marchande, d’adéquation à un usage particulier ou d’absence d’erreurs.
Les auteurs et contributeurs de ce dépôt ne garantissent pas l’exactitude, l’exhaustivité, la fiabilité ou la pertinence du contenu pour un quelconque usage.
Toute utilisation du contenu de ce dépôt se fait aux seuls risques et périls de l’utilisateur.
En aucun cas, les auteurs, contributeurs ou organisations associées à ce dépôt ne pourront être tenus responsables de dommages directs ou indirects, pertes de données, pertes financières ou de toute autre conséquence résultant de l’utilisation, de la modification ou de la redistribution du contenu par des tiers.
  
# Simulateur de parc de bâtiments   
Ce dépôt contient le code nécessaire pour simuler en parallèle (en utilisant Dask) les bâtiments listés et caractérisés dans un fichier csv (par exemple,building-test-from-sampler.csv) en utilisant le processus développé par le NREL (OpenStudio-HPXML). Cet outil de simulation se lance à partir du fichier "main.py". Ce fichier fait appel à divers scripts et fonctions définis dans les fichiers suivants:  
- Le fichier "config.py": ce script permet de configurer la simulation.   
- Le fichier "hpxml_input_schema.py": ce script permet d'extraire les requis du schéma de données HPXML qui sera utilisé lors du prétraitement.   
- Le fichier "preprocessing.py": ce script formalise le prétraitement des données contenues dans le fichier csv utilisé en entrée, notamment pour s'assurer que les contraintes du schéma de données HPXML est respecté.  
- Le fichier "upgrading.py": ce script permet de créer des scénarios de mesures à appliquer aux bâtiments listés dans le fichier csv.  
- Le fichier "parallelization.py": ce script définit la fonction utilisée pour paralléliser les simulations de chacun des bâtiments.  
- Le fichier "building.py": ce script définit la classe "Building" qui est principalement dédiée à générer pour chaque bâtiment simulé le fichier OSW (OpenStudio Workflow), soit la "recette" à appliquer pour simuler chaque bâtiment.   
- Le fichier "postprocessing.py": ce script traite les données simulées de tous les bâtiments listés dans le fichier csv.  

## Étape 1 - Installation  
Afin de pouvoir rouler le simulateur, 2 possibilités d'installation sont suggérées.  
  
### Méthode 1: en utilisant Docker et Visual Studio Code avec l'extension Dev Containers de Microsoft  
Cette méthode consiste à faire rouler le code à l'intérieur d'un container docker de développement. L'installation et la mise en route de cette méthode est entièrement documentée [ici](https://code.visualstudio.com/docs/devcontainers/containers). Cette procédure implique notamment d'installer Docker, Visual Studio Code et une de ses extensions appelée "Dev Containers" (développée par Microsoft).  

Une fois l'installation complétée, il suffit de cloner le dépôt présent et d'utiliser l'extension "Dev Containers" pour construire et ouvrir le container de développement prêt à l'emploi. La construction de ce container se base sur les fichiers inclus dans le répertoire ".devcontainer". Il est à noter que le container inclut une installation du SDK d'OpenStudio (version 3.9).   

### Méthode 2: en utilisant le gestionnaire de paquet UV et le SDK d'OpenStudio (version 3.9)  
Cette deuxìème méthode consiste à installer un environnement virtuel Python en utilisant UV et à utiliser le SDK d'OpenStudio (version 3.9) pour les simulations des bâtiments. Cette méthode nécessite donc d'installer UV selon la procédure documentée [ici](https://docs.astral.sh/uv/getting-started/installation/) et le SDK d'OpenStudio se trouvant [ici](https://github.com/NREL/OpenStudio/releases/tag/v3.9.0).  

Une fois l'installation de ces 2 outils complétée, il suffit de cloner le dépôt GitHub présent. En utilisant UV (et plus spécialement la commande uv sync) dans le répertoire du dépôt, UV créera l'environnement virtuel nécessaire pour rouler le code du simulateur.      

Dans cette configuration, il faudra également modifier le fichier "parallelization.py" à la ligne 57 et ajuster le chemin d'accès au SDK dans le fichier "config.py" à la ligne 19.  
  
## Étape 2 - Génération du fichier csv listant les bâtiments à simuler  
Une application avec interface graphique a été développée afin de créer des fichiers csv contenant une liste de bâtiments représentatifs du Québec contenant les attributs nécessaires à leurs simulations. Cette application est contenue dans un container Docker disponible [ici](https://hub.docker.com/r/bdelcroix/lte-sampler-residential). L'installation de Docker est donc un pré-requis à son utilisation.    

## Étape 3 - Lancer sa première simulation  
Une fois les étapes 1 et 2 complétées, il est maintenant possible d'effectuer une simulation de parc de bâtiments en lançant le fichier main.py. À noter qu'il faudra, préalablement, spécifier le bon chemin vers le fichier csv décrivant la liste des bâtiments à simuler (fichier csv généré lors de l'étape 2).    

----------------------------------------------------------------------------  
# Disclaimer  
## Project Status and Limitation of Liability  
This repository contains code, data, and documentation that is under active development. The content is provided "as is", without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or absence of defects.
The authors and contributors of this repository make no guarantees regarding the accuracy, completeness, reliability, or suitability of the content for any specific use.
Any use of the content is made entirely at the user’s own risk.
Under no circumstances shall the authors, contributors, or any affiliated organizations be held liable for any direct or indirect damages, data loss, financial loss, or any other consequences arising from the use, modification, or redistribution of the content by third parties.
  
# Building Stock Simulator  
This repository contains the code needed to simulate in parallel (using Dask) the buildings that are listed and described in a CSV file (e.g., building-test-from-sampler.csv) using the process developed by NREL (OpenStudio-HPXML). This simulation tool is launched from the file "main.py". This file calls various scripts and functions defined in the following files:  
- The file "config.py": this script configures the simulation.  
- The file "hpxml_input_schema.py": this script extracts the requirements from the HPXML data schema that will be used during preprocessing.  
- The file "preprocessing.py": this script formalizes the preprocessing of data contained in the input CSV file, notably to ensure the HPXML data schema constraints are respected.  
- The file "upgrading.py": this script enables the creation of upgrade scenarios to be applied to the buildings listed in the CSV file.  
- The file "parallelization.py": this script defines the function used to parallelize the simulation of each building.  
- The file "building.py": this script defines the "Building" class, which is mainly responsible for generating the OSW (OpenStudio Workflow) file for each simulated building—the "recipe" for simulating each building.  
- The file "postprocessing.py": this script processes the simulation data for all buildings listed in the CSV file.
  
## Step 1 - Installation  
To run the simulator, two installation options are suggested.  
  
### Method 1: Using Docker and Visual Studio Code with Microsoft’s Dev Containers Extension
This method consists of running the code inside a development Docker container. The installation and setup for this method are fully documented [here](https://code.visualstudio.com/docs/devcontainers/containers). This procedure involves installing Docker, Visual Studio Code, and one of its extensions called “Dev Containers” (developed by Microsoft).

Once installation is completed, simply clone this repository and use the "Dev Containers" extension to build and open the ready-to-use development container. The container setup is based on the files included in the ".devcontainer" directory. Note that the container includes an installation of the OpenStudio SDK (version 3.9).

### Method 2: Using the UV Package Manager and the OpenStudio SDK (Version 3.9)
This second method involves installing a virtual Python environment using UV and using the OpenStudio SDK (version 3.9) for building simulations. You need to install UV as documented [here](https://docs.astral.sh/uv/getting-started/installation/) and the OpenStudio SDK found [here](https://github.com/NREL/OpenStudio/releases/tag/v3.9.0).

Once these two tools are installed, simply clone this GitHub repository. Using UV (specifically the "uv sync" command) in the repository directory, UV will create the virtual environment needed to run the simulator’s code.

With this setup, you will also need to modify the "parallelization.py" file at line 57 and adjust the path to the SDK in the "config.py" file at line 19.

## Step 2 - Generate the CSV File Listing Buildings to Simulate
A graphical user interface (GUI) application has been developed to create CSV files containing a list of representative buildings in Quebec with the necessary attributes for their simulation. This application is contained in a Docker container available [here](https://hub.docker.com/r/bdelcroix/lte-sampler-residential). Therefore, Docker installation is a prerequisite for its use.

## Step 3 - Launch Your First Simulation
Once steps 1 and 2 are completed, you can now perform a building stock simulation by running the main.py file. Note that you must first specify the correct path to the CSV file describing the list of buildings to simulate (CSV file generated during step 2).
  

## Running without a dev container

`config.OPENSTUDIO_RUNNER` decides how OpenStudio is invoked, so VS Code and the
Dev Containers extension are no longer required:

| setting | what it does |
| --- | --- |
| `"auto"` (default) | uses an installed binary if there is one, else Docker. Inside the dev container `openstudio` is on `PATH` and `docker` is not, so it picks native there and Docker on a bare host — no configuration either way. |
| `"docker"` | always shells out to `config.DOCKER_IMAGE`, which already carries OpenStudio 3.9.0. Runs from an ordinary Windows/macOS/Linux shell with only Docker installed. |
| `"native"` | always calls an installed binary — `config.OPENSTUDIO_EXE` if it points at one, otherwise `openstudio` on `PATH`. |

`main.py` prints which runner it resolved, and how, before starting.

Under the docker runner the project is bind-mounted at `config.CONTAINER_WORKSPACE`
and every path written into an `in.osw` is translated to it, so the OSW files
contain `/workspace/...` rather than host paths. See `osrunner.py`. The old manual
edit to `parallelization.py` described under Method 2 is no longer needed.

```powershell
python main.py buildings.csv
```

## Checking a sample before simulating it

`main.py` refuses to start when the CSV carries something OpenStudio will reject —
an invalid choice, a required blank, or a combination that is legal field by field
but fails inside `BuildResidentialHPXML` (an apartment unit on a conditioned
basement). It exits non-zero and names the buildings, rather than failing part-way
through a batch.

```powershell
python main.py buildings.csv --repair    # correct the findings and continue
python validate_sampler_csv.py buildings.csv -o fixed.csv   # or do it separately
```

## Testing

```powershell
python main.py buildings.csv --dry-run   # write every in.osw, run nothing (~seconds)
python -m pytest                         # ~30 tests, no Docker, no dask (~2 s)
python -m pytest -m slow                 # one building end to end through Docker
```

`--dry-run` produces exactly the inputs OpenStudio would be given without running
it, which is how the test suite asserts on them. Other useful flags: `--limit N`
to process only the first N buildings, and `--serial` to run without dask.
