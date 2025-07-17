import os
import sys
import subprocess

# Pillow — установка, если нужно
try:
    from PIL import Image, ImageTk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageTk

import tkinter as tk

CAR_SCALE = 0.5  # масштаб машины по ширине окна

class CarOnBackgroundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Car on Road")

        # Загружаем изображения
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.bg_image = Image.open(os.path.join(script_dir, "Background.png"))
        self.car_image = Image.open(os.path.join(script_dir, "car.png"))

        # Холст
        self.canvas = tk.Canvas(root, highlightthickness=0, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Состояния
        self._last_w = None
        self._last_h = None
        self._pending_geometry = False
        self._resize_after_id = None  # таймер для отложенной обработки

        # Подписка на изменение
        self.root.bind("<Configure>", self.on_configure)

        # Первая отрисовка
        self.root.after(0, self.initial_draw)

    def initial_draw(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        side = min(w, h)
        self._last_w = w
        self._last_h = h
        self.set_square_geometry(side)

    def set_square_geometry(self, side):
        self._pending_geometry = True
        self.root.geometry(f"{side}x{side}")

    def on_configure(self, event):
        if self._pending_geometry:
            self._pending_geometry = False
            return

        # Отложенный вызов, чтобы дождаться завершения изменения размера
        if self._resize_after_id is not None:
            self.root.after_cancel(self._resize_after_id)

        self._resize_after_id = self.root.after(300, self.on_resize_complete)

    def on_resize_complete(self):
        self._resize_after_id = None

        w = self.root.winfo_width()
        h = self.root.winfo_height()

        if self.root.state() == "zoomed":
            self.root.state("normal")
            self.set_square_geometry(min(w, h))
            return

        if self._last_w is not None and self._last_h is not None:
            dw = abs(w - self._last_w)
            dh = abs(h - self._last_h)

            if dw > dh:
                self.set_square_geometry(w)
                return
            elif dh > dw:
                self.set_square_geometry(h)
                return

        self._last_w = w
        self._last_h = h

        size = min(w, h)
        self.redraw(size)

    def redraw(self, size):
        if size < 100:
            return

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
