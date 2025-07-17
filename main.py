import os
import sys
import subprocess

# Проверка и установка Pillow
try:
    from PIL import Image, ImageTk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageTk

import tkinter as tk

CAR_SCALE = 0.5  # Маштаб машины относительно стороны окна

class CarOnBackgroundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Car on Road")

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.bg_image = Image.open(os.path.join(script_dir, "Background.png"))
        self.car_image = Image.open(os.path.join(script_dir, "car.png"))

        self._last_size = None
        self._pending_resize = False

        self.root.bind("<Configure>", self.on_configure)

    def on_configure(self, event):
        # Запускаем только один resize после отпускания мыши
        if not self._pending_resize:
            self._pending_resize = True
            self.root.after_idle(self.enforce_square)

    def enforce_square(self):
        self._pending_resize = False

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        if width == height:
            size = width
        else:
            size = min(width, height)
            self.root.geometry(f"{size}x{size}")
            return  # Ждём следующего Configure после выравнивания

        if size == self._last_size:
            return
        self._last_size = size

        self.redraw(size)

    def redraw(self, size):
        self.canvas.config(width=size, height=size)
        self.canvas.delete("all")

        # Фон
        bg_resized = self.bg_image.resize((size, size), Image.LANCZOS)
        self.tk_bg = ImageTk.PhotoImage(bg_resized)
        self.canvas.create_image(size // 2, size // 2, image=self.tk_bg)

        # Машина
        car_w = int(size * CAR_SCALE)
        car_h = int(car_w * self.car_image.height / self.car_image.width)
        car_resized = self.car_image.resize((car_w, car_h), Image.LANCZOS)
        self.tk_car = ImageTk.PhotoImage(car_resized)
        self.canvas.create_image(size // 2, int(size * 0.85), image=self.tk_car)

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(300, 300)
    app = CarOnBackgroundApp(root)
    root.mainloop()
