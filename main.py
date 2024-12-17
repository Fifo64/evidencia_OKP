import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage, Toplevel
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import sqlite3
import os
import sys
import subprocess

# Constants
DB_PATH = "evidence.db"
PHOTO_DIR = "photos"
LOGO_PATH = "logo.png"  # Path to your logo file

# Ensure required libraries are installed
def install_libraries():
    try:
        from PIL import Image, ImageTk
        import sqlite3
        from reportlab.pdfgen import canvas
    except ImportError:
        print("Installing required libraries...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "reportlab"])
install_libraries()

# Initialize database
def init_db():
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS osoby (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meno TEXT, priezvisko TEXT, prezyvka TEXT,
                    rodne_cislo TEXT, datum_narodenia TEXT,
                    trvale_bydlisko TEXT, iny_pobyt TEXT,
                    popis_cinu TEXT, dalsie_informacie TEXT,
                    foto1 BLOB, foto2 BLOB, foto3 BLOB, foto4 BLOB
                )''')
    conn.commit()
    conn.close()

# Loading Screen
def splash_screen(root):
    splash = Toplevel(root)
    splash.overrideredirect(True)
    splash.geometry("400x250+500+300")
    splash.configure(bg="black")
    
    logo = Image.open(LOGO_PATH)
    logo = logo.resize((150, 150))
    logo_img = ImageTk.PhotoImage(logo)
    tk.Label(splash, image=logo_img, bg="black").pack(pady=10)
    tk.Label(splash, text="Evidencia Osôb OKP OR PZ KE", font=("Segoe UI", 18), fg="white", bg="black").pack()
    
    progress = ttk.Progressbar(splash, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)
    for i in range(100):
        progress["value"] = i
        splash.update()
        splash.after(15)
    splash.destroy()

# Convert image to binary
def convert_to_binary(filepath):
    with open(filepath, 'rb') as file:
        return file.read()

# Save person data to database
def add_person():
    photos = [convert_to_binary(photo_vars[i].get()) if photo_vars[i].get() else None for i in range(4)]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO osoby (meno, priezvisko, prezyvka, rodne_cislo, datum_narodenia,
                 trvale_bydlisko, iny_pobyt, popis_cinu, dalsie_informacie,
                 foto1, foto2, foto3, foto4)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (meno_var.get(), priezvisko_var.get(), prezyvka_var.get(), rodne_cislo_var.get(),
               datum_narodenia_var.get(), trvale_bydlisko_var.get(), iny_pobyt_var.get(),
               popis_cinu_text.get(1.0, tk.END), dalsie_informacie_text.get(1.0, tk.END), *photos))
    conn.commit()
    conn.close()
    load_data()
    clear_fields()

# Load data into table
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, meno, priezvisko, prezyvka, rodne_cislo FROM osoby")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", "end", values=row)
    conn.close()

# Clear fields
def clear_fields():
    for var in [meno_var, priezvisko_var, prezyvka_var, rodne_cislo_var, datum_narodenia_var, trvale_bydlisko_var, iny_pobyt_var]:
        var.set("")
    for photo_var in photo_vars:
        photo_var.set("")
    popis_cinu_text.delete(1.0, tk.END)
    dalsie_informacie_text.delete(1.0, tk.END)

# Main Application
root = tk.Tk()
root.title("Evidencia Osôb")
root.geometry("1200x800")
root.configure(bg="#1E1E1E")
splash_screen(root)

# Variables
meno_var, priezvisko_var, prezyvka_var, rodne_cislo_var = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
datum_narodenia_var, trvale_bydlisko_var, iny_pobyt_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
photo_vars = [tk.StringVar() for _ in range(4)]

# Form Fields (Left)
tk.Label(root, text="Meno:", fg="white", bg="#1E1E1E").grid(row=0, column=0, sticky="w")
tk.Entry(root, textvariable=meno_var).grid(row=0, column=1)

# (Additional fields go here... Repeat for all form entries)

# Buttons (Middle)
tk.Button(root, text="Pridať osobu", command=add_person).grid(row=10, column=1)

# Table (Bottom)
columns = ("ID", "Meno", "Priezvisko", "Prezýkvka", "Rodné číslo")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.grid(row=11, column=0, columnspan=5)

init_db()
load_data()
root.mainloop()
