import os
import json
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

DEFAULT_DIR = os.path.expandvars(r"%APPDATA%\SimpleAccSwitch")
DEFAULT_FILE = os.path.join(DEFAULT_DIR, "accounts.txt")
CONFIG_FILE = os.path.join(DEFAULT_DIR, "config.json")

LANGUAGES = {
    "English": {
        "window_title": "Simple Steam Account Switcher",
        "settings_title": "Settings",
        "add_frame": " Add Account ",
        "login_label": "Account Login:",
        "pass_label": "Password (optional):",
        "add_btn": "Save Account",
        "login_btn": "Login to Selected",
        "del_btn": "Delete",
        "settings_btn": "Settings",
        "theme_label": "Theme:",
        "lang_label": "Language:",
        "file_label": "Accounts File Path:",
        "browse_btn": "Browse...",
        "dark": "Dark",
        "light": "Light",
        "err_title": "Error",
        "warn_title": "Warning",
        "info_title": "Information",
        "enter_login": "Enter account login!",
        "acc_exists": "This account is already in the list.",
        "select_acc_del": "Select an account to delete!",
        "del_confirm": "Delete account {account} from the list?",
        "select_acc_login": "Select an account to login!",
        "steam_error": "Failed to start Steam: {e}",
        "config_err": "Failed to save config: {e}",
        "read_err": "Failed to read accounts file: {e}",
        "write_err": "Failed to write account: {e}",
        "del_err": "Failed to delete account: {e}"
    },
    "Русский": {
        "window_title": "Простой переключатель аккаунтов Steam",
        "settings_title": "Настройки",
        "add_frame": " Добавить аккаунт ",
        "login_label": "Логин аккаунта:",
        "pass_label": "Пароль (необязательно):",
        "add_btn": "Сохранить аккаунт",
        "login_btn": "Войти в выбранный",
        "del_btn": "Удалить",
        "settings_btn": "Настройки",
        "theme_label": "Тема:",
        "lang_label": "Язык:",
        "file_label": "Путь к файлу аккаунтов:",
        "browse_btn": "Обзор...",
        "dark": "Тёмная",
        "light": "Светлая",
        "err_title": "Ошибка",
        "warn_title": "Внимание",
        "info_title": "Информация",
        "enter_login": "Введите логин аккаунта!",
        "acc_exists": "Этот аккаунт уже есть в списке.",
        "select_acc_del": "Выберите аккаунт для удаления!",
        "del_confirm": "Удалить аккаунт {account} из списка?",
        "select_acc_login": "Выберите аккаунт для входа!",
        "steam_error": "Не удалось запустить Steam: {e}",
        "config_err": "Не удалось сохранить конфиг: {e}",
        "read_err": "Не удалось прочитать файл аккаунтов: {e}",
        "write_err": "Не удалось записать аккаунт: {e}",
        "del_err": "Не удалось удалить аккаунт: {e}"
    }
}

