import os
import csv
import random
from datetime import date
from kivy.clock import Clock  # CRITICAL: Needed for timer
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.utils import platform

# =========================================================================
# 1. MATH & LOGIC
# =========================================================================

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
# 2. THE ETERNAL DATABASE
# =========================================================================

GUIDE_DATA = {
    "1. The Iron Philosophy": {"subtitle": "POWER + HYPERTROPHY", "body": "The Hybrid Athlete needs Strength and Size. PHAT combines them.\n\n• Days 1-2: Power (3-5 Reps). Builds density.\n• Days 4-6: Hypertrophy (8-15 Reps). Builds size.\n\nHeavy lifting builds the engine. Volume builds the fuel tank."},
    "2. The RAMP Warmup": {"subtitle": "DON'T STRETCH COLD", "body": "• R (Raise): Sweat first.\n• A (Activate): Glutes/Core.\n• M (Mobilize): Dynamic moves.\n• P (Potentiate): Warmup sets."},
    "3. The Big 3": {"subtitle": "TECHNICAL MASTERY", "body": "SQUAT: Tripod foot. Break bar across traps.\nBENCH: Leg drive back. Arch tight.\nDEADLIFT: Pull slack. Push floor away."},
    "4. Overload": {"subtitle": "DO MORE", "body": "1. Intensity (+2.5kg)\n2. Volume (+1 Rep)\n3. Density (Less Rest)\n4. Technique (Slower)"},
    "5. Nutrition": {"subtitle": "FUEL", "body": "Surplus = Growth.\nDeficit = Cut.\nProtein = 1g/lb.\nSleep = 8 Hours (The best steroid)."},
    "6. CNS Fatigue": {"subtitle": "SYSTEM MANAGEMENT", "body": "If grip is weak or motivation is zero, you are fried. Take a deload week (50% volume)."},
    "7. Equipment": {"subtitle": "TOOLS", "body": "Barbells = Mass.\nDumbbells = Balance.\nCables = Isolation.\nMachines = Failure safely."},
    "8. Injury": {"subtitle": "STAY SAFE", "body": "Good Pain = Dull ache (DOMS).\nBad Pain = Sharp/Joint.\nFix: Form > Weight."}
}

