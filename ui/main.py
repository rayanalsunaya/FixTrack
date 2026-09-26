from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# the 8 usage patterns, same order as the database
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


class SetupScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 20
        self.spacing = 15

        self.add_widget(Label(text="How do you mostly use your car?", font_size=20))

        self.pattern_spinner = Spinner(text=patterns[0], values=patterns)
        self.add_widget(self.pattern_spinner)

        self.add_widget(Label(text="Preferred oil change interval (km):"))

        self.interval_input = TextInput(text="5000", multiline=False)
        self.add_widget(self.interval_input)

        continue_button = Button(text="Continue")
        continue_button.bind(on_press=self.on_continue)
        self.add_widget(continue_button)

    def on_continue(self, instance):
        pattern_number = patterns.index(self.pattern_spinner.text) + 1
        interval = self.interval_input.text
        print("pattern chosen:", pattern_number)
        print("interval chosen:", interval)


class FixTrackApp(App):
    def build(self):
        return SetupScreen()


FixTrackApp().run()
