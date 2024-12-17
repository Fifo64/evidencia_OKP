import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os

# Nastavenie základných ciest
DB_PATH = "evidence.db"
PHOTO_DIR = "photos"

# Inicializácia databázy
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
                    dalsie_informacie TEXT
                )''')
    conn.commit()
    conn.close()

# Funkcia na pridanie osoby
def add_person():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO osoby (meno, priezvisko, rodne_cislo, datum_narodenia, 
                                    trvale_bydlisko, iny_pobyt, popis_cinu, dalsie_informacie)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (meno_var.get(), priezvisko_var.get(), rodne_cislo_var.get(), datum_narodenia_var.get(),
               trvale_bydlisko_var.get(), iny_pobyt_var.get(), popis_cinu_text.get(1.0, tk.END),
               dalsie_informacie_text.get(1.0, tk.END)))
    conn.commit()
    conn.close()
    load_data()
    clear_fields()

# Funkcia na načítanie údajov do tabuľky
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, meno, priezvisko FROM osoby")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

# Vymazanie polí formulára
def clear_fields():
    for var in [meno_var, priezvisko_var, rodne_cislo_var, datum_narodenia_var, trvale_bydlisko_var, iny_pobyt_var]:
        var.set("")
    popis_cinu_text.delete(1.0, tk.END)
    dalsie_informacie_text.delete(1.0, tk.END)

# Hlavné okno
app = tk.Tk()
app.title("Evidencia osôb")
app.geometry("1200x600")
app.configure(bg="white")

# Premenné
meno_var = tk.StringVar()
priezvisko_var = tk.StringVar()
rodne_cislo_var = tk.StringVar()
datum_narodenia_var = tk.StringVar()
trvale_bydlisko_var = tk.StringVar()
iny_pobyt_var = tk.StringVar()

# Formulár
tk.Label(app, text="Meno").grid(row=0, column=0)
tk.Entry(app, textvariable=meno_var).grid(row=0, column=1)

tk.Label(app, text="Priezvisko").grid(row=1, column=0)
tk.Entry(app, textvariable=priezvisko_var).grid(row=1, column=1)

tk.Label(app, text="Rodné číslo").grid(row=2, column=0)
tk.Entry(app, textvariable=rodne_cislo_var).grid(row=2, column=1)

tk.Label(app, text="Popis činu").grid(row=3, column=0)
popis_cinu_text = tk.Text(app, height=4, width=30)
popis_cinu_text.grid(row=3, column=1)

# Tlačidlá
tk.Button(app, text="Pridať osobu", command=add_person).grid(row=4, column=0, columnspan=2)

# Tabuľka
columns = ("ID", "Meno", "Priezvisko")
tree = ttk.Treeview(app, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=5, column=0, columnspan=2)

init_db()
load_data()
app.mainloop()
