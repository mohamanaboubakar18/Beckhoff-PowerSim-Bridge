# Beckhoff-PowerSim-Bridge — Gestionnaire d'Interfaces de Simulation (ADS) & IHM
<img width="1919" height="1024" alt="1" src="https://github.com/user-attachments/assets/b17415dc-2a5a-40fe-bb60-a1281faac92d" />


## Contexte & Objectif du Projet
Ce démonstrateur technique répond aux problématiques d'intégration, de test et de maintenance d'outils de simulation d'automatisme au sein d'environnements industriels complexes de conversion d'énergie.

Lors de la validation de lois de commande sur automates Beckhoff (TwinCAT), il est crucial d'interfacer le code automate avec des modèles physiques de puissance sans dépendre du matériel réel. Cette architecture modulaire en Python permet de :
1. Gérer dynamiquement la table d'échange automate via un référentiel JSON déclaratif et le protocole ADS (pyads).
2. Simuler la physique d'un variateur de puissance (inertie mécanique, appel de courant statorique, thermique IGBT par effet Joule, logique de disjonction/Trip).
3. Superviser l'ensemble et valider les sécurités via une IHM web interactive (forçage I/O et injection de pannes matérielles).

---

## Architecture Logicielle & Fonctionnalités

L'architecture découple la communication industrielle, le modèle mathématique et l'interface utilisateur pour garantir la maintenabilité :

* **io_mapping.json** : Mapping des variables échangées (entrées/sorties PLC, types de données, valeurs d'initialisation).
* **ads_bridge.py** : Wrapper de communication. Intègre un mode "Mock" autonome : si la DLL TwinCAT (TcAdsDll.dll) est absente de la machine, le système bascule silencieusement sur une mémoire partagée virtuelle pour garantir l'exécution de l'IHM et des tests.
* **converter_model.py** : Modèle dynamique discret du variateur (constante de temps mécanique, pertes thermiques, seuils critiques).
* **app_hmi.py** : IHM Streamlit avec rafraîchissement temps réel (courbes transitoires et supervision mémoire PLC).
* **test_simulation.py** : Suite de tests automatisés pytest validant la hiérarchie des commandes et le déclenchement immédiat des sécurités électriques.

---

## Installation & Démarrage Rapide (Sans automate requis)

Grâce au mode Mock ADS intégré, l'application et les tests peuvent être exécutés sur n'importe quel poste, même sans TwinCAT installé.


# 1. Cloner le dépôt et installer les dépendances
git clone [https://github.com/mohamanaboubakar18/Beckhoff-PowerSim-Bridge.git](https://github.com/mohamanaboubakar18/Beckhoff-PowerSim-Bridge.git)
cd Beckhoff-PowerSim-Bridge
pip install -r requirements.txt

# 2. Exécuter la suite de tests unitaires (Validation I/O & Protections)
python -m pytest -v

# 3. Lancer l'IHM de supervision et de simulation
python -m streamlit run app_hmi.py
Note pour l'utilisation avec un runtime TwinCAT 3 actif : dans app_hmi.py, passez use_mock=False et renseignez l'ams_net_id cible dans io_mapping.json.

Validation & Tests HIL (Hardware-in-the-Loop)
1. Injection de défauts électrothermiques
Le simulateur permet de valider le comportement du contrôleur face à des incidents critiques d'exploitation (surtension du Bus DC, perte de refroidissement IGBT, ouverture de disjoncteur HTA amont).

<img width="800" height="426" alt="demo_Beckhoff" src="https://github.com/user-attachments/assets/babb11aa-b0d4-4822-b49e-02e5f551b018" />


3. Tests Unitaires Automatisés
L'intégrité de la logique de protection et du forçage de la table d'échange est validée par intégration continue.

<img width="1920" height="1020" alt="pytest" src="https://github.com/user-attachments/assets/d944c15b-eb7d-427b-bb81-5683ddf22bdb" />


Profil & Approche "Terrain + Code"
Mohaman ABOUBAKAR — Élève-ingénieur Généraliste (Génie Électrique, Électronique & Info. Industrielle) à l'ENIB.

Ce code reflète une double culture technique :
Concevoir des simulateurs logiciels robustes nécessite de comprendre la physique des équipements. Fort de 6 ans d'expérience préalable comme Chef d'équipe Maintenance de Postes HT/BT (réseaux, transformateurs, cellules HTA, relais de protection numériques), j'architecture le code de simulation en pensant aux défauts électriques réels et aux contraintes d'exploitation sur site.

Contact : mohamanaboubakar18@gmail.com
