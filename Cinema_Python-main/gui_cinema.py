import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from services.cinema_service import CinemaService
from models.exceptions import CinemaException
from models.enums import StyleFilm, TypeSalle
from models.reservation import Tarif

class Colors:
    """Palette de couleurs élégante et moderne"""
    DARK = "#1a1a1a"
    DARKER = "#0d0d0d"
    LIGHT = "#f5f5f5"
    LIGHTER = "#ffffff"
    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    SECONDARY = "#64748b"
    SUCCESS = "#16a34a"
    WARNING = "#ea580c"
    DANGER = "#dc2626"
    BORDER = "#e5e7eb"


class CinemaGUI:
    def __init__(self, root):
        self.root = root
        self.service = CinemaService()
        self.seance_selectionnee = None
        self.seance_index = -1
        self._reservation_en_cours = None
        self._seat_vars = {}
        self._seances_affichees = []  # Pour stocker les references aux seances affichees
        self._selected_seances_date = None  # Date sélectionnée pour l'affichage
        
        self.setup_window()
        self.setup_styles()
        self.create_interface()
        
    def setup_window(self):
        """Configure la fenêtre principale"""
        self.root.title("🎬 Cinéma - Système de Réservation")
        
        # Ouvrir en plein écran
        self.root.state('zoomed')  # Pour Windows
        self.root.minsize(1000, 600)
        
        # Couleur de fond
        self.root.configure(bg=Colors.LIGHT)
        
    def setup_styles(self):
        """Configure les styles ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame
        style.configure('TFrame', background=Colors.LIGHT)
        style.configure('Content.TFrame', background=Colors.LIGHTER)
        style.configure('Card.TFrame', background='white', relief='flat')
        
        # Labels
        style.configure('TLabel', background=Colors.LIGHT, foreground=Colors.DARK)
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), 
                       foreground=Colors.PRIMARY, background=Colors.LIGHT)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11), 
                       foreground=Colors.SECONDARY, background=Colors.LIGHT)
        style.configure('SectionTitle.TLabel', font=('Segoe UI', 11, 'bold'),
                       foreground=Colors.PRIMARY, background=Colors.LIGHTER)
        
        # Boutons
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.configure('Primary.TButton', background=Colors.PRIMARY, 
                       foreground='white', borderwidth=0, padding=10)
        style.map('Primary.TButton',
                 background=[('active', Colors.PRIMARY_HOVER), ('pressed', '#1e40af')])
        
        style.configure('Success.TButton', background=Colors.SUCCESS, 
                       foreground='white', borderwidth=0, padding=10)
        style.map('Success.TButton',
                 background=[('active', '#15803d'), ('pressed', '#166534')])
        
        # Entry - avec bordure visible
        style.configure('TEntry', font=('Segoe UI', 10), padding=10, 
                       fieldbackground='white', foreground=Colors.DARK)
        style.configure('TCombobox', font=('Segoe UI', 10), padding=8,
                       fieldbackground='white', foreground=Colors.DARK)
        
        # Notebook
        style.configure('TNotebook', background=Colors.LIGHT, borderwidth=0)
        style.configure('TNotebook.Tab', font=('Segoe UI', 11, 'bold'),
                       padding=[20, 12])
        style.map('TNotebook.Tab',
                 background=[('selected', Colors.LIGHTER), ('', '#e5e7eb')])
        
        # Treeview avec meilleur styling
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=32,
                       background=Colors.LIGHTER, foreground=Colors.DARK,
                       fieldbackground=Colors.LIGHTER, borderwidth=1)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'),
                       background=Colors.PRIMARY, foreground='white', 
                       borderwidth=0, padding=10)
        style.map('Treeview.Heading', background=[('active', '#1d4ed8')])
        style.map('Treeview', background=[('selected', '#dbeafe')],
                 foreground=[('selected', Colors.DARK)])
        
    def create_interface(self):
        """Crée l'interface principale"""
        # Header
        self.create_header()
        
        # Contenu
        content = ttk.Frame(self.root, style='Content.TFrame')
        content.pack(fill='both', expand=True)
        
        # Notebook
        self.create_notebook(content)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Crée le header"""
        header = tk.Frame(self.root, bg=Colors.PRIMARY, height=100)
        header.pack(side='top', fill='x')
        header.pack_propagate(False)
        
        content = tk.Frame(header, bg=Colors.PRIMARY)
        content.pack(fill='both', expand=True, padx=40, pady=20)
        
        title = tk.Label(content, text="🎬 CINÉMA DELUXE",
                        font=('Segoe UI', 32, 'bold'),
                        fg='white', bg=Colors.PRIMARY)
        title.pack(anchor='w')
        
        subtitle = tk.Label(content, text="Réservez vos places facilement",
                           font=('Segoe UI', 11),
                           fg='white', bg=Colors.PRIMARY)
        subtitle.pack(anchor='w')
        
    def create_notebook(self, parent):
        """Crée les onglets"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_seances_tab(self.notebook)
        self.create_historique_tab(self.notebook)
        self.create_stats_tab(self.notebook)
        self.create_manager_tab(self.notebook)
    
    def switch_to_seances_tab(self):
        """Change vers l'onglet Séances et l'actualise"""
        self.load_seances_beautifully()
        self.notebook.select(0)  # L'onglet Séances est à l'index 0
    
    def switch_to_salles_tab(self):
        """Change vers l'onglet Manager Salles"""
        # L'onglet Manager est à l'index 3, puis Salles est le 3e sous-onglet
        self.notebook.select(3)  # Aller au Manager
        # On suppose que le manager_notebook est accessible
        if hasattr(self, 'manager_notebook'):
            self.manager_notebook.select(2)  # Salles est à l'index 2
        
    def create_seances_tab(self, notebook):
        """Onglet des séances - Design moderne avec film selector et sidebar"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='📅 Séances')
        
        # Header avec titre dynamique
        self.seances_title_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        self.seances_title_frame.pack(fill='x', padx=20, pady=20)
        
        self.seances_title_label = tk.Label(self.seances_title_frame, text='Séances d\'Aujourd\'hui',
                        font=('Segoe UI', 20, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        self.seances_title_label.pack(side='left', fill='x', expand=True)
        
        ttk.Button(self.seances_title_frame, text='🔄 Actualiser',
                  command=self.load_seances_beautifully,
                  style='Primary.TButton').pack(side='right')
        
        # Main container avec sidebar
        main_container = tk.Frame(frame, bg=Colors.LIGHTER)
        main_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # GAUCHE: Container scrollable principal
        left_container = tk.Frame(main_container, bg=Colors.LIGHTER)
        left_container.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Canvas scrollable pour les séances du jour
        canvas = tk.Canvas(left_container, bg=Colors.LIGHTER, relief='flat', 
                          highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(left_container, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.LIGHTER)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Sélecteur de film
        film_selector = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
        film_selector.pack(fill='x', padx=10, pady=(0, 20))
        
        tk.Label(film_selector, text='Sélectionner un Film',
                font=('Segoe UI', 12, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=15, pady=(10, 5))
        
        self.seances_film_selector = ttk.Combobox(film_selector, state='readonly', width=50)
        self.seances_film_selector['values'] = [f.titre for f in self.service.films]
        self.seances_film_selector.pack(fill='x', padx=15, pady=(0, 15))
        self.seances_film_selector.bind('<<ComboboxSelected>>', 
                                        lambda e: self.load_seances_beautifully())
        
        # Container pour les séances du jour
        self.seances_display_frame = tk.Frame(scrollable_frame, bg=Colors.LIGHTER)
        self.seances_display_frame.pack(fill='both', expand=True, padx=10)
        
        # DROITE: Sidebar avec autres jours
        sidebar = tk.Frame(main_container, bg='white', relief='solid', bd=1, width=200)
        sidebar.pack(side='right', fill='y', padx=(15, 0))
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text='Autres Jours',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.PRIMARY, bg='white').pack(fill='x', padx=10, pady=(10, 5))
        
        # Container pour les jours
        self.sidebar_days_frame = tk.Frame(sidebar, bg='white')
        self.sidebar_days_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.load_seances_beautifully()
        
    def load_seances_beautifully(self, event=None):
        """Charge et affiche les séances de manière élégante"""
        # Nettoyer l'affichage principal
        for widget in self.seances_display_frame.winfo_children():
            widget.destroy()
        
        # Nettoyer la sidebar
        for widget in self.sidebar_days_frame.winfo_children():
            widget.destroy()
        
        # Obtenir le film sélectionné
        film_titre = self.seances_film_selector.get()
        if not film_titre:
            empty_label = tk.Label(self.seances_display_frame,
                                  text='Sélectionnez un film',
                                  font=('Segoe UI', 14),
                                  fg=Colors.SECONDARY,
                                  bg=Colors.LIGHTER)
            empty_label.pack(pady=50)
            return
        
        # Trouver le film
        film_selectionnee = None
        for f in self.service.films:
            if f.titre == film_titre:
                film_selectionnee = f
                break
        
        if not film_selectionnee:
            return
        
        # Obtenir les dates
        from datetime import datetime, timedelta
        aujourd_hui = datetime.now().date()
        demain = aujourd_hui + timedelta(days=1)
        surdemain = aujourd_hui + timedelta(days=2)
        
        # Déterminer quelle date afficher
        if self._selected_seances_date is not None:
            date_affichee = self._selected_seances_date
            date_label = date_affichee.strftime('%d/%m/%Y')
        else:
            date_affichee = aujourd_hui
            date_label = "Séances d'aujourd'hui"
        
        # Afficher les séances de la date sélectionnée
        self._display_seances_for_date(self.seances_display_frame, 
                                      film_selectionnee, date_affichee, 
                                      date_label)
        
        # Afficher la sidebar avec les autres jours
        self._display_sidebar_days(film_selectionnee, demain, surdemain)
        
    def _display_seances_for_date(self, parent_frame, film, date, title):
        """Affiche les séances d'un film pour une date donnée"""
        # Filtrer les séances pour cette date
        seances_du_jour = [s for s in self.service.get_toutes_seances()
                          if s.film == film and s.horaire.date() == date]
        seances_du_jour.sort(key=lambda s: s.horaire.time())
        
        if not seances_du_jour:
            no_seance = tk.Label(parent_frame,
                                text=f'Aucune séance pour ce film ce jour',
                                font=('Segoe UI', 13),
                                fg=Colors.WARNING,
                                bg=Colors.LIGHTER)
            no_seance.pack(pady=50)
            return
        
        # Grouper par horaire
        seances_par_horaire = {}
        for seance in seances_du_jour:
            horaire_str = seance.horaire.strftime('%H:%M')
            if horaire_str not in seances_par_horaire:
                seances_par_horaire[horaire_str] = []
            seances_par_horaire[horaire_str].append(seance)
        
        # Afficher chaque horaire
        for horaire_str in sorted(seances_par_horaire.keys()):
            seances = seances_par_horaire[horaire_str]
            
            # Header de l'horaire
            horaire_header = tk.Frame(parent_frame, bg=Colors.PRIMARY)
            horaire_header.pack(fill='x', padx=0, pady=(15, 0))
            
            tk.Label(horaire_header, text=f'  {horaire_str}',
                    font=('Segoe UI', 14, 'bold'),
                    fg='white', bg=Colors.PRIMARY).pack(side='left', padx=10, pady=10)
            
            # Salles pour cet horaire
            salles_frame = tk.Frame(parent_frame, bg='white', relief='solid', bd=1)
            salles_frame.pack(fill='x', padx=0, pady=(0, 10))
            
            for seance in seances:
                # Card de salle
                salle_card = tk.Frame(salles_frame, bg=Colors.LIGHT, relief='solid', bd=1)
                salle_card.pack(fill='x', padx=10, pady=10)
                
                # Info de la salle
                info_frame = tk.Frame(salle_card, bg=Colors.LIGHT)
                info_frame.pack(fill='x', padx=15, pady=10)
                
                salle_name = tk.Label(info_frame, text=f'{seance.salle.nom}',
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=Colors.DARK, bg=Colors.LIGHT)
                salle_name.pack(side='left', padx=(0, 20))
                
                type_label = tk.Label(info_frame, text=f'Type: {seance.salle.type_salle.value}',
                                     font=('Segoe UI', 10),
                                     fg=Colors.SECONDARY, bg=Colors.LIGHT)
                type_label.pack(side='left', padx=(0, 20))
                
                # Capacité et places
                dispo_text = f'{seance.places_disponibles}/{seance.salle.capacite} places'
                if seance.places_disponibles == 0:
                    dispo_color = Colors.DANGER
                    dispo_text = 'COMPLET'
                elif seance.places_disponibles < 5:
                    dispo_color = Colors.WARNING
                else:
                    dispo_color = Colors.SUCCESS
                
                dispo_label = tk.Label(info_frame, text=dispo_text,
                                      font=('Segoe UI', 10, 'bold'),
                                      fg=dispo_color, bg=Colors.LIGHT)
                dispo_label.pack(side='right', padx=(20, 0))
                
                # Barre de progression pour les places
                progress_frame = tk.Frame(salle_card, bg=Colors.LIGHT)
                progress_frame.pack(fill='x', padx=15, pady=(0, 10))
                
                occupied_ratio = seance.places_reservees / seance.salle.capacite
                progress_width = int(300 * occupied_ratio)
                
                # Barre
                bar_bg = tk.Frame(progress_frame, bg='#e5e7eb', height=8, width=300)
                bar_bg.pack(fill='x')
                bar_bg.pack_propagate(False)
                
                bar_fill = tk.Frame(bar_bg, bg=dispo_color, height=8, width=progress_width)
                bar_fill.pack(side='left', fill='y')
                
                # Bouton de réservation
                if seance.places_disponibles > 0:
                    btn_frame = tk.Frame(salle_card, bg=Colors.LIGHT)
                    btn_frame.pack(fill='x', padx=15, pady=(10, 0))
                    
                    def make_reserve_handler(s):
                        def on_reserve():
                            self.seance_selectionnee = s
                            self.open_quick_reservation(s)
                        return on_reserve
                    
                    ttk.Button(btn_frame, text='RESERVER',
                             command=make_reserve_handler(seance),
                             style='Success.TButton').pack(side='right')
    
    def _display_sidebar_days(self, film, day1, day2):
        """Affiche tous les 7 jours dans la sidebar - cliquables"""
        # PATCH: On récupère toutes les séances pour le film une seule fois,
        # avec la reconstruction de l'occupation, pour corriger les bugs de
        # données et améliorer les performances.
        all_seances_for_film = [s for s in self._get_seances_with_rebuilt_occupancy() if s.film == film]

        from datetime import datetime, timedelta
        
        aujourd_hui = datetime.now().date()
        
        # Ajouter aujourd'hui en haut
        day_card = tk.Frame(self.sidebar_days_frame, bg='white', relief='solid', bd=1, cursor='hand2')
        day_card.pack(fill='x', pady=(0, 10))
        
        def make_click_handler(selected_day, film_obj):
            def on_click(event):
                # Vider l'affichage principal avant de redessiner les séances du jour cliqué.
                # C'est le correctif clé pour n'afficher que les séances du jour sélectionné.
                for widget in self.seances_display_frame.winfo_children():
                    widget.destroy()

                self._selected_seances_date = selected_day
                # Mettre à jour le titre
                if selected_day == aujourd_hui:
                    titre = "Séances d'Aujourd'hui"
                elif selected_day == aujourd_hui + timedelta(days=1):
                    titre = "Séances de Demain"
                else:
                    jour_name = selected_day.strftime('%A')
                    jour_name_fr = {'Monday': 'Lundi', 'Tuesday': 'Mardi', 'Wednesday': 'Mercredi',
                                   'Thursday': 'Jeudi', 'Friday': 'Vendredi', 'Saturday': 'Samedi',
                                   'Sunday': 'Dimanche'}.get(jour_name, jour_name)
                    titre = f"Séances du {jour_name_fr} {selected_day.strftime('%d/%m/%Y')}"
                
                self.seances_title_label.config(text=titre)
                self._display_seances_for_date(self.seances_display_frame, 
                                              film_obj, selected_day, titre)
            return on_click
        
        # Jour d'aujourd'hui
        day_card.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        date_str = aujourd_hui.strftime('%d/%m')
        day_label = tk.Label(day_card, text=f'Aujourd\'hui\n{date_str}',
                            font=('Segoe UI', 10, 'bold'),
                            fg=Colors.PRIMARY, bg='white', cursor='hand2')
        day_label.pack(fill='x', padx=8, pady=(8, 5))
        day_label.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        # Compter les séances
        seances_jour = [s for s in all_seances_for_film if s.horaire.date() == aujourd_hui]

        nb_seances = len(seances_jour)
        count_label = tk.Label(day_card, text=f'{nb_seances} séance(s)',
                              font=('Segoe UI', 9),
                              fg=Colors.SECONDARY, bg='white', cursor='hand2')
        count_label.pack(fill='x', padx=8, pady=(0, 8))
        count_label.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        # Horaires
        horaires = sorted(set(s.horaire.strftime('%H:%M') for s in seances_jour))
        horaires_str = ', '.join(horaires) if horaires else 'Aucune'
        
        horaires_label = tk.Label(day_card, text=horaires_str,
                                 font=('Segoe UI', 8),
                                 fg=Colors.SECONDARY, bg='white', cursor='hand2')
        horaires_label.pack(fill='x', padx=8, pady=(0, 8))
        horaires_label.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        # Les 6 jours suivants
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        for i in range(1, 7):  # Les 6 jours suivants
            day = aujourd_hui + timedelta(days=i)
            jour_num = day.weekday()  # 0=Monday, 6=Sunday
            jour_name = day_names[jour_num]
            
            # Card du jour - cliquable
            day_card = tk.Frame(self.sidebar_days_frame, bg='#f3f4f6', relief='solid', bd=1, cursor='hand2')
            day_card.pack(fill='x', pady=(0, 10))
            
            # Bind click sur toute la card
            day_card.bind('<Button-1>', make_click_handler(day, film))
            
            # Jour et date
            date_str = day.strftime('%d/%m')
            day_label = tk.Label(day_card, text=f'{jour_name}\n{date_str}',
                                font=('Segoe UI', 10, 'bold'),
                                fg=Colors.PRIMARY, bg='#f3f4f6', cursor='hand2')
            day_label.pack(fill='x', padx=8, pady=(8, 5))
            day_label.bind('<Button-1>', make_click_handler(day, film))
            
            # Compter les séances
            seances_jour = [s for s in all_seances_for_film if s.horaire.date() == day]

            nb_seances = len(seances_jour)
            count_label = tk.Label(day_card, text=f'{nb_seances} séance(s)',
                                  font=('Segoe UI', 9),
                                  fg=Colors.SECONDARY, bg='#f3f4f6', cursor='hand2')
            count_label.pack(fill='x', padx=8, pady=(0, 8))
            count_label.bind('<Button-1>', make_click_handler(day, film))
            
            # Horaires
            horaires = sorted(set(s.horaire.strftime('%H:%M') for s in seances_jour))
            horaires_str = ', '.join(horaires) if horaires else 'Aucune'
            
            horaires_label = tk.Label(day_card, text=horaires_str,
                                     font=('Segoe UI', 8),
                                     fg=Colors.DARK, bg='#f3f4f6',
                                     wraplength=180, justify='left', cursor='hand2')
            horaires_label.pack(fill='x', padx=8, pady=(0, 8))
            horaires_label.bind('<Button-1>', make_click_handler(day, film))
        
    def create_reservation_tab(self, notebook):
        """Onglet de réservation"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🎫 Réserver')
        canvas = tk.Canvas(frame, bg=Colors.LIGHTER, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set, bg=Colors.LIGHTER)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        title = tk.Label(scrollable, text='Creer une Reservation',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=30, pady=(30, 25))
        
        # Section 1: Choisir un film
        self.create_section(scrollable, '1. Choisir un Film')
        
        film_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        film_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        tk.Label(film_frame, text='Film',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=15, pady=(15, 5))
        self.reservation_film_combo = ttk.Combobox(film_frame, state='readonly', width=50)
        self.reservation_film_combo['values'] = [f.titre for f in self.service.films]
        self.reservation_film_combo.pack(fill='x', padx=15, pady=(0, 15))
        self.reservation_film_combo.bind('<<ComboboxSelected>>', self.on_reservation_film_select)
        
        # Section 2: Choisir une seance (date/heure)
        self.create_section(scrollable, '2. Choisir une Seance (Date et Heure)')
        
        seance_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        seance_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        tk.Label(seance_frame, text='Seance disponible',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=15, pady=(15, 5))
        
        list_frame = tk.Frame(seance_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        self.seances_listbox = tk.Listbox(list_frame, height=5,
                                          font=('Segoe UI', 10),
                                          bg='white', relief='solid',
                                          bd=1, highlightthickness=0,
                                          selectmode=tk.SINGLE,
                                          activestyle='none')
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient='vertical',
                                       command=self.seances_listbox.yview)
        self.seances_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.seances_listbox.pack(side='left', fill='both', expand=True)
        list_scrollbar.pack(side='right', fill='y')
        
        self.seances_listbox.bind('<<ListboxSelect>>', self.on_seance_select)
        
        # Section 3: Infos
        self.create_section(scrollable, '3. Vos Informations')
        
        info_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        # Nom
        tk.Label(info_frame, text='Nom Complet',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=15, pady=(15, 5))
        self.nom_entry = ttk.Entry(info_frame, width=40)
        self.nom_entry.pack(fill='x', padx=15, pady=(0, 15))
        self.nom_entry.bind('<KeyRelease>', self.update_recap)
        
        # Places et Tarif sur la meme ligne
        row_frame = tk.Frame(info_frame, bg='white')
        row_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        col1 = tk.Frame(row_frame, bg='white')
        col1.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        tk.Label(col1, text='Nombre de Places',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 5))
        self.places_spinbox = ttk.Spinbox(col1, from_=1, to=10, width=8)
        self.places_spinbox.set('1')
        self.places_spinbox.pack(anchor='w')
        self.places_spinbox.bind('<KeyRelease>', self.update_recap)
        
        col2 = tk.Frame(row_frame, bg='white')
        col2.pack(side='left', fill='x', expand=True, padx=(15, 0))
        
        tk.Label(col2, text='Tarif',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 5))
        self.tarif_combo = ttk.Combobox(col2, state='readonly', width=20)
        tarifs = self.service.tarifs
        self.tarif_combo['values'] = [str(t) for t in tarifs]
        if tarifs:
            self.tarif_combo.set(str(tarifs[0]))
        self.tarif_combo.pack(fill='x')
        self.tarif_combo.bind('<<ComboboxSelected>>', self.update_recap)
        
        # Section 4: Recapitulatif
        self.create_section(scrollable, '4. Recapitulatif')
        
        recap_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        recap_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        self.recap_label = tk.Label(recap_frame,
                                   text='Selectionnez un film et une seance...',
                                   font=('Courier', 10),
                                   fg=Colors.SECONDARY,
                                   bg='white', justify='left',
                                   wraplength=500,
                                   padx=15, pady=15)
        self.recap_label.pack(fill='both', expand=True)
        
        # Bouton reserver
        btn_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        btn_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        ttk.Button(btn_frame, text='RESERVER',
                  command=self.faire_reservation,
                  style='Success.TButton').pack(side='right', fill='x', expand=True)
        
        self.load_seances_reservation()
        
    def create_historique_tab(self, notebook):
        """Onglet historique"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='📋 Historique')
        
        # Header
        header = tk.Frame(frame, bg=Colors.LIGHTER)
        header.pack(fill='x', padx=20, pady=20)
        
        title = tk.Label(header, text='Historique des Réservations',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(side='left', fill='x', expand=True)
        
        btn_frame = tk.Frame(header, bg=Colors.LIGHTER)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text='🔄 Actualiser',
                  command=self.load_reservations,
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text='🗑️ Effacer',
                  command=self.clear_reservations).pack(side='left')
        
        # Contenu
        content_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.reservations_text = scrolledtext.ScrolledText(
            content_frame, height=24, font=('Consolas', 10),
            bg='white', relief='solid', bd=1,
            wrap=tk.WORD, padx=10, pady=10)
        self.reservations_text.pack(fill='both', expand=True)
        
        self.load_reservations()
        
    def create_stats_tab(self, notebook):
        """Onglet statistiques"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='📊 Statistiques')
        
        # Header
        header = tk.Frame(frame, bg=Colors.LIGHTER)
        header.pack(fill='x', padx=20, pady=20)
        
        title = tk.Label(header, text='Statistiques',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(side='left', fill='x', expand=True)
        
        ttk.Button(header, text='🔄 Actualiser',
                  command=self.load_stats,
                  style='Primary.TButton').pack(side='right')
        
        # Contenu
        content_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.stats_text = scrolledtext.ScrolledText(
            content_frame, height=24, font=('Consolas', 10),
            bg='white', relief='solid', bd=1,
            wrap=tk.WORD, padx=10, pady=10)
        self.stats_text.pack(fill='both', expand=True)
        
        self.load_stats()


    def create_manager_tab(self, notebook):
        """Onglet manager pour gérer le cinéma"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='⚙️ Manager')
        
        # Notebook interne pour les sous-sections
        self.manager_notebook = ttk.Notebook(frame)
        self.manager_notebook.pack(fill='both', expand=True, padx=20, pady=20)
       
        try:
            self.create_mdp(self.manager_notebook)
        except Exception:
            pass

    def create_mdp(self, notebook) : 
        """Onglet de saisie du mot de passe manager."""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🔒 MDP')

        content = tk.Frame(frame, bg=Colors.LIGHTER)
        content.pack(fill='both', expand=True, padx=30, pady=30)

        tk.Label(content, text="Accès Manager",
                font=('Segoe UI', 16, 'bold'), fg=Colors.PRIMARY, bg=Colors.LIGHTER).pack(anchor='w')

        tk.Label(content, text="Entrez le mot de passe (1234) :",
                font=('Segoe UI', 11), fg=Colors.DARK, bg=Colors.LIGHTER).pack(anchor='w', pady=(15, 5))

        self.mgr_mdp_entry = ttk.Entry(content, width=30, show='*')
        self.mgr_mdp_entry.pack(anchor='w')

        def check_mdp(event=None):
            from tkinter import messagebox
            val = (self.mgr_mdp_entry.get() or '').strip()
            if val == '1234':
                try:
                    messagebox.showinfo('Succès', 'Mot de passe accepté')
                except Exception:
                    pass

                # Ajouter les onglets manager si pas déjà faits
                if not getattr(self, '_manager_unlocked', False):
                    try:
                        self.create_manager_films_tab(self.manager_notebook)
                        self.create_manager_seances_tab(self.manager_notebook)
                        self.create_manager_salles_tab(self.manager_notebook)
                        self.create_manager_tarifs_tab(self.manager_notebook)
                        self.create_manager_rapports_tab(self.manager_notebook)

                        # Charger les listes initiales (silencieux en cas d'erreur)
                        try:
                            self.load_manager_films_list()
                            self.load_manager_seances_list()
                            self.load_manager_salles_list()
                            self.load_manager_tarifs_list()
                        except Exception:
                            pass

                        self._manager_unlocked = True
                        # Sélectionner le premier onglet manager ajouté
                        try:
                            self.manager_notebook.select(1)
                        except Exception:
                            pass
                        # Supprimer l'onglet MDP
                        try:
                            self.manager_notebook.forget(frame)
                        except Exception:
                            pass
                    except Exception:
                        pass
                return 1
            else:
                try:
                    messagebox.showerror('Erreur', 'Mot de passe incorrect')
                except Exception:
                    pass
                return 0

        btn_frame = tk.Frame(content, bg=Colors.LIGHTER)
        btn_frame.pack(fill='x', pady=(20, 0))

        validate_btn = ttk.Button(btn_frame, text='Valider', command=check_mdp, style='Primary.TButton')
        validate_btn.pack(side='left')

        # Lier la touche Entrée au contrôle
        self.mgr_mdp_entry.bind('<Return>', lambda e: check_mdp())
        
    def create_manager_films_tab(self, notebook):
        """Manager: Gestion des films"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🎬 Films')
        
        # Canvas avec scrollbar
        canvas = tk.Canvas(frame, bg=Colors.LIGHTER, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set, bg=Colors.LIGHTER)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        title = tk.Label(scrollable, text='📽️ Créer un Film',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=30, pady=(30, 30))
        
        # Form Card
        form_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        # Nom du film
        tk.Label(form_frame, text='📽️ Titre du film',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_film_nom = ttk.Entry(form_frame, width=50)
        self.mgr_film_nom.pack(fill='x', padx=20, pady=(0, 20))
        
        # Durée et Genre
        row1_frame = tk.Frame(form_frame, bg='white')
        row1_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        col1 = tk.Frame(row1_frame, bg='white')
        col1.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        tk.Label(col1, text='⏱️ Durée (min)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_film_duree = ttk.Spinbox(col1, from_=30, to=300, width=12)
        self.mgr_film_duree.set('120')
        self.mgr_film_duree.pack(anchor='w')
        
        col2 = tk.Frame(row1_frame, bg='white')
        col2.pack(side='right', fill='x', expand=True)
        
        tk.Label(col2, text='🎭 Genre',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_film_genre = ttk.Combobox(col2, state='readonly', width=15)
        self.mgr_film_genre['values'] = [s.value for s in StyleFilm]
        if self.mgr_film_genre['values']:
            self.mgr_film_genre.set(self.mgr_film_genre['values'][0])
        self.mgr_film_genre.pack(fill='x')
        
        # Note et Réalisateur
        row2_frame = tk.Frame(form_frame, bg='white')
        row2_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        col3 = tk.Frame(row2_frame, bg='white')
        col3.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        tk.Label(col3, text='⭐ Note (0-10)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_film_note = ttk.Spinbox(col3, from_=0, to=10, increment=0.5, width=12)
        self.mgr_film_note.set('7.0')
        self.mgr_film_note.pack(anchor='w')
        
        col4 = tk.Frame(row2_frame, bg='white')
        col4.pack(side='right', fill='x', expand=True)
        
        
        
        # Bouton
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(btn_frame, text='➕ Ajouter Film',
                  command=self.mgr_creer_film,
                  style='Success.TButton').pack(side='right')
        
        # SECTION: Liste des films
        list_title = tk.Label(scrollable, text='📽️ Films Existants',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=30, pady=(30, 20))
        
        # Listbox des films
        tree_frame = tk.Frame(scrollable, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
        
        cols = ('Titre', 'Durée', 'Genre', 'Note')
        self.mgr_films_treeview = ttk.Treeview(tree_frame, columns=cols, show='headings', style='Treeview')
        
        for col in cols:
            self.mgr_films_treeview.heading(col, text=col)
        
        self.mgr_films_treeview.column('Titre', width=250)
        self.mgr_films_treeview.column('Durée', width=100, anchor='center')
        self.mgr_films_treeview.column('Genre', width=120)
        self.mgr_films_treeview.column('Note', width=80, anchor='center')
        
        scrollbar_films = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mgr_films_treeview.yview)
        self.mgr_films_treeview.configure(yscrollcommand=scrollbar_films.set)
        
        self.mgr_films_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_films.pack(side='right', fill='y')
        
        # Boutons d'action pour les films
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_film, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_film).pack(side='left')
        
    def create_manager_seances_tab(self, notebook):
        """Manager: Gestion des séances"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🎥 Séances')
        
        # Canvas avec scrollbar pour rendre la page scrollable
        canvas = tk.Canvas(frame, bg=Colors.LIGHTER, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set, bg=Colors.LIGHTER)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        title = tk.Label(scrollable, text='📅 Créer une Séance',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 30))
        
        # Form
        form_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=40, pady=30)
        
        # Film
        tk.Label(form_frame, text='🎬 Film',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_seance_film = ttk.Combobox(form_frame, state='readonly', width=40)
        self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
        self.mgr_seance_film.pack(fill='x', padx=20, pady=(0, 20))
        
        # Salle et Date
        row1 = tk.Frame(form_frame, bg='white')
        row1.pack(fill='x', padx=20, pady=(0, 20))
        
        c1 = tk.Frame(row1, bg='white')
        c1.pack(side='left', fill='x', expand=True, padx=(0, 15))
        tk.Label(c1, text='🏛️ Salle', font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_seance_salle = ttk.Combobox(c1, state='readonly', width=15)
        self.mgr_seance_salle['values'] = [s.nom for s in self.service.salles]
        self.mgr_seance_salle.pack(fill='x')
        
        c2 = tk.Frame(row1, bg='white')
        c2.pack(side='right', fill='x', expand=True)
        tk.Label(c2, text='📅 Date (YYYY-MM-DD)', font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_seance_date = ttk.Entry(c2, width=20)
        self.mgr_seance_date.pack(fill='x')
        
        # Heure
        tk.Label(form_frame, text='🕐 Horaire (HH:MM)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(0, 8))
        self.mgr_seance_heure = ttk.Entry(form_frame, width=20)
        self.mgr_seance_heure.pack(anchor='w', padx=20, pady=(0, 20))
        
        # Bouton
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        ttk.Button(btn_frame, text='➕ Créer Séance',
                  command=self.mgr_creer_seance,
                  style='Success.TButton').pack(side='right')
        
        # SECTION: Liste des séances
        list_title = tk.Label(scrollable, text='📅 Séances Existantes',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=20, pady=(30, 20))
        
        # Listbox des séances
        tree_frame = tk.Frame(scrollable, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=40, pady=(0, 20))
        
        # Colonnes pour les données des séances. Le film et la date sont dans l'arborescence.
        cols = ('Salle', 'Horaire', 'Places')
        self.mgr_seances_treeview = ttk.Treeview(tree_frame, columns=cols, show='tree headings')
        
        # Colonne 0 : L'arborescence Jour -> Film
        self.mgr_seances_treeview.heading('#0', text='Jour / Film')
        self.mgr_seances_treeview.column('#0', width=300, minwidth=250, stretch=tk.NO)
        
        # Autres colonnes
        self.mgr_seances_treeview.heading('Salle', text='Salle')
        self.mgr_seances_treeview.column('Salle', width=200, anchor='w')
        self.mgr_seances_treeview.heading('Horaire', text='Horaire')
        self.mgr_seances_treeview.column('Horaire', width=100, anchor='center')
        self.mgr_seances_treeview.heading('Places', text='Places')
        self.mgr_seances_treeview.column('Places', width=120, anchor='center')
        
        scrollbar_seances = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mgr_seances_treeview.yview)
        self.mgr_seances_treeview.configure(yscrollcommand=scrollbar_seances.set)
        
        self.mgr_seances_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_seances.pack(side='right', fill='y')
        
        # Boutons d'action pour les séances
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_seance,
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_seance).pack(side='left')
        
    def create_manager_salles_tab(self, notebook):
        """Manager: Gestion des salles"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🏛️ Salles')
        
        # Canvas avec scrollbar pour rendre la page scrollable
        canvas = tk.Canvas(frame, bg=Colors.LIGHTER, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable.bind('<Configure>',
                       lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set, bg=Colors.LIGHTER)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        title = tk.Label(scrollable, text='🏢 Créer une Salle',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 30))
        form_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=40, pady=30)
        
        # Nom
        tk.Label(form_frame, text='📍 Nom de la salle',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_salle_nom = ttk.Entry(form_frame, width=40)
        self.mgr_salle_nom.pack(fill='x', padx=20, pady=(0, 20))
        
        # Capacité et Type
        row = tk.Frame(form_frame, bg='white')
        row.pack(fill='x', padx=20, pady=(0, 20))
        
        c1 = tk.Frame(row, bg='white')
        c1.pack(side='left', fill='x', expand=True, padx=(0, 15))
        tk.Label(c1, text='🎫 Capacité', font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_salle_capacite = ttk.Spinbox(c1, from_=10, to=500, width=12)
        self.mgr_salle_capacite.set('100')
        self.mgr_salle_capacite.pack(anchor='w')
        
        c2 = tk.Frame(row, bg='white')
        c2.pack(side='right', fill='x', expand=True)
        tk.Label(c2, text='📺 Type', font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_salle_type = ttk.Combobox(c2, state='readonly', width=15)
        self.mgr_salle_type['values'] = [t.value for t in TypeSalle]
        if self.mgr_salle_type['values']:
            self.mgr_salle_type.set(self.mgr_salle_type['values'][0])
        self.mgr_salle_type.pack(fill='x')
        
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        ttk.Button(btn_frame, text='➕ Ajouter Salle',
                  command=self.mgr_creer_salle,
                  style='Success.TButton').pack(side='right')
        
        # SECTION: Liste des salles
        list_title = tk.Label(scrollable, text='🏛️ Salles Existantes',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=20, pady=(30, 20))
        
        # Listbox des salles
        tree_frame = tk.Frame(scrollable, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=40, pady=(0, 20))
        
        cols = ('Numéro', 'Nom', 'Capacité', 'Type')
        self.mgr_salles_treeview = ttk.Treeview(tree_frame, columns=cols, show='headings')
        
        for col in cols:
            self.mgr_salles_treeview.heading(col, text=col)
        
        self.mgr_salles_treeview.column('Numéro', width=80, anchor='center')
        self.mgr_salles_treeview.column('Nom', width=200)
        self.mgr_salles_treeview.column('Capacité', width=100, anchor='center')
        self.mgr_salles_treeview.column('Type', width=150)
        
        scrollbar_salles = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mgr_salles_treeview.yview)
        self.mgr_salles_treeview.configure(yscrollcommand=scrollbar_salles.set)
        
        self.mgr_salles_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_salles.pack(side='right', fill='y')
        
        # Boutons d'action pour les salles
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_salle, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_salle).pack(side='left')
        
    def create_manager_tarifs_tab(self, notebook):
        """Manager: Gestion des tarifs"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='💰 Tarifs')
        
        # Canvas scrollable
        canvas = tk.Canvas(frame, bg=Colors.LIGHTER, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set, bg=Colors.LIGHTER)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Formulaire de création
        title = tk.Label(scrollable, text='💰 Créer un Tarif',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 30))
        
        form_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=40, pady=30)
        
        tk.Label(form_frame, text='Libellé du tarif',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_tarif_label = ttk.Entry(form_frame, width=40)
        self.mgr_tarif_label.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(form_frame, text='Coefficient (ex: 0.8 pour -20%)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(0, 8))
        self.mgr_tarif_coeff = ttk.Spinbox(form_frame, from_=0.1, to=2.0, increment=0.1, width=15)
        self.mgr_tarif_coeff.set('1.0')
        self.mgr_tarif_coeff.pack(anchor='w', padx=20, pady=(0, 20))
        
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        ttk.Button(btn_frame, text='➕ Ajouter Tarif',
                  command=self.mgr_creer_tarif,
                  style='Success.TButton').pack(side='right')

        # Liste des tarifs
        list_title = tk.Label(scrollable, text='💰 Tarifs Existants',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=20, pady=(30, 20))
        
        tree_frame = tk.Frame(scrollable, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=40, pady=(0, 20))
        
        cols = ('Libellé', 'Coefficient', 'Exemple Prix')
        self.mgr_tarifs_treeview = ttk.Treeview(tree_frame, columns=cols, show='headings')
        
        for col in cols:
            self.mgr_tarifs_treeview.heading(col, text=col)
        
        self.mgr_tarifs_treeview.column('Libellé', width=250)
        self.mgr_tarifs_treeview.column('Coefficient', width=120, anchor='center')
        self.mgr_tarifs_treeview.column('Exemple Prix', width=150, anchor='center')
        
        scrollbar_tarifs = ttk.Scrollbar(tree_frame, orient='vertical', command=self.mgr_tarifs_treeview.yview)
        self.mgr_tarifs_treeview.configure(yscrollcommand=scrollbar_tarifs.set)
        
        self.mgr_tarifs_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_tarifs.pack(side='right', fill='y')
        
        # Boutons d'action
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_tarif, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_tarif).pack(side='left')
        
    def create_manager_rapports_tab(self, notebook):
        """Manager: Rapports et analytiques"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='📊 Rapports')
        
        title = tk.Label(frame, text='📈 Rapports du Cinéma',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 0))
        
        btn_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        btn_frame.pack(fill='x', padx=20, pady=(10, 20))
        ttk.Button(btn_frame, text='🔄 Actualiser',
                  command=self.load_rapports,
                  style='Primary.TButton').pack(side='right')
        
        content_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.rapports_text = scrolledtext.ScrolledText(
            content_frame, height=24, font=('Courier', 10),
            bg='white', relief='solid', bd=1, padx=10, pady=10)
        self.rapports_text.pack(fill='both', expand=True)
        
        self.load_rapports()
        
    def create_section(self, parent, title):
        """Crée une section avec meilleur style"""
        container = tk.Frame(parent, bg=Colors.LIGHTER)
        container.pack(fill='x', padx=30, pady=(25, 12))
        
        label = tk.Label(container, text=title,
                        font=('Segoe UI', 12, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        label.pack(anchor='w')
        
        # Ligne de séparation
        separator = tk.Frame(container, bg=Colors.BORDER, height=2)
        separator.pack(fill='x', pady=(8, 0))
        
    def create_footer(self):
        """Crée le footer"""
        footer = tk.Frame(self.root, bg=Colors.LIGHT, height=50)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        
        content = tk.Frame(footer, bg=Colors.LIGHT)
        content.pack(fill='both', expand=True, padx=40, pady=10)
        
        time_label = tk.Label(content,
                             text=f"⏰ {datetime.now().strftime('%d/%m/%Y - %H:%M')}",
                             font=('Segoe UI', 9),
                             fg=Colors.SECONDARY, bg=Colors.LIGHT)
        time_label.pack(side='left')
        
        version_label = tk.Label(content, text='✨ Cinéma v4.0',
                                font=('Segoe UI', 9, 'bold'),
                                fg=Colors.PRIMARY, bg=Colors.LIGHT)
        version_label.pack(side='right')
        
    def _get_seances_with_rebuilt_occupancy(self):
        """
        PATCH: Reconstruit l'état d'occupation des places pour chaque séance.
        Ceci est un correctif pour un bug où les objets Seance partagent leur état,
        entraînant des réservations incorrectes entre différentes séances/jours.
        La source de vérité est la liste globale des réservations.
        """
        all_seances = self.service.get_toutes_seances()
        
        # 1. Réinitialiser complètement l'état de chaque séance.
        for seance in all_seances:
            seance.places_occupees = set()
            seance.places_reservees = 0
            
        # 2. Reconstruire l'état à partir de la liste des réservations.
        for reservation in self.service.reservations:
            # S'assurer que la réservation a des numéros de place et une séance valide.
            # La modification du modèle Reservation garantit que `numeros_places` existe.
            if reservation.numeros_places and hasattr(reservation, 'seance'):
                # Mettre à jour l'objet séance correspondant.
                # Ceci suppose que reservation.seance est une référence à un objet dans all_seances.
                reservation.seance.places_occupees.update(reservation.numeros_places)
                # Mettre à jour le compteur de places réservées pour être cohérent.
                reservation.seance.places_reservees = len(reservation.seance.places_occupees)
                
        return all_seances

    def load_seances_reservation(self):
        """Charge la liste des films"""
        # Rien à faire ici maintenant, sera appelé au démarrage
        pass
    
    def on_reservation_film_select(self, event=None):
        """Gère la sélection du film"""
        film_titre = self.reservation_film_combo.get()
        if not film_titre:
            self.seances_listbox.delete(0, tk.END)
            self._seances_affichees = []  # Liste des seances pour referencing
            return
        
        # Trouver le film
        film_selectionnee = None
        for f in self.service.films:
            if f.titre == film_titre:
                film_selectionnee = f
                break
        
        if not film_selectionnee:
            return
        
        # Afficher les séances de ce film, groupées par date
        self.seances_listbox.delete(0, tk.END)
        self._seances_affichees = []  # Reset
        
        toutes_seances = self._get_seances_with_rebuilt_occupancy()
        seances_du_film = [s for s in toutes_seances if s.film == film_selectionnee]
        
        if not seances_du_film:
            self.seances_listbox.insert(tk.END, "Aucune séance pour ce film")
            return
        
        # Grouper par date
        seances_par_date = {}
        for seance in seances_du_film:
            date_str = seance.horaire.strftime('%d/%m/%Y')
            if date_str not in seances_par_date:
                seances_par_date[date_str] = []
            seances_par_date[date_str].append(seance)
        
        # Afficher groupé par date
        for date_str in sorted(seances_par_date.keys()):
            self.seances_listbox.insert(tk.END, f"--- {date_str} ---")
            self._seances_affichees.append(None)  # Header, pas une seance
            for seance in sorted(seances_par_date[date_str], key=lambda s: s.horaire):
                status = "COMPLET" if seance.est_complete else f"{seance.places_disponibles} places"
                self.seances_listbox.insert(tk.END,
                    f"  [{seance.horaire.strftime('%H:%M')}] Salle {seance.salle.nom} - {status}")
                self._seances_affichees.append(seance)  # Stocker la reference
                
    def on_seance_select(self, event):
        """Gère la sélection"""
        selection = self.seances_listbox.curselection()
        if selection:
            index_sel = selection[0]
            # Vérifier si c'est un header
            item = self.seances_listbox.get(index_sel)
            if item.startswith('---') or not item.strip():
                messagebox.showinfo('Info', 'Sélectionnez une séance spécifique')
                return
            
            # Récupérer la séance référencée
            if hasattr(self, '_seances_affichees') and index_sel < len(self._seances_affichees):
                seance = self._seances_affichees[index_sel]
                if seance is not None:
                    self.seance_selectionnee = seance
                    self.update_recap()
                else:
                    messagebox.showinfo('Info', 'Sélectionnez une séance spécifique')
            else:
                messagebox.showwarning('Erreur', 'Impossible de récupérer la séance')
            
    def update_recap(self, event=None):
        """Met à jour le récapitulatif"""
        if not self.seance_selectionnee:
            self.recap_label.config(text='Sélectionnez une séance...')
            return
            
        nom = self.nom_entry.get().strip()
        try:
            nb_places = int(self.places_spinbox.get())
        except:
            nb_places = 1
            
        tarif_text = self.tarif_combo.get()
        tarif = next((t for t in self.service.tarifs if str(t) == tarif_text), None)
        if not tarif:
            # Fallback au premier tarif si la sélection est invalide
            tarif = self.service.tarifs[0] if self.service.tarifs else None
                
        PRIX_BASE = 10.00
        prix_unitaire = (PRIX_BASE + self.seance_selectionnee.salle.supplement_prix) * tarif.coeff
        prix_total = round(prix_unitaire * nb_places, 2)
        
        recap = f"""Film: {self.seance_selectionnee.film.titre}
Salle: {self.seance_selectionnee.salle.nom}
Horaire: {self.seance_selectionnee.horaire.strftime('%d/%m/%Y à %H:%M')}
Client: {nom if nom else '(À remplir)'}
Places: {nb_places} × {tarif.label}
Total: {prix_total} €"""
        
        self.recap_label.config(text=recap, fg=Colors.DARK)
        
    def faire_reservation(self):
        """Effectue la réservation"""
        if self.seance_selectionnee is None:
            messagebox.showwarning('Attention', 'Sélectionnez une séance')
            return
            
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showwarning('Attention', 'Entrez votre nom')
            return
            
        try:
            nb_places = int(self.places_spinbox.get())
        except:
            messagebox.showerror('Erreur', 'Nombre invalide')
            return
            
        tarif_text = self.tarif_combo.get()
        tarif = next((t for t in self.service.tarifs if str(t) == tarif_text), None)
                
        if not tarif:
            messagebox.showerror('Erreur', 'Tarif invalide')
            return
            
        self._reservation_en_cours = {
            "nom": nom,
            "nb_places": nb_places,
            "tarif": tarif,
        }
        
        self.open_seat_selection()
        
    def open_quick_reservation(self, seance):
        """Fenêtre rapide de réservation directement depuis l'onglet Séances"""
        window = tk.Toplevel(self.root)
        window.title('Réserver une Séance')
        window.configure(bg=Colors.LIGHT)
        window.grab_set()
        # Plein écran
        window.state('zoomed')
        
        # Header
        title = tk.Label(window, text='Réserver une Séance',
                        font=('Segoe UI', 16, 'bold'),
                        bg=Colors.PRIMARY, fg='white', pady=15)
        title.pack(fill='x')
        
        # Info de la séance
        info = tk.Label(window, text=f'{seance.film.titre}\n{seance.salle.nom} • {seance.horaire.strftime("%H:%M")}',
                       font=('Segoe UI', 11),
                       bg=Colors.LIGHT, fg=Colors.SECONDARY, pady=10)
        info.pack(fill='x')
        
        # Frame pour les champs
        form_frame = tk.Frame(window, bg=Colors.LIGHT)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Nom
        tk.Label(form_frame, text='Votre Nom',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        nom_entry = ttk.Entry(form_frame, width=40)
        nom_entry.pack(fill='x', pady=(0, 15))
        
        # Nombre de places
        tk.Label(form_frame, text='Nombre de Places',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        places_spinbox = ttk.Spinbox(form_frame, from_=1, to=seance.places_disponibles, width=10)
        places_spinbox.set('1')
        places_spinbox.pack(anchor='w', pady=(0, 15))
        
        # Tarif
        tk.Label(form_frame, text='Tarif',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        tarif_combo = ttk.Combobox(form_frame, state='readonly', width=37)
        tarifs = self.service.tarifs
        tarif_combo['values'] = [str(t) for t in tarifs]
        if tarifs:
            tarif_combo.set(str(tarifs[0]))
        tarif_combo.pack(fill='x')
        
        # Boutons
        btn_frame = tk.Frame(window, bg=Colors.LIGHT)
        btn_frame.pack(fill='x', padx=20, pady=(20, 20))
        
        def on_confirm():
            nom = nom_entry.get().strip()
            if not nom:
                messagebox.showwarning('Attention', 'Veuillez entrer votre nom')
                return
            
            try:
                nb_places = int(places_spinbox.get())
            except:
                messagebox.showerror('Erreur', 'Nombre invalide')
                return
            
            tarif_text = tarif_combo.get()
            tarif = next((t for t in self.service.tarifs if str(t) == tarif_text), None)
            
            if not tarif:
                messagebox.showerror('Erreur', 'Tarif invalide')
                return
            
            # Stocker les infos
            self._reservation_en_cours = {
                "nom": nom,
                "nb_places": nb_places,
                "tarif": tarif,
            }
            
            window.destroy()
            self.open_seat_selection()
        
        ttk.Button(btn_frame, text='Annuler',
                  command=window.destroy).pack(side='right', padx=(10, 0))
        
        ttk.Button(btn_frame, text='RESERVER',
                  command=on_confirm,
                  style='Success.TButton').pack(side='right')
        
    def open_seat_selection(self):
        """Fenêtre de sélection des places"""
        seance = self.seance_selectionnee
        if not seance or not self._reservation_en_cours:
            return
            
        nb = self._reservation_en_cours["nb_places"]
        
        window = tk.Toplevel(self.root)
        window.title(f'Sélectionnez {nb} place(s)')
        # Plein écran pour cette fenêtre
        window.state('zoomed')
        window.configure(bg=Colors.LIGHT)
        window.grab_set()
        # Header
        title = tk.Label(window, text=f'🎬 Sélectionnez {nb} place(s)',
                        font=('Segoe UI', 16, 'bold'),
                        bg=Colors.PRIMARY, fg='white', pady=15)
        title.pack(fill='x')
        
        # Info
        info = tk.Label(window, text=f'{seance.film.titre} • {seance.salle.nom} • {seance.horaire.strftime("%H:%M")}',
                       font=('Segoe UI', 11),
                       bg=Colors.LIGHT, fg=Colors.SECONDARY, pady=10)
        info.pack(fill='x')
        
        # Compteur de places sélectionnées
        counter_frame = tk.Frame(window, bg=Colors.LIGHT)
        counter_frame.pack(fill='x', padx=20, pady=10)
        
        counter_label = tk.Label(counter_frame, text=f'Places sélectionnées: 0/{nb}',
                                font=('Segoe UI', 11, 'bold'),
                                fg=Colors.PRIMARY, bg=Colors.LIGHT)
        counter_label.pack(anchor='w')
        
        # Légende
        legend_frame = tk.Frame(window, bg=Colors.LIGHT)
        legend_frame.pack(fill='x', padx=20, pady=5)
        
        legend_items = [
            (Colors.SUCCESS, 'Libre'),
            (Colors.DANGER, 'Occupée'),
            (Colors.PRIMARY, 'Sélectionnée')
        ]
        
        for color, label in legend_items:
            item = tk.Frame(legend_frame, bg=Colors.LIGHT)
            item.pack(side='left', padx=(0, 25))
            
            tk.Label(item, text='■', font=('Arial', 14), fg=color, bg=Colors.LIGHT).pack(side='left', padx=(0, 8))
            tk.Label(item, text=label, font=('Segoe UI', 10), fg=Colors.DARK, bg=Colors.LIGHT).pack(side='left')
        
        # Frame scrollable pour le grid de places
        grid_scroll_frame = tk.Frame(window, bg=Colors.LIGHT)
        grid_scroll_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        canvas = tk.Canvas(grid_scroll_frame, bg=Colors.LIGHT, relief='solid', bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(grid_scroll_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.LIGHT)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind scroll wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        grid_frame = scrollable_frame
        
        self._seat_vars = {}
        self._seat_buttons = {}
        self._selected_count = [0]  # Liste pour éviter les problèmes de scope
        
        def update_counter():
            count = sum(1 for v in self._seat_vars.values() if v.get() == 1)
            self._selected_count[0] = count
            if count == nb:
                counter_label.config(fg=Colors.SUCCESS, text=f'✅ Places sélectionnées: {count}/{nb}')
            else:
                counter_label.config(fg=Colors.PRIMARY, text=f'Places sélectionnées: {count}/{nb}')
        
        for num in range(1, seance.salle.capacite + 1):
            var = tk.IntVar()
            self._seat_vars[num] = var
            
            is_occupied = num in seance.places_occupees
            
            if is_occupied:
                btn = tk.Label(grid_frame, text=str(num), width=5, height=3,
                              bg=Colors.DANGER, fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='solid', bd=1)
                self._seat_buttons[num] = btn
            else:
                def make_click_handler(n, v):
                    def handler():
                        current = v.get()
                        # Vérifier si on peut ajouter une place
                        if current == 0 and self._selected_count[0] >= nb:
                            messagebox.showwarning('Limite atteinte', 
                                f'Vous pouvez sélectionner maximum {nb} place(s)')
                            return
                        
                        v.set(1 - current)
                        btn = self._seat_buttons[n]
                        if v.get() == 1:
                            btn.config(bg=Colors.PRIMARY, fg='white')
                        else:
                            btn.config(bg=Colors.SUCCESS, fg='white')
                        update_counter()
                    return handler
                
                btn = tk.Button(grid_frame, text=str(num), width=5, height=3,
                               bg=Colors.SUCCESS, fg='white',
                               font=('Segoe UI', 10, 'bold'),
                               relief='solid', bd=1, activebackground='#047857',
                               activeforeground='white',
                               command=make_click_handler(num, var))
                self._seat_buttons[num] = btn
                
            row = (num - 1) // 10
            col = (num - 1) % 10
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
        
        # Boutons d'action
        btn_frame = tk.Frame(window, bg=Colors.LIGHT)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame, text='❌ Annuler',
                  command=window.destroy).pack(side='right', padx=(10, 0))
        
        validate_btn = ttk.Button(btn_frame, text='✅ Valider la Réservation',
                  command=lambda: self.validate_seats(window, nb),
                  style='Success.TButton')
        validate_btn.pack(side='right')
                  
    def _toggle_seat(self, var, int_var, btn, num, seance):
        """Bascule une place avec visual feedback"""
        int_var.set(1 - int_var.get())
        
        if int_var.get() == 1:
            btn.config(bg=Colors.PRIMARY, fg='white')
        else:
            btn.config(bg=Colors.SUCCESS, fg='white')
        
    def validate_seats(self, window, nb):
        """Valide la sélection des places"""
        seance = self.seance_selectionnee
        nom = self._reservation_en_cours["nom"]
        tarif = self._reservation_en_cours["tarif"]
        
        # Récupérer les places sélectionnées
        places = [n for n, v in self._seat_vars.items()
                 if v.get() == 1 and n not in seance.places_occupees]
        
        # Validation stricte: exactement le nombre de places demandé
        if len(places) < nb:
            messagebox.showerror('Erreur', 
                f'❌ Vous devez sélectionner exactement {nb} place(s)!\n\n'
                f'Actuellement sélectionnées: {len(places)}')
            return
            
        if len(places) > nb:
            messagebox.showerror('Erreur',
                f'❌ Vous avez sélectionné trop de places!\n\n'
                f'Sélectionnées: {len(places)} - Demandées: {nb}')
            return
            
        try:
            reservation = self.service.creer_reservation_avec_seance(
                self.seance_selectionnee, nom, nb, tarif, numeros_places=places)
                
            window.destroy()
            
            messagebox.showinfo('Succès',
                f"""🎉 Réservation confirmée!

🎫 Ticket: {reservation.id}
👤 Client: {nom}
🎬 Film: {reservation.seance.film.titre}
🪑 Sièges: {', '.join(str(p) for p in sorted(places))}
💰 Total: {reservation.prix_total} €

⏰ Présentez-vous 15 minutes avant!""")
            
            self.seance_selectionnee = None
            self._reservation_en_cours = None
            
            self.load_seances_beautifully()
            self.load_reservations()
            self.load_stats()
            
        except CinemaException as e:
            messagebox.showerror('Erreur', str(e))
        except Exception as e:
            messagebox.showerror('Erreur', f'Erreur: {e}')
            
    def load_reservations(self):
        """Charge l'historique"""
        self.reservations_text.delete(1.0, tk.END)
        
        if not self.service.reservations:
            self.reservations_text.insert(tk.END,
                '🎬 Aucune réservation pour l\'instant.\n\n'
                'Utilisez l\'onglet "Réserver" pour faire une réservation!')
        else:
            self.reservations_text.insert(tk.END,
                f'📋 HISTORIQUE ({len(self.service.reservations)} réservation(s))\n')
            self.reservations_text.insert(tk.END, '=' * 60 + '\n\n')
            
            for i, res in enumerate(self.service.reservations, 1):
                self.reservations_text.insert(tk.END, f'--- Réservation #{i} ---\n')
                self.reservations_text.insert(tk.END, str(res))
                self.reservations_text.insert(tk.END, '\n' + '-' * 40 + '\n\n')
                
    def clear_reservations(self):
        """Efface l'historique"""
        if not self.service.reservations:
            messagebox.showinfo('Info', 'Aucune réservation à effacer')
            return
            
        if messagebox.askyesno('Confirmation',
                              'Êtes-vous sûr? Cette action est irréversible.'):
            self.service.reservations.clear()
            self.load_reservations()
            self.load_stats()
    
    def creer_film(self):
        """Crée un nouveau film"""
        nom = self.film_nom.get().strip()
        if not nom:
            messagebox.showwarning('Attention', 'Entrez le nom du film')
            return
            
        try:
            duree = int(self.film_duree.get())
            if duree < 30 or duree > 300:
                messagebox.showwarning('Attention', 'La durée doit être entre 30 et 300 minutes')
                return
        except ValueError:
            messagebox.showerror('Erreur', 'Durée invalide')
            return
            
        genre_str = self.film_genre.get()
        if not genre_str:
            messagebox.showwarning('Attention', 'Sélectionnez un genre')
            return
            
        try:
            note = float(self.film_note.get())
            if note < 0 or note > 10:
                messagebox.showwarning('Attention', 'La note doit être entre 0 et 10')
                return
        except ValueError:
            messagebox.showerror('Erreur', 'Note invalide')
            return
            
        realisateur = self.film_realisateur.get().strip()
        synopsis = self.film_synopsis.get("1.0", tk.END).strip()
        
        try:
            # Créer le film via le service
            from models.film import Film
            
            # Trouver le genre correspondant
            genre_enum = None
            for g in StyleFilm:
                if g.value == genre_str:
                    genre_enum = g
                    break
                    
            if not genre_enum:
                messagebox.showerror('Erreur', 'Genre invalide')
                return
                
            film = Film(
                titre=nom,
                duree=duree,
                style=genre_enum,
                note=note,
                realisateur=realisateur if realisateur else "Anonyme",
                resume=synopsis if synopsis else "Pas de synopsis"
            )
            
            self.service.films.append(film)
            
            messagebox.showinfo('Succès',
                f"""Film créé avec succès!

Titre: {nom}
Genre: {genre_str}
Durée: {duree} min
Note: {note}/10
Réalisateur: {realisateur if realisateur else 'Non spécifié'}""")
            
            # Réinitialiser le formulaire
            self.film_nom.delete(0, tk.END)
            self.film_duree.set('120')
            self.film_genre.set(self.film_genre['values'][0] if self.film_genre['values'] else '')
            self.film_note.set('7.0')
            self.film_realisateur.delete(0, tk.END)
            self.film_synopsis.delete("1.0", tk.END)
            
        except Exception as e:
            messagebox.showerror('Erreur', f'Erreur lors de la création: {e}')
    
    def mgr_creer_film(self):
        """Manager: Crée un nouveau film"""
        nom = self.mgr_film_nom.get().strip()
        if not nom:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Veuillez entrer le titre du film')
            return
            
        if len(nom) < 2:
            messagebox.showwarning('⚠️ Titre trop court', 'Le titre doit contenir au moins 2 caractères')
            return
            
        try:
            duree = int(self.mgr_film_duree.get())
            if duree < 30:
                messagebox.showwarning('⚠️ Durée insuffisante', 'La durée minimale est de 30 minutes')
                return
            if duree > 300:
                messagebox.showwarning('⚠️ Durée excessive', 'La durée maximale est de 300 minutes')
                return
        except ValueError:
            messagebox.showerror('❌ Format invalide', 'La durée doit être un nombre entier (en minutes)')
            return
            
        genre_str = self.mgr_film_genre.get()
        if not genre_str:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Sélectionnez un genre pour le film')
            return
            
        try:
            note = float(self.mgr_film_note.get())
            if note < 0:
                messagebox.showwarning('⚠️ Note invalide', 'La note ne peut pas être inférieure à 0')
                return
            if note > 10:
                messagebox.showwarning('⚠️ Note invalide', 'La note ne peut pas dépasser 10')
                return
        except ValueError:
            messagebox.showerror('❌ Format invalide', 'La note doit être un nombre (0-10)')
            return
            
        try:
            from models.film import Film
            
            genre_enum = None
            for g in StyleFilm:
                if g.value == genre_str:
                    genre_enum = g
                    break
            #resume = self.mgr_film_synopsis.get("1.0", tk.END).strip()
                    
            if not genre_enum:
                messagebox.showerror('Erreur', f'Genre "{genre_str}" non trouve')
                return
                
            film = Film(titre=nom, duree=duree, style=genre_enum, note=note, resume="Pas de synopsis")
            self.service.films.append(film)
            
            # Créer automatiquement 4 séances par jour sur 3 jours pour le nouveau film
            self.service.creer_seances_pour_film(film)
            
            messagebox.showinfo('Succes', 
                f'Film: {nom}\nDuree: {duree}min\nGenre: {genre_str}\nNote: {note}/10\n\nSeances creees automatiquement!\nMaintenant, creez une salle!')
            
            # Reinitialiser le formulaire
            self.mgr_film_nom.delete(0, tk.END)
            self.mgr_film_duree.set('120')
            self.mgr_film_genre.set(self.mgr_film_genre['values'][0] if self.mgr_film_genre['values'] else '')
            self.mgr_film_note.set('7.0')
            
            # Actualiser les listes
            self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
            self.seances_film_selector['values'] = [f.titre for f in self.service.films]
            self.seances_film_selector.set(nom)  # Sélectionner le nouveau film
            self.load_manager_films_list()
            self.switch_to_seances_tab()  # Aller au onglet Seances pour voir les seances creees
            
        except Exception as e:
            messagebox.showerror('Erreur systeme', f'Impossible de creer le film:\n{str(e)}')
    
    def load_manager_films_list(self):
        """Actualise la liste des films"""
        if not hasattr(self, 'mgr_films_treeview'):
            return
        
        # Clear existing items
        for i in self.mgr_films_treeview.get_children():
            self.mgr_films_treeview.delete(i)
        
        # Add new items
        for i, film in enumerate(self.service.films):
            values = (
                film.titre,
                f"{film.duree} min",
                film.style.value,
                f"{film.note}/10"
            )
            self.mgr_films_treeview.insert('', 'end', iid=i, values=values)
    
    def load_manager_seances_list(self):
        """Actualise la liste des séances de manière hiérarchique (par jour puis par film)."""
        if not hasattr(self, 'mgr_seances_treeview'):
            return
        
        # 1. Vider l'arbre existant
        for i in self.mgr_seances_treeview.get_children():
            self.mgr_seances_treeview.delete(i)

        # 2. Récupérer et grouper les données
        all_seances = sorted(self._get_seances_with_rebuilt_occupancy(), key=lambda s: s.horaire)
        
        seances_par_jour = {}
        for seance in all_seances:
            jour = seance.horaire.date()
            if jour not in seances_par_jour:
                seances_par_jour[jour] = {}
            
            film_titre = seance.film.titre
            if film_titre not in seances_par_jour[jour]:
                seances_par_jour[jour][film_titre] = []
            
            seances_par_jour[jour][film_titre].append(seance)

        # 3. Remplir l'arbre avec la structure hiérarchique
        day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        month_names_fr = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        
        for jour, films_du_jour in seances_par_jour.items():
            # Créer le noeud parent pour le jour
            jour_str = f"{day_names_fr[jour.weekday()]} {jour.day} {month_names_fr[jour.month]} {jour.year}"
            jour_id = str(jour)
            self.mgr_seances_treeview.insert('', 'end', iid=jour_id, text=jour_str, open=True)

            for film_titre, seances_du_film in films_du_jour.items():
                # Créer le noeud pour le film
                film_id = f"{jour_id}_{film_titre}"
                self.mgr_seances_treeview.insert(jour_id, 'end', iid=film_id, text=f"🎬 {film_titre}", open=True)

                for seance in seances_du_film:
                    # Créer la feuille pour la séance (la ligne de donnée)
                    values = (
                        seance.salle.nom,
                        seance.horaire.strftime('%H:%M'),
                        f"{seance.places_reservees}/{seance.salle.capacite}"
                    )
                    self.mgr_seances_treeview.insert(film_id, 'end', iid=seance.id, text="", values=values)
    
    def load_manager_salles_list(self):
        """Actualise la liste des salles"""
        if not hasattr(self, 'mgr_salles_treeview'):
            return
        
        for i in self.mgr_salles_treeview.get_children():
            self.mgr_salles_treeview.delete(i)
        
        for i, salle in enumerate(self.service.salles):
            values = (
                salle.numero,
                salle.nom,
                f"{salle.capacite} places",
                salle.type_salle.value
            )
            self.mgr_salles_treeview.insert('', 'end', iid=i, values=values)
    
    def mgr_modifier_film(self):
        """Modifie un film sélectionné"""
        selection = self.mgr_films_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner un film à modifier')
            return
        
        film_index = int(selection[0])
        film = self.service.films[film_index]
        
        # Fenêtre de modification
        window = tk.Toplevel(self.root)
        window.title(f'Modifier: {film.titre}')
        window.geometry('500x550')
        window.configure(bg=Colors.LIGHT)
        
        # Header
        tk.Label(window, text=f'✏️ Modifier Film',
                font=('Segoe UI', 14, 'bold'),
                bg=Colors.PRIMARY, fg='white', pady=10).pack(fill='x')
        
        # Form
        form = tk.Frame(window, bg=Colors.LIGHT)
        form.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titre
        tk.Label(form, text='Titre:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        titre_entry = ttk.Entry(form, width=40)
        titre_entry.insert(0, film.titre)
        titre_entry.pack(fill='x', pady=(0, 15))
        
        # Durée
        tk.Label(form, text='Durée (min):', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        duree_spinbox = ttk.Spinbox(form, from_=30, to=300, width=15)
        duree_spinbox.set(film.duree)
        duree_spinbox.pack(anchor='w', pady=(0, 15))
        
        # Genre
        tk.Label(form, text='Genre:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        genre_combo = ttk.Combobox(form, state='readonly', width=37)
        genre_combo['values'] = [s.value for s in StyleFilm]
        genre_combo.set(film.style.value)
        genre_combo.pack(fill='x', pady=(0, 15))
        
        # Note
        tk.Label(form, text='Note (0-10):', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        note_spinbox = ttk.Spinbox(form, from_=0, to=10, increment=0.5, width=15)
        note_spinbox.set(film.note)
        note_spinbox.pack(anchor='w', pady=(0, 20))
        
        # Synopsis
        tk.Label(form, text='Synopsis:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        synopsis_text = tk.Text(form, height=5, width=40, wrap=tk.WORD, relief='solid', bd=1)
        synopsis_text.insert("1.0", film.resume)
        synopsis_text.pack(fill='x', pady=(0, 15))
        
        # Boutons
        btn_frame = tk.Frame(form, bg=Colors.LIGHT)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        def save_changes():
            try:
                film.titre = titre_entry.get().strip()
                film.duree = int(duree_spinbox.get())
                film.note = float(note_spinbox.get())
                film.resume = synopsis_text.get("1.0", tk.END).strip()
                
                for g in StyleFilm:
                    if g.value == genre_combo.get():
                        film.style = g
                        break
                
                messagebox.showinfo('✅ Succès', 'Film modifié avec succès!')
                self.load_manager_films_list()
                self.load_manager_seances_list()
                self.load_seances_beautifully()
                window.destroy()
            except Exception as e:
                messagebox.showerror('❌ Erreur', f'Erreur: {e}')
        
        ttk.Button(btn_frame, text='Annuler',
                  command=window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(btn_frame, text='✅ Enregistrer',
                  command=save_changes,
                  style='Success.TButton').pack(side='right')
    
    def mgr_supprimer_film(self):
        """Supprime un film sélectionné"""
        selection = self.mgr_films_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner un film à supprimer')
            return
        
        film_index = int(selection[0])
        film = self.service.films[film_index]
        
        if messagebox.askyesno('Confirmation', 
                              f'Êtes-vous sûr de vouloir supprimer "{film.titre}"?\n\nCette action supprimera aussi toutes ses séances.'):
            # Supprimer les séances du film
            self.service.seances = [s for s in self.service.seances if s.film != film]
            # Supprimer le film
            del self.service.films[film_index]
            
            messagebox.showinfo('✅ Succès', f'Film "{film.titre}" supprimé!')
            self.load_manager_films_list()
            self.load_manager_seances_list()
            self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
            self.seances_film_selector['values'] = [f.titre for f in self.service.films]
            self.load_seances_beautifully()
    
    def mgr_creer_seance(self):
        """Manager: Crée une nouvelle séance"""
        film_titre = self.mgr_seance_film.get().strip()
        salle_nom = self.mgr_seance_salle.get().strip()
        date_str = self.mgr_seance_date.get().strip()
        heure_str = self.mgr_seance_heure.get().strip()
        
        # Validation des champs obligatoires
        if not film_titre:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Sélectionnez un film')
            return
        if not salle_nom:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Sélectionnez une salle')
            return
        if not date_str:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Entrez la date (YYYY-MM-DD)')
            return
        if not heure_str:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Entrez l\'horaire (HH:MM)')
            return
        
        try:
            from datetime import datetime
            
            # Valider le format de la date et heure
            try:
                horaire = datetime.strptime(f"{date_str} {heure_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror('❌ Format invalide', 
                    'Format incorrect!\nDate: YYYY-MM-DD (ex: 2025-12-15)\nHeure: HH:MM (ex: 14:30)')
                return
            
            # Vérifier que la date n'est pas dans le passé
            if horaire < datetime.now():
                messagebox.showwarning('⚠️ Date invalide', 
                    'Impossible de créer une séance dans le passé!')
                return
            
            # Trouver le film
            film = next((f for f in self.service.films if f.titre == film_titre), None)
            if not film:
                messagebox.showerror('❌ Film non trouvé', 
                    f'Le film "{film_titre}" n\'existe pas.\nCréez-le d\'abord dans l\'onglet Films.')
                return
            
            # Trouver la salle
            salle = next((s for s in self.service.salles if s.nom == salle_nom), None)
            if not salle:
                messagebox.showerror('❌ Salle non trouvée', 
                    f'La salle "{salle_nom}" n\'existe pas.\nCréez-la d\'abord dans l\'onglet Salles.')
                return
                
            # Créer la séance avec un ID unique
            from models.seance import Seance
            seance_id = f"S{len(self.service.seances)+1:02d}"
            seance = Seance(id=seance_id, film=film, salle=salle, horaire=horaire)
            self.service.seances.append(seance)
            
            messagebox.showinfo('Succes',
                f'Film: {film_titre}\nSalle: {salle_nom}\nDate: {date_str}\nHeure: {heure_str}\n\nSeance creee! Allez a Seances.')
            
            # Reinitialiser
            self.mgr_seance_film.set('')
            self.mgr_seance_salle.set('')
            self.mgr_seance_date.delete(0, tk.END)
            self.mgr_seance_heure.delete(0, tk.END)
            
            # Aller a l'onglet Seances
            self.switch_to_seances_tab()
            
        except Exception as e:
            messagebox.showerror('❌ Erreur système', f'Impossible de créer la séance:\n{str(e)}')
    
    def mgr_modifier_seance(self):
        """Modifie une séance sélectionnée"""
        selection = self.mgr_seances_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner une séance à modifier')
            return
        
        seance_id = selection[0]
        seance = next((s for s in self.service.seances if s.id == seance_id), None)
        
        if not seance:
            messagebox.showwarning('⚠️ Sélection invalide', 'Veuillez sélectionner une séance spécifique (une ligne avec une heure), et non un jour ou un titre de film.')
            return
        
        # Fenêtre de modification
        window = tk.Toplevel(self.root)
        window.title(f'Modifier Séance')
        window.geometry('500x450')
        window.configure(bg=Colors.LIGHT)
        
        # Header
        tk.Label(window, text=f'✏️ Modifier Séance',
                font=('Segoe UI', 14, 'bold'),
                bg=Colors.PRIMARY, fg='white', pady=10).pack(fill='x')
        
        # Form
        form = tk.Frame(window, bg=Colors.LIGHT)
        form.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Film
        tk.Label(form, text='Film:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        film_combo = ttk.Combobox(form, state='readonly', width=40)
        film_combo['values'] = [f.titre for f in self.service.films]
        film_combo.set(seance.film.titre)
        film_combo.pack(fill='x', pady=(0, 15))
        
        # Salle
        tk.Label(form, text='Salle:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        salle_combo = ttk.Combobox(form, state='readonly', width=40)
        salle_combo['values'] = [s.nom for s in self.service.salles]
        salle_combo.set(seance.salle.nom)
        salle_combo.pack(fill='x', pady=(0, 15))
        
        # Date et Heure
        tk.Label(form, text='Date (YYYY-MM-DD):', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        date_entry = ttk.Entry(form, width=40)
        date_entry.insert(0, seance.horaire.strftime('%Y-%m-%d'))
        date_entry.pack(fill='x', pady=(0, 15))
        
        tk.Label(form, text='Horaire (HH:MM):', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        heure_entry = ttk.Entry(form, width=40)
        heure_entry.insert(0, seance.horaire.strftime('%H:%M'))
        heure_entry.pack(fill='x', pady=(0, 20))
        
        # Boutons
        btn_frame = tk.Frame(form, bg=Colors.LIGHT)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        def save_changes():
            try:
                from datetime import datetime
                
                film = next((f for f in self.service.films if f.titre == film_combo.get()), None)
                salle = next((s for s in self.service.salles if s.nom == salle_combo.get()), None)
                
                if not film or not salle:
                    messagebox.showerror('❌ Erreur', 'Film ou Salle invalide')
                    return
                
                horaire = datetime.strptime(f"{date_entry.get()} {heure_entry.get()}", "%Y-%m-%d %H:%M")
                
                seance.film = film
                seance.salle = salle
                seance.horaire = horaire
                
                messagebox.showinfo('✅ Succès', 'Séance modifiée avec succès!')
                self.load_manager_seances_list()
                self.load_seances_beautifully()
                window.destroy()
            except Exception as e:
                messagebox.showerror('❌ Erreur', f'Erreur: {e}')
        
        ttk.Button(btn_frame, text='Annuler',
                  command=window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(btn_frame, text='✅ Enregistrer',
                  command=save_changes,
                  style='Success.TButton').pack(side='right')
    
    def mgr_supprimer_seance(self):
        """Supprime une séance sélectionnée"""
        selection = self.mgr_seances_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner une séance à supprimer')
            return
        
        seance_id = selection[0]
        seance = next((s for s in self.service.seances if s.id == seance_id), None)
        
        if not seance:
            messagebox.showwarning('⚠️ Sélection invalide', 'Veuillez sélectionner une séance spécifique (une ligne avec une heure), et non un jour ou un titre de film.')
            return
        
        if messagebox.askyesno('Confirmation',
                              f'Êtes-vous sûr de vouloir supprimer cette séance?\n\n{seance.film.titre} - {seance.horaire.strftime("%d/%m/%Y à %H:%M")}'):
            seance_index_to_delete = -1
            for i, s_item in enumerate(self.service.seances):
                if s_item.id == seance_id:
                    seance_index_to_delete = i
                    break
            
            if seance_index_to_delete != -1:
                del self.service.seances[seance_index_to_delete]
                messagebox.showinfo('✅ Succès', 'Séance supprimée!')
                self.load_manager_seances_list()
                self.load_seances_beautifully()
    
    def mgr_creer_salle(self):
        """Manager: Crée une nouvelle salle"""
        nom = self.mgr_salle_nom.get().strip()
        if not nom:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Veuillez entrer le nom de la salle')
            return
        
        if len(nom) < 2:
            messagebox.showwarning('⚠️ Nom trop court', 'Le nom doit contenir au moins 2 caractères')
            return
        
        try:
            capacite = int(self.mgr_salle_capacite.get())
            if capacite < 10:
                messagebox.showwarning('⚠️ Capacité insuffisante', 'La capacité minimale est de 10 places')
                return
            if capacite > 500:
                messagebox.showwarning('⚠️ Capacité excessive', 'La capacité maximale est de 500 places')
                return
        except ValueError:
            messagebox.showerror('❌ Format invalide', 'La capacité doit être un nombre entier')
            return
        
        type_str = self.mgr_salle_type.get()
        if not type_str:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Sélectionnez un type de salle')
            return
        
        try:
            type_enum = None
            for t in TypeSalle:
                if t.value == type_str:
                    type_enum = t
                    break
            
            if not type_enum:
                messagebox.showerror('❌ Erreur', f'Type "{type_str}" non trouvé')
                return
            
            from models.salle import Salle
            # Générer un numéro unique (basé sur le nombre de salles existantes)
            numero = len(self.service.salles) + 1
            salle = Salle(numero=numero, nom=nom, capacite=capacite, type_salle=type_enum)
            self.service.salles.append(salle)
            
            messagebox.showinfo('Succes', 
                f'Nom: {nom}\nCapacite: {capacite} places\nType: {type_str}\n\nMaintenant, creez une seance!')
            
            # Reinitialiser
            self.mgr_salle_nom.delete(0, tk.END)
            self.mgr_salle_capacite.set('100')
            self.mgr_salle_type.set(self.mgr_salle_type['values'][0] if self.mgr_salle_type['values'] else '')
            
            # Actualiser les listes
            self.mgr_seance_salle['values'] = [s.nom for s in self.service.salles]
            
            # Aller au Manager -> Seances
            if hasattr(self, 'manager_notebook'):
                self.notebook.select(3)  # Manager
                self.manager_notebook.select(1)  # Seances
            
        except Exception as e:
            messagebox.showerror('❌ Erreur système', f'Impossible de créer la salle:\n{str(e)}')
    
    def mgr_modifier_salle(self):
        """Modifie une salle sélectionnée"""
        selection = self.mgr_salles_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner une salle à modifier')
            return
        
        salle_index = int(selection[0])
        salle = self.service.salles[salle_index]
        
        # Fenêtre de modification
        window = tk.Toplevel(self.root)
        window.title(f'Modifier: {salle.nom}')
        window.geometry('500x400')
        window.configure(bg=Colors.LIGHT)
        
        # Header
        tk.Label(window, text=f'✏️ Modifier Salle',
                font=('Segoe UI', 14, 'bold'),
                bg=Colors.PRIMARY, fg='white', pady=10).pack(fill='x')
        
        # Form
        form = tk.Frame(window, bg=Colors.LIGHT)
        form.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Nom
        tk.Label(form, text='Nom:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        nom_entry = ttk.Entry(form, width=40)
        nom_entry.insert(0, salle.nom)
        nom_entry.pack(fill='x', pady=(0, 15))
        
        # Capacité
        tk.Label(form, text='Capacité:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        capacite_spinbox = ttk.Spinbox(form, from_=10, to=500, width=15)
        capacite_spinbox.set(salle.capacite)
        capacite_spinbox.pack(anchor='w', pady=(0, 15))
        
        # Type
        tk.Label(form, text='Type:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        type_combo = ttk.Combobox(form, state='readonly', width=37)
        type_combo['values'] = [t.value for t in TypeSalle]
        type_combo.set(salle.type_salle.value)
        type_combo.pack(fill='x', pady=(0, 20))
        
        # Boutons
        btn_frame = tk.Frame(form, bg=Colors.LIGHT)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        def save_changes():
            try:
                salle.nom = nom_entry.get().strip()
                salle.capacite = int(capacite_spinbox.get())
                
                for t in TypeSalle:
                    if t.value == type_combo.get():
                        salle.type_salle = t
                        break
                
                messagebox.showinfo('✅ Succès', 'Salle modifiée avec succès!')
                self.load_manager_salles_list()
                self.load_manager_seances_list()
                self.load_seances_beautifully()
                window.destroy()
            except Exception as e:
                messagebox.showerror('❌ Erreur', f'Erreur: {e}')
        
        ttk.Button(btn_frame, text='Annuler',
                  command=window.destroy).pack(side='right', padx=(10, 0))
        ttk.Button(btn_frame, text='✅ Enregistrer',
                  command=save_changes,
                  style='Success.TButton').pack(side='right')
    
    def mgr_supprimer_salle(self):
        """Supprime une salle sélectionnée"""
        selection = self.mgr_salles_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner une salle à supprimer')
            return
        
        salle_index = int(selection[0])
        salle = self.service.salles[salle_index]
        
        if messagebox.askyesno('Confirmation',
                              f'Êtes-vous sûr de vouloir supprimer la salle "{salle.nom}"?\n\nCette action supprimera aussi toutes ses séances.'):
            # Supprimer les séances de la salle
            self.service.seances = [s for s in self.service.seances if s.salle != salle]
            # Supprimer la salle
            del self.service.salles[salle_index]
            
            messagebox.showinfo('✅ Succès', f'Salle "{salle.nom}" supprimée!')
            self.load_manager_salles_list()
            self.mgr_seance_salle['values'] = [s.nom for s in self.service.salles]
            self.load_manager_seances_list()
            self.load_seances_beautifully()

    def load_manager_tarifs_list(self):
        """Actualise la liste des tarifs dans le Treeview du manager."""
        if not hasattr(self, 'mgr_tarifs_treeview'):
            return
        
        for i in self.mgr_tarifs_treeview.get_children():
            self.mgr_tarifs_treeview.delete(i)
        
        PRIX_BASE = 10.00
        for i, tarif in enumerate(self.service.tarifs):
            exemple_prix = PRIX_BASE * tarif.coeff
            values = (
                tarif.label,
                f"{tarif.coeff:.2f} (soit {tarif.coeff:.0%})",
                f"{exemple_prix:.2f} €"
            )
            self.mgr_tarifs_treeview.insert('', 'end', iid=i, values=values)

    def mgr_creer_tarif(self):
        """Crée un nouveau tarif."""
        label = self.mgr_tarif_label.get().strip()
        if not label:
            messagebox.showwarning('⚠️ Champ obligatoire', 'Veuillez entrer un libellé pour le tarif.')
            return
        
        try:
            coeff = float(self.mgr_tarif_coeff.get())
            if not (0.1 <= coeff <= 2.0):
                messagebox.showwarning('⚠️ Valeur invalide', 'Le coefficient doit être entre 0.1 et 2.0.')
                return
        except ValueError:
            messagebox.showerror('❌ Format invalide', 'Le coefficient doit être un nombre.')
            return

        new_tarif = Tarif(label=label, coeff=coeff)
        self.service.tarifs.append(new_tarif)
        
        messagebox.showinfo('✅ Succès', f'Le tarif "{label}" a été créé avec succès.')
        
        self.mgr_tarif_label.delete(0, tk.END)
        self.mgr_tarif_coeff.set('1.0')
        
        self.load_manager_tarifs_list()
        # Mettre à jour les combobox de réservation
        self.tarif_combo['values'] = [str(t) for t in self.service.tarifs]

    def mgr_modifier_tarif(self):
        """Modifie un tarif sélectionné."""
        selection = self.mgr_tarifs_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner un tarif à modifier.')
            return
        
        tarif_index = int(selection[0])
        tarif = self.service.tarifs[tarif_index]

        # Fenêtre de modification
        window = tk.Toplevel(self.root)
        window.title(f'Modifier: {tarif.label}')
        window.geometry('400x300')
        window.configure(bg=Colors.LIGHT)

        form = tk.Frame(window, bg=Colors.LIGHT)
        form.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(form, text='Libellé:', bg=Colors.LIGHT).pack(anchor='w')
        label_entry = ttk.Entry(form, width=40)
        label_entry.insert(0, tarif.label)
        label_entry.pack(fill='x', pady=(0, 15))

        tk.Label(form, text='Coefficient:', bg=Colors.LIGHT).pack(anchor='w')
        coeff_spinbox = ttk.Spinbox(form, from_=0.1, to=2.0, increment=0.1, width=15)
        coeff_spinbox.set(f"{tarif.coeff:.1f}")
        coeff_spinbox.pack(anchor='w', pady=(0, 20))

        def save_changes():
            tarif.label = label_entry.get().strip()
            tarif.coeff = float(coeff_spinbox.get())
            messagebox.showinfo('✅ Succès', 'Tarif modifié.')
            self.load_manager_tarifs_list()
            self.tarif_combo['values'] = [str(t) for t in self.service.tarifs]
            window.destroy()

        ttk.Button(form, text='Enregistrer', command=save_changes, style='Success.TButton').pack(side='right')
        ttk.Button(form, text='Annuler', command=window.destroy).pack(side='right', padx=(0, 10))

    def mgr_supprimer_tarif(self):
        """Supprime un tarif sélectionné."""
        selection = self.mgr_tarifs_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner un tarif à supprimer.')
            return
        
        tarif_index = int(selection[0])
        tarif = self.service.tarifs[tarif_index]

        if messagebox.askyesno('Confirmation', f'Êtes-vous sûr de vouloir supprimer le tarif "{tarif.label}"?'):
            del self.service.tarifs[tarif_index]
            messagebox.showinfo('✅ Succès', 'Tarif supprimé.')
            self.load_manager_tarifs_list()
            self.tarif_combo['values'] = [str(t) for t in self.service.tarifs]
    
    def load_rapports(self):
        """Charge les rapports manager"""
        try:
            self.rapports_text.delete(1.0, tk.END)
            
            content = "📊 RAPPORTS DU CINÉMA\n"
            content += "=" * 75 + "\n\n"
            
            # Résumé général
            nb_films = len(self.service.films)
            nb_salles = len(self.service.salles)
            nb_seances = len(self._get_seances_with_rebuilt_occupancy())
            nb_reservations = len(self.service.reservations)
            
            content += f"📈 STATISTIQUES GÉNÉRALES\n"
            content += "-" * 75 + "\n"
            content += f"Films en catalogue              : {nb_films:>10}\n"
            content += f"Salles disponibles              : {nb_salles:>10}\n"
            content += f"Séances programmées             : {nb_seances:>10}\n"
            content += f"Total réservations              : {nb_reservations:>10}\n\n"
            
            # Revenus
            if nb_reservations > 0:
                revenus_total = sum(r.prix_total for r in self.service.reservations)
                places_vendues = sum(r.nb_places for r in self.service.reservations)
                ticket_moyen = revenus_total / places_vendues if places_vendues > 0 else 0
                
                content += f"💰 REVENUS\n"
                content += "-" * 75 + "\n"
                content += f"Revenus totaux                  : {revenus_total:>10.2f}€\n"
                content += f"Places vendues                  : {places_vendues:>10}\n"
                content += f"Ticket moyen                    : {ticket_moyen:>10.2f}€\n\n"
                
                # Films populaires
                content += f"🎬 FILMS LES PLUS POPULAIRES (Top 5)\n"
                content += "-" * 75 + "\n"
                films_pop = {}
                for r in self.service.reservations:
                    titre = r.seance.film.titre
                    if titre not in films_pop:
                        films_pop[titre] = {'places': 0, 'revenus': 0}
                    films_pop[titre]['places'] += r.nb_places
                    films_pop[titre]['revenus'] += r.prix_total
                
                if films_pop:
                    for i, (film, stats) in enumerate(sorted(films_pop.items(), 
                                         key=lambda x: x[1]['revenus'], reverse=True)[:5], 1):
                        content += f"{i}. {film:40} {stats['places']:>4} places  {stats['revenus']:>10.2f}€\n"
                else:
                    content += "Aucune réservation pour le moment.\n"
                    
                content += "\n"
                
                # Occupations par salle
                content += f"🏛️ OCCUPATION PAR SALLE\n"
                content += "-" * 75 + "\n"
                occupations = {}
                for r in self.service.reservations:
                    salle = r.seance.salle.nom
                    if salle not in occupations:
                        occupations[salle] = 0
                    occupations[salle] += r.nb_places
                
                for salle, total in sorted(occupations.items()):
                    content += f"  {salle:40} {total:>4} places\n"
            else:
                content += "📭 Aucune réservation pour le moment.\n"
                content += "Les rapports s'afficheront une fois que les clients feront des réservations.\n"
            
            content += "\n" + "=" * 75
            content += f"\nActualisé le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
            
            self.rapports_text.insert(tk.END, content)
        except Exception as e:
            self.rapports_text.delete(1.0, tk.END)
            self.rapports_text.insert(tk.END, f"❌ Erreur lors du chargement des rapports:\n{str(e)}")
            
    def load_stats(self):
        """Charge les stats"""
        self.stats_text.delete(1.0, tk.END)
        
        total_seances = len(self._get_seances_with_rebuilt_occupancy())
        total_res = len(self.service.reservations)
        
        self.stats_text.insert(tk.END, '📊 STATISTIQUES\n')
        self.stats_text.insert(tk.END, '=' * 50 + '\n\n')
        
        self.stats_text.insert(tk.END, f'Séances: {total_seances}\n')
        self.stats_text.insert(tk.END, f'Réservations: {total_res}\n')
        
        if total_res > 0:
            revenus = sum(r.prix_total for r in self.service.reservations)
            places = sum(r.nb_places for r in self.service.reservations)
            
            self.stats_text.insert(tk.END, f'Places vendues: {places}\n')
            self.stats_text.insert(tk.END, f'Revenus: {revenus:.2f} €\n\n')
            
            self.stats_text.insert(tk.END, '🎬 Films populaires:\n')
            films = {}
            for r in self.service.reservations:
                titre = r.seance.film.titre
                if titre not in films:
                    films[titre] = 0
                films[titre] += r.nb_places
                
            for film, count in sorted(films.items(), key=lambda x: x[1], reverse=True):
                self.stats_text.insert(tk.END, f'  • {film}: {count} places\n')
        else:
            self.stats_text.insert(tk.END, 'Aucune réservation pour le moment.\n')


def main():
    root = tk.Tk()
    app = CinemaGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
