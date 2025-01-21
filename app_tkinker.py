import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import secrets
import string
import datetime

# biblioteka do szyfrowania/odszyfrowywania
from cryptography.fernet import Fernet

# Nazwa pliku, w którym przechowujemy zaszyfrowane hasła
HISTORY_FILE = "password_history.json"
# Nazwa pliku z kluczem do szyfrowania/odszyfrowywania
KEY_FILE = "secret.key"

# ------------------------------------
# 1. Obsługa klucza szyfrującego
# ------------------------------------

def load_or_create_key():
    """
    Ładuje klucz z pliku KEY_FILE.
    Jeśli plik nie istnieje, generuje nowy klucz, zapisuje go w pliku i zwraca.
    Zwraca obiekt klasy Fernet z załadowanym kluczem.
    """
    if not os.path.exists(KEY_FILE):
        # Generujemy nowy klucz
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

# Używamy jednej instancji Fernet w całej aplikacji
fernet = load_or_create_key()

# ------------------------------------
# 2. Historia w pamięci (plaintext)
# ------------------------------------
# Struktura (dla każdej pozycji):
# {
#   "application": "Nazwa aplikacji",
#   "password": "Hasło w postaci jawnej (plaintext)",
#   "created_at": "YYYY-MM-DD HH:MM:SS"
# }
password_history = []

# ------------------------------------
# 3. Funkcje do odczytu/zapisu pliku JSON (z szyfrowaniem)
# ------------------------------------

def save_history_to_file():
    """
    Zapisuje aktualną historię `password_history` do pliku w formacie JSON,
    szyfrując pole "password".
    """
    # Przygotowujemy listę, w której hasła będą zaszyfrowane
    encrypted_list = []

    for record in password_history:
        plaintext_pwd = record["password"].encode("utf-8")  # bity do szyfrowania
        encrypted_pwd = fernet.encrypt(plaintext_pwd)       # bajty zaszyfrowane
        # zamieniamy bajty na tekst (base64) do JSON:
        encrypted_pwd_str = encrypted_pwd.decode("utf-8")

        encrypted_record = {
            "application": record["application"],
            "password_encrypted": encrypted_pwd_str,
            "created_at": record["created_at"]
        }
        encrypted_list.append(encrypted_record)

    # Zapis do pliku JSON
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(encrypted_list, f, ensure_ascii=False, indent=2)

def load_history_from_file():
    """
    Wczytuje historię z pliku JSON (o ile istnieje),
    odszyfrowuje pole "password_encrypted" i zwraca listę rekordów z plaintextowym hasłem.
    """
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        encrypted_list = json.load(f)

    loaded_history = []
    for record in encrypted_list:
        encrypted_pwd_str = record["password_encrypted"]
        # z powrotem zamieniamy na bajty
        encrypted_pwd = encrypted_pwd_str.encode("utf-8")
        # odszyfrowujemy
        decrypted_pwd = fernet.decrypt(encrypted_pwd).decode("utf-8")

        decrypted_record = {
            "application": record["application"],
            "password": decrypted_pwd,
            "created_at": record["created_at"]
        }
        loaded_history.append(decrypted_record)

    return loaded_history

# ------------------------------------
# 4. Funkcje logiki aplikacji
# ------------------------------------

def generate_password():
    """
    Funkcja generująca hasło na podstawie ustawień z interfejsu.
    Zapisuje również nazwę aplikacji podaną przez użytkownika
    i aktualizuje historię oraz zapisuje ją do pliku.
    """
    try:
        length = int(length_var.get())
    except ValueError:
        output_label.config(text="Nieprawidłowa długość hasła!")
        return

    if length <= 0:
        output_label.config(text="Długość hasła musi być większa od 0!")
        return

    # Zbuduj zestaw znaków
    characters = string.ascii_lowercase  # zawsze używamy liter małych
    if uppercase_var.get():
        characters += string.ascii_uppercase
    if digits_var.get():
        characters += string.digits
    if symbols_var.get():
        # Można ograniczyć się do bezpiecznych znaków specjalnych
        characters += "!@#$%^&*()-_=+[]{}<>?/"

    if not characters:
        output_label.config(text="Zaznacz co najmniej jeden rodzaj znaków!")
        return

    # Generowanie hasła (biblioteka 'secrets' dla kryptograficznej losowości)
    generated_password = "".join(secrets.choice(characters) for _ in range(length))

    # Pobierz nazwę aplikacji/serwisu
    app_name = application_var.get().strip()
    if not app_name:
        app_name = "(Nie podano nazwy aplikacji)"

    # Wyświetlenie w GUI
    output_label.config(text=f"Wygenerowane hasło: {generated_password}")

    # Zapis do historii (plaintext w pamięci)
    record = {
        "application": app_name,
        "password": generated_password,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    password_history.append(record)

    # Aktualizujemy widok list
    update_history_list()
    update_apps_list()

    # Zapis do pliku (z szyfrowaniem haseł)
    save_history_to_file()

def update_history_list():
    """
    Aktualizuje widok listy historii haseł w interfejsie.
    """
    history_listbox.delete(0, tk.END)
    for idx, record in enumerate(password_history, start=1):
        # Format: [1] [Aplikacja] hasło | data
        item_text = f"[{idx}] [{record['application']}] {record['password']} | {record['created_at']}"
        history_listbox.insert(tk.END, item_text)

def clear_history():
    """
    Czyści całą historię wygenerowanych haseł w pamięci i w pliku.
    """
    if messagebox.askyesno("Potwierdzenie", "Czy na pewno wyczyścić całą historię?"):
        password_history.clear()
        update_history_list()
        update_apps_list()

        # Nadpisujemy plik pustą listą
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)

        output_label.config(text="Historia została wyczyszczona.")

