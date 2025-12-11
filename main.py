import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from services.cinema_service import CinemaService
from models.enums import Tarif
from models.exceptions import CinemaException

class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.service = CinemaService()
        self.seance_selectionnee = None
        self.seance_index = -1
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        self.root.title("🎬 Système de Réservation Cinéma")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        # Titre principal
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, text="🎬 SYSTÈME DE RÉSERVATION CINÉMA", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Onglet 1: Réservation
        self.create_reservation_tab()
        
        # Onglet 2: Mes réservations
        self.create_reservations_tab()
        
    def create_reservation_tab(self):
        # Frame principal pour la réservation
        reservation_frame = ttk.Frame(self.notebook)
        self.notebook.add(reservation_frame, text="Faire une réservation")
        
        # Section séances
        seances_frame = ttk.LabelFrame(reservation_frame, text="Séances disponibles", padding=10)
        seances_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Liste des séances
        self.seances_listbox = tk.Listbox(seances_frame, height=8, font=('Courier', 10))
        self.seances_listbox.pack(fill='both', expand=True)
        self.seances_listbox.bind('<<ListboxSelect>>', self.on_seance_select)
        
        # Charger les séances
        self.load_seances()
        
        # Section informations client
        client_frame = ttk.LabelFrame(reservation_frame, text="Informations de réservation", padding=10)
        client_frame.pack(fill='x', padx=10, pady=5)
        
        # Nom du client
        ttk.Label(client_frame, text="Nom:").grid(row=0, column=0, sticky='w', padx=5)
        self.nom_entry = ttk.Entry(client_frame, width=30)
        self.nom_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Nombre de places
        ttk.Label(client_frame, text="Nombre de places:").grid(row=1, column=0, sticky='w', padx=5)
        self.places_spinbox = ttk.Spinbox(client_frame, from_=1, to=10, width=10)
        self.places_spinbox.set("1")
        self.places_spinbox.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Tarif
        ttk.Label(client_frame, text="Tarif:").grid(row=2, column=0, sticky='w', padx=5)
        self.tarif_combo = ttk.Combobox(client_frame, width=25, state='readonly')
        tarifs = list(Tarif)
        self.tarif_combo['values'] = [t.label for t in tarifs]
        self.tarif_combo.set(tarifs[0].label)
        self.tarif_combo.grid(row=2, column=1, padx=5, pady=2)
        
        # Bouton de réservation
        self.reserver_btn = ttk.Button(client_frame, text="Réserver", command=self.faire_reservation)
        self.reserver_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
    def create_reservations_tab(self):
        # Frame pour les réservations
        reservations_frame = ttk.Frame(self.notebook)
        self.notebook.add(reservations_frame, text="Mes réservations")
        
        # Titre
        ttk.Label(reservations_frame, text="Historique des réservations", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Zone de texte avec scrollbar
        self.reservations_text = scrolledtext.ScrolledText(reservations_frame, 
                                                          height=20, 
                                                          font=('Courier', 10))
        self.reservations_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Bouton actualiser
        refresh_btn = ttk.Button(reservations_frame, text="Actualiser", 
                                command=self.load_reservations)
        refresh_btn.pack(pady=5)
        
        # Charger les réservations
        self.load_reservations()
        
    def load_seances(self):
        self.seances_listbox.delete(0, tk.END)
        seances = self.service.get_toutes_seances()
        for i, seance in enumerate(seances):
            self.seances_listbox.insert(tk.END, f"{i+1}. {seance}")
            
    def on_seance_select(self, event):
        selection = self.seances_listbox.curselection()
        if selection:
            self.seance_index = selection[0]
            self.seance_selectionnee = self.service.get_toutes_seances()[self.seance_index]
            
    def faire_reservation(self):
        if self.seance_selectionnee is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner une séance.")
            return
            
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showwarning("Attention", "Veuillez entrer votre nom.")
            return
            
        try:
            nb_places = int(self.places_spinbox.get())
            if nb_places <= 0:
                messagebox.showerror("Erreur", "Le nombre de places doit être positif.")
                return
        except ValueError:
            messagebox.showerror("Erreur", "Nombre de places invalide.")
            return
            
        # Récupérer le tarif sélectionné
        tarif_label = self.tarif_combo.get()
        tarif = None
        for t in Tarif:
            if t.label == tarif_label:
                tarif = t
                break
                
        if tarif is None:
            messagebox.showerror("Erreur", "Tarif invalide.")
            return
            
        try:
            # Créer la réservation
            reservation = self.service.creer_reservation(self.seance_index, nom, nb_places, tarif)
            
            # Afficher le succès
            messagebox.showinfo("Succès", 
                              f"Réservation créée avec succès!\n\n"
                              f"Ticket #{reservation.id}\n"
                              f"Film: {reservation.seance.film.titre}\n"
                              f"Places: {nb_places}\n"
                              f"Total: {reservation.prix_total} €")
            
            # Réinitialiser les champs
            self.nom_entry.delete(0, tk.END)
            self.places_spinbox.set("1")
            self.tarif_combo.set(list(Tarif)[0].label)
            
            # Actualiser les listes
            self.load_seances()
            self.load_reservations()
            
        except CinemaException as e:
            messagebox.showerror("Erreur", f"Erreur de réservation: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
            
    def load_reservations(self):
        self.reservations_text.delete(1.0, tk.END)
        
        if not self.service.reservations:
            self.reservations_text.insert(tk.END, "Aucune réservation effectuée.")
        else:
            for i, reservation in enumerate(self.service.reservations, 1):
                self.reservations_text.insert(tk.END, f"--- Réservation {i} ---\n")
                self.reservations_text.insert(tk.END, str(reservation))
                self.reservations_text.insert(tk.END, "\n\n")

def main():
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
