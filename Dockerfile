# Utilisation d'une image Python
FROM python:3.9

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers
COPY requirements.txt requirements.txt
COPY . .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["python", "app.py"]