def copy_to_clipboard():
    """
    Kopiuje aktualnie wyświetlane hasło (z output_label) do schowka.
    """
    text = output_label.cget("text")
    prefix = "Wygenerowane hasło: "
    if text.startswith(prefix):
        # Wyciągamy samą część hasła
        generated_password = text[len(prefix):]
        root.clipboard_clear()
        root.clipboard_append(generated_password)
        output_label.config(text=f"{text} (skopiowano!)")
    else:
        # Brak wygenerowanego hasła do skopiowania
        output_label.config(text="Najpierw wygeneruj hasło!")

# ------------------------------------
# 5. NOWA SEKCJA: Zapisane hasła do programów
# ------------------------------------

def update_apps_list():
    """
    Aktualizuje listę aplikacji (programów). Wyświetlamy tylko nazwy aplikacji.
    """
    apps_listbox.delete(0, tk.END)
    for record in password_history:
        apps_listbox.insert(tk.END, record['application'])

def copy_password_from_apps_listbox():
    """
    Kopiuje do schowka hasło z aktualnie wybranej aplikacji w `apps_listbox`.
    """
    selection = apps_listbox.curselection()
    if not selection:
        messagebox.showwarning("Brak wyboru", "Nie wybrano pozycji do skopiowania hasła.")
        return

    # Pierwszy (i jedyny) wybrany indeks
    index = selection[0]
    # Hasło z password_history odpowiadające wybranemu wierszowi
    pwd = password_history[index]["password"]
    app_name = password_history[index]["application"]

    root.clipboard_clear()
    root.clipboard_append(pwd)
    messagebox.showinfo("Skopiowano!", f"Hasło dla „{app_name}” skopiowane do schowka!")

# ------------------------------------
# 6. Konfiguracja interfejsu tkinter
# ------------------------------------

root = tk.Tk()
root.title("Password Generator (tkinter)")

# --- Ramka z ustawieniami ---
settings_frame = ttk.LabelFrame(root, text="Ustawienia hasła")
settings_frame.pack(padx=10, pady=10, fill="x")

# Nazwa aplikacji/serwisu
ttk.Label(settings_frame, text="Nazwa aplikacji/serwisu:").grid(
    row=0, column=0, padx=5, pady=5, sticky="e")
application_var = tk.StringVar()
application_entry = ttk.Entry(settings_frame, textvariable=application_var, width=25)
application_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Długość
ttk.Label(settings_frame, text="Długość hasła:").grid(
    row=1, column=0, padx=5, pady=5, sticky="e")
length_var = tk.StringVar(value="12")
length_entry = ttk.Entry(settings_frame, textvariable=length_var, width=10)
length_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Checkboxy
uppercase_var = tk.BooleanVar(value=True)
uppercase_check = ttk.Checkbutton(settings_frame, text="Wielkie litery (A-Z)", variable=uppercase_var)
uppercase_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

digits_var = tk.BooleanVar(value=True)
digits_check = ttk.Checkbutton(settings_frame, text="Cyfry (0-9)", variable=digits_var)
digits_check.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

symbols_var = tk.BooleanVar(value=True)
symbols_check = ttk.Checkbutton(settings_frame, text="Znaki specjalne (!@#$%^&*...)", variable=symbols_var)
symbols_check.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Przycisk generowania
generate_button = ttk.Button(settings_frame, text="Generuj hasło", command=generate_password)
generate_button.grid(row=5, column=0, padx=5, pady=5, sticky="e")

# Przycisk kopiowania (tylko z output_label)
copy_button = ttk.Button(settings_frame, text="Kopiuj do schowka", command=copy_to_clipboard)
copy_button.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# Wyświetlanie wygenerowanego hasła
output_label = ttk.Label(root, text="(Tutaj pojawi się wygenerowane hasło)", foreground="blue")
output_label.pack(padx=10, pady=5)

# --- NOWA RAMKA: Zapisane hasła do programów ---
apps_frame = ttk.LabelFrame(root, text="Zapisane hasła do programów")
apps_frame.pack(padx=10, pady=5, fill="both", expand=False)

# Listbox z samymi nazwami aplikacji
apps_listbox = tk.Listbox(apps_frame, height=5, width=50)
apps_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

# Pasek przewijania (jeśli dużo aplikacji)
apps_scrollbar = ttk.Scrollbar(apps_frame, orient="vertical", command=apps_listbox.yview)
apps_scrollbar.pack(side=tk.RIGHT, fill="y")
apps_listbox.config(yscrollcommand=apps_scrollbar.set)

# Przyciski do obsługi listy aplikacji
apps_copy_button = ttk.Button(root, text="Kopiuj hasło wybranej aplikacji", command=copy_password_from_apps_listbox)
apps_copy_button.pack(pady=5)

# --- Ramka z historią ---
history_frame = ttk.LabelFrame(root, text="Historia wygenerowanych haseł")
history_frame.pack(padx=10, pady=5, fill="both", expand=True)

history_listbox = tk.Listbox(history_frame, height=10, width=60)
history_listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

# Pasek przewijania historii
scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")
history_listbox.config(yscrollcommand=scrollbar.set)

# Przycisk do czyszczenia historii
clear_button = ttk.Button(root, text="Wyczyść historię", command=clear_history)
clear_button.pack(pady=5)

# ------------------------------------
# 7. Główna logika startowa
# ------------------------------------

def main():
    """
    Ładuje historię z pliku, odszyfrowuje, a potem uruchamia główną pętlę tkinter.
    """
    global password_history
    password_history = load_history_from_file()
    update_history_list()
    update_apps_list()
    root.mainloop()

if __name__ == "__main__":
    main()
