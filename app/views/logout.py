import os

def logout():
    if os.path.exists(".token"):
        os.remove(".token")
        print("✅ Déconnexion réussie.")
    else:
        print("ℹ️ Aucun utilisateur connecté.")
