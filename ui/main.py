from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Line
from datetime import date, timedelta
import sqlite3
import pickle
import pandas as pd
import os
 
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "..", "Database", "fixtrack.db")
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "usage_model.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "..", "models", "model_columns.pkl")
CAR_IMAGE_PATH = os.path.join(BASE_DIR, "car_icon.png")
APP_ICON_PATH = os.path.join(BASE_DIR, "app_icon.png")
 
# FixTrack brand colors (same as the mockup and banner)
CREAM = (0.98, 0.965, 0.937, 1)  # Warm Ivory
NAVY = (0.106, 0.137, 0.247, 1)
CORAL = (1, 0.42, 0.29, 1)
WHITE = (1, 1, 1, 1)
 
Window.clearcolor = CREAM
 
patterns = [
    "Work commute only",
    "Work + daily errands",
    "Heavy daily use (delivery)",
    "Frequent intercity travel",
    "Secondary / backup vehicle",
    "Driven by a private driver",
    "Weekend-only use",
    "Rare use / occasions only"
]
 
 
# each dropdown option gets its own white card with a coral border,
# instead of the default large gray Kivy look
class StyledSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.color = NAVY
        self.size_hint_y = None
        self.height = 42
 
        with self.canvas.before:
            Color(*WHITE)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            Color(*CORAL)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1.2)
 
        self.bind(pos=self.update_graphics, size=self.update_graphics)
 
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)
 
 
def save_to_database(pattern_number, interval):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
 
    cursor.execute("SELECT id FROM vehicles LIMIT 1")
    row = cursor.fetchone()
 
    if row is None:
        cursor.execute(
            "INSERT INTO vehicles (user_id, make, model) VALUES (1, 'Test Car', 'Demo')"
        )
        vehicle_id = cursor.lastrowid
    else:
        vehicle_id = row[0]
 
    cursor.execute(
        "SELECT estimated_km_per_day FROM usage_patterns WHERE id = ?", (pattern_number,)
    )
    usage_rate = cursor.fetchone()[0]
 
    cursor.execute(
        """
        INSERT INTO vehicle_profile (vehicle_id, usage_pattern_id, preferred_interval_km, current_usage_rate)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(vehicle_id) DO UPDATE SET
            usage_pattern_id = excluded.usage_pattern_id,
            preferred_interval_km = excluded.preferred_interval_km,
            current_usage_rate = excluded.current_usage_rate
        """,
        (vehicle_id, pattern_number, interval, usage_rate),
    )
 
    conn.commit()
    conn.close()
 
 
def predict_result(pattern_number, interval):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(COLUMNS_PATH, "rb") as f:
        columns = pickle.load(f)
 
    row = pd.DataFrame([[interval]], columns=["preferred_interval"])
    for col in columns:
        if col != "preferred_interval":
            row[col] = 0
 
    pattern_col = "usage_pattern_" + str(pattern_number)
    if pattern_col in row.columns:
        row[pattern_col] = 1
 
    row = row[columns]
 
    predicted_km_per_day = model.predict(row)[0]
    days_left = interval / predicted_km_per_day
    predicted_date = date.today() + timedelta(days=days_left)
 
    return predicted_km_per_day, predicted_date
 
 
def styled_label(text, size=16, bold=False):
    label = Label(text=text, color=NAVY, font_size=size, bold=bold)
    label.size_hint_y = None
    label.height = 36
    return label
 
 
# hides the currently selected value from the dropdown list when it
# opens, so you don't see the same option twice (once closed, once
# again as the first row in the list) - same behavior as an iPhone picker
class FilteredSpinner(Spinner):
    def _toggle_dropdown(self, *largs):
        if not self.is_open:
            self.values = [p for p in patterns if p != self.text]
        super()._toggle_dropdown(*largs)
 
 
def wrap_spinner_with_arrow(spinner, height=48):
    # puts a border around the closed spinner and a small down-arrow
    # on the right, so it's obvious it's tappable and has more options
    wrapper = FloatLayout(size_hint_y=None, height=height)
 
    with wrapper.canvas.after:
        Color(*CORAL)
        border = Line(rounded_rectangle=(wrapper.x, wrapper.y, wrapper.width, wrapper.height, 8), width=1.4)
 
    def update_border(*args):
        border.rounded_rectangle = (wrapper.x, wrapper.y, wrapper.width, wrapper.height, 8)
 
    wrapper.bind(pos=update_border, size=update_border)
 
    spinner.size_hint = (1, 1)
    spinner.pos_hint = {"x": 0, "y": 0}
    wrapper.add_widget(spinner)
 
    arrow = Label(text="v", color=CORAL, bold=True, size_hint=(None, None), size=(24, 24))
    arrow.pos_hint = {"right": 0.97, "center_y": 0.5}
    wrapper.add_widget(arrow)
 
    return wrapper
 
 
def styled_button(text):
    btn = Button(text=text, background_normal="", background_color=CORAL, color=WHITE)
    btn.size_hint_y = None
    btn.height = 50
    return btn
 
 
class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=14)
 
        car_image = Image(source=CAR_IMAGE_PATH, size_hint_y=None, height=110)
        layout.add_widget(car_image)
 
        layout.add_widget(styled_label("How do you mostly use your car?", size=20, bold=True))
        layout.add_widget(styled_label("Tap below to choose from 8 options", size=12))
 
        self.pattern_spinner = FilteredSpinner(
            text=patterns[0], values=patterns,
            option_cls=StyledSpinnerOption,
            background_normal="", background_color=WHITE, color=NAVY
        )
        layout.add_widget(wrap_spinner_with_arrow(self.pattern_spinner))
 
        layout.add_widget(styled_label("Preferred oil change interval (km):"))
 
        self.interval_input = TextInput(
            text="5000", multiline=False, halign="center",
            background_color=WHITE, foreground_color=NAVY,
            size_hint_y=None, height=48
        )
        self.interval_input.bind(
            width=lambda widget, value: setattr(widget, "text_size", (value, None))
        )
        layout.add_widget(self.interval_input)
 
        continue_button = styled_button("Continue")
        continue_button.bind(on_press=self.on_continue)
        layout.add_widget(continue_button)
 
        layout.add_widget(Label())
 
        self.add_widget(layout)
 
    def on_continue(self, instance):
        pattern_number = patterns.index(self.pattern_spinner.text) + 1
        interval = int(self.interval_input.text)
 
        save_to_database(pattern_number, interval)
        usage_rate, predicted_date = predict_result(pattern_number, interval)
 
        result_screen = self.manager.get_screen("result")
        result_screen.show_result(usage_rate, predicted_date)
        self.manager.current = "result"
 
 
class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=18)
 
        layout.add_widget(styled_label("Your maintenance prediction", size=20, bold=True))
 
        self.rate_label = styled_label("")
        layout.add_widget(self.rate_label)
 
        self.date_label = styled_label("", size=24, bold=True)
        layout.add_widget(self.date_label)
 
        layout.add_widget(Label())
 
        self.add_widget(layout)
 
    def show_result(self, usage_rate, predicted_date):
        self.rate_label.text = "Estimated usage: " + str(round(usage_rate, 1)) + " km/day"
        self.date_label.text = "Next maintenance: " + str(predicted_date)
 
 
class FixTrackApp(App):
    icon = APP_ICON_PATH
 
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SetupScreen(name="setup"))
        sm.add_widget(ResultScreen(name="result"))
        return sm
 
 
FixTrackApp().run()



 




