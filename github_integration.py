# /home/sebastien/IA_AGENT/github_integration.py
import os
import base64
import logging
from github import Github
from config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME, BRANCH_NAME

class GitHubIntegration:
    def __init__(self):
        """ Initialisation de l'API GitHub """
        self.g = Github(GITHUB_TOKEN)
        self.repo = self.g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        logging.info(f"Connecté à {REPO_OWNER}/{REPO_NAME} sur GitHub.")

    def get_file_content(self, file_path):
        """ Récupérer le contenu d'un fichier depuis GitHub et le décoder correctement """
        try:
            logging.info(f"Récupération du fichier : {file_path}")
            file = self.repo.get_contents(file_path, ref=BRANCH_NAME)
            content = base64.b64decode(file.content).decode("utf-8")
            logging.info(f"Contenu récupéré : {content.strip()}")
            return content
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du fichier {file_path}: {e}")
            return None  # Éviter un crash si le fichier n'existe pas

    def update_file(self, file_path, content, message):
        """ Mettre à jour un fichier sur GitHub en encodant en UTF-8 """
        try:
            logging.info(f"Mise à jour du fichier : {file_path}")
            file = self.repo.get_contents(file_path, ref=BRANCH_NAME)
            self.repo.update_file(file.path, message, content.encode("utf-8"), file.sha, branch=BRANCH_NAME)
            logging.info(f"Fichier {file_path} mis à jour avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du fichier {file_path}: {e}")

    def list_files(self, directory):
        """ Liste récursive de tous les fichiers dans un répertoire en excluant 'node_modules' """
        file_list = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d != 'node_modules']  # Exclure node_modules
            for file in files:
                full_path = os.path.join(root, file)
                file_list.append(full_path)
        logging.info(f"Fichiers listés dans {directory}: {len(file_list)} trouvés.")
        return file_list

