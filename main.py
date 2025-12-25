import os
import csv
import ssl
import random
from datetime import date
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.network.urlrequest import UrlRequest 

# --- SSL FIX FOR ANDROID IMAGES ---
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# =========================================================================
# 1. ASSET & MATH ENGINE
# =========================================================================

def get_img(name, real_url=None):
    if real_url: return real_url
    clean = name.replace(" ", "+")
    return f"https://placehold.co/600x400/121212/00FF88/png?text={clean}&font=roboto"

def calculate_plates(weight):
    try:
        w = float(weight)
        if w < 20: return "Bar Only"
        rem = (w - 20) / 2
        plates = [25, 20, 15, 10, 5, 2.5, 1.25]
        load = []
        for p in plates:
            while rem >= p:
                load.append(str(p))
                rem -= p
        return f"Side: {', '.join(load)}" if load else "Bar Only"
    except: return "Invalid"

def calculate_1rm(weight, reps):
    try:
        w, r = float(weight), int(reps)
        return int(w * (1 + r / 30)) if r > 1 else int(w)
    except: return 0

# =========================================================================
# 2. THE BLACK BOOK (8 Chapters - Full Text)
# =========================================================================

GUIDE_DATA = {
    "1. The Iron Philosophy": {
        "subtitle": "POWER HYPERTROPHY ADAPTIVE TRAINING",
        "body": "The 'Hybrid Athlete' needs Strength and Size. PHAT combines them.\n\n• Days 1-2: Power (3-5 Reps). Builds density.\n• Days 4-6: Hypertrophy (8-15 Reps). Builds size.\n\nHeavy lifting builds the engine. Volume builds the fuel tank."
    },
    "2. The RAMP Warmup": {
        "subtitle": "STOP STRETCHING COLD MUSCLES",
        "body": "Static stretching reduces power. Use RAMP:\n\n• R (Raise): Sweat before you lift.\n• A (Activate): Glute bridges, Band pulls.\n• M (Mobilize): Dynamic arm circles.\n• P (Potentiate): Warmup sets (Bar -> 50% -> 70% -> Work)."
    },
    "3. Mechanics: The Big 3": {
        "subtitle": "TECHNICAL MASTERY",
        "body": "SQUAT: Tripod foot. Break the bar across traps. Hip crease below knee.\n\nBENCH: Retract scapula. Leg drive backward. Bar path is a 'J' curve.\n\nDEADLIFT: Pull slack out of bar until it clicks. Push the earth away."
    },
    "4. Progressive Overload": {
        "subtitle": "THE LAW OF GROWTH",
        "body": "You must do more than last time.\n\n1. Intensity: +2.5kg (The King).\n2. Volume: +1 Rep.\n3. Density: Less rest.\n4. Technique: Slower reps.\n\nIf you aren't tracking, you're guessing."
    },
    "5. Nutrition & Recovery": {
        "subtitle": "FUEL & SLEEP",
        "body": "CALORIES: Growth = Surplus (+300). Cutting = Deficit (-500).\n\nPROTEIN: 1g per lb of bodyweight.\n\nSLEEP: 7-9 hours. This is non-negotiable for testosterone production."
    },
    "6. CNS Fatigue": {
        "subtitle": "MANAGE THE SYSTEM",
        "body": "Power days tax the Central Nervous System.\n\nSIGNS OF FATIGUE:\n- Weak grip strength.\n- Waking up tired.\n\nDELOAD: Every 6-8 weeks, reduce volume by 50%."
    },
    "7. Equipment Guide": {
        "subtitle": "CHOOSE YOUR WEAPON",
        "body": "BARBELLS: Main lifts (1-6 reps). Max load.\n\nDUMBBELLS: Secondary lifts. Fixes imbalances.\n\nCABLES: Constant tension. Isolation.\n\nMACHINES: Failure training safely."
    },
    "8. Injury Protocol": {
        "subtitle": "GOOD PAIN VS BAD PAIN",
        "body": "DOMS (Good): Dull ache in muscle belly. 24h later.\n\nINJURY (Bad): Sharp, shooting pain in joint. Instant.\n\nTHE FIX:\n1. Check Form.\n2. Check Mobility.\n3. STOP immediately."
    }
}

# =========================================================================
# 3. THE COMPLETE DATABASE (All Variations Included)
# =========================================================================

