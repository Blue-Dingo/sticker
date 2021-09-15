from tkinter import Tk, Label, PhotoImage
from os.path import dirname, join
from time import time


def initattrs(default: dict, optional: list = []):
    def decorator(func):
        def header__init__(self, *args, **kwargs):
            allowed = list(default) + optional
            default.update(kwargs)
            self.__dict__.update((k, v) for k, v in default.items() if k in allowed)
            func(self, *args, **kwargs)

        return header__init__

    return decorator


def mutiple(f: float, m=1):
    if f % 1 == 0:
        return m
    else:
        return mutiple(f * 10, m * 10)


class App(Tk):
    def __init__(self):
        super().__init__()
        self.config(bg=TP_COLOR)
        self.attributes("-transparentcolor", TP_COLOR, "-fullscreen", 1)
        self.attributes("-topmost", 1)
        # self.geometry("640x640")
        # self.overrideredirect(1)
        w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()

        s = Sticker(self, file="runner.gif", scale=0.5, anchor="bottomleft", xy=(0, 0))
        s.movie.set(loop=True)
        s.animation.set(schedule=[0, 20], xy=[[0, 0], [w + 100, 0]], loop=True, delay=40)

        s = Sticker(self, file="scratch.gif", scale=0.5, anchor="bottomleft", xy=(-150, 0))
        s.movie.set(loop=True)
        s.animation.set(schedule=[0, 1, 5], xy=[[0, 0], [150, 0], [0, 0]], loop=True, delay=55)

        # s = Sticker(self, file="wall.gif", scale=1.5, anchor="left", xy=(0, 0))
        # s.movie.set(exc=16, loop=True, delay=3)


class Sticker(Label):
    @initattrs(dict(anchor="topleft", xy=(0, 0), scale=1), ["file"])
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.config(bg=TP_COLOR)
        self.parent = parent
        self.x, self.y = self.xy
        self.image = PhotoImage(file=join(PATH, self.file))
        self.size = self.resize(self.image, self.scale)
        self.config(image=self.image)

        self.movie = Movie(self)
        self.animation = Animation(self)

        self.set_position()
        self.bind("<Double-Button-1>", self.remove)

    def resize(self, image, scale):
        if scale != 1:
            m = mutiple(scale)
            image = image.zoom(int(scale * m)).subsample(m)
        return image.width(), image.height()

    def remove(self, event):
        self.destroy()

    def set_position(self):
        self.update()
        win_w, win_h = self.parent.winfo_width(), self.parent.winfo_height()
        w, h = self.size
        x = self.x + int((win_w - w) / 2)
        y = self.y + int((win_h - h) / 2)
        if "top" in self.anchor:
            y = self.y
        elif "bottom" in self.anchor:
            y = self.y + win_h - h
        if "left" in self.anchor:
            x = self.x
        elif "right" in self.anchor:
            x = self.x + win_w - w
        self.place(x=x, y=y)


class Movie:
    @initattrs(dict(fps=10, exc=-1, loop=False, delay=0))
    def __init__(self, parent):
        self.parent = parent

    def set(self, **kwargs):
        self.__dict__.update(kwargs)
        self.get_images()
        self.resize()
        self.play()

    def get_images(self):
        self.images = []
        file = join(PATH, self.parent.file)
        try:
            i = 0
            while True:
                if i != self.exc:
                    image = PhotoImage(file=file, format=f"gif - {i}")
                    self.images.append(image)
                i += 1
        except:
            pass

    def resize(self):
        scale = self.parent.scale
        if scale != 1:
            m = mutiple(scale)
            for i, image in enumerate(self.images):
                self.images[i] = image.zoom(int(scale * m)).subsample(m)

    def play(self):
        self.curr_idx = 0
        self.update()

    def stop(self):
        if self.loop:
            self.parent.after(self.delay * 1000, self.play)

    def changeImage(self, index):
        self.parent.config(image=self.images[index])

    def update(self):
        self.changeImage(self.curr_idx)

        if self.curr_idx < len(self.images) - 1:
            self.curr_idx += 1
            self.parent.after(int(1000 / self.fps), self.update)
        else:
            self.curr_image = 0
            self.stop()


class Animation:
    @initattrs(dict(fps=60, loop=False, delay=0), ["schedule", "xy"])
    def __init__(self, parent):
        self.parent = parent

    def set(self, **kwargs):
        self.__dict__.update(kwargs)
        self.play()

    def play(self):
        self.starttime = time()
        self.update()

    def stop(self):
        if self.loop:
            self.parent.after(self.delay * 1000, self.play)

    def update(self):
        elapsed = time() - self.starttime
        t = self.schedule
        x, y = zip(*self.xy)
        idx = 0
        x0, y0 = self.parent.xy

        idx = len(t) - 1
        for i, v in enumerate(t):
            if elapsed < v:
                idx = i
                break
        ax = (x[idx] - x[idx - 1]) / (t[idx] - t[idx - 1])
        ay = (y[idx] - y[idx - 1]) / (t[idx] - t[idx - 1])
        bx = x[idx] - ax * t[idx]
        by = y[idx] - ay * t[idx]
        if elapsed >= t[-1]:
            self.parent.x = x0 + x[idx]
            self.parent.y = y0 + y[idx]
            self.stop()
        else:
            self.parent.x = x0 + ax * elapsed + bx
            self.parent.y = y0 + ay * elapsed + by
            self.parent.after(int(1000 / self.fps), self.update)
        self.parent.set_position()


if __name__ == "__main__":

    PATH = dirname(__file__)
    TP_COLOR = "#abcdef"

    app = App()
    app.mainloop()
