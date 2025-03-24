# /home/sebastien/IA_AGENT/main.py
from agent import Agent
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    logging.info("Agent en cours d'initialisation...")
    agent = Agent()

    # Lire la consigne à partir de consigne.txt sur GitHub
    consigne_path = 'consigne.txt'
    logging.info(f"Lecture de la consigne depuis {consigne_path}...")
    
    consigne = agent.github.get_file_content(consigne_path)  # Correction ici

    if consigne:
        logging.info(f"Consigne lue : {consigne.strip()}")
    else:
        logging.warning("Aucune consigne trouvée ou fichier vide.")

    # Traiter la consigne
    logging.info("Traitement de la consigne...")
    agent.process_consigne(consigne)

if __name__ == "__main__":
    main()

