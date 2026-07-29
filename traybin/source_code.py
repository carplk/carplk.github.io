import ctypes
import os
import sys
import threading
import time
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

def is_recycle_bin_empty():
    class SHQUERYRBINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("i64Size", ctypes.c_longlong),
            ("i64NumItems", ctypes.c_longlong)
        ]
    
    query_info = SHQUERYRBINFO()
    query_info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
    ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(query_info))
    return query_info.i64NumItems == 0

def create_bin_image(is_empty):
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    if is_empty:
        draw.rectangle([16, 24, 48, 56], outline="white", width=4)
        draw.rectangle([12, 16, 52, 22], fill="white")
        draw.rectangle([26, 8, 38, 14], fill="white")
    else:
        draw.rectangle([16, 24, 48, 56], fill="#4185F4", outline="white", width=4)
        draw.rectangle([12, 16, 52, 22], fill="white")
        draw.rectangle([26, 8, 38, 14], fill="white")
        draw.line([24, 32, 40, 32], fill="white", width=3)
        draw.line([24, 40, 40, 40], fill="white", width=3)
        
    return image

def open_bin(icon, item):
    os.system("start shell:RecycleBinFolder")

def clear_bin(icon, item):
    ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
    update_icon(icon)

def update_icon(icon):
    empty = is_recycle_bin_empty()
    icon.icon = create_bin_image(empty)
    icon.title = "Корзина: пуста" if empty else "Корзина: есть файлы"

def check_status(icon):
    while icon.visible:
        update_icon(icon)
        time.sleep(3)

def setup(icon):
    icon.visible = True
    threading.Thread(target=check_status, args=(icon,), daemon=True).start()

def main():
    initial_empty = is_recycle_bin_empty()
    image = create_bin_image(initial_empty)
    
    menu = pystray.Menu(
        item('Открыть корзину', open_bin),
        item('Очистить корзину', clear_bin),
        pystray.Menu.SEPARATOR,
        item('Выход', lambda icon, item: icon.stop())
    )
    
    icon = pystray.Icon("RecycleBinTray", image, "Корзина", menu)
    icon.run(setup)

if __name__ == "__main__":
    main()
