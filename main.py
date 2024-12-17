import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Toplevel
from PIL import Image, ImageTk
import sqlite3
import os
import time

# Cesty k súborom a databáze
DB_PATH = "evidence.db"
PHOTO_DIR = "photos"
LOGO_PATH = "logo.png"

# Inicializácia databázy a priečinkov
def init_db():
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS osoby (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meno TEXT,
        priezvisko TEXT,
        rodne_cislo TEXT,
        datum_narodenia TEXT,
        trvale_bydlisko TEXT,
        iny_pobyt TEXT,
        popis_cinu TEXT,
        dalsie_informacie TEXT,
        prezyvka TEXT,
        foto_path TEXT
    )''')
    conn.commit()
    conn.close()

# Úvodná obrazovka s progress barom
def splash_screen():
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("500x300")
    splash.configure(bg="black")

    # Nadpis
    tk.Label(splash, text="Načítavanie Evidencie osôb OKP OR PZ KE", 
             fg="white", bg="black", font=("Times New Roman", 16)).pack(pady=20)

    # Progress bar
    progress = ttk.Progressbar(splash, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=30)

    # Simulácia načítavania
    for i in range(101):
        progress['value'] = i
        splash.update()
        time.sleep(0.02)  # Čas načítania

    splash.destroy()

# Hlavná aplikácia
def main_app():
    app = tk.Tk()
    app.title("Evidencia osôb")
    app.geometry("1500x800")
    app.configure(bg="black")

    # Premenné pre formulár
    meno_var = tk.StringVar()
    priezvisko_var = tk.StringVar()
    rodne_cislo_var = tk.StringVar()
    datum_narodenia_var = tk.StringVar()
    trvale_bydlisko_var = tk.StringVar()
    iny_pobyt_var = tk.StringVar()
    prezyvka_var = tk.StringVar()
    photo_var = tk.StringVar()

    # Hlavný nadpis
    tk.Label(app, text="Evidencia osôb OKP OR PZ KE", fg="white", bg="black", font=("Times New Roman", 18)).pack(pady=10)

    # Formulár na pridanie údajov
    fields = [("Meno", meno_var), ("Priezvisko", priezvisko_var), ("Rodné číslo", rodne_cislo_var),
              ("Dátum narodenia", datum_narodenia_var), ("Trvalé bydlisko", trvale_bydlisko_var),
              ("Iné bydlisko", iny_pobyt_var), ("Prezývka", prezyvka_var)]

    for i, (label, var) in enumerate(fields):
        tk.Label(app, text=label, fg="white", bg="black", font=("Times New Roman", 12)).place(x=50, y=80 + i * 40)
        tk.Entry(app, textvariable=var).place(x=200, y=80 + i * 40, width=300)

    # Tabuľka
    columns = ["ID", "Meno", "Priezvisko", "Rodné číslo", "Dátum narodenia", "Trvalé bydlisko", "Iné bydlisko", "Popis činu", "Ďalšie informácie", "Prezývka"]
    tree = ttk.Treeview(app, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.place(x=50, y=350, width=1400, height=400)

    # Tlačidlá
    tk.Button(app, text="Pridať osobu", bg="white", fg="black").place(x=600, y=80)
    tk.Button(app, text="Vymazať osobu", bg="white", fg="black").place(x=600, y=120)
    tk.Button(app, text="Upraviť osobu", bg="white", fg="black").place(x=600, y=160)

    app.mainloop()

# Spustenie aplikácie
if __name__ == "__main__":
    init_db()
    splash_screen()
    main_app()
