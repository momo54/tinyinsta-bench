# Utiliser une image de base Debian ou Ubuntu qui inclut Python
FROM python:3.9-slim


# Mettre à jour et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    postgresql-client-17 \
    postgresql-contrib-17 \
    && rm -rf /var/lib/apt/lists/*


# Installer pandas et matplotlib en utilisant pip
RUN pip install pandas matplotlib


WORKDIR /work
