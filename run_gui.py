"""
🎬 CINÉMA - SYSTÈME DE RÉSERVATION
Interface Graphique Tkinter

Ce fichier lance l'application avec l'interface graphique moderne.
Utilisez main.py pour la version console ou gui_cinema.py pour la version complète.
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