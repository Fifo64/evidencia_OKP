import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Toplevel
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
import os

DB_PATH = "evidence.db"
PHOTO_DIR = "photos"
LOGO_PATH = "logo.png"

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
        foto1 TEXT,
        foto2 TEXT,
        foto3 TEXT,
        foto4 TEXT
    )''')
    conn.commit()
    conn.close()

# Splash screen
def splash_screen():
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("400x200+500+300")
    splash.configure(bg="black")
    tk.Label(splash, text="Načítavam aplikáciu...", font=("Times New Roman", 14), fg="white", bg="black").pack(pady=50)
    progress = ttk.Progressbar(splash, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)
    for i in range(100):
        progress["value"] = i
        splash.update()
        splash.after(15)
    splash.destroy()

# Pridanie osoby
def add_person():
    fotos = [photo_vars[i].get() for i in range(4)]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO osoby (meno, priezvisko, rodne_cislo, datum_narodenia, trvale_bydlisko, iny_pobyt,
                 popis_cinu, dalsie_informacie, prezyvka, foto1, foto2, foto3, foto4)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (meno_var.get(), priezvisko_var.get(), rodne_cislo_var.get(), datum_narodenia_var.get(),
               trvale_bydlisko_var.get(), iny_pobyt_var.get(), popis_cinu_text.get(1.0, tk.END),
               dalsie_informacie_text.get(1.0, tk.END), prezyvka_var.get(), *fotos))
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
        tree.insert("", "end", values=row[:-4])
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

# Detail osoby
def view_details():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Výstraha", "Nevybrali ste žiadnu osobu.")
        return
    item = tree.item(selected[0])["values"]
    detail_win = Toplevel()
    detail_win.title("Detail osoby")
    detail_win.configure(bg="black")
    
    fields = [("Meno", item[1]), ("Priezvisko", item[2]), ("Rodné číslo", item[3]),
              ("Dátum narodenia", item[4]), ("Trvalé bydlisko", item[5]), ("Iné bydlisko", item[6]),
              ("Popis činu", item[7]), ("Ďalšie informácie", item[8]), ("Prezývka", item[9])]
    for i, (label, value) in enumerate(fields):
        tk.Label(detail_win, text=f"{label}: {value}", fg="white", bg="black").pack(anchor="w")

    # Fotografie
    for i in range(4):
        if item[10 + i]:
            img = Image.open(item[10 + i])
            img = img.resize((150, 150))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(detail_win, image=photo, bg="black")
            label.image = photo
            label.pack()

# Vymazanie polí
def clear_fields():
    for var in [meno_var, priezvisko_var, rodne_cislo_var, datum_narodenia_var, trvale_bydlisko_var, iny_pobyt_var, prezyvka_var]:
        var.set("")
    for photo_var in photo_vars:
        photo_var.set("")
    popis_cinu_text.delete(1.0, tk.END)
    dalsie_informacie_text.delete(1.0, tk.END)

# Hlavné okno
app = tk.Tk()
app.title("Evidencia osôb")
app.geometry("1500x800")
app.configure(bg="black")
splash_screen()

# Premenné
meno_var = tk.StringVar()
priezvisko_var = tk.StringVar()
rodne_cislo_var = tk.StringVar()
datum_narodenia_var = tk.StringVar()
trvale_bydlisko_var = tk.StringVar()
iny_pobyt_var = tk.StringVar()
prezyvka_var = tk.StringVar()
photo_vars = [tk.StringVar() for _ in range(4)]

# Formulár
tk.Label(app, text="Meno:", fg="white", bg="black").grid(row=1, column=0)
tk.Entry(app, textvariable=meno_var).grid(row=1, column=1)
# Rovnaké pre ostatné polia...

# Tlačidlá
tk.Button(app, text="Pridať osobu", command=add_person).grid(row=10, column=0)
tk.Button(app, text="Vymazať osobu", command=delete_person).grid(row=10, column=1)
tk.Button(app, text="Detail osoby", command=view_details).grid(row=10, column=2)

# Tabuľka
columns = ["ID", "Meno", "Priezvisko", "Rodné číslo", "Dátum narodenia", "Trvalé bydlisko", "Iné bydlisko"]
tree = ttk.Treeview(app, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.grid(row=11, column=0, columnspan=4)

init_db()
load_data()
app.mainloop()

