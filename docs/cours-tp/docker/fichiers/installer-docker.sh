#!/bin/bash
# Installe Docker Engine sur Debian 13 (ou 12) en suivant la documentation officielle :
# https://docs.docker.com/engine/install/debian/
# Script interactif de l'association TutoTech (Nicolas BODAINE), licence CC BY 4.0.
# À lancer en root, ou avec sudo depuis un compte administrateur.

# Couleurs des messages
INFO="\033[1;34m[INFO]\033[0m"
SUCCESS="\033[1;32m[SUCCÈS]\033[0m"
WARNING="\033[1;33m[ATTENTION]\033[0m"
ERROR="\033[1;31m[ERREUR]\033[0m"

# En root, pas besoin de sudo (Debian n'installe pas sudo si un mot de passe root a été défini)
if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
elif command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  echo -e "$ERROR Lance ce script en root (su -) ou installe sudo."
  exit 1
fi

# Pose une question et renvoie 0 si la réponse est « oui »
demander_confirmation() {
  echo -e "$1 (oui/non)"
  read -r reponse
  [[ "$reponse" == "oui" ]]
}

# Étape 1 : suppression des paquets non officiels qui entrent en conflit avec Docker
if demander_confirmation "$INFO Voulez-vous supprimer les anciennes versions de Docker ?"; then
  for pkg in docker.io docker-compose docker-doc podman-docker containerd runc; do
    $SUDO apt-get remove -y "$pkg" 2>/dev/null
  done
  echo -e "$SUCCESS Anciennes versions de Docker supprimées."
else
  echo -e "$WARNING Passage à l'étape suivante sans supprimer les anciennes versions."
fi

# Étape 2 : installation de Docker depuis le dépôt officiel
if demander_confirmation "$INFO Voulez-vous installer Docker (installation basée sur la documentation officielle) ?"; then
  $SUDO apt-get update
  $SUDO apt-get install -y ca-certificates curl
  # Clé qui permet à apt de vérifier la signature des paquets Docker
  $SUDO install -m 0755 -d /etc/apt/keyrings
  $SUDO curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  $SUDO chmod a+r /etc/apt/keyrings/docker.asc
  # Déclaration du dépôt Docker (format .sources)
  $SUDO tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
  $SUDO apt-get update
  if ! $SUDO apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; then
    echo -e "$ERROR L'installation des paquets Docker a échoué : lis les messages ci-dessus."
    exit 1
  fi
  # Démarrage du service maintenant et à chaque démarrage de la machine
  $SUDO systemctl enable --now docker
  # Vérification
  $SUDO docker run --rm hello-world && echo -e "$SUCCESS Docker installé avec succès."
else
  echo -e "$WARNING Docker n'a pas été installé."
fi

# Étape 3 : ajout d'un utilisateur au groupe docker
if demander_confirmation "$INFO Voulez-vous ajouter un utilisateur au groupe docker ?"; then
  echo "Veuillez entrer le nom de l'utilisateur :"
  read -r utilisateur
  if ! id "$utilisateur" &>/dev/null; then
    echo -e "$ERROR L'utilisateur $utilisateur n'existe pas. Veuillez vérifier son nom."
  elif $SUDO usermod -aG docker "$utilisateur"; then
    echo -e "$SUCCESS L'utilisateur $utilisateur a été ajouté au groupe docker. Il doit se déconnecter et se reconnecter pour que ce soit pris en compte."
  else
    echo -e "$ERROR Impossible d'ajouter $utilisateur au groupe docker (Docker est-il installé ?)."
  fi
else
  echo -e "$WARNING Aucun utilisateur n'a été ajouté au groupe docker."
fi

echo -e "$SUCCESS Script terminé. Merci d'avoir utilisé cet installateur Docker élaboré par Nicolas BODAINE de l'association TutoTech !"
