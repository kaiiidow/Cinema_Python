import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from services.cinema_service import CinemaService
from models.enums import Tarif, StyleFilm, TypeSalle
from models.exceptions import CinemaException


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
        
        self.setup_window()
        self.setup_styles()
        self.create_interface()
        
    def setup_window(self):
        """Configure la fenêtre principale"""
        self.root.title("🎬 Cinéma - Système de Réservation")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # Centre la fenêtre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 1400) // 2
        y = (self.root.winfo_screenheight() - 800) // 2
        self.root.geometry(f"1400x800+{x}+{y}")
        
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
        self.create_reservation_tab(self.notebook)
        self.create_historique_tab(self.notebook)
        self.create_stats_tab(self.notebook)
        self.create_manager_tab(self.notebook)
    
    def switch_to_seances_tab(self):
        """Change vers l'onglet Séances et l'actualise"""
        self.load_seances_tree()
        self.notebook.select(0)  # L'onglet Séances est à l'index 0
    
    def switch_to_salles_tab(self):
        """Change vers l'onglet Manager Salles"""
        # L'onglet Manager est à l'index 4, puis Salles est le 3e sous-onglet
        self.notebook.select(4)  # Aller au Manager
        # On suppose que le manager_notebook est accessible
        if hasattr(self, 'manager_notebook'):
            self.manager_notebook.select(2)  # Salles est à l'index 2
        
    def create_seances_tab(self, notebook):
        """Onglet des séances"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='📅 Séances')
        
        # Header
        header = tk.Frame(frame, bg=Colors.LIGHTER)
        header.pack(fill='x', padx=20, pady=20)
        
        title = tk.Label(header, text='Séances Disponibles',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(side='left', fill='x', expand=True)
        
        ttk.Button(header, text='🔄 Actualiser',
                  command=self.load_seances_tree,
                  style='Primary.TButton').pack(side='right')
        
        # Légende
        legend = tk.Frame(frame, bg=Colors.LIGHTER)
        legend.pack(fill='x', padx=20, pady=(0, 15))
        
        legend_items = [
            ('#dcfce7', 'Places disponibles'),
            ('#fef3c7', 'Places limitées'),
            ('#fee2e2', 'Complet')
        ]
        
        for color, label in legend_items:
            item = tk.Frame(legend, bg=Colors.LIGHTER)
            item.pack(side='left', padx=(0, 20))
            
            tk.Label(item, text='■', font=('Arial', 12), fg=color, bg=Colors.LIGHTER).pack(side='left', padx=(0, 8))
            tk.Label(item, text=label, font=('Segoe UI', 9), fg=Colors.DARK, bg=Colors.LIGHTER).pack(side='left')
        
        # Tableau
        table_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        columns = ('Horaire', 'Film', 'Salle', 'Type', 'Places')
        self.seances_tree = ttk.Treeview(table_frame, columns=columns,
                                         show='headings', height=20)
        
        self.seances_tree.heading('Horaire', text='⏰ Horaire')
        self.seances_tree.heading('Film', text='🎞️ Film')
        self.seances_tree.heading('Salle', text='🏛️ Salle')
        self.seances_tree.heading('Type', text='📺 Type Salle')
        self.seances_tree.heading('Places', text='🎫 Places')
        
        self.seances_tree.column('Horaire', width=110, anchor='center')
        self.seances_tree.column('Film', width=400, anchor='w')
        self.seances_tree.column('Salle', width=120, anchor='center')
        self.seances_tree.column('Type', width=130, anchor='center')
        self.seances_tree.column('Places', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical',
                                 command=self.seances_tree.yview)
        self.seances_tree.configure(yscrollcommand=scrollbar.set)
        
        self.seances_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Tags pour les couleurs
        self.seances_tree.tag_configure('full', background='#fee2e2', foreground=Colors.DARK)
        self.seances_tree.tag_configure('low', background='#fef3c7', foreground=Colors.DARK)
        self.seances_tree.tag_configure('available', background='#dcfce7', foreground=Colors.DARK)
        
        self.load_seances_tree()
        
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
        
        title = tk.Label(scrollable, text='Créer une Réservation',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=30, pady=(30, 25))
        
        # Section 1: Sélection séance
        self.create_section(scrollable, '1️⃣ Sélectionner une Séance')
        
        list_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        list_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        self.seances_listbox = tk.Listbox(list_frame, height=6,
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
        
        # Section 2: Infos
        self.create_section(scrollable, '2️⃣ Vos Informations')
        
        info_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        # Nom
        tk.Label(info_frame, text='👤 Nom Complet',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=15, pady=(15, 5))
        self.nom_entry = ttk.Entry(info_frame, width=40)
        self.nom_entry.pack(fill='x', padx=15, pady=(0, 15))
        self.nom_entry.bind('<KeyRelease>', self.update_recap)
        
        # Places et Tarif sur la même ligne
        row_frame = tk.Frame(info_frame, bg='white')
        row_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        col1 = tk.Frame(row_frame, bg='white')
        col1.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        tk.Label(col1, text='🎫 Nombre de Places',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 5))
        self.places_spinbox = ttk.Spinbox(col1, from_=1, to=10, width=8)
        self.places_spinbox.set('1')
        self.places_spinbox.pack(anchor='w')
        self.places_spinbox.bind('<KeyRelease>', self.update_recap)
        
        col2 = tk.Frame(row_frame, bg='white')
        col2.pack(side='right', fill='x', expand=True)
        
        tk.Label(col2, text='💰 Tarif',
                font=('Segoe UI', 10, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 5))
        self.tarif_combo = ttk.Combobox(col2, state='readonly', width=20)
        tarifs = list(Tarif)
        self.tarif_combo['values'] = [f"{t.label} ({t.coeff*100:.0f}%)" for t in tarifs]
        self.tarif_combo.set(f"{tarifs[0].label} ({tarifs[0].coeff*100:.0f}%)")
        self.tarif_combo.pack(fill='x')
        self.tarif_combo.bind('<<ComboboxSelected>>', self.update_recap)
        
        # Section 3: Récapitulatif
        self.create_section(scrollable, '3️⃣ Récapitulatif')
        
        recap_frame = tk.Frame(scrollable, bg='white', relief='solid', bd=1)
        recap_frame.pack(fill='x', padx=30, pady=(0, 25))
        
        self.recap_label = tk.Label(recap_frame,
                                   text='Sélectionnez une séance...',
                                   font=('Courier', 10),
                                   fg=Colors.SECONDARY,
                                   bg='white', justify='left',
                                   wraplength=500,
                                   padx=15, pady=15)
        self.recap_label.pack(fill='both', expand=True)
        
        # Bouton réserver
        btn_frame = tk.Frame(scrollable, bg=Colors.LIGHTER)
        btn_frame.pack(fill='x', padx=30, pady=(0, 30))
        
        ttk.Button(btn_frame, text='🎫 RÉSERVER',
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
        
        self.create_manager_films_tab(self.manager_notebook)
        self.create_manager_seances_tab(self.manager_notebook)
        self.create_manager_salles_tab(self.manager_notebook)
        self.create_manager_tarifs_tab(self.manager_notebook)
        self.create_manager_rapports_tab(self.manager_notebook)
        
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
        
        tk.Label(col4, text='� Synopsis',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', pady=(0, 8))
        self.mgr_film_synopsis_short = ttk.Entry(col4, width=30)
        self.mgr_film_synopsis_short.pack(fill='x')
        
        # Synopsis complet
        tk.Label(form_frame, text='� Description complète',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(20, 8))
        self.mgr_film_synopsis = tk.Text(form_frame, height=3, width=50,
                                     font=('Segoe UI', 10), wrap=tk.WORD,
                                     relief='solid', bd=1, padx=5, pady=5)
        self.mgr_film_synopsis.pack(fill='x', padx=20, pady=(0, 20))
        
        # Bouton
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(btn_frame, text='➕ Ajouter Film',
                  command=self.mgr_creer_film,
                  style='Success.TButton').pack(side='right')
        
    def create_manager_seances_tab(self, notebook):
        """Manager: Gestion des séances"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🎥 Séances')
        
        title = tk.Label(frame, text='📅 Créer une Séance',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 30))
        
        # Form
        form_frame = tk.Frame(frame, bg='white', relief='solid', bd=1)
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
        
    def create_manager_salles_tab(self, notebook):
        """Manager: Gestion des salles"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='🏛️ Salles')
        
        title = tk.Label(frame, text='🏢 Créer une Salle',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 30))
        
        form_frame = tk.Frame(frame, bg='white', relief='solid', bd=1)
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
        
        # Supplément
        tk.Label(form_frame, text='💰 Supplément prix (€)',
                font=('Segoe UI', 11, 'bold'),
                fg=Colors.DARK, bg='white').pack(anchor='w', padx=20, pady=(0, 8))
        self.mgr_salle_supplement = ttk.Spinbox(form_frame, from_=0, to=20, increment=0.5, width=12)
        self.mgr_salle_supplement.set('0')
        self.mgr_salle_supplement.pack(anchor='w', padx=20, pady=(0, 20))
        
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))
        ttk.Button(btn_frame, text='➕ Ajouter Salle',
                  command=self.mgr_creer_salle,
                  style='Success.TButton').pack(side='right')
        
    def create_manager_tarifs_tab(self, notebook):
        """Manager: Vue des tarifs"""
        frame = ttk.Frame(notebook, style='Content.TFrame')
        notebook.add(frame, text='💰 Tarifs')
        
        title = tk.Label(frame, text='💳 Tarifs Actuels',
                        font=('Segoe UI', 18, 'bold'),
                        fg=Colors.PRIMARY, bg=Colors.LIGHTER)
        title.pack(fill='x', padx=20, pady=(20, 30))
        
        # Tableau des tarifs
        content_frame = tk.Frame(frame, bg=Colors.LIGHTER)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.tarifs_text = scrolledtext.ScrolledText(
            content_frame, height=20, font=('Courier', 11),
            bg='white', relief='solid', bd=1, padx=10, pady=10)
        self.tarifs_text.pack(fill='both', expand=True)
        
        self.load_tarifs()
        
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
        
    def load_seances_tree(self):
        """Charge le tableau"""
        for item in self.seances_tree.get_children():
            self.seances_tree.delete(item)
            
        for seance in self.service.get_toutes_seances():
            horaire = seance.horaire.strftime('%H:%M')
            film = seance.film.titre
            salle = seance.salle.nom
            type_salle = seance.salle.type_salle.value
            dispo = f"{seance.places_disponibles}/{seance.salle.capacite}"
            
            if seance.places_disponibles == 0:
                tag = 'full'
            elif seance.places_disponibles < 10:
                tag = 'low'
            else:
                tag = 'available'
                
            self.seances_tree.insert('', 'end',
                                   values=(horaire, film, salle, type_salle, dispo),
                                   tags=(tag,))
                                   
    def load_seances_reservation(self):
        """Charge la liste"""
        self.seances_listbox.delete(0, tk.END)
        
        for i, seance in enumerate(self.service.get_toutes_seances()):
            status = "COMPLET" if seance.est_complete else f"{seance.places_disponibles} places"
            self.seances_listbox.insert(tk.END,
                f"[{seance.horaire.strftime('%H:%M')}] {seance.film.titre} - {status}")
                
    def on_seance_select(self, event):
        """Gère la sélection"""
        selection = self.seances_listbox.curselection()
        if selection:
            self.seance_index = selection[0]
            self.seance_selectionnee = self.service.get_toutes_seances()[self.seance_index]
            self.update_recap()
            
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
        tarif = list(Tarif)[0]
        for t in Tarif:
            if t.label in tarif_text:
                tarif = t
                break
                
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
        tarif = None
        for t in Tarif:
            if t.label in tarif_text:
                tarif = t
                break
                
        if not tarif:
            messagebox.showerror('Erreur', 'Tarif invalide')
            return
            
        self._reservation_en_cours = {
            "nom": nom,
            "nb_places": nb_places,
            "tarif": tarif,
        }
        
        self.open_seat_selection()
        
    def open_seat_selection(self):
        """Fenêtre de sélection des places"""
        seance = self.seance_selectionnee
        if not seance or not self._reservation_en_cours:
            return
            
        nb = self._reservation_en_cours["nb_places"]
        
        window = tk.Toplevel(self.root)
        window.title(f'Sélectionnez {nb} place(s)')
        window.geometry('800x600')
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
        
        # Grid de places
        grid_frame = tk.Frame(window, bg=Colors.LIGHT)
        grid_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
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
            reservation = self.service.creer_reservation(
                self.seance_index, nom, nb, tarif, numeros_places=places)
                
            window.destroy()
            
            messagebox.showinfo('Succès',
                f"""🎉 Réservation confirmée!

