# /home/sebastien/IA_AGENT/agent.py

from github_integration import GitHubIntegration
from project_analyzer import ProjectAnalyzer
from config import MODEL_PATH
from transformers import LlamaTokenizer, LlamaForCausalLM,PreTrainedTokenizerFast
import json,os,sys,time

class Agent:
    def __init__(self):
        self.github = GitHubIntegration()
        self.project_analyzer = ProjectAnalyzer(self.github)
        if not os.path.exists(MODEL_PATH):
            raise ValueError(f"Le répertoire du modèle n'existe pas à {MODEL_PATH}")
        # Chargement du modèle LLaMA
        self.model = LlamaForCausalLM.from_pretrained(MODEL_PATH,local_files_only=True,revision=None)
        #self.tokenizer = LlamaTokenizer.from_pretrained(MODEL_PATH,local_files_only=True,legacy=False)
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_PATH, local_files_only=True)
        self.tokenizer.add_special_tokens({'pad_token':'<PAD>'})
        self.tokenizer.pad_token = "<PAD>"
        self.tokenizer.pad_token_id = self.tokenizer.convert_tokens_to_ids("<PAD>") 
        self.model.eval()  # Mode évaluation pour l'inférence

    def generate_code(self, prompt):
        """ Génère du code en réponse à un prompt donné en utilisant le modèle LLaMA """
        print("\n📤 Prompt envoyé au modèle :\n" + prompt)
        print("\n⏳ Génération en cours...", end="", flush=True)
         # Tokenisation du prompt
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        attention_mask = inputs.attention_mask
        # Extraction des ids de tokens pour l'entrée
        input_ids = inputs["input_ids"]

        eos_token_id = self.model.config.eos_token_id
        outputs = self.model.generate(
            input_ids,  # Passer les identifiants de tokens
            attention_mask=attention_mask,
            max_new_tokens=400,
            temperature=0.3,  # Contrôle la créativité, un peu plus aléatoire
            top_p=0.5,  # Utilise la probabilité cumulative pour générer des mots
            no_repeat_ngram_size=3,  # Évite la répétition de n-grammes
            pad_token_id=eos_token_id,  # Assure une gestion correcte des tokens de fin
            num_return_sequences=1
        )
        
        # Décodage des sorties en texte
        generated_code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if generated_code.startswith(prompt):
            generated_code = generated_code[len(prompt):].strip()
        if prompt in generated_code:
            generated_code = generated_code.replace(prompt, '').strip()
        # Supprime l'animation de chargement et affiche la réponse
        print("\r✅ Réponse reçue !")
        print("\n📥 Réponse brute du modèle :\n" + generated_code) 
        return generated_code

    def correct_code(self, file_path, content):
        """ Corrige un fichier en tenant compte des erreurs d'import et de cohérence """
        # Analyser les imports et les classes du projet
        imports = self.project_analyzer.get_imports()
        structure = self.project_analyzer.get_project_structure()
        
        # Générer un prompt basé sur le contenu du fichier et les erreurs possibles
        prompt = f"Corrige les erreurs d'import et de cohérence dans ce fichier :\n{content}\n\nStructure du projet : {structure}\nImports : {imports}"
        
        # Générer le code corrigé
        corrected_code = self.generate_code(prompt)
        
        # Mettre à jour le fichier sur GitHub
        self.github.update_file(file_path, corrected_code, f"Correction de {file_path}")

    def process_consigne(self, consigne):
        """ Traite la consigne donnée (ex. corriger les erreurs de code ou implémenter une fonctionnalité) """
        # Test préliminaire : envoyer une question au LLM
        test_prompt = "Comment vas-tu ? Répond en français."
        print("📤 Envoi du prompt au LLM : ", test_prompt)
        # Envoi du prompt et récupération de la réponse
        response = self.generate_code(test_prompt)
        # Afficher la réponse dans la console
        print("📥 Réponse du LLM : ", response)
 
        if "corrige" in consigne:
            # Analyser tous les fichiers du projet pour trouver les erreurs
            print("Corriger les erreurs de cohérence et d'import...")
            files = self.github.list_files("/")
            for file_path in files:
                if file_path.endswith((".js", ".ts", ".tsx")):
                    content = self.github.get_file_content(file_path)
                    self.correct_code(file_path, content)
        elif "code moi" in consigne:
            # Implémenter une nouvelle fonctionnalité décrite dans dev.txt
            print("Implémentation d'une fonctionnalité...")
            self.implement_feature_from_dev()

    def implement_feature_from_dev(self):
        """ Implémente la première fonctionnalité non réalisée dans dev.txt """
        dev_file_path = 'dev.txt'
        dev_content = self.github.get_file_content(dev_file_path)
        features = json.loads(dev_content)
        for feature in features["fonctionnalites"]:
            if not feature['developpe']:
                print(f"Implémentation de la fonctionnalité: {feature['description']}")
                # Construire le prompt pour demander au modèle de générer les fichiers à modifier et le code à insérer
                prompt = f"""
Voici les fichiers du projet et leurs contenus: {self.project_analyzer.get_project_structure()}.
Voici la description de la fonctionnalité : {feature['description']}.

Tu dois générer un **JSON strictement valide** contenant la liste des fichiers à modifier ou à créer, et le code à insérer dans chaque fichier.  
Le format attendu est :
```json
{{
  "fichiers": [
    {{
      "nom": "src/components/PlayButton.js",
      "code": "import React from 'react';\nexport default function PlayButton() {{ return <button>Jouer</button>; }}"
    }},
    {{
      "nom": "src/screens/ShopScreen.js",
      "code": "import React from 'react';\nexport default function ShopScreen() {{ return <div>Boutique</div>; }}"
    }}
  ]
}}
Ne génère rien d'autre que ce format JSON valide. """
                # Générer la réponse à partir du modèle
                response = self.generate_code(prompt)
                # Analyser la réponse du modèle pour extraire les fichiers et le code
                try:
                    modification_data = json.loads(response)
                    self.apply_modifications(modification_data)
                    print(f"✅ Fonctionnalité implémentée avec succès.")
                except json.JSONDecodeError:
                    print("❌ Erreur lors de la parsing de la réponse JSON du modèle")
                break  # Quitte la boucle après avoir traité la première fonctionnalité non développée
    def apply_modifications(self, modification_data):
        """ Applique les modifications sur le projet en fonction de la réponse JSON du modèle """
        for modification in modification_data['fichiers']:
            file_path = modification['nom']
            new_code = modification['code']
            
            # Mettre à jour le fichier sur GitHub
            self.github.update_file(file_path, new_code, f"Ajout de la fonctionnalité dans {file_path}")

