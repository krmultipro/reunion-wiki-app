# Image Python légère basée sur Debian slim
FROM python:3.10-slim

# Empêche Python de générer des fichiers .pyc
# Force l'affichage immédiat des logs (important en Docker)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie seulement requirements.txt pour optimiser le cache Docker
COPY requirements.txt ./

# Installation des dépendances sans conserver le cache pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du projet dans /app
COPY . .

# Expose le port interne de l’application
EXPOSE 8000

#Utilise un user non-root (meilleure sécurité)
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser 

# Lance Gunicorn avec 1 worker en production
CMD sh -c "python migrate.py && gunicorn -w 1 -b 0.0.0.0:8000 app:app"