EXERCISE_DB = {
    # --- PHAT SPLIT ---
    "Upper Power": [
        {"name": "Bench Press", "type": "POWER", "reps": "3x5", "cue": "Leg Drive.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bench_press_1.svg/800px-Bench_press_1.svg.png"},
        {"name": "Bent Rows", "type": "POWER", "reps": "3x5", "cue": "Explosive.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bent-over_row_1.svg/640px-Bent-over_row_1.svg.png"},
        {"name": "Overhead Press", "type": "POWER", "reps": "3x6", "cue": "Head thru.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Shoulder_press_1.svg/640px-Shoulder_press_1.svg.png"},
        {"type": "Shuffle", "pool": [{"name": "Weighted Pullups", "reps": "3x6", "img": "https://upload.wikimedia.org/wikipedia/commons/0/00/Pull-up-2.png"}, {"name": "Lat Pulldown", "reps": "3x10", "img": get_img("Lat Pulldown")}]},
        {"type": "Shuffle", "pool": [{"name": "Skullcrushers", "reps": "3x10", "img": get_img("Skullcrusher")}, {"name": "Barbell Curl", "reps": "3x10", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Barbell_curl_1.svg/640px-Barbell_curl_1.svg.png"}]}
    ],
    "Lower Power": [
        {"name": "Squat", "type": "POWER", "reps": "3x5", "cue": "Deep.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Squats.png/640px-Squats.png"},
        {"name": "Deadlift", "type": "POWER", "reps": "3x5", "cue": "Hinge.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Barbell-deadlift.png/800px-Barbell-deadlift.png"},
        {"type": "Shuffle", "pool": [{"name": "Leg Press", "reps": "3x10", "img": get_img("Leg Press")}, {"name": "Hack Squat", "reps": "3x8", "img": get_img("Hack Squat")}]},
        {"type": "Shuffle", "pool": [{"name": "Leg Curl", "reps": "3x12", "img": get_img("Leg Curl")}, {"name": "Calf Raise", "reps": "4x15", "img": get_img("Calf Raise")}]}
    ],
    "Push Hyper": [
        {"name": "Inc DB Press", "type": "HYPER", "reps": "3x10", "cue": "Upper chest.", "img": get_img("Incline DB")},
        {"name": "Seat Shoulder", "type": "HYPER", "reps": "3x12", "cue": "Tension.", "img": get_img("Seated Press")},
        {"type": "Shuffle", "pool": [{"name": "Cable Fly", "reps": "3x15", "img": get_img("Cable Fly")}, {"name": "Lat Raise", "reps": "4x15", "img": get_img("Lat Raise")}]},
        {"type": "Shuffle", "pool": [{"name": "Pushdown", "reps": "3x15", "img": get_img("Tricep Push")}, {"name": "Dips", "reps": "Failure", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Dips_1.png/640px-Dips_1.png"}]}
    ],
    "Pull Hyper": [
        {"name": "BB Rows", "type": "HYPER", "reps": "4x10", "cue": "Volume.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bent-over_row_1.svg/640px-Bent-over_row_1.svg.png"},
        {"name": "Lat Pulldown", "type": "HYPER", "reps": "3x12", "cue": "Squeeze.", "img": get_img("Lat Pull")},
        {"type": "Shuffle", "pool": [{"name": "Face Pull", "reps": "4x15", "img": get_img("Face Pull")}, {"name": "Shrugs", "reps": "3x15", "img": get_img("Shrugs")}]},
        {"type": "Shuffle", "pool": [{"name": "Hammer Curl", "reps": "3x12", "img": get_img("Hammer Curl")}, {"name": "Preacher Curl", "reps": "3x12", "img": get_img("Preacher")}]}
    ],
    "Legs Hyper": [
        {"name": "Front Squat", "type": "HYPER", "reps": "3x10", "cue": "Quads.", "img": get_img("Front Squat")},
        {"name": "RDL", "type": "HYPER", "reps": "3x12", "cue": "Stretch.", "img": get_img("RDL")},
        {"type": "Shuffle", "pool": [{"name": "Leg Ext", "reps": "3x15", "img": get_img("Leg Ext")}, {"name": "Lunges", "reps": "3x20", "img": get_img("Lunges")}]}
    ],

    # --- SPECIALTY SPLITS ---
    "Chest Focus": [
        {"name": "Barbell Bench", "reps": "4x8", "cue": "Heavy.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Bench_press_1.svg/800px-Bench_press_1.svg.png"},
        {"name": "Inc DB Press", "reps": "3x10", "cue": "Upper.", "img": get_img("Inc DB Press")},
        {"name": "Weighted Dips", "reps": "3x10", "cue": "Lower.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Dips_1.png/640px-Dips_1.png"},
        {"name": "Cable Flys", "reps": "3x15", "cue": "Iso.", "img": get_img("Cable Flys")},
        {"name": "Pushups", "reps": "2xFail", "cue": "Burn.", "img": get_img("Pushups")}
    ],
    "Back Focus": [
        {"name": "Deadlift", "reps": "3x5", "cue": "Mass.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Barbell-deadlift.png/800px-Barbell-deadlift.png"},
        {"name": "Weighted Pullups", "reps": "3x8", "cue": "Width.", "img": "https://upload.wikimedia.org/wikipedia/commons/0/00/Pull-up-2.png"},
        {"name": "T-Bar Row", "reps": "3x10", "cue": "Thick.", "img": get_img("T-Bar")},
        {"name": "Straight Arm Pulldown", "reps": "3x15", "cue": "Lats.", "img": get_img("Straight Arm")}
    ],
    "Shoulder Focus": [
        {"name": "OHP", "reps": "4x8", "cue": "Mass.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Shoulder_press_1.svg/640px-Shoulder_press_1.svg.png"},
        {"name": "Arnold Press", "reps": "3x12", "cue": "Rotation.", "img": get_img("Arnold Press")},
        {"name": "Lat Raises", "reps": "5x15", "cue": "Width.", "img": get_img("Lat Raise")},
        {"name": "Face Pulls", "reps": "3x15", "cue": "Rear.", "img": get_img("Face Pull")}
    ],
    "Leg Focus": [
        {"name": "Squat", "reps": "4x8", "cue": "Mass.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Squats.png/640px-Squats.png"},
        {"name": "Leg Press", "reps": "3x12", "cue": "Load.", "img": get_img("Leg Press")},
        {"name": "Lunges", "reps": "3x20", "cue": "Uni.", "img": get_img("Lunges")},
        {"name": "Leg Curl", "reps": "3x15", "cue": "Hams.", "img": get_img("Leg Curl")}
    ],
    "Bicep Blaster": [
        {"name": "Barbell Curl", "reps": "4x8", "cue": "Heavy.", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Barbell_curl_1.svg/640px-Barbell_curl_1.svg.png"},
        {"name": "Incline Curl", "reps": "3x10", "cue": "Long head.", "img": get_img("Inc Curl")},
        {"name": "Hammer Curl", "reps": "3x12", "cue": "Brachialis.", "img": get_img("Ham Curl")},
        {"name": "Cable 21s", "reps": "2 Sets", "cue": "Burn.", "img": get_img("Cable Curl")}
    ],
    "Tricep Torture": [
        {"name": "Close Grip Bench", "reps": "4x8", "cue": "Mass.", "img": get_img("Close Grip")},
        {"name": "Skullcrushers", "reps": "3x10", "cue": "Medial.", "img": get_img("Skullcrusher")},
        {"name": "Rope Pushdown", "reps": "3x15", "cue": "Lateral.", "img": get_img("Rope Push")}
    ],

    # --- CONDITIONING ---
    "HIIT": [
        {"name": "Burpees", "reps": "45s", "img": get_img("Burpees")},
        {"name": "Box Jumps", "reps": "45s", "img": get_img("Box Jump")},
        {"name": "Mtn Climbers", "reps": "45s", "img": get_img("Climbers")}
    ],
    "Tabata (4 mins)": [
        {"name": "Sprint", "reps": "20s/10s", "cue": "8 Rounds.", "img": get_img("Sprint")},
        {"name": "Kettlebell Swing", "reps": "20s/10s", "cue": "8 Rounds.", "img": get_img("KB Swing")}
    ],
    "EMOM (10 mins)": [
        {"name": "Thrusters", "reps": "10/min", "cue": "Pace it.", "img": get_img("Thruster")},
        {"name": "Pullups", "reps": "5/min", "cue": "Strict.", "img": "https://upload.wikimedia.org/wikipedia/commons/0/00/Pull-up-2.png"}
    ],

    # --- MOBILITY ---
    "Mobility": [
        {"name": "90/90 Stretch", "reps": "60s", "cue": "Hips.", "img": get_img("90-90")},
        {"name": "Cat Cow", "reps": "60s", "cue": "Spine.", "img": get_img("Cat Cow")},
        {"name": "Wall Slides", "reps": "60s", "cue": "Shoulders.", "img": get_img("Wall Slide")},
        {"name": "World Greatest", "reps": "60s", "cue": "Full Body.", "img": get_img("WGS")}
    ],
    "Desk Undo": [
        {"name": "Chin Tucks", "reps": "20 reps", "cue": "Neck.", "img": get_img("Chin Tuck")},
        {"name": "Doorway Stretch", "reps": "60s", "cue": "Chest.", "img": get_img("Door Stretch")}
    ],
    "Squat Primer": [
        {"name": "Ankle Rocks", "reps": "20 reps", "cue": "Dorsiflexion.", "img": get_img("Ankle")},
        {"name": "Goblet Hold", "reps": "60s", "cue": "Depth.", "img": get_img("Goblet")}
    ]
}

# =========================================================================
# 4. ENGINE
# =========================================================================

class AppEngine:
    def __init__(self):
        self.log_file = 'iron_vault_log.csv'
        self.ensure_csv()
        self.tonnage = 0

    def ensure_csv(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                csv.writer(f).writerow(["Date", "Exercise", "Weight", "Reps", "1RM"])

    def save_log(self, ex, w, r):
        try: self.tonnage += float(w) * int(r)
        except: pass
        with open(self.log_file, 'a', newline='') as f:
            csv.writer(f).writerow([date.today(), ex, w, r, calculate_1rm(w, r)])
        return True 

    def get_history(self, ex):
        if not os.path.exists(self.log_file): return "New"
        with open(self.log_file, 'r') as f:
            rows = list(csv.reader(f))
            for row in reversed(rows[1:]):
                if row[1] == ex: return f"Last: {row[2]}kg x {row[3]}"
        return "New"

    def generate(self, mode):
        self.tonnage = 0
        playlist = []
        if mode not in ["Mobility", "Desk Undo", "Squat Primer", "HIIT", "Tabata (4 mins)", "EMOM (10 mins)"]:
            playlist.extend([{"name": "Arm Circles", "reps": "60s", "type": "WARMUP", "history": "-"},
                             {"name": "Band Pulls", "reps": "20 reps", "type": "WARMUP", "history": "-"}])
        
        if mode in EXERCISE_DB:
            for slot in EXERCISE_DB[mode]:
                ex = slot.copy()
                if "pool" in slot: ex = random.choice(slot["pool"]).copy()
                ex["history"] = self.get_history(ex.get("name", ""))
                ex["cue"] = ex.get("cue", "Form Focus.")
                if "type" not in ex: ex["type"] = "WORKOUT"
                playlist.append(ex)
        
        return playlist

engine = AppEngine()

# =========================================================================
# 5. UI
# =========================================================================

KV = '''
ScreenManager:
    HomeScreen:
    WorkoutScreen:
    GuideScreen:
    ToolsScreen:

<HomeScreen>:
    name: 'home'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.05, 0.05, 0.05, 1
        
        MDTopAppBar:
            title: "IRON VAULT"
            right_action_items: [["book-open-variant", lambda x: app.open_guide()], ["calculator", lambda x: app.open_tools()]]
            elevation: 0
            md_bg_color: 0.05, 0.05, 0.05, 1
            specific_text_color: 0, 1, 0.53, 1

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "15dp"
                adaptive_height: True

                MDLabel:
                    text: "PHAT SYSTEM"
                    theme_text_color: "Custom"
                    text_color: 1, 0.3, 0.3, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 2
                    spacing: "10dp"
                    adaptive_height: True
                    MDRaisedButton:
                        text: "UPPER POWER"
                        size_hint_x: 1
                        md_bg_color: 0.2, 0.2, 0.2, 1
                        on_release: app.start_workout("Upper Power")
                    MDRaisedButton:
                        text: "LOWER POWER"
                        size_hint_x: 1
                        md_bg_color: 0.2, 0.2, 0.2, 1
                        on_release: app.start_workout("Lower Power")

                MDGridLayout:
                    cols: 3
                    spacing: "10dp"
                    adaptive_height: True
                    MDRaisedButton:
                        text: "PUSH HYP"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Push Hyper")
                    MDRaisedButton:
                        text: "PULL HYP"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Pull Hyper")
                    MDRaisedButton:
                        text: "LEGS HYP"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Legs Hyper")

                MDLabel:
                    text: "SPECIALTY"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0.53, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 2
                    spacing: "10dp"
                    adaptive_height: True
                    MDRaisedButton:
                        text: "CHEST FOCUS"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Chest Focus")
                    MDRaisedButton:
                        text: "BACK FOCUS"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Back Focus")
                    MDRaisedButton:
                        text: "SHOULDER FOCUS"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Shoulder Focus")
                    MDRaisedButton:
                        text: "LEG FOCUS"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Leg Focus")
                    MDRaisedButton:
                        text: "BICEP BLASTER"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Bicep Blaster")
                    MDRaisedButton:
                        text: "TRICEP TORTURE"
                        size_hint_x: 1
                        md_bg_color: 0.15, 0.15, 0.15, 1
                        on_release: app.start_workout("Tricep Torture")

                MDLabel:
                    text: "CONDITIONING"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0.53, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 2
                    spacing: "10dp"
                    adaptive_height: True
                    MDRaisedButton:
                        text: "TABATA (4m)"
                        size_hint_x: 1
                        md_bg_color: 1, 0.5, 0, 1
                        on_release: app.start_workout("Tabata (4 mins)")
                    MDRaisedButton:
                        text: "EMOM (10m)"
                        size_hint_x: 1
                        md_bg_color: 1, 0.5, 0, 1
                        on_release: app.start_workout("EMOM (10 mins)")
                    MDRaisedButton:
                        text: "DESK UNDO"
                        size_hint_x: 1
                        md_bg_color: 0, 0.5, 0.5, 1
                        on_release: app.start_workout("Desk Undo")
                    MDRaisedButton:
                        text: "SQUAT PRIMER"
                        size_hint_x: 1
                        md_bg_color: 0, 0.5, 0.5, 1
                        on_release: app.start_workout("Squat Primer")
                    MDRaisedButton:
                        text: "MOBILITY"
                        size_hint_x: 1
                        md_bg_color: 0, 0.5, 0.5, 1
                        on_release: app.start_workout("Mobility")

<WorkoutScreen>:
    name: 'workout'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.05, 0.05, 0.05, 1
        
        MDTopAppBar:
            title: root.phase
            left_action_items: [["arrow-left", lambda x: root.exit()]]
            md_bg_color: 0.05, 0.05, 0.05, 1
            specific_text_color: 0, 1, 0.53, 1

        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "20dp"
            
            MDLabel:
                text: root.ex_name
                halign: "center"
                font_style: "H4"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                adaptive_height: True
            
            MDLabel:
                text: root.ex_reps + "\\n" + root.ex_hist
                halign: "center"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.7, 0.7, 0.7, 1
                adaptive_height: True

            MDLabel:
                text: root.ex_cue
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.5, 1
                font_style: "Subtitle1"
                adaptive_height: True

            MDBoxLayout:
                spacing: "20dp"
                adaptive_height: True
                pos_hint: {"center_x": .5}
                MDTextField:
                    id: w_input
                    hint_text: "Kg"
                    mode: "rectangle"
                    size_hint_x: 0.3
                    text_color_normal: 1, 1, 1, 1
                    text_color_focus: 0, 1, 0.53, 1
                MDTextField:
                    id: r_input
                    hint_text: "Reps"
                    mode: "rectangle"
                    size_hint_x: 0.3
                    text_color_normal: 1, 1, 1, 1
                    text_color_focus: 0, 1, 0.53, 1

            MDLabel:
                text: root.timer_txt
                halign: "center"
                font_style: "H4"
                theme_text_color: "Custom"
                text_color: 1, 0.2, 0.2, 1
                adaptive_height: True

            MDRaisedButton:
                text: "LOG & NEXT"
                size_hint_x: 1
                height: "60dp"
                md_bg_color: 0, 0.6, 0.3, 1
                on_release: root.next()

            Widget:

<GuideScreen>:
    name: 'guide'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.05, 0.05, 0.05, 1
        MDTopAppBar:
            title: "BLACK BOOK"
            left_action_items: [["arrow-left", lambda x: app.back_home()]]
            md_bg_color: 0.05, 0.05, 0.05, 1
            specific_text_color: 0, 1, 0.53, 1
        
        ScrollView:
            MDBoxLayout:
                id: guide_box
                orientation: 'vertical'
                padding: "20dp"
                spacing: "30dp"
                adaptive_height: True

<ToolsScreen>:
    name: 'tools'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.05, 0.05, 0.05, 1
        MDTopAppBar:
            title: "TOOLS"
            left_action_items: [["arrow-left", lambda x: app.back_home()]]
            md_bg_color: 0.05, 0.05, 0.05, 1
            specific_text_color: 0, 1, 0.53, 1
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "20dp"
            
            MDTextField:
                id: plate_in
                hint_text: "Weight (kg)"
                text_color_normal: 1, 1, 1, 1
            MDRaisedButton:
                text: "CALC PLATES"
                on_release: root.calc_plate()
            MDLabel:
                id: plate_out
                text: "Load:"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
            
            Widget:
'''

class HomeScreen(MDScreen): pass
class ToolsScreen(MDScreen):
    def calc_plate(self):
        self.ids.plate_out.text = calculate_plates(self.ids.plate_in.text)

class GuideScreen(MDScreen):
    def on_enter(self):
        box = self.ids.guide_box
        box.clear_widgets()
        for title, content in GUIDE_DATA.items():
            box.add_widget(MDLabel(text=title, font_style="H5", theme_text_color="Custom", text_color=(0, 1, 0.53, 1), adaptive_height=True))
            box.add_widget(MDLabel(text=content["subtitle"], font_style="Subtitle1", theme_text_color="Custom", text_color=(1, 0.3, 0.3, 1), adaptive_height=True))
            box.add_widget(MDLabel(text=content["body"], theme_text_color="Custom", text_color=(0.9, 0.9, 0.9, 1), adaptive_height=True))
            box.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))

class WorkoutScreen(MDScreen):
    ex_name = StringProperty("Loading...")
    ex_reps = StringProperty("-")
    ex_hist = StringProperty("-")
    ex_cue = StringProperty("-")
    phase = StringProperty("WARMUP")
    timer_txt = StringProperty("")
    
    queue = []
    idx = 0
    timer = None
    sec = 90

    def load(self, playlist):
        self.queue = playlist
        self.idx = 0
        self.show()

    def show(self):
        if self.idx < len(self.queue):
            data = self.queue[self.idx]
            self.ex_name = data["name"]
            self.ex_reps = data["reps"]
            self.ex_cue = data.get("cue", "")
            self.ex_hist = data.get("history", "-")
            self.phase = data.get("type", "WORKOUT")
            self.ids.w_input.text = ""
            self.ids.r_input.text = ""
            self.stop_timer()
        else:
            self.exit()

    def next(self):
        w, r = self.ids.w_input.text, self.ids.r_input.text
        if w and r: engine.save_log(self.ex_name, w, r)
        self.start_timer()
        if self.idx < len(self.queue) - 1:
            self.idx += 1
            Clock.schedule_once(lambda dt: self.show(), 0.5)
        else:
            self.exit()

    def start_timer(self):
        self.stop_timer()
        self.sec = 90
        self.timer = Clock.schedule_interval(self.tick, 1)

    def tick(self, dt):
        self.sec -= 1
        self.timer_txt = f"REST: {self.sec}s"
        if self.sec <= 0: self.stop_timer()

    def stop_timer(self):
        if self.timer: self.timer.cancel()
        self.timer_txt = ""

    def exit(self):
        self.stop_timer()
        MDApp.get_running_app().root.current = 'home'

class IronVaultApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return Builder.load_string(KV)

    def start_workout(self, mode):
        self.root.get_screen('workout').load(engine.generate(mode))
        self.root.current = 'workout'

    def open_guide(self): self.root.current = 'guide'
    def open_tools(self): self.root.current = 'tools'
    def back_home(self): self.root.current = 'home'

if __name__ == '__main__':
    IronVaultApp().run()
