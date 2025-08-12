# Utilise une image officielle Python compatible avec pyagrum et streamlit
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier tout le projet dans le conteneur
COPY . /app

# Installer les dépendances système nécessaires à pyagrum et matplotlib
RUN apt-get update && \
    apt-get install -y build-essential graphviz libgraphviz-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port utilisé par Streamlit
EXPOSE 8501

# Commande pour lancer l’application Streamlit
CMD ["streamlit", "run", "ui/Dashboard.py"]