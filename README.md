# Epic Events CRM

Epic Events CRM est une application en ligne de commande écrite en Python 3.  
Elle permet de gérer les clients, contrats et événements pour l'entreprise Epic Events.

## 🚀 Fonctionnalités
- Gestion des utilisateurs avec rôles (commercial, gestion, support)
- Gestion des clients, contrats et événements
- Sécurité des mots de passe avec bcrypt
- Base de données SQLite légère et portable
- Respect du principe du moindre privilège

## 📌 Technologies
- Python 3.9+
- SQLite
- bcrypt

## ⚙️ Installation

### 1. Cloner le projet

```bash
git git@github.com:annelsopenclassrooms/Projet_12_Backend.git
```

### 2. Créer un environnement virtuel et l’activer :
   ```sh
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```
### 3. Installer les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

### 4. Créer un utilisateur
   ```sh
   python create_user.py
   ```

### 5. Lancer l'application
   ```sh
   python main.py
   ```

## Structure des tables

Les principales tables :

    users (username, password haché, prénom, nom, rôle)

    clients (prénom, nom, email, téléphone, société, commercial responsable)

    contracts (client, commercial, montants, statut)

    events (contrat, client, support, lieu, dates)

    roles (nom du rôle)



    