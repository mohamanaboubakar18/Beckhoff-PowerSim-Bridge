# Beckhoff-PowerSim-Bridge — Gestionnaire d'Interfaces de Simulation (ADS) & IHM

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Beckhoff ADS](https://img.shields.io/badge/Beckhoff-TwinCAT%20ADS%20(pyads)-red.svg)](https://github.com/stlehmann/pyads)
[![Streamlit HMI](https://img.shields.io/badge/HMI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](https://docs.pytest.org/)

## Contexte & Objectif du Projet
Ce micro-projet a été conçu comme démonstrateur technique pour répondre aux problématiques d'**intégration et de maintenance d'outils de simulation d'automatisme** au sein d'environnements de conversion d'énergie (**GE Vernova — Power Conversion**).

Lors de la validation de lois de commande sur automates **Beckhoff (TwinCAT)**, les équipes d'ingénierie ont besoin d'interfacer le code automate avec des modèles physiques de convertisseurs sans dépendre du matériel réel. Cet outil propose une architecture modulaire en Python permettant de :
1. **Gérer dynamiquement les interfaces automate** via un fichier de configuration déclaratif (`io_mapping.json`) et le protocole **ADS (`pyads`)**.
2. **Simuler en boucle fermée** le comportement électrothermique d'un convertisseur de puissance (inertie, courant statorique, thermique IGBT par effet Joule, protections).
3. **Superviser et tester les sécurités** via une **IHM dédiée** permettant le forçage d'I/O et l'injection de défauts électriques (surtension Bus DC, perte de ventilation, déclenchement disjoncteur).

---

## Architecture Logicielle

L'architecture découple strictement la couche de communication industrielle, le modèle physique et l'interface homme-machine afin de faciliter la maintenance évolutive :

* **`io_mapping.json`** : Référentiel unique des variables échangées (entrées/sorties automate, types de données `BOOL`/`LREAL`, valeurs d'initialisation).
* **`ads_bridge.py`** : Wrapper autour de `pyads`. Intègre un **mode Mock autonome** (basculement transparent sur une mémoire partagée si aucun runtime TwinCAT n'est détecté sur le poste) ainsi qu'une table de **forçage de variables**.
* **`converter_model.py`** : Modèle dynamique discret du variateur de puissance et de ses seuils de disjonction (Trip).
* **`app_hmi.py`** : Interface Homme-Machine interactive sous Streamlit (pilotage, courbes transitoires et table d'échange ADS en temps réel).
* **`test_simulation.py`** : Suite de tests unitaires automatisés sous `pytest` validant le forçage d'interfaces et la mise en sécurité du convertisseur.

---

## Installation & Démarrage Rapide (Sans TwinCAT requis)

Grâce au mode *Mock ADS* intégré, vous pouvez tester l'intégralité de la chaîne de simulation et l'IHM en 3 commandes :

```bash
# 1. Cloner le dépôt et installer les dépendances
git clone [https://github.com/mohamanaboubakar18/Beckhoff-PowerSim-Bridge.git](https://github.com/mohamanaboubakar18/Beckhoff-PowerSim-Bridge.git)
cd Beckhoff-PowerSim-Bridge
pip install -r requirements.txt

# 2. Exécuter la suite de tests unitaires (Validation I/O & Protections)
python -m pytest -v

# 3. Lancer l'IHM de supervision et de simulation
streamlit run app_hmi.py


À propos de l'auteur — L'approche "Terrain + Code"
Mohaman ABOUBAKAR — Élève-ingénieur à l'ENIB (Brest) en Génie Électrique, Électronique & Informatique Industrielle, fort de 6 ans d'expérience préalable comme Technicien Supérieur & Chef d'équipe Maintenance HT/BT (ENEO).

Pourquoi cette double approche ? Avoir exploité, consigné et dépanné de vrais équipements de puissance (transformateurs, cellules HTA, relais de protection SEPAM) pendant 6 ans me permet de concevoir des outils de simulation et des IHM pensés pour l'utilisateur final : lisibilité immédiate des états de défaut, scénarios de test réalistes et robustesse du code.

Contact : mohamanaboubakar18@gmail.com 