import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Toplevel
from PIL import Image, ImageTk
import sqlite3
import os

DB_PATH = "evidence.db"
PHOTO_DIR = "photos"
LOGO_PATH = "logo.png"  # Cesta k logu

# Inicializácia databázy a priečinka na fotografie
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

# Pridanie osoby
def add_person():
    foto_path = photo_var.get()
    if foto_path:
        file_name = os.path.join(PHOTO_DIR, os.path.basename(foto_path))
        Image.open(foto_path).save(file_name)
        foto_path = file_name
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO osoby (meno, priezvisko, rodne_cislo, datum_narodenia, trvale_bydlisko, iny_pobyt,
        popis_cinu, dalsie_informacie, prezyvka, foto_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (meno_var.get(), priezvisko_var.get(), rodne_cislo_var.get(), datum_narodenia_var.get(),
         trvale_bydlisko_var.get(), iny_pobyt_var.get(), popis_cinu_text.get(1.0, tk.END),
         dalsie_informacie_text.get(1.0, tk.END), prezyvka_var.get(), foto_path))
    conn.commit()
    conn.close()
    load_data()
    clear_fields()

# Načítanie údajov
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM osoby")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", "end", values=row[:-1])
    conn.close()

# Mazanie osoby
def delete_person():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Výstraha", "Nevybrali ste žiadnu osobu.")
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for item in selected:
        person_id = tree.item(item)["values"][0]
        c.execute("DELETE FROM osoby WHERE id=?", (person_id,))
    conn.commit()
    conn.close()
    load_data()

