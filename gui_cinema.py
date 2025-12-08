import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from services.cinema_service import CinemaService
from models.enums import Tarif, StyleFilm, TypeSalle
from models.exceptions import CinemaException

class CinemaGUI:
    def __init__(self, root):
        self.root = root
        self.service = CinemaService()
        self.seance_selectionnee = None
        self.seance_index = -1
        
        self.setup_window()
        self.create_styles()
        self.create_main_interface()
        
    def setup_window(self):
        self.root.title("🎬 Cinéma - Système de Réservation")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Icône (si disponible)
        try:
            self.root.iconbitmap('cinema.ico')
        except:
            pass
            
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f'1000x700+{x}+{y}')
        
    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour le titre
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#2c3e50')
        
        # Style pour les boutons
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        
        # Style pour les frames
        style.configure('Card.TFrame', relief='raised', borderwidth=2)
        
    def create_main_interface(self):
        # Header avec titre
        self.create_header()
        
        # Corps principal avec notebook
        self.create_notebook()
        
        # Footer avec informations
        self.create_footer()
        
    def create_header(self):
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Titre principal
        title_label = ttk.Label(header_frame, 
                               text="🎬 CINÉMA DELUXE", 
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(header_frame, 
                                 text="Système de Réservation en Ligne",
                                 font=('Arial', 12))
        subtitle_label.pack()
        
    def create_notebook(self):
        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Onglets
        self.create_seances_tab()
        self.create_reservation_tab()
        self.create_historique_tab()
        self.create_stats_tab()
        
    def create_seances_tab(self):
        """Onglet pour voir toutes les séances"""
        seances_frame = ttk.Frame(self.notebook)
        self.notebook.add(seances_frame, text="📅 Séances")
        
        # Titre
        ttk.Label(seances_frame, text="Séances Disponibles", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame pour la liste des séances
        list_frame = ttk.Frame(seances_frame)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview pour afficher les séances de façon plus jolie
        columns = ('Horaire', 'Film', 'Salle', 'Type', 'Disponible')
        self.seances_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configuration des colonnes
        self.seances_tree.heading('Horaire', text='Horaire')
        self.seances_tree.heading('Film', text='Film')
        self.seances_tree.heading('Salle', text='Salle')
        self.seances_tree.heading('Type', text='Type Salle')
        self.seances_tree.heading('Disponible', text='Places Dispo.')
        
        self.seances_tree.column('Horaire', width=100)
        self.seances_tree.column('Film', width=200)
        self.seances_tree.column('Salle', width=150)
        self.seances_tree.column('Type', width=120)
        self.seances_tree.column('Disponible', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.seances_tree.yview)
        self.seances_tree.configure(yscrollcommand=scrollbar.set)
        
        self.seances_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bouton actualiser
        ttk.Button(seances_frame, text="Actualiser", 
                  command=self.load_seances_tree).pack(pady=10)
        
        # Charger les données
        self.load_seances_tree()
        
    def create_reservation_tab(self):
        """Onglet pour faire une réservation"""
        reservation_frame = ttk.Frame(self.notebook)
        self.notebook.add(reservation_frame, text="🎫 Réserver")
        
        # Titre
        ttk.Label(reservation_frame, text="Nouvelle Réservation", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(reservation_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Section 1: Sélection de séance
        seance_frame = ttk.LabelFrame(main_frame, text="1. Choisir une séance", padding=15)
        seance_frame.pack(fill='x', pady=(0, 10))
        
        self.seances_listbox = tk.Listbox(seance_frame, height=6, font=('Courier', 10))
        self.seances_listbox.pack(fill='x')
        self.seances_listbox.bind('<<ListboxSelect>>', self.on_seance_select)
        
        # Section 2: Informations client
        client_frame = ttk.LabelFrame(main_frame, text="2. Vos informations", padding=15)
        client_frame.pack(fill='x', pady=(0, 10))
        
        # Grille pour les champs
        info_frame = ttk.Frame(client_frame)
        info_frame.pack(fill='x')
        
        # Nom
        ttk.Label(info_frame, text="Nom complet:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.nom_entry = ttk.Entry(info_frame, width=30, font=('Arial', 10))
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Nombre de places
        ttk.Label(info_frame, text="Nombre de places:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.places_spinbox = ttk.Spinbox(info_frame, from_=1, to=10, width=10, font=('Arial', 10))
        self.places_spinbox.set("1")
        self.places_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Tarif
        ttk.Label(info_frame, text="Type de tarif:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.tarif_combo = ttk.Combobox(info_frame, width=27, state='readonly', font=('Arial', 10))
        tarifs = list(Tarif)
        self.tarif_combo['values'] = [f"{t.label} ({t.coeff*100:.0f}%)" for t in tarifs]
        self.tarif_combo.set(f"{tarifs[0].label} ({tarifs[0].coeff*100:.0f}%)")
        self.tarif_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Section 3: Récapitulatif et validation
        recap_frame = ttk.LabelFrame(main_frame, text="3. Récapitulatif", padding=15)
        recap_frame.pack(fill='x', pady=(0, 10))
        
        self.recap_label = ttk.Label(recap_frame, text="Sélectionnez une séance pour voir le récapitulatif", 
                                   font=('Arial', 10), foreground='gray')
        self.recap_label.pack(anchor='w')
        
        # Bouton de réservation
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x')
        
        self.reserver_btn = ttk.Button(btn_frame, text="🎫 RÉSERVER", 
                                     style='Action.TButton',
                                     command=self.faire_reservation)
        self.reserver_btn.pack(side='right', padx=10)
        
        # Charger les séances
        self.load_seances_reservation()
        
        # Binding pour mise à jour du récapitulatif
        self.nom_entry.bind('<KeyRelease>', self.update_recap)
        self.places_spinbox.bind('<ButtonRelease-1>', self.update_recap)
        self.places_spinbox.bind('<KeyRelease>', self.update_recap)
        self.tarif_combo.bind('<<ComboboxSelected>>', self.update_recap)
        
    def create_historique_tab(self):
        """Onglet pour l'historique des réservations"""
        historique_frame = ttk.Frame(self.notebook)
        self.notebook.add(historique_frame, text="📋 Historique")
        
        # Titre
        ttk.Label(historique_frame, text="Historique des Réservations", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(historique_frame)
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.reservations_text = scrolledtext.ScrolledText(text_frame, 
                                                          height=20, 
                                                          font=('Courier', 10),
                                                          wrap='word')
        self.reservations_text.pack(fill='both', expand=True)
        
        # Frame pour les boutons
        btn_frame = ttk.Frame(historique_frame)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Actualiser", 
                  command=self.load_reservations).pack(side='left')
        ttk.Button(btn_frame, text="Effacer l'historique", 
                  command=self.clear_reservations).pack(side='right')
        
        # Charger les réservations
        self.load_reservations()
        
    def create_stats_tab(self):
        """Onglet pour les statistiques"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistiques")
        
        # Titre
        ttk.Label(stats_frame, text="Statistiques du Cinéma", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame pour les stats
        stats_content = ttk.Frame(stats_frame)
        stats_content.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(stats_content, 
                                                   height=25, 
                                                   font=('Arial', 11),
                                                   wrap='word')
        self.stats_text.pack(fill='both', expand=True)
        
        # Bouton actualiser
        ttk.Button(stats_frame, text="Actualiser les statistiques", 
                  command=self.load_stats).pack(pady=10)
        
        # Charger les stats
        self.load_stats()
        
    def create_footer(self):
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill='x', padx=10, pady=5)
        
        status_label = ttk.Label(footer_frame, 
                               text=f"Système initialisé - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                               font=('Arial', 9),
                               foreground='gray')
        status_label.pack(side='left')
        
        version_label = ttk.Label(footer_frame, 
                                text="v2.0 - Interface Tkinter",
                                font=('Arial', 9),
                                foreground='gray')
        version_label.pack(side='right')
        
    def load_seances_tree(self):
        # Vider le tree
        for item in self.seances_tree.get_children():
            self.seances_tree.delete(item)
            
        # Ajouter les séances
        seances = self.service.get_toutes_seances()
        for seance in seances:
            horaire = seance.horaire.strftime('%H:%M')
            film = seance.film.titre
            salle = seance.salle.nom
            type_salle = seance.salle.type_salle.value
            dispo = f"{seance.places_disponibles}/{seance.salle.capacite}"
            
            # Coloration selon disponibilité
            if seance.places_disponibles == 0:
                tags = ('complet',)
            elif seance.places_disponibles < 10:
                tags = ('peu',)
            else:
                tags = ('disponible',)
                
            self.seances_tree.insert('', 'end', 
                                   values=(horaire, film, salle, type_salle, dispo),
                                   tags=tags)
        
        # Configuration des tags de couleur
        self.seances_tree.tag_configure('complet', background='#ffcccc')
        self.seances_tree.tag_configure('peu', background='#fff3cd')
        self.seances_tree.tag_configure('disponible', background='#d4edda')
        
    def load_seances_reservation(self):
        self.seances_listbox.delete(0, tk.END)
        seances = self.service.get_toutes_seances()
        for i, seance in enumerate(seances):
            status = "COMPLET" if seance.est_complete else f"{seance.places_disponibles} places"
            self.seances_listbox.insert(tk.END, f"{i+1}. [{seance.horaire.strftime('%H:%M')}] {seance.film.titre} - {status}")
            
    def on_seance_select(self, event):
        selection = self.seances_listbox.curselection()
        if selection:
            self.seance_index = selection[0]
            self.seance_selectionnee = self.service.get_toutes_seances()[self.seance_index]
            self.update_recap()
            
    def update_recap(self, event=None):
        if not self.seance_selectionnee:
            self.recap_label.config(text="Sélectionnez une séance pour voir le récapitulatif")
            return
            
        nom = self.nom_entry.get().strip()
        try:
            nb_places = int(self.places_spinbox.get())
        except:
            nb_places = 1
            
        # Récupérer le tarif
        tarif_text = self.tarif_combo.get()
        tarif = list(Tarif)[0]  # Par défaut
        for t in Tarif:
            if t.label in tarif_text:
                tarif = t
                break
                
        # Calculer le prix estimé
        PRIX_BASE = 10.00
        prix_unitaire = (PRIX_BASE + self.seance_selectionnee.salle.supplement_prix) * tarif.coeff
        prix_total = round(prix_unitaire * nb_places, 2)
        
        recap_text = f"""📽️ Film: {self.seance_selectionnee.film.titre}
🏛️ Salle: {self.seance_selectionnee.salle.nom} ({self.seance_selectionnee.salle.type_salle.value})
🕐 Horaire: {self.seance_selectionnee.horaire.strftime('%d/%m/%Y à %H:%M')}
👤 Client: {nom if nom else '[À remplir]'}
🎫 Places: {nb_places} x {tarif.label}
💰 Total estimé: {prix_total} €"""
        
        self.recap_label.config(text=recap_text, foreground='black')
        
    def faire_reservation(self):
        if self.seance_selectionnee is None:
            messagebox.showwarning("Attention", "Veuillez sélectionner une séance.")
            return
            
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showwarning("Attention", "Veuillez entrer votre nom.")
            self.nom_entry.focus()
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
        tarif_text = self.tarif_combo.get()
        tarif = None
        for t in Tarif:
            if t.label in tarif_text:
                tarif = t
                break
                
        if tarif is None:
            messagebox.showerror("Erreur", "Tarif invalide.")
            return

        self._reservation_en_cours = {
            "nom": nom,
            "nb_places": nb_places,
            "tarif": tarif,
        }

        self.ouvrir_selection_places()

    def ouvrir_selection_places(self):
        """Ouvre une fenêtre avec toutes les places de la salle sous forme de grille."""
        seance = self.seance_selectionnee
        if not seance or not self._reservation_en_cours:
            return

        nb_demande = self._reservation_en_cours["nb_places"]

        top = tk.Toplevel(self.root)
        top.title(f"Choisissez vos {nb_demande} place(s)")
        top.grab_set()  # bloque l'interaction avec la fenêtre principale

        ttk.Label(
            top,
            text=f"Sélectionnez {nb_demande} place(s) pour {seance.film.titre}\n"
                 f"Salle {seance.salle.nom} - capacité {seance.salle.capacite}",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        grille_frame = ttk.Frame(top)
        grille_frame.pack(padx=10, pady=5)

        # On garde les variables des checkboxes pour savoir ce qui est coché
        self._seat_vars = {}

        nb_par_ligne = 10  # 10 sièges par rangée pour l'affichage
        for num in range(1, seance.salle.capacite + 1):
            var = tk.IntVar(value=0)
            cb = tk.Checkbutton(
                grille_frame,
                text=str(num),
                variable=var,
                indicatoron=False,  # bouton "plein" plutôt que case à cocher classique
                width=4,
                padx=2,
                pady=2
            )

            # Si la place est occupée, on la désactive
            if num in seance.places_occupees:
                cb.config(state="disabled")
                cb.configure(fg="gray")
            cb.grid(row=(num - 1) // nb_par_ligne, column=(num - 1) % nb_par_ligne, padx=2, pady=2)

            self._seat_vars[num] = var

        # Boutons de validation / annulation
        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=10, fill="x")

        ttk.Button(
            btn_frame,
            text="Annuler",
            command=top.destroy
        ).pack(side="right", padx=5)

        ttk.Button(
            btn_frame,
            text="Valider les places",
            command=lambda: self.valider_selection_places(top)
        ).pack(side="right", padx=5)

    def valider_selection_places(self, window: tk.Toplevel):
        """Récupère les places cochées, vérifie, crée la réservation et ferme la fenêtre."""
        seance = self.seance_selectionnee
        if not seance or not self._reservation_en_cours:
            window.destroy()
            return

        nb_demande = self._reservation_en_cours["nb_places"]
        nom = self._reservation_en_cours["nom"]
        tarif = self._reservation_en_cours["tarif"]

        # On récupère les numéros cochés et libres
        places_choisies = [
            num for num, var in self._seat_vars.items()
            if var.get() == 1 and num not in seance.places_occupees
        ]

        if len(places_choisies) != nb_demande:
            messagebox.showerror(
                "Erreur",
                f"Vous devez sélectionner exactement {nb_demande} place(s).\n"
                f"Vous en avez sélectionné {len(places_choisies)}."
            )
            return

        # On crée réellement la réservation via le service
        try:
            reservation = self.service.creer_reservation(
                self.seance_index,
                nom,
                len(places_choisies),
                tarif,
                numeros_places=places_choisies,
            )
        except CinemaException as e:
            messagebox.showerror("Erreur de réservation", str(e))
            return
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
            return

        # Si tout va bien on ferme la fenêtre de choix
        window.destroy()


        try:
            # Créer la réservation
            #reservation = self.service.creer_reservation(self.seance_index, nom, nb_places, tarif)
            
            # Afficher le succès avec plus de détails
            success_message = f"""✅ RÉSERVATION CONFIRMÉE ✅



🎫 Numéro de ticket: {reservation.id}
👤 Client: {nom}
📽️ Film: {reservation.seance.film.titre}
🏛️ Salle: {reservation.seance.salle.nom}
🕐 Horaire: {reservation.seance.horaire.strftime('%d/%m/%Y à %H:%M')}
🎫 Places: {len(places_choisies)} × {tarif.label}
🪑 Sièges: {', '.join(str(p) for p in sorted(places_choisies))}
💰 Total payé: {reservation.prix_total} €

Merci de votre confiance! 
Présentez-vous 15 minutes avant la séance."""
            
            messagebox.showinfo("Réservation confirmée", success_message)
            
            # Réinitialiser les champs
            self.nom_entry.delete(0, tk.END)
            self.places_spinbox.set("1")
            self.tarif_combo.set(f"{list(Tarif)[0].label} ({list(Tarif)[0].coeff*100:.0f}%)")
            self.seance_selectionnee = None
            self.seance_index = -1
            self._reservation_en_cours = None 

            # Actualiser toutes les vues
            self.load_seances_tree()
            self.load_seances_reservation()
            self.load_reservations()
            self.load_stats()
            self.update_recap()
            
        except CinemaException as e:
            messagebox.showerror("Erreur de réservation", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
            
    def load_reservations(self):
        self.reservations_text.delete(1.0, tk.END)
        
        if not self.service.reservations:
            self.reservations_text.insert(tk.END, 
                                        "🎬 Aucune réservation effectuée pour le moment.\n\n"
                                        "Utilisez l'onglet 'Réserver' pour créer votre première réservation!")
        else:
            self.reservations_text.insert(tk.END, 
                                        f"📋 HISTORIQUE DES RÉSERVATIONS ({len(self.service.reservations)} réservation(s))\n")
            self.reservations_text.insert(tk.END, "="*60 + "\n\n")
            
            for i, reservation in enumerate(self.service.reservations, 1):
                self.reservations_text.insert(tk.END, f"--- RÉSERVATION #{i} ---\n")
                self.reservations_text.insert(tk.END, str(reservation))
                self.reservations_text.insert(tk.END, "\n" + "-"*40 + "\n\n")
                
    def clear_reservations(self):
        if not self.service.reservations:
            messagebox.showinfo("Information", "Aucune réservation à effacer.")
            return
            
        if messagebox.askyesno("Confirmation", 
                              "Êtes-vous sûr de vouloir effacer tout l'historique?\n"
                              "Cette action est irréversible."):
            self.service.reservations.clear()
            self.load_reservations()
            self.load_stats()
            messagebox.showinfo("Succès", "Historique effacé avec succès.")
            
    def load_stats(self):
        self.stats_text.delete(1.0, tk.END)
        
        # Statistiques générales
        total_seances = len(self.service.get_toutes_seances())
        total_reservations = len(self.service.reservations)
        
        self.stats_text.insert(tk.END, "📊 STATISTIQUES DU CINÉMA\n")
        self.stats_text.insert(tk.END, "="*50 + "\n\n")
        
        # Stats de base
        self.stats_text.insert(tk.END, "📈 DONNÉES GÉNÉRALES:\n")
        self.stats_text.insert(tk.END, f"   • Nombre de séances programmées: {total_seances}\n")
        self.stats_text.insert(tk.END, f"   • Total des réservations: {total_reservations}\n")
        
        if total_reservations > 0:
            # Revenus
            revenus_total = sum(r.prix_total for r in self.service.reservations)
            places_vendues = sum(r.nb_places for r in self.service.reservations)
            
            self.stats_text.insert(tk.END, f"   • Places vendues: {places_vendues}\n")
            self.stats_text.insert(tk.END, f"   • Revenus générés: {revenus_total:.2f} €\n\n")
            
            # Stats par film
            self.stats_text.insert(tk.END, "🎬 POPULARITÉ DES FILMS:\n")
            films_stats = {}
            for r in self.service.reservations:
                titre = r.seance.film.titre
                if titre not in films_stats:
                    films_stats[titre] = {'places': 0, 'revenus': 0}
                films_stats[titre]['places'] += r.nb_places
                films_stats[titre]['revenus'] += r.prix_total
                
            for film, stats in sorted(films_stats.items(), key=lambda x: x[1]['places'], reverse=True):
                self.stats_text.insert(tk.END, 
                    f"   • {film}: {stats['places']} places ({stats['revenus']:.2f} €)\n")
                
            # Stats par tarif
            self.stats_text.insert(tk.END, "\n💰 RÉPARTITION DES TARIFS:\n")
            tarifs_stats = {}
            for r in self.service.reservations:
                tarif = r.tarif.label
                if tarif not in tarifs_stats:
                    tarifs_stats[tarif] = 0
                tarifs_stats[tarif] += r.nb_places
                
            for tarif, count in sorted(tarifs_stats.items(), key=lambda x: x[1], reverse=True):
                pourcentage = (count / places_vendues) * 100
                self.stats_text.insert(tk.END, f"   • {tarif}: {count} places ({pourcentage:.1f}%)\n")
                
            # Stats par salle
            self.stats_text.insert(tk.END, "\n🏛️ OCCUPATION DES SALLES:\n")
            for seance in self.service.get_toutes_seances():
                taux = ((seance.salle.capacite - seance.places_disponibles) / seance.salle.capacite) * 100
                self.stats_text.insert(tk.END, 
                    f"   • {seance.salle.nom}: {taux:.1f}% occupé "
                    f"({seance.salle.capacite - seance.places_disponibles}/{seance.salle.capacite})\n")
        else:
            self.stats_text.insert(tk.END, "\n💡 Aucune réservation pour l'instant.\n")
            self.stats_text.insert(tk.END, "Les statistiques détaillées apparaîtront après les premières réservations.\n")

def main():
    root = tk.Tk()
    app = CinemaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()