EXERCISE_DB = {
    # --- PHAT SPLIT (FULL BODY COVERAGE GUARANTEED) ---
    "Upper Power": [
        {"name": "Bench Press", "reps": "3x5", "cue": "Chest Power", "icon": "arm-flex", "type": "POWER"},
        {"name": "Bent Over Rows", "reps": "3x5", "cue": "Back Thickness", "icon": "rowing", "type": "POWER"},
        {"name": "Overhead Press", "reps": "3x6", "cue": "Shoulder Mass", "icon": "human-handsup", "type": "POWER"},
        {"name": "Weighted Pullups", "reps": "3x6", "cue": "Lat Width", "icon": "human-handsup", "type": "POWER"},
        {"name": "Barbell Curls", "reps": "3x8", "cue": "Bicep Mass", "icon": "arm-flex", "type": "ACC"},
        {"name": "Skullcrushers", "reps": "3x8", "cue": "Tricep Mass", "icon": "arm-flex-outline", "type": "ACC"}
    ],
    "Lower Power": [
        {"name": "Squat", "reps": "3x5", "cue": "Quad Power", "icon": "human-male-height", "type": "POWER"},
        {"name": "Deadlift", "reps": "3x5", "cue": "Posterior Chain", "icon": "weight-lifter", "type": "POWER"},
        {"name": "Leg Press", "reps": "3x10", "cue": "Leg Volume", "icon": "car-brake-pedal", "type": "ACC"},
        {"name": "Leg Curl", "reps": "3x10", "cue": "Hamstrings", "icon": "seat-recline-normal", "type": "ACC"},
        {"name": "Calf Raise", "reps": "4x15", "cue": "Calves", "icon": "arrow-up-bold", "type": "ACC"}
    ],
    "Push Hyper": [
        {"name": "Inc DB Press", "reps": "3x10", "cue": "Upper Chest", "icon": "dumbbell", "type": "HYPER"},
        {"name": "Seated Press", "reps": "3x12", "cue": "Shoulders", "icon": "human-handsup", "type": "HYPER"},
        {"name": "Cable Fly", "reps": "3x15", "cue": "Chest Iso", "icon": "butterfly", "type": "HYPER"},
        {"name": "Lat Raise", "reps": "4x15", "cue": "Side Delts", "icon": "bird", "type": "HYPER"},
        {"name": "Tricep Pushdown", "reps": "3x15", "cue": "Triceps", "icon": "arrow-down-bold", "type": "HYPER"},
        {"name": "Dips", "reps": "Failure", "cue": "Burnout", "icon": "format-vertical-align-bottom", "type": "FINISHER"}
    ],
    "Pull Hyper": [
        {"name": "Barbell Rows", "reps": "4x10", "cue": "Back Density", "icon": "rowing", "type": "HYPER"},
        {"name": "Lat Pulldown", "reps": "3x12", "cue": "Back Width", "icon": "tshirt-v", "type": "HYPER"},
        {"name": "Face Pulls", "reps": "4x15", "cue": "Rear Delts", "icon": "eye-outline", "type": "HYPER"},
        {"name": "Shrugs", "reps": "3x15", "cue": "Traps", "icon": "tshirt-v", "type": "HYPER"},
        {"name": "Hammer Curl", "reps": "3x12", "cue": "Forearms", "icon": "gavel", "type": "HYPER"},
        {"name": "Preacher Curl", "reps": "3x12", "cue": "Bicep Peak", "icon": "arm-flex", "type": "HYPER"}
    ],
    "Legs Hyper": [
        {"name": "Front Squat", "reps": "3x10", "cue": "Quads", "icon": "human-male-height", "type": "HYPER"},
        {"name": "Lunges", "reps": "3x20", "cue": "Unilateral", "icon": "walk", "type": "HYPER"},
        {"name": "Leg Ext", "reps": "3x15", "cue": "Quad Iso", "icon": "seat-recline-normal", "type": "HYPER"},
        {"name": "Goblet Squat", "reps": "3x12", "cue": "Depth", "icon": "dumbbell", "type": "HYPER"},
        {"name": "Seated Calf", "reps": "4x20", "cue": "Calves", "icon": "arrow-up-bold", "type": "HYPER"}
    ],
    
    # --- SPECIALTY SPLITS ---
    "Bicep Blaster": [{"name": "BB Curl", "reps": "4x8", "icon": "arm-flex"}, {"name": "Inc Curl", "reps": "3x10", "icon": "dumbbell"}, {"name": "Hammer", "reps": "3x12", "icon": "gavel"}, {"name": "21s", "reps": "2 Sets", "icon": "flash"}],
    "Tricep Torture": [{"name": "C.G. Bench", "reps": "4x8", "icon": "arm-flex-outline"}, {"name": "Skullcrush", "reps": "3x10", "icon": "dumbbell"}, {"name": "Pushdown", "reps": "3x15", "icon": "arrow-down-bold"}, {"name": "Dips", "reps": "Fail", "icon": "format-vertical-align-bottom"}],
    "Chest Focus": [{"name": "Bench", "reps": "4x8", "icon": "arm-flex"}, {"name": "Inc DB", "reps": "3x10", "icon": "dumbbell"}, {"name": "Dips", "reps": "3xFail", "icon": "format-vertical-align-bottom"}, {"name": "Fly", "reps": "3x15", "icon": "butterfly"}, {"name": "Pushups", "reps": "2xFail", "icon": "arrow-down-bold"}],
    "Back Focus": [{"name": "Deadlift", "reps": "3x5", "icon": "weight-lifter"}, {"name": "Pullups", "reps": "3xFail", "icon": "human-handsup"}, {"name": "T-Bar", "reps": "3x10", "icon": "rowing"}, {"name": "Pulldown", "reps": "3x15", "icon": "arrow-down-bold"}],
    "Shoulder Focus": [{"name": "OHP", "reps": "4x8", "icon": "human-handsup"}, {"name": "Arnold", "reps": "3x12", "icon": "dumbbell"}, {"name": "Lat Raise", "reps": "5x15", "icon": "bird"}, {"name": "Face Pull", "reps": "3x15", "icon": "eye-outline"}],
    "Leg Focus": [{"name": "Squat", "reps": "4x8", "icon": "human-male-height"}, {"name": "Leg Press", "reps": "3x12", "icon": "car-brake-pedal"}, {"name": "Lunges", "reps": "3x20", "icon": "walk"}, {"name": "Leg Curl", "reps": "3x15", "icon": "seat-recline-normal"}],
    
    # --- CONDITIONING & FLOWS ---
    "HIIT": [{"name": "Burpees", "reps": "45s", "icon": "run-fast"}, {"name": "Box Jumps", "reps": "45s", "icon": "arrow-up-bold"}, {"name": "Climbers", "reps": "45s", "icon": "run"}],
    "Tabata": [{"name": "Sprints", "reps": "20s/10s", "icon": "run-fast"}, {"name": "Swings", "reps": "20s/10s", "icon": "kettlebell"}],
    "EMOM": [{"name": "Thrusters", "reps": "10/min", "icon": "dumbbell"}, {"name": "Pullups", "reps": "5/min", "icon": "human-handsup"}],
    "Animal Flow": [
        {"name": "Beast Crawl", "reps": "60s", "cue": "Knees Hovering", "icon": "dog-side"},
        {"name": "Crab Walk", "reps": "60s", "cue": "Hips High", "icon": "human-handsdown"},
        {"name": "Scorpion Reach", "reps": "10/side", "cue": "Rotate Hips", "icon": "yoga"},
        {"name": "Ape Hops", "reps": "60s", "cue": "Lateral", "icon": "run"}
    ],
    
    # --- RECOVERY ---
    "Desk Undo": [{"name": "Chin Tucks", "reps": "20 reps", "icon": "head"}, {"name": "Doorway Stretch", "reps": "60s", "icon": "door"}, {"name": "Thoracic Ext", "reps": "60s", "icon": "yoga"}],
    "Squat Primer": [{"name": "90/90", "reps": "60s", "icon": "seat-recline-normal"}, {"name": "Ankle Rocks", "reps": "20 reps", "icon": "foot-print"}, {"name": "Goblet Hold", "reps": "60s", "icon": "dumbbell"}],
    "Mobility": [{"name": "Cat Cow", "reps": "60s", "icon": "yoga"}, {"name": "90/90", "reps": "60s", "icon": "seat-recline-normal"}, {"name": "Deep Squat", "reps": "60s", "icon": "human-male-height"}]
}

