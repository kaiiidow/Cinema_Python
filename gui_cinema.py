import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from PIL import Image, ImageTk
from datetime import datetime
from services.cinema_service import CinemaService
from models.exceptions import CinemaException
from models.exceptions import CinemaException, ConflitSeanceException
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
    """
    Classe principale de l'interface graphique pour le système de cinéma.

    Gère la création de la fenêtre, des widgets, des onglets et de toute
    l'interaction utilisateur.
    """
    def __init__(self, root):
        self.root = root
        self.service = CinemaService()
        self.seance_selectionnee = None
        self.seance_index = -1
        self._reservation_en_cours = None
        self._seat_vars = {}
        self._seances_affichees = []  # Pour stocker les references aux seances affichees
        self._selected_seances_date = None  # Date sélectionnée pour l'affichage
        self._seances_tab_selected_film_titre = None
        self.active_canvas = None  # Référence au canvas actuellement sous le curseur pour le scroll
        
        self.setup_window()
        self.setup_styles()
        self.create_interface()
        
    def _on_mousewheel(self, event):
        if self.active_canvas and self.active_canvas.winfo_exists():
            self.active_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def setup_window(self):
        """Configure les propriétés de la fenêtre principale de l'application."""
        self.root.title("🎬 Cinéma - Système de Réservation")
        
        self.root.state('zoomed')  # Démarrage en mode plein écran
        self.root.minsize(1000, 600)
        
        self.root.configure(bg=Colors.LIGHT)

        # Lie l'événement de la molette de la souris à une méthode unique pour
        # gérer le défilement du canvas actif.
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def setup_styles(self):
        """Définit les styles personnalisés pour les widgets ttk."""
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
        """Construit les composants principaux de l'interface."""
        self.create_header()
        content = ttk.Frame(self.root, style='Content.TFrame')
        content.pack(fill='both', expand=True)
        self.create_notebook(content)
        self.create_footer()
        
    def create_header(self):
        """Crée l'en-tête supérieur de l'application."""
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
        """Crée le conteneur d'onglets (Notebook) et y ajoute les onglets principaux."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_seances_tab(self.notebook)
        self.create_historique_tab(self.notebook)
        self.create_stats_tab(self.notebook)
        self.create_manager_tab(self.notebook)
    
    def switch_to_seances_tab(self):
        """Bascule vers l'onglet 'Séances' et actualise son contenu."""
        self.load_seances_beautifully()
        self.notebook.select(0)
    
    def switch_to_salles_tab(self):
        """Bascule vers l'onglet de gestion des salles dans le panneau manager."""
        self.notebook.select(3)
        if hasattr(self, 'manager_notebook'):
            self.manager_notebook.select(2)
        
    def create_seances_tab(self, notebook):
        """Crée l'onglet principal de consultation des séances."""
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
        
        # Conteneur principal divisé en deux (contenu et barre latérale)
        main_container = tk.Frame(frame, bg=Colors.LIGHTER)
        main_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Partie gauche : contenu principal scrollable
        left_container = tk.Frame(main_container, bg=Colors.LIGHTER)
        left_container.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Utilisation d'un Canvas pour permettre le défilement de contenu complexe
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
        
        # Assigne ce canvas comme cible pour le défilement par la molette
        canvas.bind('<Enter>', lambda e, c=canvas: setattr(self, 'active_canvas', c))
        canvas.bind('<Leave>', lambda e: setattr(self, 'active_canvas', None))

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Sélecteur de film
        film_selector = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
        film_selector.pack(fill='x', padx=10, pady=(0, 20))
        
        tk.Label(film_selector, text='Rechercher un Film',
                font=('Segoe UI', 12, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=15, pady=(10, 5))
        
        # Barre de recherche avec icône intégrée
        search_bar_frame = tk.Frame(film_selector, bg=Colors.LIGHT, relief='solid', bd=1)
        search_bar_frame.pack(fill='x', padx=15, pady=(0, 10))

        search_icon_label = tk.Label(search_bar_frame, text='🔍', font=('Segoe UI', 12), bg=Colors.LIGHT, fg=Colors.SECONDARY)
        search_icon_label.pack(side='left', padx=(10, 5))

        self.film_search_entry = tk.Entry(search_bar_frame, font=('Segoe UI', 11),
                                          bg=Colors.LIGHT, fg=Colors.DARK, relief='flat', bd=0,
                                          insertbackground=Colors.DARK)
        self.film_search_entry.pack(side='left', fill='x', expand=True, pady=8)
        self.film_search_entry.bind('<KeyRelease>', self._update_film_search_results)
        
        # Conteneur scrollable pour les résultats de la recherche
        results_container = tk.Frame(film_selector, height=130, bg='white')
        results_container.pack(fill='x', expand=True, padx=15, pady=(0, 15))
        results_container.pack_propagate(False)

        results_canvas = tk.Canvas(results_container, bg='white', highlightthickness=0)
        results_scrollbar = ttk.Scrollbar(results_container, orient='vertical', command=results_canvas.yview)
        self.film_search_results_frame = tk.Frame(results_canvas, bg='white')

        self.film_search_results_frame.bind(
            "<Configure>",
            lambda e: results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        )

        results_canvas.create_window((0, 0), window=self.film_search_results_frame, anchor="nw")
        results_canvas.configure(yscrollcommand=results_scrollbar.set)

        # Assigne ce canvas comme cible pour le défilement par la molette
        results_canvas.bind('<Enter>', lambda e, c=results_canvas: setattr(self, 'active_canvas', c))
        results_canvas.bind('<Leave>', lambda e: setattr(self, 'active_canvas', None))

        results_canvas.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
        
        # Conteneur où les détails du film et ses séances seront affichés
        self.seances_display_frame = tk.Frame(scrollable_frame, bg=Colors.LIGHTER)
        self.seances_display_frame.pack(fill='both', expand=True, padx=10)
        
        # Partie droite : barre latérale pour la navigation par jour
        sidebar = tk.Frame(main_container, bg='white', relief='solid', bd=1, width=200)
        sidebar.pack(side='right', fill='y', padx=(15, 0))
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text='Autres Jours',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.PRIMARY, bg='white').pack(fill='x', padx=10, pady=(10, 5))
        
        self.sidebar_days_frame = tk.Frame(sidebar, bg='white')
        self.sidebar_days_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self._update_film_search_results()  # Peuple la liste des films au démarrage
        self.load_seances_beautifully()
        
    def load_seances_beautifully(self, event=None):
        """Actualise l'affichage de l'onglet 'Séances'."""
        for widget in self.seances_display_frame.winfo_children():
            widget.destroy()
        
        for widget in self.sidebar_days_frame.winfo_children():
            widget.destroy()

        # Obtenir les dates
        from datetime import datetime, timedelta
        aujourd_hui = datetime.now().date()
        demain = aujourd_hui + timedelta(days=1)
        surdemain = aujourd_hui + timedelta(days=2)
        
        # Récupère l'objet Film correspondant au titre sélectionné
        film_titre = self._seances_tab_selected_film_titre
        film_selectionnee = None
        if film_titre:
            for f in self.service.films:
                if f.titre == film_titre:
                    film_selectionnee = f
                    break

        if not film_selectionnee:
            # Affiche un message si aucun film n'est sélectionné
            empty_label = tk.Label(self.seances_display_frame,
                                  text='Sélectionnez un film pour voir les séances',
                                  font=('Segoe UI', 14),
                                  fg=Colors.SECONDARY,
                                  bg=Colors.LIGHTER)
            empty_label.pack(pady=50)
        else:
            # Affiche les détails et les séances pour le film et la date choisis
            if self._selected_seances_date is not None:
                date_affichee = self._selected_seances_date
                date_label = date_affichee.strftime('%d/%m/%Y')
            else:
                date_affichee = aujourd_hui
                date_label = "Séances d'aujourd'hui"
            
            self._display_seances_for_date(self.seances_display_frame, 
                                          film_selectionnee, date_affichee, 
                                          date_label)
        
        # La barre latérale est toujours affichée pour permettre la navigation
        self._display_sidebar_days(film_selectionnee, demain, surdemain)
        
    def _display_film_details(self, parent_frame, film):
        """Construit et affiche la fiche détaillée d'un film."""
        details_card = tk.Frame(parent_frame, bg='white', relief='solid', bd=1)
        details_card.pack(fill='x', pady=(0, 20))

        # Poster à gauche
        poster_label = tk.Label(details_card, bg='white')
        poster_label.pack(side='left', padx=20, pady=20)
        
        try:
            img = Image.open(film.poster_path)
            img.thumbnail((200, 300))  # Redimensionne en conservant le ratio
            poster_image = ImageTk.PhotoImage(img)
            poster_label.config(image=poster_image)
            poster_label.image = poster_image  # Garde une référence pour éviter le garbage collection
        except (FileNotFoundError, AttributeError):
            # Affiche une image de remplacement si le poster n'est pas trouvé
            placeholder = Image.new('RGB', (200, 300), color=Colors.BORDER)
            poster_image = ImageTk.PhotoImage(placeholder)
            poster_label.config(image=poster_image, text="Image non trouvée", compound='center', fg=Colors.SECONDARY)
            poster_label.image = poster_image

        # Partie droite : informations textuelles
        details_frame = tk.Frame(details_card, bg='white')
        details_frame.pack(side='left', fill='both', expand=True, padx=(0, 20), pady=20)

        tk.Label(details_frame, text=film.titre, font=('Segoe UI', 18, 'bold'), fg=Colors.DARK, bg='white', wraplength=500, justify='left').pack(anchor='w')

        # Métadonnées (durée, genre, note)
        meta_frame = tk.Frame(details_frame, bg='white')
        meta_frame.pack(fill='x', pady=(10, 15))
        
        meta_items = [
            f"⏱️ {film.duree} min",
            f"🎭 {film.style.value}",
            f"⭐ {film.note}/10"
        ]
        for item_text in meta_items:
            tk.Label(meta_frame, text=item_text, font=('Segoe UI', 10), fg=Colors.SECONDARY, bg='white').pack(side='left', padx=(0, 20))

        tk.Label(details_frame, text="Synopsis", font=('Segoe UI', 11, 'bold'), fg=Colors.DARK, bg='white').pack(anchor='w')
        synopsis_text = tk.Text(details_frame, height=6, wrap=tk.WORD, relief='flat', bd=0,
                                font=('Segoe UI', 10), fg=Colors.DARK, bg='white',
                                highlightthickness=1, highlightbackground=Colors.BORDER)
        synopsis_text.pack(fill='both', expand=True, pady=(5, 0))
        synopsis_text.insert('1.0', film.resume)
        synopsis_text.config(state='disabled')  # Rend le champ de texte non éditable

    def _display_seances_for_date(self, parent_frame, film, date, title):
        """Affiche les séances d'un film pour une date donnée."""
        
        self._display_film_details(parent_frame, film)

        # Filtre les séances pour le film et la date spécifiés
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
        
        # Regroupe les séances par heure pour un affichage clair
        seances_par_horaire = {}
        for seance in seances_du_jour:
            horaire_str = seance.horaire.strftime('%H:%M')
            if horaire_str not in seances_par_horaire:
                seances_par_horaire[horaire_str] = []
            seances_par_horaire[horaire_str].append(seance)
        
        # Affiche une section pour chaque groupe d'horaires
        for horaire_str in sorted(seances_par_horaire.keys()):
            seances = seances_par_horaire[horaire_str]
            
            # Header de l'horaire
            horaire_header = tk.Frame(parent_frame, bg=Colors.PRIMARY)
            horaire_header.pack(fill='x', padx=0, pady=(15, 0))
            
            tk.Label(horaire_header, text=f'  {horaire_str}',
                    font=('Segoe UI', 14, 'bold'),
                    fg='white', bg=Colors.PRIMARY).pack(side='left', padx=10, pady=10)
            
            # Affiche les différentes salles pour cet horaire
            salles_frame = tk.Frame(parent_frame, bg='white', relief='solid', bd=1)
            salles_frame.pack(fill='x', padx=0, pady=(0, 10))
            
            for seance in seances:
                salle_card = tk.Frame(salles_frame, bg=Colors.LIGHT, relief='solid', bd=1)
                salle_card.pack(fill='x', padx=10, pady=10)
                
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
                
                # Affiche la disponibilité avec un code couleur
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
                
                # Barre de progression visuelle pour le taux d'occupation
                progress_frame = tk.Frame(salle_card, bg=Colors.LIGHT)
                progress_frame.pack(fill='x', padx=15, pady=(0, 10))
                
                occupied_ratio = seance.places_reservees / seance.salle.capacite
                progress_width = int(300 * occupied_ratio)
                
                bar_bg = tk.Frame(progress_frame, bg='#e5e7eb', height=8, width=300)
                bar_bg.pack(fill='x')
                bar_bg.pack_propagate(False)
                
                bar_fill = tk.Frame(bar_bg, bg=dispo_color, height=8, width=progress_width)
                bar_fill.pack(side='left', fill='y')
                
                # Bouton de réservation
                    btn_frame = tk.Frame(salle_card, bg=Colors.LIGHT)
                    btn_frame.pack(fill='x', padx=15, pady=(10, 0))
                    
                    def make_reserve_handler(s):
                        def on_reserve():
                            self.seance_selectionnee = s
                            self.open_quick_reservation(s)
                        return on_reserve
                    
                    ttk.Button(btn_frame, text='RESERVER',
                                 command=make_reserve_handler(seance),
                                 style='Success.TButton',
                                 state='normal' if seance.places_disponibles > 0 else 'disabled').pack(side='right')
    
    def _display_sidebar_days(self, film, day1, day2):
        """Construit la barre latérale de navigation par jour."""
        # NOTE: Les séances sont récupérées avec l'occupation reconstruite pour
        # garantir la cohérence des données affichées, contournant un bug potentiel
        # de partage d'état entre objets Seance.
        all_seances_for_film = [s for s in self._get_seances_with_rebuilt_occupancy() if s.film == film]

        from datetime import datetime, timedelta
        
        aujourd_hui = datetime.now().date()
        
        # Carte pour le jour actuel
        day_card = tk.Frame(self.sidebar_days_frame, bg='white', relief='solid', bd=1, cursor='hand2')
        day_card.pack(fill='x', pady=(0, 10))
        
        def make_click_handler(selected_day, film_obj):
            def on_click(event):
                if film_obj is None:
                    messagebox.showinfo("Action requise", "Veuillez d'abord sélectionner un film dans la liste de recherche.")
                    return

                for widget in self.seances_display_frame.winfo_children():
                    widget.destroy()

                self._selected_seances_date = selected_day
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
        
        day_card.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        date_str = aujourd_hui.strftime('%d/%m')
        day_label_text = f'Aujourd\'hui\n{date_str}'
        day_label = tk.Label(day_card, text=day_label_text,
                            font=('Segoe UI', 10, 'bold'),
                            fg=Colors.PRIMARY, bg='white', cursor='hand2')
        day_label.pack(fill='x', padx=8, pady=(8, 5))
        day_label.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        if film:
            seances_jour = [s for s in all_seances_for_film if s.horaire.date() == aujourd_hui]
        else:
            seances_jour = []

        nb_seances = len(seances_jour)
        count_label = tk.Label(day_card, text=f'{nb_seances} séance(s)',
                              font=('Segoe UI', 9),
                              fg=Colors.SECONDARY, bg='white', cursor='hand2')
        count_label.pack(fill='x', padx=8, pady=(0, 8))
        count_label.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        horaires = sorted(set(s.horaire.strftime('%H:%M') for s in seances_jour))
        horaires_str = ', '.join(horaires) if horaires else 'Aucune'
        
        horaires_label = tk.Label(day_card, text=horaires_str,
                                 font=('Segoe UI', 8),
                                 fg=Colors.SECONDARY, bg='white', cursor='hand2')
        horaires_label.pack(fill='x', padx=8, pady=(0, 8))
        horaires_label.bind('<Button-1>', make_click_handler(aujourd_hui, film))
        
        # Cartes pour les 6 jours suivants
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        for i in range(1, 7):
            day = aujourd_hui + timedelta(days=i)
            jour_num = day.weekday()
            jour_name = day_names[jour_num]
            
            day_card = tk.Frame(self.sidebar_days_frame, bg='#f3f4f6', relief='solid', bd=1, cursor='hand2')
            day_card.pack(fill='x', pady=(0, 10))
            
            day_card.bind('<Button-1>', make_click_handler(day, film))
            
            date_str = day.strftime('%d/%m')
            day_label = tk.Label(day_card, text=f'{jour_name}\n{date_str}',
                                font=('Segoe UI', 10, 'bold'),
                                fg=Colors.PRIMARY, bg='#f3f4f6', cursor='hand2')
            day_label.pack(fill='x', padx=8, pady=(8, 5))
            day_label.bind('<Button-1>', make_click_handler(day, film))
            
            if film:
                seances_jour = [s for s in all_seances_for_film if s.horaire.date() == day]
            else:
                seances_jour = []

            nb_seances = len(seances_jour)
            count_label = tk.Label(day_card, text=f'{nb_seances} séance(s)',
                                  font=('Segoe UI', 9),
                                  fg=Colors.SECONDARY, bg='#f3f4f6', cursor='hand2')
            count_label.pack(fill='x', padx=8, pady=(0, 8))
            count_label.bind('<Button-1>', make_click_handler(day, film))
            
            horaires = sorted(set(s.horaire.strftime('%H:%M') for s in seances_jour))
            horaires_str = ', '.join(horaires) if horaires else 'Aucune'
            
            horaires_label = tk.Label(day_card, text=horaires_str,
                                     font=('Segoe UI', 8),
                                     fg=Colors.DARK, bg='#f3f4f6',
                                     wraplength=180, justify='left', cursor='hand2')
            horaires_label.pack(fill='x', padx=8, pady=(0, 8))
            horaires_label.bind('<Button-1>', make_click_handler(day, film))
        
    def _update_film_search_results(self, event=None):
        """Met à jour la liste des films en fonction de la recherche."""
        search_term = self.film_search_entry.get()
        
        for widget in self.film_search_results_frame.winfo_children():
            widget.destroy()
        
        films_trouves = self.service.rechercher_films(search_term)
        
        if not films_trouves:
            no_result_label = tk.Label(self.film_search_results_frame, text="Aucun film trouvé",
                                       font=('Segoe UI', 10), fg=Colors.SECONDARY, bg='white',
                                       padx=15, pady=10)
            no_result_label.pack(anchor='w')
        else:
            for film in films_trouves:
                result_label = tk.Label(self.film_search_results_frame, text=film.titre,
                                        font=('Segoe UI', 11), fg=Colors.DARK, bg='white',
                                        anchor='w', padx=15, pady=10, cursor="hand2")
                result_label.pack(fill='x')

                result_label.bind("<Button-1>", lambda e, f=film: self._on_film_search_select(f))
                result_label.bind("<Enter>", lambda e, label=result_label: label.config(bg=Colors.LIGHT))
                result_label.bind("<Leave>", lambda e, label=result_label: label.config(bg='white'))
        
        # Force une mise à jour du layout pour que la scrollregion du canvas soit correcte.
        self.film_search_results_frame.update_idletasks()

    def _on_film_search_select(self, film_obj):
        """Gère la sélection d'un film dans la liste de recherche."""
        # Stocke le titre sélectionné et actualise l'affichage des séances.
        self._seances_tab_selected_film_titre = film_obj.titre
        self.load_seances_beautifully()
        
        # Réinitialise la barre de recherche et la liste des résultats pour
        # faciliter une nouvelle recherche.
        self.film_search_entry.delete(0, tk.END)
        self._update_film_search_results()
        
    def create_historique_tab(self, notebook):
        """Crée l'onglet d'historique des réservations."""
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

        ttk.Button(btn_frame, text='🗑️ Annuler la réservation',
                  command=self.annuler_reservation_selectionnee).pack(side='left')
        
        ttk.Button(btn_frame, text='🗑️ Effacer',
                  command=self.clear_reservations).pack(side='left')
        
        content_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)

        cols = ('ID', 'Film', 'Date', 'Heure', 'Salle', 'Sièges', 'Prix')
        self.reservations_treeview = ttk.Treeview(tree_frame, columns=cols, show='headings', style='Treeview')

        for col in cols:
            self.reservations_treeview.heading(col, text=col)

        self.reservations_treeview.column('ID', width=100, anchor='center')
        self.reservations_treeview.column('Film', width=250)
        self.reservations_treeview.column('Date', width=100, anchor='center')
        self.reservations_treeview.column('Heure', width=80, anchor='center')
        self.reservations_treeview.column('Salle', width=150)
        self.reservations_treeview.column('Sièges', width=150)
        self.reservations_treeview.column('Prix', width=80, anchor='e')

        # Configure les tags pour un affichage en "zèbre" (lignes alternées)
        self.reservations_treeview.tag_configure('oddrow', background='white')
        self.reservations_treeview.tag_configure('evenrow', background=Colors.LIGHT)

        scrollbar_reservations = ttk.Scrollbar(tree_frame, orient='vertical', command=self.reservations_treeview.yview)
        self.reservations_treeview.configure(yscrollcommand=scrollbar_reservations.set)
        self.reservations_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_reservations.pack(side='right', fill='y')
        
        self.load_reservations()
        
    def create_stats_tab(self, notebook):
        """Crée l'onglet des statistiques générales."""
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
        
        content_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)

        cols = ('Valeur',)
        self.stats_treeview = ttk.Treeview(tree_frame, columns=cols, show='tree headings', style='Treeview')

        self.stats_treeview.heading('#0', text='Métrique')
        self.stats_treeview.column('#0', width=400, minwidth=300)

        self.stats_treeview.heading('Valeur', text='Valeur')
        self.stats_treeview.column('Valeur', width=200, anchor='e')

        scrollbar_stats = ttk.Scrollbar(tree_frame, orient='vertical', command=self.stats_treeview.yview)
        self.stats_treeview.configure(yscrollcommand=scrollbar_stats.set)
        self.stats_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_stats.pack(side='right', fill='y')

        self.load_stats()


    def create_manager_tab(self, notebook):
        """Crée l'onglet principal du panneau de gestion (Manager)."""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='⚙️ Manager')
        
        self.manager_notebook = ttk.Notebook(frame)
        self.manager_notebook.pack(fill='both', expand=True, padx=20, pady=20)
       
        try:
            self.create_mdp(self.manager_notebook)
        except Exception:
            pass

    def create_mdp(self, notebook) : 
        """Crée l'onglet de saisie du mot de passe pour l'accès manager."""
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

                # Déverrouille et crée les onglets de gestion
                if not getattr(self, '_manager_unlocked', False):
                    try:
                        self.create_manager_films_tab(self.manager_notebook)
                        self.create_manager_seances_tab(self.manager_notebook)
                        self.create_manager_salles_tab(self.manager_notebook)
                        self.create_manager_tarifs_tab(self.manager_notebook)
                        self.create_manager_rapports_tab(self.manager_notebook)

                        # Charge les données initiales dans les nouveaux onglets
                        try:
                            self.load_manager_films_list()
                            self.load_manager_seances_list()
                            self.load_manager_salles_list()
                            self.load_manager_tarifs_list()
                        except Exception:
                            pass

                        self._manager_unlocked = True
                        try:
                            self.manager_notebook.select(1)
                        except Exception:
                            pass
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

        self.mgr_mdp_entry.bind('<Return>', lambda e: check_mdp())
        
    def create_manager_films_tab(self, notebook):
        """Crée l'onglet de gestion des films pour le manager."""
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
        
        form_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=30, pady=(0, 30))
        
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
        
        tk.Label(form_frame, text='🖼️ Fichier Poster (optionnel)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(0, 8))
        self.mgr_film_poster = ttk.Entry(form_frame, width=50)
        self.mgr_film_poster.pack(fill='x', padx=20, pady=(0, 20))
        self.mgr_film_poster.insert(0, "nom-du-fichier.jpg")

        tk.Label(form_frame, text='📝 Synopsis',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(0, 8))
        self.mgr_film_synopsis = tk.Text(form_frame, height=4, width=50, wrap=tk.WORD,
                                         relief='solid', bd=1, font=('Segoe UI', 10))
        self.mgr_film_synopsis.pack(fill='x', padx=20, pady=(0, 20))

        
        
        
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(btn_frame, text='➕ Ajouter Film',
                  command=self.mgr_creer_film,
                  style='Success.TButton').pack(side='right')
        
        list_title = tk.Label(scrollable, text='📽️ Films Existants',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=30, pady=(30, 20))
        
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
        
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_film, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_film).pack(side='left')
        
    def create_manager_seances_tab(self, notebook):
        """Crée l'onglet de gestion des séances pour le manager."""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🎥 Séances')
        
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
        
        form_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=40, pady=30)
        
        tk.Label(form_frame, text='🎬 Film',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_seance_film = ttk.Combobox(form_frame, state='readonly', width=40)
        self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
        self.mgr_seance_film.pack(fill='x', padx=20, pady=(0, 20))
        
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
        
        tk.Label(form_frame, text='🕐 Horaire (HH:MM)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(0, 8))
        self.mgr_seance_heure = ttk.Entry(form_frame, width=20)
        self.mgr_seance_heure.pack(anchor='w', padx=20, pady=(0, 20))
        
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        ttk.Button(btn_frame, text='➕ Créer Séance',
                  command=self.mgr_creer_seance,
                  style='Success.TButton').pack(side='right')
        
        list_title = tk.Label(scrollable, text='📅 Séances Existantes',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=20, pady=(30, 20))
        
        tree_frame = tk.Frame(scrollable, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=40, pady=(0, 20))
        
        # Le film et la date sont affichés hiérarchiquement dans l'arborescence.
        cols = ('Salle', 'Horaire', 'Places')
        self.mgr_seances_treeview = ttk.Treeview(tree_frame, columns=cols, show='tree headings')
        
        # Colonne 0 : L'arborescence Jour -> Film
        self.mgr_seances_treeview.heading('#0', text='Jour / Film')
        self.mgr_seances_treeview.column('#0', width=300, minwidth=250, stretch=tk.NO)
        
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
        
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_seance,
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_seance).pack(side='left')
        
    def create_manager_salles_tab(self, notebook):
        """Crée l'onglet de gestion des salles pour le manager."""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🏛️ Salles')
        
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
        
        tk.Label(form_frame, text='📍 Nom de la salle',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_salle_nom = ttk.Entry(form_frame, width=40)
        self.mgr_salle_nom.pack(fill='x', padx=20, pady=(0, 20))
        
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
        
        list_title = tk.Label(scrollable, text='🏛️ Salles Existantes',
                             font=('Segoe UI', 18, 'bold'),
                             fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        list_title.pack(fill='x', padx=20, pady=(30, 20))
        
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
        
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_salle, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_salle).pack(side='left')
        
    def create_manager_tarifs_tab(self, notebook):
        """Crée l'onglet de gestion des tarifs pour le manager."""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='💰 Tarifs')
        
        canvas = tk.Canvas(frame, bg=Colors.LIGHTER, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollable = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set, bg=Colors.LIGHTER)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

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
        
        action_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        action_frame.pack(fill='x', padx=40, pady=(0, 30))
        
        ttk.Button(action_frame, text='✏️ Modifier',
                  command=self.mgr_modifier_tarif, style='Primary.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text='🗑️ Supprimer',
                  command=self.mgr_supprimer_tarif).pack(side='left')
        
    def create_manager_rapports_tab(self, notebook):
        """Crée l'onglet des rapports analytiques pour le manager."""
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
        
        tree_frame = tk.Frame(content_frame)
        tree_frame.pack(fill='both', expand=True)

        cols = ('Détail', 'Valeur')
        self.rapports_treeview = ttk.Treeview(tree_frame, columns=cols, show='tree headings', style='Treeview')

        self.rapports_treeview.heading('#0', text='Catégorie / Item')
        self.rapports_treeview.column('#0', width=350, minwidth=300)

        self.rapports_treeview.heading('Détail', text='Détail')
        self.rapports_treeview.column('Détail', width=200, anchor='center')
        self.rapports_treeview.heading('Valeur', text='Valeur')
        self.rapports_treeview.column('Valeur', width=200, anchor='e')

        scrollbar_rapports = ttk.Scrollbar(tree_frame, orient='vertical', command=self.rapports_treeview.yview)
        self.rapports_treeview.configure(yscrollcommand=scrollbar_rapports.set)
        self.rapports_treeview.pack(side='left', fill='both', expand=True)
        scrollbar_rapports.pack(side='right', fill='y')
        
        self.load_rapports()
        
    def create_section(self, parent, title):
        """Crée un titre de section stylisé avec un séparateur."""
        container = tk.Frame(parent, bg=Colors.LIGHTER)
        container.pack(fill='x', padx=30, pady=(25, 12))
        
        label = tk.Label(container, text=title,
                        font=('Segoe UI', 12, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        label.pack(anchor='w')
        
        separator = tk.Frame(container, bg=Colors.BORDER, height=2)
        separator.pack(fill='x', pady=(8, 0))
        
    def create_footer(self):
        """Crée le pied de page de l'application."""
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
        Reconstruit l'état d'occupation des places pour chaque séance.

        NOTE: Cette méthode est un contournement critique. Elle corrige un bug où
        les objets Seance pourraient partager incorrectement leur état d'occupation.
        En réinitialisant et en reconstruisant l'occupation à partir de la liste
        globale des réservations (la source de vérité), on garantit la
        cohérence des données à chaque affichage.
        """
        all_seances = self.service.get_toutes_seances()
        
        for seance in all_seances:
            seance.places_occupees = set()
            seance.places_reservees = 0
            
        for reservation in self.service.reservations:
            if reservation.numeros_places and hasattr(reservation, 'seance'):
                reservation.seance.places_occupees.update(reservation.numeros_places)
                reservation.seance.places_reservees = len(reservation.seance.places_occupees)
                
        return all_seances
        
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
        btn_frame.pack(fill='x', padx=20, pady=20)
        
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
        """Ouvre la fenêtre de sélection des sièges pour la réservation en cours."""
        seance = self.seance_selectionnee
        if not seance or not self._reservation_en_cours:
            return
            
        nb = self._reservation_en_cours["nb_places"]
        
        window = tk.Toplevel(self.root)
        window.title(f'Sélectionnez {nb} place(s)')
        window.state('zoomed')
        window.configure(bg=Colors.LIGHT)
        window.grab_set()
        title = tk.Label(window, text=f'🎬 Sélectionnez {nb} place(s)',
                        font=('Segoe UI', 16, 'bold'),
                        bg=Colors.PRIMARY, fg='white', pady=15)
        title.pack(fill='x')
        
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
        
        # Grille des sièges dans un conteneur scrollable
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
        
        canvas.bind('<Enter>', lambda e, c=canvas: setattr(self, 'active_canvas', c))
        canvas.bind('<Leave>', lambda e: setattr(self, 'active_canvas', None))
        
        grid_frame = scrollable_frame
        
        self._seat_vars = {}
        self._seat_buttons = {}
        self._selected_count = [0]  # Utilise une liste pour que la variable soit mutable dans les closures
        
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
        
        btn_frame = tk.Frame(window, bg=Colors.LIGHT)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame, text='❌ Annuler',
                  command=window.destroy).pack(side='right', padx=(10, 0))
        
        validate_btn = ttk.Button(btn_frame, text='✅ Valider la Réservation',
                  command=lambda: self.validate_seats(window, nb),
                  style='Success.TButton')
        validate_btn.pack(side='right')
                  
    def validate_seats(self, window, nb):
        """Valide la sélection des sièges et finalise la réservation."""
        seance = self.seance_selectionnee
        nom = self._reservation_en_cours["nom"]
        tarif = self._reservation_en_cours["tarif"]
        
        places = [n for n, v in self._seat_vars.items()
                 if v.get() == 1 and n not in seance.places_occupees]
        
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
        """Actualise l'affichage de l'historique des réservations."""
        for i in self.reservations_treeview.get_children():
            self.reservations_treeview.delete(i)
        
        if not self.service.reservations:
            pass
        else:
            for i, res in enumerate(sorted(self.service.reservations, key=lambda r: r.seance.horaire, reverse=True)):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                sieges_str = ', '.join(map(str, sorted(res.numeros_places))) if res.numeros_places else f"{res.nb_places} place(s)"
                values = (
                    res.id,
                    res.seance.film.titre,
                    res.seance.horaire.strftime('%d/%m/%Y'),
                    res.seance.horaire.strftime('%H:%M'),
                    res.seance.salle.nom,
                    sieges_str,
                    f"{res.prix_total:.2f} €"
                )
                self.reservations_treeview.insert('', 'end', iid=res.id, values=values, tags=(tag,))

    def annuler_reservation_selectionnee(self):
        """Gère l'annulation d'une réservation sélectionnée dans l'historique."""
        selection = self.reservations_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Aucune sélection', 'Veuillez sélectionner une réservation à annuler.')
            return

        reservation_id = selection[0]
        
        if messagebox.askyesno('Confirmation d\'annulation',
                              f'Êtes-vous sûr de vouloir annuler la réservation {reservation_id} ?\nCette action est irréversible.'):
            
            success = self.service.annuler_reservation(reservation_id)
            
            if success:
                messagebox.showinfo('✅ Succès', 'La réservation a été annulée avec succès.')
                self.load_reservations()
                self.load_stats()
                self.load_rapports()
                self.load_seances_beautifully()
            else:
                messagebox.showerror('❌ Erreur', 'Impossible de trouver ou d\'annuler cette réservation.')
                
    def clear_reservations(self):
        """Supprime toutes les réservations de l'historique."""
        if not self.service.reservations:
            messagebox.showinfo('Info', 'Aucune réservation à effacer.')
            return
            
        if messagebox.askyesno('⚠️ Confirmation',
                              'Êtes-vous sûr de vouloir effacer TOUTES les réservations ?\nCette action est irréversible.'):
            for reservation in self.service.reservations:
                reservation.seance.liberer_places(reservation.nb_places, reservation.numeros_places)

            self.service.reservations.clear()
            messagebox.showinfo('✅ Succès', 'Toutes les réservations ont été effacées.')
            
            self.load_reservations()
            self.load_stats()
            self.load_rapports()
            self.load_seances_beautifully()
    
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
        
        resume = self.mgr_film_synopsis.get("1.0", tk.END).strip()
        poster_filename = self.mgr_film_poster.get().strip()

        try:
            from models.film import Film
            
            genre_enum = None
            for g in StyleFilm:
                if g.value == genre_str:
                    genre_enum = g
                    break
                    
            if not genre_enum:
                messagebox.showerror('Erreur', f'Genre "{genre_str}" non trouve')
                return
                
            poster_path = ""
            if poster_filename and poster_filename != "nom-du-fichier.jpg":
                poster_path = f"assets/posters/{poster_filename}"

            film = Film(titre=nom, duree=duree, style=genre_enum, note=note, poster_path=poster_path, resume=resume or "Pas de synopsis")
            self.service.films.append(film)
            
            self.service.creer_seances_pour_film(film)
            
            messagebox.showinfo('Succes', 
                f'Film: {nom}\nDuree: {duree}min\nGenre: {genre_str}\nNote: {note}/10\n\nSeances creees automatiquement!\nMaintenant, creez une salle!')
            
            # Reinitialiser le formulaire
            self.mgr_film_nom.delete(0, tk.END)
            self.mgr_film_duree.set('120')
            self.mgr_film_genre.set(self.mgr_film_genre['values'][0] if self.mgr_film_genre['values'] else '')
            self.mgr_film_note.set('7.0')
            self.mgr_film_synopsis.delete("1.0", tk.END)
            self.mgr_film_poster.delete(0, tk.END)
            self.mgr_film_poster.insert(0, "nom-du-fichier.jpg")
            
            self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
            
            # Mettre à jour l'onglet Séances pour sélectionner le nouveau film
            self._seances_tab_selected_film_titre = nom
            if hasattr(self, 'film_search_entry'):
                self.film_search_entry.delete(0, tk.END)
                self.film_search_entry.insert(0, nom)
                self._update_film_search_results()

            self.load_manager_films_list()
            self.switch_to_seances_tab()
            
        except Exception as e:
            messagebox.showerror('Erreur systeme', f'Impossible de creer le film:\n{str(e)}')
    
    def load_manager_films_list(self):
        """Actualise la liste des films dans le Treeview du manager."""
        if not hasattr(self, 'mgr_films_treeview'):
            return
        
        for i in self.mgr_films_treeview.get_children():
            self.mgr_films_treeview.delete(i)
        
        for i, film in enumerate(self.service.films):
            values = (
                film.titre,
                f"{film.duree} min",
                film.style.value,
                f"{film.note}/10"
            )
            self.mgr_films_treeview.insert('', 'end', iid=i, values=values)
    
    def load_manager_seances_list(self):
        """Actualise la liste des séances dans le Treeview du manager."""
        if not hasattr(self, 'mgr_seances_treeview'):
            return
        
        for i in self.mgr_seances_treeview.get_children():
            self.mgr_seances_treeview.delete(i)

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

        day_names_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        month_names_fr = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        
        for jour, films_du_jour in seances_par_jour.items():
            jour_str = f"{day_names_fr[jour.weekday()]} {jour.day} {month_names_fr[jour.month]} {jour.year}"
            jour_id = str(jour)
            self.mgr_seances_treeview.insert('', 'end', iid=jour_id, text=jour_str, open=True)

            for film_titre, seances_du_film in films_du_jour.items():
                film_id = f"{jour_id}_{film_titre}"
                self.mgr_seances_treeview.insert(jour_id, 'end', iid=film_id, text=f"🎬 {film_titre}", open=True)

                for seance in seances_du_film:
                    values = (
                        seance.salle.nom,
                        seance.horaire.strftime('%H:%M'),
                        f"{seance.places_reservees}/{seance.salle.capacite}"
                    )
                    self.mgr_seances_treeview.insert(film_id, 'end', iid=seance.id, text="", values=values)
    
    def load_manager_salles_list(self):
        """Actualise la liste des salles dans le Treeview du manager."""
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
        """Ouvre une fenêtre pour modifier un film sélectionné."""
        selection = self.mgr_films_treeview.selection()
        if not selection:
            messagebox.showwarning('⚠️ Sélection', 'Veuillez sélectionner un film à modifier')
            return
        
        film_index = int(selection[0])
        film = self.service.films[film_index]
        
        window = tk.Toplevel(self.root)
        window.title(f'Modifier: {film.titre}')
        window.geometry('500x550')
        window.configure(bg=Colors.LIGHT)
        
        tk.Label(window, text=f'✏️ Modifier Film',
                font=('Segoe UI', 14, 'bold'),
                bg=Colors.PRIMARY, fg='white', pady=10).pack(fill='x')
        
        form = tk.Frame(window, bg=Colors.LIGHT)
        form.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(form, text='Titre:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        titre_entry = ttk.Entry(form, width=40)
        titre_entry.insert(0, film.titre)
        titre_entry.pack(fill='x', pady=(0, 15))
        
        tk.Label(form, text='Durée (min):', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        duree_spinbox = ttk.Spinbox(form, from_=30, to=300, width=15)
        duree_spinbox.set(film.duree)
        duree_spinbox.pack(anchor='w', pady=(0, 15))
        
        tk.Label(form, text='Genre:', font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg=Colors.LIGHT).pack(anchor='w', pady=(0, 5))
        genre_combo = ttk.Combobox(form, state='readonly', width=37)
        genre_combo['values'] = [s.value for s in StyleFilm]
        genre_combo.set(film.style.value)
        genre_combo.pack(fill='x', pady=(0, 15))
        
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
            self.service.seances = [s for s in self.service.seances if s.film.titre != film.titre]
            # Supprimer le film
            del self.service.films[film_index]
            
            # Si le film supprimé était celui sélectionné, on réinitialise la vue
            if self._seances_tab_selected_film_titre == film.titre:
                self._seances_tab_selected_film_titre = None
                if hasattr(self, 'film_search_entry'):
                    self.film_search_entry.delete(0, tk.END)
                    self._update_film_search_results()

            messagebox.showinfo('✅ Succès', f'Film "{film.titre}" supprimé!')
            self.load_manager_films_list()
            self.load_manager_seances_list()
            self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
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
            # seance = Seance(id=seance_id, film=film, salle=salle, horaire=horaire) <-- Bug: doublon
            nouvelle_seance = Seance(id=seance_id, film=film, salle=salle, horaire=horaire)

            # --- VÉRIFICATION ANTI-CONFLIT ---
            seance_en_conflit = self.service.verifier_conflit_seance(nouvelle_seance)
            if seance_en_conflit:
                messagebox.showerror('❌ Conflit de programmation',
                    f"Impossible de créer cette séance.\n\n"
                    f"La salle '{salle.nom}' est déjà occupée à ce créneau par le film "
                    f"'{seance_en_conflit.film.titre}' à "
                    f"{seance_en_conflit.horaire.strftime('%H:%M')}.")
                return
            # --- FIN DE LA VÉRIFICATION ---

            self.service.seances.append(nouvelle_seance)
            
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
        """Charge les rapports manager dans un Treeview."""
        if not hasattr(self, 'rapports_treeview'):
            return # Ne rien faire si l'onglet manager n'est pas débloqué

        try:
            # Vider le treeview
            for i in self.rapports_treeview.get_children():
                self.rapports_treeview.delete(i)
            
            stats = self.service.get_statistiques()
            
            # --- Section Générale ---
            general_id = self.rapports_treeview.insert('', 'end', text='📈 Statistiques Générales', open=True)
            self.rapports_treeview.insert(general_id, 'end', values=('Films en catalogue', '', stats['total_films']))
            self.rapports_treeview.insert(general_id, 'end', values=('Salles disponibles', '', stats['total_salles']))
            self.rapports_treeview.insert(general_id, 'end', values=('Séances programmées', '', stats['total_seances']))
            self.rapports_treeview.insert(general_id, 'end', values=('Total réservations', '', stats['total_reservations']))

            if stats['total_reservations'] > 0:
                # --- Section Revenus ---
                revenus_id = self.rapports_treeview.insert('', 'end', text='💰 Revenus', open=True)
                self.rapports_treeview.insert(revenus_id, 'end', values=('Revenus totaux', '', f"{stats['total_revenus']:.2f} €"))
                self.rapports_treeview.insert(revenus_id, 'end', values=('Places vendues', '', stats['total_places_vendues']))
                ticket_moyen = stats['total_revenus'] / stats['total_places_vendues'] if stats['total_places_vendues'] > 0 else 0
                self.rapports_treeview.insert(revenus_id, 'end', values=('Ticket moyen', '', f"{ticket_moyen:.2f} €"))

                # --- Section Films Populaires ---
                films_id = self.rapports_treeview.insert('', 'end', text='🎬 Films Populaires', open=True)
                films_pop_sorted = sorted(stats['films_populaires'].items(), key=lambda item: item[1]['revenus'], reverse=True)
                for film, data in films_pop_sorted:
                    self.rapports_treeview.insert(films_id, 'end', text=f"  {film}", values=(f"{data['places']} places", f"{data['revenus']:.2f} €"))

                # --- Section Occupation Salles ---
                salles_id = self.rapports_treeview.insert('', 'end', text='🏛️ Taux d\'Occupation par Salle', open=True)
                for salle, data in sorted(stats['occupation_salles'].items()):
                    taux = (data['places_vendues'] / data['capacite_totale']) * 100 if data['capacite_totale'] > 0 else 0
                    self.rapports_treeview.insert(salles_id, 'end', text=f"  {salle}", values=(f"{data['places_vendues']} / {data['capacite_totale']} places", f"{taux:.1f}%"))

                # --- Section Répartition Tarifs ---
                tarifs_id = self.rapports_treeview.insert('', 'end', text='🏷️ Répartition par Tarif', open=True)
                total_places = stats['total_places_vendues']
                for tarif, places in sorted(stats['repartition_tarifs'].items()):
                    pourcentage = (places / total_places) * 100 if total_places > 0 else 0
                    self.rapports_treeview.insert(tarifs_id, 'end', text=f"  {tarif}", values=(f"{places} places", f"{pourcentage:.1f}%"))
            else:
                self.rapports_treeview.insert('', 'end', text='📭 Aucune réservation pour le moment.', values=('', 'Les rapports s\'afficheront ici.', ''))
            
            # Footer
            self.rapports_treeview.insert('', 'end', text='') # Spacer
            self.rapports_treeview.insert('', 'end', text=f"Dernière actualisation : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")

        except Exception as e:
            # Vider en cas d'erreur et afficher le message
            for i in self.rapports_treeview.get_children():
                self.rapports_treeview.delete(i)
            self.rapports_treeview.insert('', 'end', text=f"❌ Erreur lors du chargement des rapports", values=(str(e), '', ''))
            
    def load_stats(self):
        """Charge les statistiques dans le Treeview."""
        if not hasattr(self, 'stats_treeview'):
            return

        # Vider le treeview
        for i in self.stats_treeview.get_children():
            self.stats_treeview.delete(i)

        stats = self.service.get_statistiques()

        # --- Section Résumé ---
        resume_id = self.stats_treeview.insert('', 'end', text='Résumé Global', open=True)
        self.stats_treeview.insert(resume_id, 'end', text='  Total des réservations', values=(stats['total_reservations'],))
        self.stats_treeview.insert(resume_id, 'end', text='  Nombre total de places vendues', values=(stats['total_places_vendues'],))
        self.stats_treeview.insert(resume_id, 'end', text='  Chiffre d\'affaires total', values=(f"{stats['total_revenus']:.2f} €",))

        if stats['total_reservations'] > 0:
            # --- Section Films Populaires ---
            films_id = self.stats_treeview.insert('', 'end', text='🎬 Films les plus populaires (par places vendues)', open=True)
            
            # Trier les films par nombre de places
            films_pop_sorted = sorted(stats['films_populaires'].items(), key=lambda item: item[1]['places'], reverse=True)
            
            for film, data in films_pop_sorted:
                self.stats_treeview.insert(films_id, 'end', text=f"  {film}", values=(f"{data['places']} places",))
        else:
            self.stats_treeview.insert('', 'end', text='Aucune réservation pour le moment.', open=True)


def main():
    root = tk.Tk()
    app = CinemaGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
