# Dockerfile

FROM python:3.11.8-bullseye

# Copie de votre code source dans le conteneur
COPY . /app
WORKDIR /app

# Get Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

# Installation des dépendances nécessaires
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exécution du script env.sh lors de la construction de l'image
RUN chmod +x /app/env.sh && /app/env.sh
