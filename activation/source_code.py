import subprocess
import threading
import sys
import os
import tkinter as tk
from tkinter import messagebox

# Проверка и запрос прав администратора (необходимы для slmgr)
def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Функция для определения стиля окна (скрытое или видимое в зависимости от галочки)
def get_window_style():
    return "Normal" if show_console_var.get() else "Hidden"

# Функция активации Windows
def activate_windows():
    btn_win.config(state="disabled")
    lbl_status.config(text="Идёт активация Windows...", fg="#58a6ff")

    def run():
        commands = [
            'cscript //nologo C:\\Windows\\System32\\slmgr.vbs /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX',
            'cscript //nologo C:\\Windows\\System32\\slmgr.vbs /skms kms.digiboy.ir',
            'cscript //nologo C:\\Windows\\System32\\slmgr.vbs /ato'
        ]
        
        win_style = get_window_style()
        for cmd in commands:
            if win_style == "Normal":
                ps_wrap = f'powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Normal -Command "{cmd}"'
                subprocess.run(ps_wrap, shell=True)
            else:
                subprocess.run(cmd, shell=True, capture_output=True)

        messagebox.showinfo("Результат", "Команды активации Windows отправлены!\nПроверьте статус в настройках системы.")
        lbl_status.config(text="Готово к работе", fg="#8b949e")
        btn_win.config(state="normal")

    threading.Thread(target=run, daemon=True).start()

# Активация Office через отдельный скрипт Ohook (AIO.cmd)
def activate_office():
    btn_office.config(state="disabled")
    lbl_status.config(text="Идёт активация Office...", fg="#58a6ff")

    def run():
        win_style = get_window_style()
        # Скачивание и запуск .cmd скрипта напрямую через irm и iex в PowerShell
        ps_cmd = (
            f'powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle {win_style} -Command '
            '"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
            'irm https://raw.githubusercontent.com/massgravel/Microsoft-Activation-Scripts/refs/heads/master/MAS/Separate-Files-Version/Activators/Ohook_Activation_AIO.cmd | iex"'
        )
        subprocess.run(ps_cmd, shell=True)

        messagebox.showinfo("Успех", "Процесс активации Office завершён!")
        lbl_status.config(text="Готово к работе", fg="#8b949e")
        btn_office.config(state="normal")

    threading.Thread(target=run, daemon=True).start()

# --- Создание графического интерфейса (GUI) ---
root = tk.Tk()
root.title("Активатор Windows & Office")
root.geometry("420x380")
root.resizable(False, False)

# Тёмная палитра
BG_COLOR = "#0d1117"
CARD_COLOR = "#161b22"
TEXT_COLOR = "#c9d1d9"
BTN_WIN_COLOR = "#1f6beb"
BTN_OFF_COLOR = "#238636"

root.configure(bg=BG_COLOR)

card = tk.Frame(root, bg=CARD_COLOR, highlightbackground="#30363d", highlightthickness=1)
card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=345)

# Заголовок
lbl_title = tk.Label(
    card, text="Активация в один клик", 
    font=("Segoe UI", 16, "bold"), 
    bg=CARD_COLOR, fg="#f0f6fc"
)
lbl_title.pack(pady=(15, 5))

# Статус
lbl_status = tk.Label(
    card, text="Готово к работе", 
    font=("Segoe UI", 9), 
    bg=CARD_COLOR, fg="#8b949e"
)
lbl_status.pack(pady=(0, 10))

# Кнопка Windows
btn_win = tk.Button(
    card, text="Активировать Windows", 
    font=("Segoe UI", 11, "bold"),
    bg=BTN_WIN_COLOR, fg="#ffffff",
    activebackground="#388bfd", activeforeground="#ffffff",
    bd=0, cursor="hand2",
    command=activate_windows
)
btn_win.pack(fill="x", padx=30, ipady=6, pady=6)

# Кнопка Office
btn_office = tk.Button(
    card, text="Активировать MS Office (Ohook)", 
    font=("Segoe UI", 11, "bold"),
    bg=BTN_OFF_COLOR, fg="#ffffff",
    activebackground="#2ea44f", activeforeground="#ffffff",
    bd=0, cursor="hand2",
    command=activate_office
)
btn_office.pack(fill="x", padx=30, ipady=6, pady=6)

# Галочка для показа терминала
show_console_var = tk.BooleanVar(value=False)
chk_show_console = tk.Checkbutton(
    card, 
    text="Показывать окно консоли", 
    variable=show_console_var,
    font=("Segoe UI", 8),
    bg=CARD_COLOR, fg="#c9d1d9",
    activebackground=CARD_COLOR, activeforeground="#ffffff",
    selectcolor=BG_COLOR,
    cursor="hand2"
)
chk_show_console.pack(pady=(4, 6))

# Подсказка снизу
lbl_info = tk.Label(
    card, text="Требуются права Администратора", 
    font=("Segoe UI", 8), 
    bg=CARD_COLOR, fg="#484f58"
)
lbl_info.pack(side="bottom", pady=10)

# Автозапрос прав администратора при старте скрипта
if __name__ == "__main__":
    if not is_admin():
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        root.mainloop()