WARMUPS = [
    {"name": "Arm Circles", "reps": "30s", "cue": "Dynamic", "icon": "refresh", "type": "WARMUP"},
    {"name": "Band Pulls", "reps": "20 Reps", "cue": "Rear Delts", "icon": "arrow-left-right", "type": "WARMUP"}
]

COOLDOWNS = {
    "General": {"name": "Childs Pose", "reps": "60s", "cue": "Relax Spine", "icon": "human-child", "type": "COOLDOWN"}
}

# =========================================================================
# 3. ENGINE (SAFE STORAGE)
# =========================================================================

class AppEngine:
    def __init__(self):
        self.log_file = None 

    def init_storage(self, user_data_dir):
        if platform == 'android':
            from android.storage import app_storage_path
            self.dir = app_storage_path()
        else:
            self.dir = user_data_dir
        self.log_file = os.path.join(self.dir, 'iron_log.csv')
        if not os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'w', newline='') as f:
                    csv.writer(f).writerow(["Date", "Exercise", "Weight", "Reps", "1RM"])
            except: pass

    def save_log(self, ex, w, r):
        if not self.log_file: return
        try:
            with open(self.log_file, 'a', newline='') as f:
                csv.writer(f).writerow([date.today(), ex, w, r, calculate_1rm(w, r)])
        except: pass

    def get_history(self, ex):
        if not self.log_file or not os.path.exists(self.log_file): return "New Exercise"
        try:
            with open(self.log_file, 'r') as f:
                rows = list(csv.reader(f))
                for row in reversed(rows[1:]):
                    if row[1] == ex: return f"LAST: {row[2]}kg x {row[3]}"
        except: pass
        return "New Exercise"

    def generate(self, mode):
        playlist = []
        # Warmup (Skip for flows/cardio)
        if mode not in ["Mobility", "HIIT", "Tabata", "EMOM", "Desk Undo", "Squat Primer", "Animal Flow"]:
            playlist.extend([w.copy() for w in WARMUPS])
            for p in playlist: p["history"] = "-" 

        # Main Workout
        if mode in EXERCISE_DB:
            for slot in EXERCISE_DB[mode]:
                if "type" in slot and slot["type"] == "pool":
                    ex = random.choice(slot["options"]).copy()
                else:
                    ex = slot.copy()
                ex["history"] = self.get_history(ex["name"])
                ex["type"] = "WORKOUT"
                if "icon" not in ex: ex["icon"] = "dumbbell"
                playlist.append(ex)

        # Cooldown
        if mode not in ["Mobility", "HIIT", "Tabata", "EMOM", "Desk Undo", "Squat Primer", "Animal Flow"]:
            cd = COOLDOWNS["General"].copy()
            cd["history"] = "-"
            playlist.append(cd)

        return playlist