🎫 Ticket: {reservation.id}
👤 Client: {nom}
🎬 Film: {reservation.seance.film.titre}
🪑 Sièges: {', '.join(str(p) for p in sorted(places))}
💰 Total: {reservation.prix_total} €

⏰ Présentez-vous 15 minutes avant!""")
            
            self.nom_entry.delete(0, tk.END)
            self.places_spinbox.set('1')
            self.seance_selectionnee = None
            self._reservation_en_cours = None
            
            self.load_seances_tree()
            self.load_seances_reservation()
            self.load_reservations()
            self.load_stats()
            self.update_recap()
            
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
                    
            if not genre_enum:
                messagebox.showerror('Erreur', f'Genre "{genre_str}" non trouve')
                return
                
            film = Film(titre=nom, duree=duree, style=genre_enum, note=note)
            self.service.films.append(film)
            
            messagebox.showinfo('Succes', 
                f'Film: {nom}\nDuree: {duree}min\nGenre: {genre_str}\nNote: {note}/10\n\nMaintenant, creez une salle!')
            
            # Reinitialiser le formulaire
            self.mgr_film_nom.delete(0, tk.END)
            self.mgr_film_duree.set('120')
            self.mgr_film_genre.set(self.mgr_film_genre['values'][0] if self.mgr_film_genre['values'] else '')
            self.mgr_film_note.set('7.0')
            
            # Actualiser les listes
            self.mgr_seance_film['values'] = [f.titre for f in self.service.films]
            self.load_manager_films_list()
            self.switch_to_salles_tab()
            
        except Exception as e:
            messagebox.showerror('Erreur systeme', f'Impossible de creer le film:\n{str(e)}')
    
    def load_manager_films_list(self):
        """Actualise la liste des films"""
        if not hasattr(self, 'mgr_films_listbox'):
            return
        
        self.mgr_films_listbox.delete(0, tk.END)
        for film in self.service.films:
            self.mgr_films_listbox.insert(tk.END, 
                f"{film.titre} ({film.duree}min) - {film.style.value} - Note: {film.note}/10")
    
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
            supplement = float(self.mgr_salle_supplement.get())
            if supplement < 0:
                messagebox.showwarning('⚠️ Supplément invalide', 'Le supplément ne peut pas être négatif')
                return
            if supplement > 20:
                messagebox.showwarning('⚠️ Supplément excessif', 'Le supplément maximal est de 20€')
                return
        except ValueError:
            messagebox.showerror('❌ Format invalide', 'Le supplément doit être un nombre (ex: 5.50)')
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
            self.mgr_salle_supplement.set('0')
            
            # Actualiser les listes
            self.mgr_seance_salle['values'] = [s.nom for s in self.service.salles]
            
            # Aller au Manager -> Seances
            if hasattr(self, 'manager_notebook'):
                self.notebook.select(4)  # Manager
                self.manager_notebook.select(1)  # Seances
            
        except Exception as e:
            messagebox.showerror('❌ Erreur système', f'Impossible de créer la salle:\n{str(e)}')
    
    def load_tarifs(self):
        """Charge la liste des tarifs"""
        try:
            self.tarifs_text.delete(1.0, tk.END)
            
            content = "💳 TARIFS ACTUELS\n"
            content += "=" * 70 + "\n\n"
            content += "Prix de base: 10.00€\n\n"
            content += "Type de tarif            Coefficient          Prix\n"
            content += "-" * 70 + "\n"
            
            PRIX_BASE = 10.00
            for tarif in Tarif:
                prix = PRIX_BASE * tarif.coeff
                coeff_pct = f"{tarif.coeff:.0%}"
                content += f"{tarif.label:25} {coeff_pct:>15}      {prix:>7.2f}€\n"
            
            content += "\n" + "=" * 70
            self.tarifs_text.insert(tk.END, content)
        except Exception as e:
            self.tarifs_text.delete(1.0, tk.END)
            self.tarifs_text.insert(tk.END, f"❌ Erreur: {e}")
    
    def load_rapports(self):
        """Charge les rapports manager"""
        try:
            self.rapports_text.delete(1.0, tk.END)
            
            content = "📊 RAPPORTS DU CINÉMA\n"
            content += "=" * 75 + "\n\n"
            
            # Résumé général
            nb_films = len(self.service.films)
            nb_salles = len(self.service.salles)
            nb_seances = len(self.service.get_toutes_seances())
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
        
        total_seances = len(self.service.get_toutes_seances())
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
