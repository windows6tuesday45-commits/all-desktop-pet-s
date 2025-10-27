import tkinter as tk
import random
import time
import threading
import pyttsx3
from tkinter import simpledialog

class MaxDesignPro:
    def __init__(self, root):
        self.root = root
        self.root.title("MaxDesignPro")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='white')
        self.root.wm_attributes('-transparentcolor', 'white')

        # Text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)

        # Screen info
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.width, self.height = 160, 230

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height,
                                bg='white', highlightthickness=0)
        self.canvas.pack()

        # States
        self.mood = "normal"
        self.taps = 0
        self.is_sleeping = False
        self.speech_bubble = None
        self.idle_timer = 0
        self.running = False
        self.glitching = False
        self.reading = False

        # Start position
        self.x = random.randint(50, self.screen_width - self.width - 50)
        self.y = random.randint(100, self.screen_height - self.height - 100)
        self.root.geometry(f"+{self.x}+{self.y}")

        self.draw_max()

        # Bind
        self.canvas.bind("<Button-1>", self.on_tap)
        self.canvas.bind("<Button-3>", self.show_menu)

        # Menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Feed 🍎", command=self.feed)
        self.menu.add_command(label="Drink 🥤", command=self.drink)
        self.menu.add_command(label="Sleep 😴", command=self.sleep)
        self.menu.add_command(label="Talk 💬", command=self.talk)
        self.menu.add_command(label="Sing 🎶", command=self.sing)

        # Threads
        threading.Thread(target=self.walk_around, daemon=True).start()
        threading.Thread(target=self.auto_sleep, daemon=True).start()

    # ---------- Drawing ----------
    def draw_max(self):
        self.canvas.delete("all")

        if self.reading:
            # Sitting + reading form
            sweatshirt = "#d11a2a"
            jeans = "#2a4da3"
            head_color = "#d9b28c"
            top_gray = "#8a8a8a"
            eye_white = "white"
            pupil_color = "black"
            mouth_color = "black"

            # Head
            self.canvas.create_oval(45, 40, 115, 110, fill=head_color, outline="")
            self.canvas.create_arc(45, 40, 115, 110, start=0, extent=180, fill=top_gray, outline="")
            self.canvas.create_oval(30, 55, 50, 85, fill=top_gray, outline="")
            self.canvas.create_oval(110, 55, 130, 85, fill=top_gray, outline="")

            # Eyes
            self.canvas.create_oval(60, 65, 75, 80, fill=eye_white, outline="")
            self.canvas.create_oval(85, 65, 100, 80, fill=eye_white, outline="")
            self.canvas.create_oval(66, 70, 70, 74, fill=pupil_color, outline="")
            self.canvas.create_oval(91, 70, 95, 74, fill=pupil_color, outline="")

            # Mouth
            self.canvas.create_arc(70, 90, 95, 105, start=0, extent=-180, fill=mouth_color, style=tk.ARC)

            # Body sitting
            self.canvas.create_rectangle(40, 110, 120, 170, fill=sweatshirt, outline="")
            self.canvas.create_rectangle(50, 170, 110, 190, fill=jeans, outline="")
            # Book
            self.canvas.create_rectangle(60, 150, 100, 160, fill="skyblue", outline="black")
            self.canvas.create_text(80, 155, text="📖", font=("Segoe UI", 12))

            return

        if self.mood == "angry":
            sweatshirt = "#5a0000"
            jeans = "#0b1a4f"
            eye_white = "black"
            pupil_color = "red"
            mouth_color = "yellow"
            head_color = "#cfa985"
            top_gray = "#6e6e6e"
        else:
            sweatshirt = "#d11a2a"
            jeans = "#2a4da3"
            eye_white = "white"
            pupil_color = "black"
            mouth_color = "black"
            head_color = "#d9b28c"
            top_gray = "#8a8a8a"

        shoe = "#000000"
        collar = "#b30f20"

        # Head
        self.canvas.create_oval(45, 10, 115, 80, fill=head_color, outline="")
        self.canvas.create_arc(45, 10, 115, 80, start=0, extent=180, fill=top_gray, outline="")
        self.canvas.create_oval(30, 25, 50, 55, fill=top_gray, outline="")
        self.canvas.create_oval(110, 25, 130, 55, fill=top_gray, outline="")

        # Eyes
        self.canvas.create_oval(60, 35, 75, 50, fill=eye_white, outline="")
        self.canvas.create_oval(85, 35, 100, 50, fill=eye_white, outline="")
        self.canvas.create_oval(66, 40, 70, 44, fill=pupil_color, outline="")
        self.canvas.create_oval(91, 40, 95, 44, fill=pupil_color, outline="")

        # Nose
        self.canvas.create_oval(78, 55, 82, 60, fill="brown", outline="")

        # Mouth
        if self.mood == "angry":
            self.canvas.create_rectangle(70, 65, 95, 75, fill=mouth_color, outline="black")
        elif self.mood == "sleeping":
            self.canvas.create_arc(70, 62, 95, 72, start=0, extent=-180, fill="gray", style=tk.ARC)
        else:
            self.canvas.create_arc(70, 60, 95, 75, start=0, extent=-180, fill="black", style=tk.ARC)

        # Collar & sweatshirt
        self.canvas.create_rectangle(55, 80, 105, 90, fill=collar, outline="")
        self.canvas.create_rectangle(40, 90, 120, 160, fill=sweatshirt, outline="")

        # Arms
        self.canvas.create_rectangle(25, 95, 40, 145, fill=sweatshirt, outline="")
        self.canvas.create_rectangle(120, 95, 135, 145, fill=sweatshirt, outline="")

        # Jeans & shoes
        self.canvas.create_rectangle(50, 160, 75, 210, fill=jeans, outline="")
        self.canvas.create_rectangle(85, 160, 110, 210, fill=jeans, outline="")
        self.canvas.create_oval(45, 205, 80, 220, fill=shoe, outline="")
        self.canvas.create_oval(80, 205, 115, 220, fill=shoe, outline="")

    # ---------- Interactions ----------
    def on_tap(self, event):
        if self.is_sleeping:
            self.is_sleeping = False
            self.say("Yawn... I'm awake again!")
            self.mood = "normal"
            self.draw_max()
            return

        # Every tap triggers Darkform
        self.mood = "angry"
        self.draw_max()
        self.say("Stop it!")
        self.after_darkform_sequence()

    def after_darkform_sequence(self):
        # Dialog flow after turning dark
        q1 = simpledialog.askstring("Question", "What happened to Max?")
        if q1 is not None:
            self.say("What is it?")

        # Simulate glitch flicker
        self.glitch_effect()

        q2 = simpledialog.askstring("Question", "Did you see that?")
        if q2 is not None:
            self.say("What did you see? Did you see anything?")

        # Calm down to normal
        self.mood = "normal"
        self.draw_max()

        # Sit down and read book
        self.reading = True
        self.say("I'm going to read for a bit.")
        self.draw_max()

        # After a while, back to normal
        self.root.after(8000, self.finish_reading)

    def glitch_effect(self):
        if self.glitching:
            return
        self.glitching = True

        def flicker():
            for _ in range(4):
                self.canvas.configure(bg='black')
                time.sleep(0.1)
                self.canvas.configure(bg='white')
                time.sleep(0.1)
            self.glitching = False
        threading.Thread(target=flicker, daemon=True).start()

    def finish_reading(self):
        self.reading = False
        self.draw_max()
        self.say("Okay, back to normal!")

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def feed(self):
        self.say("Yummy! Thanks for the food 🍎")
        self.mood = "normal"
        self.draw_max()
        self.taps = 0

    def drink(self):
        self.say("Ahh, refreshing 🥤")
        self.mood = "normal"
        self.draw_max()
        self.taps = 0

    def sleep(self):
        if not self.is_sleeping:
            self.is_sleeping = True
            self.say("Zzz...")
            self.mood = "sleeping"
            self.draw_max()

    def talk(self):
        questions = [
            "How’s your day?",
            "What’s your favorite movie?",
            "Got any fun plans?",
            "Do you like monkeys?",
            "Are you working hard today?",
            "What’s your dream job?",
            "What snack do you love the most?",
            "Would you travel if you could right now?"
        ]
        q = random.choice(questions)
        self.say(q)
        reply = simpledialog.askstring("Max asks:", q)
        if reply:
            self.say(f"Interesting! You said '{reply}'. Cool!")
        else:
            self.say("Heh, quiet type today?")

    def sing(self):
        self.say(random.choice(["🎵 La la la~ 🎶", "🎶 Ooh ooh ah ah~ 🎵", "Singing time! 🎤"]))

    # ---------- Say / Speak ----------
    def say(self, text):
        if self.speech_bubble:
            self.canvas.delete(self.speech_bubble)
        bubble = self.canvas.create_text(self.width//2, 10, text=text,
                                         fill="black", font=("Segoe UI", 12, "bold"))
        self.speech_bubble = bubble
        threading.Thread(target=lambda: self.engine.say(text) or self.engine.runAndWait(),
                         daemon=True).start()
        self.root.after(4000, lambda: self.canvas.delete(bubble))

    # ---------- Behaviour Threads ----------
    def walk_around(self):
        while True:
            if not self.is_sleeping and not self.reading:
                self.running = random.random() < 0.05
                speed = 6 if self.running else 2
                dx = random.choice([-speed, -speed+1, speed-1, speed])
                dy = random.choice([-speed//2, speed//2])
                self.x = max(0, min(self.x + dx, self.screen_width - self.width))
                self.y = max(0, min(self.y + dy, self.screen_height - self.height))
                self.root.geometry(f"+{self.x}+{self.y}")
            time.sleep(0.05)

    def auto_sleep(self):
        while True:
            time.sleep(20)
            self.idle_timer += 1
            if self.idle_timer >= 3 and not self.is_sleeping:
                self.is_sleeping = True
                self.mood = "sleeping"
                self.say("Zzz...")
                self.draw_max()
            if self.taps > 0:
                self.idle_timer = 0

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = MaxDesignPro(root)
    root.mainloop()
