import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Toplevel
from PIL import Image, ImageTk
import sqlite3
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
        popis_cinu TEXT,
        dalsie_informacie TEXT,
        prezyvka TEXT,
        foto_paths TEXT
    )''')
    conn.commit()
    conn.close()

# Pridanie osoby
def add_person():
    foto_paths = []
    for _ in range(4):
        file_path = filedialog.askopenfilename(title="Vyberte fotografiu", filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(PHOTO_DIR, filename)
            Image.open(file_path).save(dest_path)
            foto_paths.append(dest_path)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO osoby (meno, priezvisko, rodne_cislo, datum_narodenia, popis_cinu, dalsie_informacie, prezyvka, foto_paths)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (meno_var.get(), priezvisko_var.get(), rodne_cislo_var.get(), datum_narodenia_var.get(),
               popis_cinu_text.get(1.0, tk.END), dalsie_informacie_text.get(1.0, tk.END), prezyvka_var.get(),
               ";".join(foto_paths)))
    conn.commit()
    conn.close()
    load_data()

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

# Kliknutie na riadok - zobrazenie detailov
def show_details():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Výstraha", "Nevybrali ste žiadnu osobu.")
        return

    item = tree.item(selected_item[0])['values']
    detail_window = Toplevel(app)
    detail_window.title("Detail osoby")
    detail_window.geometry("600x400")

    tk.Label(detail_window, text=f"Meno: {item[1]}").pack(pady=5)
    tk.Label(detail_window, text=f"Priezvisko: {item[2]}").pack(pady=5)
    tk.Label(detail_window, text=f"Rodné číslo: {item[3]}").pack(pady=5)

    # Načítanie fotografií
    foto_paths = item[-1].split(";")
    for path in foto_paths:
        if os.path.exists(path):
            img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
            tk.Label(detail_window, image=img).pack()
            detail_window.mainloop()

# Tlač do PDF
def print_to_pdf():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Výstraha", "Nevybrali ste žiadnu osobu.")
        return

    item = tree.item(selected_item[0])['values']
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])

    if file_path:
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, f"Meno: {item[1]}")
        c.drawString(100, 730, f"Priezvisko: {item[2]}")
        c.drawString(100, 710, f"Rodné číslo: {item[3]}")
        c.save()
        messagebox.showinfo("Úspech", "PDF bolo úspešne vygenerované!")

# GUI aplikácie
app = tk.Tk()
app.title("Evidencia osôb")
app.geometry("1500x800")
app.configure(bg="black")

meno_var = tk.StringVar()
priezvisko_var = tk.StringVar()
rodne_cislo_var = tk.StringVar()
datum_narodenia_var = tk.StringVar()
prezyvka_var = tk.StringVar()

# Pridanie loga a nadpisu
tk.Label(app, text="Evidencia osôb OKP OR PZ KE", bg="black", fg="white", font=("Times New Roman", 18)).pack(pady=10)

# Formulár
fields = [("Meno", meno_var), ("Priezvisko", priezvisko_var), ("Rodné číslo", rodne_cislo_var), ("Dátum narodenia", datum_narodenia_var), ("Prezývka", prezyvka_var)]
for i, (label, var) in enumerate(fields):
    tk.Label(app, text=label, fg="white", bg="black").place(x=50, y=80 + i * 40)
    tk.Entry(app, textvariable=var).place(x=200, y=80 + i * 40)

# Textové polia
popis_cinu_text = scrolledtext.ScrolledText(app, width=40, height=4)
popis_cinu_text.place(x=200, y=280)
tk.Label(app, text="Popis činu", fg="white", bg="black").place(x=50, y=280)

dalsie_informacie_text = scrolledtext.ScrolledText(app, width=40, height=4)
dalsie_informacie_text.place(x=200, y=400)
tk.Label(app, text="Ďalšie informácie", fg="white", bg="black").place(x=50, y=400)

# Tlačidlá
tk.Button(app, text="Pridať osobu", command=add_person).place(x=200, y=550)
tk.Button(app, text="Zobraziť detaily", command=show_details).place(x=300, y=550)
tk.Button(app, text="Tlačiť do PDF", command=print_to_pdf).place(x=450, y=550)

# Tabuľka
columns = ["ID", "Meno", "Priezvisko", "Rodné číslo", "Dátum narodenia", "Popis činu", "Ďalšie informácie", "Prezývka"]
tree = ttk.Treeview(app, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)
tree.place(x=50, y=600, width=1400, height=200)

init_db()
load_data()
app.mainloop()

