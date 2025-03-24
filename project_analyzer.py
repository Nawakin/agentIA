# /home/sebastien/IA_AGENT/project_analyzer.py

import os
import re
from collections import defaultdict

class ProjectAnalyzer:
    def __init__(self, github_integration):
        self.github = github_integration
        self.project_structure = defaultdict(list)  # Clé : fichier, valeur : classes et fonctions
        self.imports = defaultdict(list)  # Clé : fichier, valeur : imports

    def analyze_project(self):
        """ Analyse le projet pour extraire les classes, fonctions et imports """
        files = self.github.list_files("/")
        for file_path in files:
            if file_path.endswith((".js", ".ts", ".tsx")):  # On s'intéresse aux fichiers de code
                content = self.github.get_file_content(file_path)
                classes, functions = self.extract_classes_and_functions(content)
                imports = self.extract_imports(content)
                
                self.project_structure[file_path] = {"classes": classes, "functions": functions}
                self.imports[file_path] = imports

    def extract_classes_and_functions(self, content):
        """ Extrait les classes et fonctions d'un fichier """
        classes = re.findall(r'class (\w+)', content)
        functions = re.findall(r'function (\w+)', content)
        return classes, functions

    def extract_imports(self, content):
        """ Extrait les imports d'un fichier """
        imports = re.findall(r"import (.*) from '(.*)';", content)
        return imports

    def get_project_structure(self):
        """ Retourne la structure complète du projet """
        return self.project_structure

    def get_imports(self):
        """ Retourne les imports du projet """
        return self.imports