# Úprava osoby
def edit_person():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Výstraha", "Nevybrali ste žiadnu osobu.")
        return
    item = tree.item(selected[0])["values"]
    person_id = item[0]

    # Vyplnenie údajov do formulára
    meno_var.set(item[1])
    priezvisko_var.set(item[2])
    rodne_cislo_var.set(item[3])
    datum_narodenia_var.set(item[4])
    trvale_bydlisko_var.set(item[5])
    iny_pobyt_var.set(item[6])
    popis_cinu_text.delete(1.0, tk.END)
    popis_cinu_text.insert(tk.END, item[7])
    dalsie_informacie_text.delete(1.0, tk.END)
    dalsie_informacie_text.insert(tk.END, item[8])
    prezyvka_var.set(item[9])

    # Aktualizácia
    def update_person():
        foto_path = photo_var.get()
        if foto_path:
            file_name = os.path.join(PHOTO_DIR, os.path.basename(foto_path))
            Image.open(foto_path).save(file_name)
            foto_path = file_name
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''UPDATE osoby SET meno=?, priezvisko=?, rodne_cislo=?, datum_narodenia=?, 
                     trvale_bydlisko=?, iny_pobyt=?, popis_cinu=?, dalsie_informacie=?, prezyvka=?, foto_path=?
                     WHERE id=?''',
                  (meno_var.get(), priezvisko_var.get(), rodne_cislo_var.get(), datum_narodenia_var.get(),
                   trvale_bydlisko_var.get(), iny_pobyt_var.get(), popis_cinu_text.get(1.0, tk.END),
                   dalsie_informacie_text.get(1.0, tk.END), prezyvka_var.get(), foto_path, person_id))
        conn.commit()
        conn.close()
        load_data()
        clear_fields()

    tk.Button(app, text="Uložiť zmeny", command=update_person).grid(row=11, column=2)

# Vyhľadávanie
def search():
    keyword = search_var.get()
    criterion = search_criteria_var.get()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = f"SELECT * FROM osoby WHERE {criterion} LIKE ?"
    c.execute(query, ('%' + keyword + '%',))
    rows = c.fetchall()
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", "end", values=row[:-1])
    conn.close()

# Vymazanie polí
def clear_fields():
    for var in [meno_var, priezvisko_var, rodne_cislo_var, datum_narodenia_var, trvale_bydlisko_var, iny_pobyt_var, prezyvka_var, photo_var]:
        var.set("")
    popis_cinu_text.delete(1.0, tk.END)
    dalsie_informacie_text.delete(1.0, tk.END)

# GUI aplikácie
app = tk.Tk()
app.title("Evidencia osôb")
app.geometry("1500x800")
app.configure(bg="black")

# Premenné
meno_var = tk.StringVar()
priezvisko_var = tk.StringVar()
rodne_cislo_var = tk.StringVar()
datum_narodenia_var = tk.StringVar()
trvale_bydlisko_var = tk.StringVar()
iny_pobyt_var = tk.StringVar()
prezyvka_var = tk.StringVar()
photo_var = tk.StringVar()
search_var = tk.StringVar()
search_criteria_var = tk.StringVar(value="meno")

# Pridanie log v rohoch
logo = ImageTk.PhotoImage(Image.open(LOGO_PATH).resize((50, 50)))
tk.Label(app, image=logo, bg="black").place(x=0, y=0)
tk.Label(app, image=logo, bg="black").place(x=1450, y=0)
tk.Label(app, image=logo, bg="black").place(x=0, y=750)
tk.Label(app, image=logo, bg="black").place(x=1450, y=750)

# Vyhľadávacie pole
tk.Label(app, text="HĽADAŤ OSOBU", fg="white", bg="black", font=("Times New Roman", 12)).grid(row=0, column=3, columnspan=2)
tk.Entry(app, textvariable=search_var, width=30).grid(row=1, column=3, padx=5, pady=5)
ttk.Combobox(app, textvariable=search_criteria_var, values=["meno", "priezvisko", "prezyvka", "rodne_cislo", "datum_narodenia", "popis_cinu", "dalsie_informacie"]).grid(row=1, column=4)
tk.Button(app, text="Hľadať", command=search).grid(row=1, column=5, padx=5, pady=5)

# Formulár
fields = [("Meno", meno_var), ("Priezvisko", priezvisko_var), ("Rodné číslo", rodne_cislo_var),
          ("Dátum narodenia", datum_narodenia_var), ("Trvalé bydlisko", trvale_bydlisko_var),
          ("Iné bydlisko", iny_pobyt_var), ("Prezývka", prezyvka_var)]

for i, (label_text, var) in enumerate(fields):
    tk.Label(app, text=label_text, font=("Times New Roman", 12), fg="white", bg="black").grid(row=i+2, column=0, sticky="e")
    tk.Entry(app, textvariable=var).grid(row=i+2, column=1)

# Scrollovacie textové polia
tk.Label(app, text="Popis činu", fg="white", bg="black").grid(row=9, column=0, sticky="e")
popis_cinu_text = scrolledtext.ScrolledText(app, width=40, height=4)
popis_cinu_text.grid(row=9, column=1)

tk.Label(app, text="Ďalšie informácie", fg="white", bg="black").grid(row=10, column=0, sticky="e")
dalsie_informacie_text = scrolledtext.ScrolledText(app, width=40, height=4)
dalsie_informacie_text.grid(row=10, column=1)

tk.Button(app, text="Nahrať fotografiu", command=lambda: photo_var.set(filedialog.askopenfilename())).grid(row=11, column=0)
tk.Entry(app, textvariable=photo_var, state='readonly').grid(row=11, column=1)

# Tlačidlá
tk.Button(app, text="Pridať osobu", command=add_person).grid(row=12, column=0)
tk.Button(app, text="Vymazať osobu", command=delete_person).grid(row=12, column=1)
tk.Button(app, text="Upraviť osobu", command=edit_person).grid(row=12, column=2)

# Tabuľka
columns = ["ID", "Meno", "Priezvisko", "Rodné číslo", "Dátum narodenia", "Trvalé bydlisko", "Iné bydlisko", "Popis činu", "Ďalšie informácie", "Prezývka"]
tree = ttk.Treeview(app, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)
tree.grid(row=13, column=0, columnspan=6, pady=10)

init_db()
load_data()
app.mainloop()
