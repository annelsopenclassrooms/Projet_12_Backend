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
1️⃣ Clonez le dépôt :
```bash
git clone <url-du-repo>
cd epic-events-crm
```


## Structure des tables

Les principales tables :

    users (username, password haché, prénom, nom, rôle)

    clients (prénom, nom, email, téléphone, société, commercial responsable)

    contracts (client, commercial, montants, statut)

    events (contrat, client, support, lieu, dates)

    roles (nom du rôle)


## Todo readme
finir installation y compris db et requirement

✅ Exemple d'utilisation

    Ajouter un utilisateur
    Vérifier un mot de passe
    