engine = AppEngine()

# =========================================================================
# 4. CYBERPUNK UI (FINAL)
# =========================================================================

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<NavCard@MDCard>:
    radius: [15]
    md_bg_color: 0.15, 0.15, 0.15, 1
    padding: "10dp"
    ripple_behavior: True
    orientation: 'vertical'
    size_hint_y: None
    height: "110dp"
    elevation: 2

<NavIcon@MDIcon>:
    halign: "center"
    theme_text_color: "Custom"
    text_color: 0, 1, 0.5, 1
    font_size: "36sp"

<NavText@MDLabel>:
    halign: "center"
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    bold: True
    font_style: "Caption"

ScreenManager:
    HomeScreen:
    WorkoutScreen:
    GuideScreen:
    ToolsScreen:

<HomeScreen>:
    name: 'home'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.08, 0.08, 0.08, 1
        
        MDTopAppBar:
            title: "IRON VAULT"
            right_action_items: [["book-open-variant", lambda x: app.open_guide()], ["calculator", lambda x: app.open_tools()]]
            elevation: 0
            md_bg_color: 0.08, 0.08, 0.08, 1
            specific_text_color: 0, 1, 0.5, 1
            title_color: 0, 1, 0.5, 1

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"
                adaptive_height: True

                # HEADER
                MDCard:
                    size_hint_y: None
                    height: "80dp"
                    radius: [20]
                    md_bg_color: 0.12, 0.12, 0.12, 1
                    padding: "20dp"
                    MDBoxLayout:
                        orientation: 'vertical'
                        MDLabel:
                            text: "WELCOME BACK"
                            theme_text_color: "Custom"
                            text_color: 0.5, 0.5, 0.5, 1
                            font_style: "Caption"
                        MDLabel:
                            text: "READY TO LIFT?"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            font_style: "H5"
                            bold: True

                # --- PHAT ---
                MDLabel:
                    text: "PHAT SYSTEM"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0.5, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 2
                    spacing: "15dp"
                    adaptive_height: True
                    NavCard:
                        on_release: app.start_workout("Upper Power")
                        NavIcon:
                            icon: "arm-flex"
                        NavText:
                            text: "UPPER POWER"
                    NavCard:
                        on_release: app.start_workout("Lower Power")
                        NavIcon:
                            icon: "weight-lifter"
                        NavText:
                            text: "LOWER POWER"

                MDGridLayout:
                    cols: 3
                    spacing: "10dp"
                    adaptive_height: True
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Push Hyper")
                        NavIcon:
                            icon: "arrow-up-bold-box-outline"
                        NavText:
                            text: "PUSH"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Pull Hyper")
                        NavIcon:
                            icon: "arrow-down-bold-box-outline"
                        NavText:
                            text: "PULL"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Legs Hyper")
                        NavIcon:
                            icon: "run"
                        NavText:
                            text: "LEGS"

                # --- SPECIALTY ---
                MDLabel:
                    text: "SPECIALTY"
                    theme_text_color: "Custom"
                    text_color: 1, 0.7, 0, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 3
                    spacing: "10dp"
                    adaptive_height: True
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Bicep Blaster")
                        NavIcon:
                            icon: "arm-flex"
                            text_color: 1, 0.7, 0, 1
                        NavText:
                            text: "BICEPS"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Tricep Torture")
                        NavIcon:
                            icon: "arm-flex-outline"
                            text_color: 1, 0.7, 0, 1
                        NavText:
                            text: "TRICEPS"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Chest Focus")
                        NavIcon:
                            icon: "dumbbell"
                            text_color: 1, 0.7, 0, 1
                        NavText:
                            text: "CHEST"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Back Focus")
                        NavIcon:
                            icon: "weight-lifter"
                            text_color: 1, 0.7, 0, 1
                        NavText:
                            text: "BACK"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Shoulder Focus")
                        NavIcon:
                            icon: "human-handsup"
                            text_color: 1, 0.7, 0, 1
                        NavText:
                            text: "SHOULDERS"
                    NavCard:
                        height: "90dp"
                        on_release: app.start_workout("Leg Focus")
                        NavIcon:
                            icon: "human-male-height"
                            text_color: 1, 0.7, 0, 1
                        NavText:
                            text: "LEGS"

                # --- CONDITIONING ---
                MDLabel:
                    text: "CONDITIONING"
                    theme_text_color: "Custom"
                    text_color: 0, 0.8, 1, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 2
                    spacing: "10dp"
                    adaptive_height: True
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("HIIT")
                        NavIcon:
                            icon: "run-fast"
                            text_color: 0, 0.8, 1, 1
                        NavText:
                            text: "HIIT"
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("Animal Flow")
                        NavIcon:
                            icon: "dog-side"
                            text_color: 0, 0.8, 1, 1
                        NavText:
                            text: "ANIMAL FLOW"
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("Tabata")
                        NavIcon:
                            icon: "timer-sand"
                            text_color: 0, 0.8, 1, 1
                        NavText:
                            text: "TABATA"
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("EMOM")
                        NavIcon:
                            icon: "timer-outline"
                            text_color: 0, 0.8, 1, 1
                        NavText:
                            text: "EMOM"

                # --- RECOVERY ---
                MDLabel:
                    text: "RECOVERY"
                    theme_text_color: "Custom"
                    text_color: 0.5, 0.5, 1, 1
                    bold: True
                    adaptive_height: True

                MDGridLayout:
                    cols: 3
                    spacing: "10dp"
                    adaptive_height: True
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("Desk Undo")
                        NavIcon:
                            icon: "chair-rolling"
                            text_color: 0.5, 0.5, 1, 1
                        NavText:
                            text: "DESK UNDO"
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("Squat Primer")
                        NavIcon:
                            icon: "human-male-height"
                            text_color: 0.5, 0.5, 1, 1
                        NavText:
                            text: "PRIMER"
                    NavCard:
                        height: "80dp"
                        on_release: app.start_workout("Mobility")
                        NavIcon:
                            icon: "yoga"
                            text_color: 0.5, 0.5, 1, 1
                        NavText:
                            text: "FLOW"

