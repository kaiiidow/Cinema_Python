# import curses

# def main(stdscr): # stdscr = "standard screen"
#     curses.curs_set(0)
#     curses.start_color()
#     curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
#     while
    
# curses.wrapper(main) 
# import curses

# def main(stdscr):                # stdscr = "standard screen" (fenêtre principale)
#     curses.curs_set(0)           # cacher le curseur
#     curses.start_color()         # activer les couleurs
#     curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

#     while True:
#         stdscr.clear()           # efface tout l’écran
#         stdscr.attron(curses.color_pair(1))
#         stdscr.addstr(5, 10, "Hello, curses !")  # (y, x, texte)
#         stdscr.attroff(curses.color_pair(1))
#         stdscr.refresh()         # afficher les changements

#         key = stdscr.getch()     # lire une touche
#         if key == ord('q'):      # si 'q' → quitter
#             break

# curses.wrapper(main) 

import curses

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    menu = ["🎬 Films", "📅 Séances", "🪑 Salles", "🎟️ Réservations", "Quitter"]
    current = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        title = "CINÉMA - Tableau de bord"
        stdscr.addstr(1, (w - len(title)) // 2, title, curses.A_BOLD)

        for i, item in enumerate(menu):
            x = w // 2 - len(item) // 2
            y = h // 2 - len(menu) // 2 + i
            if i == current:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            current = (current - 1) % len(menu)
        elif key == curses.KEY_DOWN:
            current = (current + 1) % len(menu)
        elif key in [10, 13]:  # Entrée
            if menu[current] == "Quitter":
                break
            stdscr.addstr(h - 2, 2, f"Tu as sélectionné : {menu[current]}")
            stdscr.refresh()
            stdscr.getch()  # attendre une touche avant retour
        elif key == ord('q'):
            break

curses.wrapper(main)