class SteamAccountSwitcher:
    def __init__(self, root):
        self.root = root
        self.load_config()
        
        self.themes = {
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#ffffff",
                "entry_bg": "#2d2d2d",
                "entry_fg": "#ffffff",
                "btn_bg": "#333333",
                "btn_fg": "#ffffff",
                "btn_active_bg": "#3e3e3e",
                "select_bg": "#007acc",
                "labelframe_fg": "#cccccc"
            },
            "light": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "btn_bg": "#e1e1e1",
                "btn_fg": "#000000",
                "btn_active_bg": "#d0d0d0",
                "select_bg": "#0078d7",
                "labelframe_fg": "#333333"
            }
        }

        self.init_main_window()
        self.apply_theme()
        self.load_accounts()

    def tr(self, key):
        lang = self.config.get("language", "English")
        return LANGUAGES.get(lang, LANGUAGES["English"]).get(key, key)

    def load_config(self):
        os.makedirs(DEFAULT_DIR, exist_ok=True)
        self.config = {
            "accounts_file": DEFAULT_FILE,
            "theme": "dark",
            "language": "English"
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception:
                pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror(self.tr("err_title"), self.tr("config_err").format(e=e))

    def init_main_window(self):
        self.root.title(self.tr("window_title"))
        self.root.geometry("400x500")
        self.root.minsize(360, 450)

        for widget in self.root.winfo_children():
            widget.destroy()

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.settings_btn = tk.Button(top_frame, text=self.tr("settings_btn"), command=self.open_settings)
        self.settings_btn.pack(side="right")

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.account_listbox = tk.Listbox(list_frame, font=("Segoe UI", 11), selectmode=tk.SINGLE)
        self.account_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.account_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.account_listbox.config(yscrollcommand=scrollbar.set)

        self.account_listbox.bind("<Double-Button-1>", lambda e: self.login_selected())

        self.add_frame = tk.LabelFrame(self.root, text=self.tr("add_frame"), font=("Segoe UI", 9))
        self.add_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(self.add_frame, text=self.tr("login_label")).pack(anchor="w", padx=5, pady=(5, 0))
        self.login_entry = tk.Entry(self.add_frame, font=("Segoe UI", 10))
        self.login_entry.pack(fill="x", padx=5, pady=2)

        tk.Label(self.add_frame, text=self.tr("pass_label")).pack(anchor="w", padx=5, pady=(5, 0))
        self.pass_entry = tk.Entry(self.add_frame, font=("Segoe UI", 10), show="*")
        self.pass_entry.pack(fill="x", padx=5, pady=2)

        self.add_btn = tk.Button(self.add_frame, text=self.tr("add_btn"), command=self.add_account)
        self.add_btn.pack(fill="x", padx=5, pady=8)

        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=10)

        self.login_btn = tk.Button(action_frame, text=self.tr("login_btn"), font=("Segoe UI", 10, "bold"), command=self.login_selected)
        self.login_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.del_btn = tk.Button(action_frame, text=self.tr("del_btn"), command=self.delete_account)
        self.del_btn.pack(side="right", padx=(5, 0))

    def apply_theme(self):
        theme_name = self.config.get("theme", "dark")
        t = self.themes[theme_name]

        self.root.config(bg=t["bg"])

        def style_widget(widget):
            w_type = widget.winfo_class()
            try:
                if w_type in ('Frame', 'Labelframe'):
                    widget.config(bg=t["bg"])
                    if w_type == 'Labelframe':
                        widget.config(fg=t["labelframe_fg"])
                elif w_type == 'Label':
                    widget.config(bg=t["bg"], fg=t["fg"])
                elif w_type == 'Button':
                    widget.config(bg=t["btn_bg"], fg=t["btn_fg"], activebackground=t["btn_active_bg"], activeforeground=t["btn_fg"], relief="flat")
                elif w_type == 'Entry':
                    widget.config(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["fg"], relief="solid", bd=1)
                elif w_type == 'Checkbutton' or w_type == 'Radiobutton':
                    widget.config(bg=t["bg"], fg=t["fg"], activebackground=t["bg"], activeforeground=t["fg"], selectcolor=t["entry_bg"])
            except Exception:
                pass
            for child in widget.winfo_children():
                style_widget(child)

        style_widget(self.root)

        self.account_listbox.config(
            bg=t["entry_bg"], 
            fg=t["entry_fg"], 
            selectbackground=t["select_bg"],
            selectforeground="#ffffff",
            highlightthickness=0,
            relief="flat"
        )

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title(self.tr("settings_title"))
        settings_win.geometry("380x320")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        theme_name = self.config.get("theme", "dark")
        t = self.themes[theme_name]
        settings_win.config(bg=t["bg"])

        tk.Label(settings_win, text=self.tr("theme_label"), font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        theme_var = tk.StringVar(value=theme_name)
        
        def change_theme_choice(val):
            self.config["theme"] = val
            self.save_config()
            self.apply_theme()
            new_t = self.themes[val]
            settings_win.config(bg=new_t["bg"])
            for widget in settings_win.winfo_children():
                try:
                    if widget.winfo_class() == 'Label':
                        widget.config(bg=new_t["bg"], fg=new_t["fg"])
                    elif widget.winfo_class() == 'Radiobutton':
                        widget.config(bg=new_t["bg"], fg=new_t["fg"], activebackground=new_t["bg"], selectcolor=new_t["entry_bg"])
                except:
                    pass

        tk.Radiobutton(settings_win, text=self.tr("dark"), variable=theme_var, value="dark", command=lambda: change_theme_choice("dark")).pack(anchor="w", padx=30)
        tk.Radiobutton(settings_win, text=self.tr("light"), variable=theme_var, value="light", command=lambda: change_theme_choice("light")).pack(anchor="w", padx=30)

        tk.Label(settings_win, text=self.tr("lang_label"), font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        lang_var = tk.StringVar(value=self.config.get("language", "English"))

        def change_lang_choice(val):
            self.config["language"] = val
            self.save_config()
            self.init_main_window()
            self.apply_theme()
            self.load_accounts()
            settings_win.destroy()
            self.open_settings()

        tk.Radiobutton(settings_win, text="English", variable=lang_var, value="English", command=lambda: change_lang_choice("English")).pack(anchor="w", padx=30)
        tk.Radiobutton(settings_win, text="Русский", variable=lang_var, value="Русский", command=lambda: change_lang_choice("Русский")).pack(anchor="w", padx=30)

        tk.Label(settings_win, text=self.tr("file_label"), font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        file_frame = tk.Frame(settings_win)
        file_frame.pack(fill="x", padx=15)
        file_frame.config(bg=t["bg"])

        path_label_val = tk.Label(file_frame, text=self.config.get("accounts_file", DEFAULT_FILE), wraplength=250, justify="left", font=("Segoe UI", 8))
        path_label_val.pack(side="left", fill="x", expand=True)

        def browse_file():
            initial_dir = os.path.dirname(self.get_current_file())
            file_path = filedialog.asksaveasfilename(
                title=self.tr("file_label"),
                initialdir=initial_dir,
                initialfile="accounts.txt",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if file_path:
                self.config["accounts_file"] = file_path
                self.save_config()
                self.load_accounts()
                path_label_val.config(text=file_path)

        browse_btn = tk.Button(file_frame, text=self.tr("browse_btn"), command=browse_file)
        browse_btn.pack(side="right", padx=5)

        for widget in settings_win.winfo_children():
            try:
                if widget.winfo_class() == 'Label':
                    widget.config(bg=t["bg"], fg=t["fg"])
                elif widget.winfo_class() == 'Radiobutton':
                    widget.config(bg=t["bg"], fg=t["fg"], activebackground=t["bg"], selectcolor=t["entry_bg"])
                elif widget.winfo_class() == 'Frame':
                    widget.config(bg=t["bg"])
            except:
                pass

    def get_current_file(self):
        path = self.config.get("accounts_file", DEFAULT_FILE)
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        return path

    def load_accounts(self):
        self.account_listbox.delete(0, tk.END)
        file_path = self.get_current_file()
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            display_name = line.split(":", 1)[0]
                            self.account_listbox.insert(tk.END, display_name)
            except Exception as e:
                messagebox.showerror(self.tr("err_title"), self.tr("read_err").format(e=e))

    def add_account(self):
        login = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not login:
            messagebox.showwarning(self.tr("warn_title"), self.tr("enter_login"))
            return

        file_path = self.get_current_file()
        
        existing_logins = []
        full_lines = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip()
                    if clean_line:
                        full_lines.append(clean_line)
                        existing_logins.append(clean_line.split(":", 1)[0])

        if login in existing_logins:
            messagebox.showinfo(self.tr("info_title"), self.tr("acc_exists"))
            return

        record = f"{login}:{password}" if password else login

        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(record + "\n")
            self.login_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            self.load_accounts()
        except Exception as e:
            messagebox.showerror(self.tr("err_title"), self.tr("write_err").format(e=e))

    def delete_account(self):
        selected = self.account_listbox.curselection()
        if not selected:
            messagebox.showwarning(self.tr("warn_title"), self.tr("select_acc_del"))
            return

        account_display = self.account_listbox.get(selected[0])
        if not messagebox.askyesno(self.tr("info_title"), self.tr("del_confirm").format(account=account_display)):
            return

        file_path = self.get_current_file()
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(file_path, "w", encoding="utf-8") as f:
                    for line in lines:
                        curr_login = line.strip().split(":", 1)[0]
                        if curr_login != account_display:
                            f.write(line)
            self.load_accounts()
        except Exception as e:
            messagebox.showerror(self.tr("err_title"), self.tr("del_err").format(e=e))

    def login_selected(self):
        selected = self.account_listbox.curselection()
        if not selected:
            messagebox.showwarning(self.tr("warn_title"), self.tr("select_acc_login"))
            return

        target_login = self.account_listbox.get(selected[0])
        
        file_path = self.get_current_file()
        account_record = target_login
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str.startswith(target_login + ":") or line_str == target_login:
                        account_record = line_str
                        break

        # Полное и надежное завершение процессов Steam
        try:
            subprocess.run(["taskkill", "/f", "/im", "steam.exe"], capture_output=True)
            subprocess.run(["taskkill", "/f", "/im", "steamwebhelper.exe"], capture_output=True)
            subprocess.run(["taskkill", "/f", "/im", "steamerrorreporter.exe"], capture_output=True)
            time.sleep(2)
        except Exception:
            pass

        steam_exe = r"C:\Program Files (x86)\Steam\steam.exe"
        if not os.path.exists(steam_exe):
            steam_exe = "steam.exe"

        parts = account_record.split(":", 1)
        try:
            # Заимствуем проверенный флаг -noreactlogin для стабильной работы переключения
            if len(parts) == 2 and parts[1]:
                subprocess.Popen([steam_exe, "-login", parts[0], parts[1], "-noreactlogin"])
            else:
                subprocess.Popen([steam_exe, "-login", parts[0], "-noreactlogin"])
        except Exception as e:
            messagebox.showerror(self.tr("err_title"), self.tr("steam_error").format(e=e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SteamAccountSwitcher(root)
    root.mainloop()