<WorkoutScreen>:
    name: 'workout'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.08, 0.08, 0.08, 1
        
        MDTopAppBar:
            title: root.phase
            left_action_items: [["arrow-left", lambda x: root.exit()]]
            md_bg_color: 0.08, 0.08, 0.08, 1
            specific_text_color: 0, 1, 0.5, 1

        MDProgressBar:
            value: root.progress
            color: 0, 1, 0.5, 1
            size_hint_y: None
            height: "4dp"

        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "20dp"
            
            MDCard:
                size_hint_y: 0.55
                orientation: 'vertical'
                radius: [25]
                md_bg_color: 0.15, 0.15, 0.15, 1
                padding: "20dp"
                spacing: "10dp"
                elevation: 4

                MDIcon:
                    icon: root.ex_icon
                    halign: "center"
                    font_size: "60sp"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0.5, 1
                
                MDLabel:
                    text: root.ex_name
                    halign: "center"
                    font_style: "H4"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                
                MDSeparator:
                    height: "1dp"
                    color: 0.3, 0.3, 0.3, 1

                MDLabel:
                    text: "TARGET: " + root.ex_reps
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0.5, 1
                    bold: True

                MDLabel:
                    text: root.ex_hist
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.6, 0.6, 0.6, 1
                    font_style: "Caption"

                MDLabel:
                    text: '"' + root.ex_cue + '"'
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 0.8, 0, 1
                    font_style: "Subtitle1"
                    italic: True

            MDBoxLayout:
                spacing: "15dp"
                size_hint_y: None
                height: "70dp"
                
                MDCard:
                    radius: [10]
                    md_bg_color: 0.12, 0.12, 0.12, 1
                    padding: "10dp"
                    MDTextField:
                        id: w_input
                        hint_text: "Weight (kg)"
                        mode: "fill"
                        fill_color_normal: 0.12, 0.12, 0.12, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_focus: 0, 1, 0.5, 1

                MDCard:
                    radius: [10]
                    md_bg_color: 0.12, 0.12, 0.12, 1
                    padding: "10dp"
                    MDTextField:
                        id: r_input
                        hint_text: "Reps"
                        mode: "fill"
                        fill_color_normal: 0.12, 0.12, 0.12, 1
                        text_color_normal: 1, 1, 1, 1
                        line_color_focus: 0, 1, 0.5, 1

            MDLabel:
                text: root.timer_txt
                halign: "center"
                font_style: "H4"
                theme_text_color: "Custom"
                text_color: 1, 0.2, 0.2, 1
                adaptive_height: True

            MDRaisedButton:
                text: "LOG SET & REST"
                size_hint_x: 1
                height: "60dp"
                md_bg_color: 0, 1, 0.5, 1
                text_color: 0, 0, 0, 1
                font_size: "18sp"
                on_release: root.next()
            
            Widget:

