    # film1 = Film("Inception", 148, 5, 'science fiction')
    # salle1 = Salle(1, 10, 10, "classique")



# Tentative de réservations
    # try:
    #     Reservation(film1, salle1, 40)
    #     Reservation(film1, salle1, 70)  # Salle pleine ici
    # except SallePleineException as e:
    #     print(f"❌ Erreur : {e}")
    # except FilmInexistantException as e:
    #     print(f"❌ Erreur : {e}")

import curses

def draw_buttons(stdscr, selected_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "🎬 Interface Cinéma (clic pour choisir)"
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(1, (w - len(title)) // 2, title)
    stdscr.attroff(curses.A_BOLD)

    buttons = ["👑 Admin", "🎟️ Utilisateur"]
    positions = []
    for i, text in enumerate(buttons):
        x = w // 2 - len(text) // 2
        y = h // 2 - len(buttons) + i * 2
        if i == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, text)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, text)
        positions.append((y, x, x + len(text)))
    stdscr.addstr(h - 2, 2, "↑↓ ou souris pour naviguer, clic ou Entrée pour valider, q pour quitter.")
    stdscr.refresh()
    return positions

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    selected_idx = 0

    while True:
        positions = draw_buttons(stdscr, selected_idx)
        key = stdscr.getch()

        if key == ord("q"):
            break

        elif key in [curses.KEY_UP, ord('w')]:
            selected_idx = (selected_idx - 1) % 2
        elif key in [curses.KEY_DOWN, ord('s')]:
            selected_idx = (selected_idx + 1) % 2

        elif key == curses.KEY_MOUSE:
            _, mx, my, _, bstate = curses.getmouse()
            if bstate & curses.BUTTON1_CLICKED:
                for i, (y, x1, x2) in enumerate(positions):
                    if y == my and x1 <= mx <= x2:
                        selected_idx = i
                        key = 10  # Simule un "Entrée"
                        break

        if key in [10, 13]:  # Entrée
            stdscr.clear()
            if selected_idx == 0:
                msg = "👑 Mode ADMIN sélectionné."
            else:
                msg = "🎟️ Mode UTILISATEUR sélectionné."
            stdscr.addstr(5, 5, msg)
            stdscr.addstr(7, 5, "Appuie sur une touche pour revenir au menu.")
            stdscr.refresh()
            stdscr.getch()

curses.wrapper(main)

import curses

def main(stdscr):                # stdscr = "standard screen" (fenêtre principale)
    curses.curs_set(0)           # cacher le curseur
    curses.start_color()         # activer les couleurs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    while True:
        stdscr.clear()           # efface tout l’écran
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(5, 10, "Hello, curses !")  # (y, x, texte)
        stdscr.attroff(curses.color_pair(1))
        stdscr.refresh()         # afficher les changements

        key = stdscr.getch()     # lire une touche
        if key == ord('q'):      # si 'q' → quitter
            break

curses.wrapper(main) 