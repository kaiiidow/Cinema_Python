"""
🎬 CINÉMA - SYSTÈME DE RÉSERVATION
Interface Graphique Tkinter

Ce fichier est le point d'entrée pour lancer l'application avec l'interface graphique moderne.
Il initialise et exécute la classe CinemaGUI.
"""

try:
    import tkinter as tk
    from gui_cinema import CinemaGUI
    
    def main():
        print("🎬 Démarrage de l'interface graphique du cinéma...")
        
        root = tk.Tk()
        app = CinemaGUI(root)
        
        print("✅ Interface chargée avec succès!")
        print("📱 Utilisez la fenêtre graphique pour interagir avec le système.")
        
        root.mainloop()
        
        print("👋 Au revoir!")

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print("❌ Erreur d'importation:", e)
    print("💡 Assurez-vous que tkinter est installé (inclus par défaut avec Python)")
except Exception as e:
    print(f"❌ Erreur: {e}")
    input("Appuyez sur Entrée pour fermer...")