<GuideScreen>:
    name: 'guide'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.08, 0.08, 0.08, 1
        MDTopAppBar:
            title: "BLACK BOOK"
            left_action_items: [["arrow-left", lambda x: app.back_home()]]
            md_bg_color: 0.08, 0.08, 0.08, 1
            specific_text_color: 0, 1, 0.5, 1
        
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
        md_bg_color: 0.08, 0.08, 0.08, 1
        MDTopAppBar:
            title: "TOOLS"
            left_action_items: [["arrow-left", lambda x: app.back_home()]]
            md_bg_color: 0.08, 0.08, 0.08, 1
            specific_text_color: 0, 1, 0.5, 1
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "20dp"
            
            MDCard:
                radius: [20]
                md_bg_color: 0.15, 0.15, 0.15, 1
                padding: "20dp"
                orientation: 'vertical'
                spacing: "20dp"
                adaptive_height: True

                MDLabel:
                    text: "PLATE CALCULATOR"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0.5, 1
                    bold: True
                    halign: "center"

                MDTextField:
                    id: plate_in
                    hint_text: "Target Weight (kg)"
                    line_color_focus: 0, 1, 0.5, 1
                    text_color_normal: 1, 1, 1, 1
                
                MDRaisedButton:
                    text: "CALCULATE LOAD"
                    size_hint_x: 1
                    md_bg_color: 0, 1, 0.5, 1
                    text_color: 0, 0, 0, 1
                    on_release: root.calc_plate()

                MDLabel:
                    id: plate_out
                    text: "Side Load: -"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    font_style: "H6"
            
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
            card = Builder.load_string('''
MDCard:
    orientation: 'vertical'
    padding: "15dp"
    spacing: "10dp"
    radius: [15]
    md_bg_color: 0.15, 0.15, 0.15, 1
    size_hint_y: None
    height: self.minimum_height
    elevation: 3
''')
            card.add_widget(MDLabel(text=title, font_style="H6", theme_text_color="Custom", text_color=(0, 1, 0.5, 1), bold=True, size_hint_y=None, height="30dp"))
            card.add_widget(MDLabel(text=content["subtitle"], font_style="Caption", theme_text_color="Custom", text_color=(1, 0.5, 0, 1), size_hint_y=None, height="20dp"))
            card.add_widget(MDLabel(text=content["body"], theme_text_color="Custom", text_color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height="80dp"))
            box.add_widget(card)

class WorkoutScreen(MDScreen):
    ex_name = StringProperty("Loading...")
    ex_reps = StringProperty("-")
    ex_hist = StringProperty("-")
    ex_cue = StringProperty("-")
    ex_icon = StringProperty("dumbbell")
    phase = StringProperty("WARMUP")
    timer_txt = StringProperty("")
    progress = NumericProperty(0)
    
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
            self.ex_icon = data.get("icon", "dumbbell")
            self.phase = data.get("type", "WORKOUT")
            self.progress = (self.idx / len(self.queue)) * 100
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
        self.theme_cls.primary_palette = "LightGreen" 
        engine.init_storage(self.user_data_dir)
        return Builder.load_string(KV)

    def start_workout(self, mode):
        self.root.get_screen('workout').load(engine.generate(mode))
        self.root.current = 'workout'

    def open_guide(self): self.root.current = 'guide'
    def open_tools(self): self.root.current = 'tools'
    def back_home(self): self.root.current = 'home'

if __name__ == '__main__':
    IronVaultApp().run()
