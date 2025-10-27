import sys, random, threading, time
import pyttsx3, psutil
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QInputDialog
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QPointF

VERSION = "BenTheWolf v2.1-Emotions"

class BenTheWolf(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ben the Wolf")
        self.setGeometry(0, 0, 300, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().size()
        self.move(screen.width()//2 - 150, screen.height()//2 - 150)

        # physics / drag / throw
        self.dragging = False
        self.throwing = False
        self.velocity = QPointF(0,0)
        self.offset = QPointF(0,0)

        # animation state
        self.tail_angle = 0
        self.tail_dir = 1
        self.mouth_open = False
        self.eye_closed = False

        # emotions: neutral, happy, angry, surprised
        self.emotion = "neutral"

        # treat / food
        self.bone_y = None
        self.food_items = []

        # random questions
        self.question_timer = QTimer()
        self.question_timer.timeout.connect(self.ask_random_question)
        self.question_timer.start(20000)

        self.question_pending = False
        self.question_popup_time = None

        # movement
        self.walk_timer = QTimer()
        self.walk_timer.timeout.connect(self.walk)
        self.walk_timer.start(200)

        # voice
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 175)

        # animation timers
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(120)

        self.gravity_timer = QTimer()
        self.gravity_timer.timeout.connect(self.apply_gravity)
        self.gravity_timer.start(30)

        # anger check timer
        self.anger_timer = QTimer()
        self.anger_timer.timeout.connect(self.check_anger)
        self.anger_timer.start(1000)

        self.show()

    # ---------- animation ----------
    def animate(self):
        self.tail_angle += self.tail_dir*10
        if abs(self.tail_angle)>40:
            self.tail_dir *= -1
        if random.random()<0.05:
            self.mouth_open = not self.mouth_open
        self.update()

    # ---------- random walk ----------
    def walk(self):
        if not self.dragging and not self.throwing:
            dx = random.choice([-10,0,10])
            dy = random.choice([-5,0,5])
            new_x = max(0, min(QApplication.primaryScreen().size().width()-self.width(), self.x()+dx))
            new_y = max(0, min(QApplication.primaryScreen().size().height()-self.height(), self.y()+dy))
            self.move(new_x,new_y)

    # ---------- gravity / treats / food ----------
    def apply_gravity(self):
        if self.throwing:
            self.velocity.setY(self.velocity.y()+1.5)
            self.move(self.x(), self.y()+int(self.velocity.y()))
            if self.y()>QApplication.primaryScreen().size().height()-350:
                self.throwing=False
                self.velocity=QPointF(0,0)
                self.say_async("Ouch! That was fun!")
                self.emotion="happy"

        # bone / food fall
        if self.bone_y is not None:
            self.bone_y += 10
            if self.bone_y>160:
                self.say_async("Thank you very much!")
                self.bone_y=None
                self.emotion="happy"

        for f in list(self.food_items):
            f["y"] += 8
            if f["y"]>200:
                self.food_items.remove(f)
                self.say_async("Yum! That was delicious!")
                self.emotion="happy"

        self.update()

    # ---------- mouse ----------
    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton:
            self.dragging=True
            self.offset=e.pos()

    def mouseMoveEvent(self,e):
        if self.dragging:
            self.move(e.globalPos()-self.offset)
        if 90<e.x()<220 and 150<e.y()<200:
            if not self.eye_closed:
                self.eye_closed=True
                self.emotion="happy"
                self.say_async("How nice of you.")
        else:
            self.eye_closed=False

    def mouseReleaseEvent(self,e):
        if self.dragging:
            self.dragging=False
            speed=abs(self.velocity.y())
            if speed>25:
                self.throwing=True

    def mouseDoubleClickEvent(self,e):
        if e.button()==Qt.LeftButton:
            self.pet()

    # ---------- menu ----------
    def contextMenuEvent(self,event):
        menu=QMenu(self)
        menu.addAction("💬 Talk", self.talk)
        menu.addAction("🍖 Feed", self.feed)
        menu.addAction("🦴 Treat", self.treat)
        menu.addAction("📖 Story", self.story)
        menu.addAction("🎮 Play", self.play)
        menu.addSeparator()
        menu.addAction("❌ Exit", self.close)
        menu.exec_(event.globalPos())

    # ---------- interactions ----------
    def talk(self):
        self.ask_questions()

    def ask_questions(self):
        while True:
            self.question_pending = True
            self.question_popup_time = time.time()
            q,ok=QInputDialog.getText(self,"Talk to Ben","Hey! What do you want to ask Ben the Wolf?")
            self.question_pending=False
            if ok and q:
                self.emotion="happy"
                self.respond(q)
            else:
                break
            more,ok2=QInputDialog.getText(self,"Talk again","Anything else you want to say?")
            if ok2 and more.lower().strip()!="no":
                self.emotion="happy"
                self.respond(more)
            else:
                self.say_async("Okay then! Talk to me anytime!")
                self.emotion="neutral"
                break

    def respond(self, user_input):
        lower=user_input.lower()
        if "time" in lower:
            from datetime import datetime
            self.say_async(f"The current time is {datetime.now().strftime('%H:%M:%S')}")
        elif "battery" in lower:
            try:
                battery=psutil.sensors_battery()
                self.say_async(f"The battery is at {battery.percent}%")
            except:
                self.say_async("Sorry, I can't read battery info.")
        else:
            responses=[
                "That's interesting!",
                "I see!",
                "Tell me more!",
                "Fascinating!",
                "Oh, really?"
            ]
            self.say_async(random.choice(responses))

    def feed(self):
        self.food_items.append({"x":random.randint(100,180),"y":-30})
        self.say_async("Here's some food coming down!")
        self.emotion="happy"

    def treat(self):
        if self.bone_y is None:
            self.bone_y=-20
            self.say_async("Catch this bone!")
            self.emotion="happy"

    def play(self):
        self.say_async(random.choice([
            "Let's play fetch!","I can run faster than you!","Tag, you're it!"
        ]))
        self.emotion="happy"

    def pet(self):
        self.say_async("How sweet of you!")
        self.happy=True
        self.emotion="happy"

    def story(self):
        story=("Once upon a time, there was a wolf named Ben. "
               "He lived on your desktop, wagging his tail happily. "
               "He loved treats, belly rubs, and good stories. "
               "And he never, ever went to sleep!")
        self.say_async(story)
        self.emotion="happy"

    # ---------- random questions ----------
    def ask_random_question(self):
        if self.question_pending:
            return
        questions=[
            "What are all these icons?",
            "Do you use this app often?",
            "What is this shortcut for?",
            "Is this one important?",
            "Can you tell me the time?",
            "How charged is your battery?"
        ]
        q=random.choice(questions)
        self.question_pending=True
        self.question_popup_time=time.time()
        ans,ok=QInputDialog.getText(self,"Ben asks",q)
        self.question_pending=False
        self.emotion="happy" if ok and ans else "neutral"
        if ok and ans:
            self.respond(ans)

    def check_anger(self):
        if self.question_pending and time.time()-self.question_popup_time>15:
            self.emotion="angry"
            self.say_async("Hey! Answer me now!")
            self.question_pending=False

    # ---------- voice ----------
    def say_async(self,text):
        threading.Thread(target=self.say,args=(text,),daemon=True).start()

    def say(self,text):
        self.engine.say(text)
        self.engine.runAndWait()

    # ---------- drawing ----------
    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # body
        p.setBrush(QColor(110,110,110))
        p.drawEllipse(70,120,160,80)

        # head
        p.setBrush(QColor(130,130,130))
        p.drawEllipse(40,60,90,70)

        # ears
        p.setBrush(QColor(90,90,90))
        p.drawPolygon([QPointF(60,50),QPointF(75,20),QPointF(90,50)])
        p.drawPolygon([QPointF(100,50),QPointF(115,20),QPointF(130,50)])

        # eyes based on emotion
        if self.emotion=="angry":
            pen=QPen(Qt.black,3)
            p.setPen(pen)
            p.drawLine(75,80,87,86) # slanted angry
            p.drawLine(105,80,117,86)
        elif self.eye_closed or self.emotion=="happy":
            pen=QPen(Qt.black,2)
            p.setPen(pen)
            p.drawLine(75,86,87,86)
            p.drawLine(105,86,117,86)
        else:
            p.setBrush(Qt.white)
            p.drawEllipse(75,80,12,12)
            p.drawEllipse(105,80,12,12)
            p.setBrush(Qt.black)
            p.drawEllipse(79,84,6,6)
            p.drawEllipse(109,84,6,6)

        # snout
        p.setBrush(QColor(150,150,150))
        p.drawEllipse(95,105,40,22)

        # nose
        p.setBrush(Qt.black)
        p.drawEllipse(130,110,10,8)

        # mouth
        pen=QPen(Qt.black,2)
        p.setPen(pen)
        if self.emotion=="angry":
            p.drawArc(105,125,30,10,0,180*16)
        elif self.mouth_open:
            p.drawArc(105,125,30,10,0,-180*16)
        else:
            p.drawLine(105,125,135,125)

        # legs
        p.setBrush(QColor(95,95,95))
        p.drawRect(100,190,15,35)
        p.drawRect(150,190,15,35)

        # tail
        p.save()
        p.translate(220,150)
        p.rotate(self.tail_angle)
        p.setBrush(QColor(80,80,80))
        p.drawPolygon([QPointF(0,0),QPointF(45,10),QPointF(20,20)])
        p.restore()

        # bone treat
        if self.bone_y is not None:
            p.setBrush(QColor(230,230,230))
            p.drawRect(140,self.bone_y,20,6)
            p.drawEllipse(135,self.bone_y-3,8,8)
            p.drawEllipse(157,self.bone_y-3,8,8)

        # food
        p.setBrush(QColor(255,180,90))
        for f in self.food_items:
            p.drawEllipse(f["x"],f["y"],20,20)

        # shadow
        p.setBrush(QColor(50,50,50,120))
        p.drawEllipse(90,220,100,15)

if __name__=="__main__":
    app=QApplication(sys.argv)
    wolf=BenTheWolf()
    sys.exit(app.exec_())
