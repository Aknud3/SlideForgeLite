from kivy.config import Config

Config.set("graphics", "fullscreen", "0")
Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "800")
Config.set("graphics", "height", "600")

import kivy
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
import os
from pptx import Presentation
import importlib.util
import sys
from tkinter import filedialog, Tk
import pyperclip
from kivy.uix.spinner import Spinner
import uuid
from kivy.uix.widget import Widget
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.uix.colorpicker import ColorPicker
from kivy.utils import get_color_from_hex
import traceback
from kivy.uix.popup import Popup


# Nastavení šedého pozadí GUI
Window.clearcolor = (242, 242, 242, 1)  # Šedé pozadí

# Slovník pro překlad GUI (čeština) do promptu (angličtina)
TRANSLATIONS = {
    "Tón prezentace": "The tone of the presentation should be",
    "Technický": "technical",
    "Základní": "casual",
    "Edukační": "educational",
    "Profesionální": "professional",
    "Obsah": "Table of Contents",
    "Ano": "Yes",
    "Ne": "No",
    "Snímek Děkujeme": "Thank You Slide",
    "Není potřeba": "Not needed",
    "Děkujeme za pozornost": "Thank You for Your Attention",
}


class Manager(ScreenManager):
    pass


# Definice barev
WHITE = (1, 1, 1, 1)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 1)
GRAY = (242 / 255.0, 242 / 255.0, 242 / 255.0, 1)

# Akcentní
RED = (208 / 255.0, 68 / 255.0, 35 / 255.0, 1)
TYRQUOISE = (35 / 255.0, 208 / 255.0, 169 / 255.0, 1)

# Doplňkové
TEXT_COLOR = (51 / 255.0, 51 / 255.0, 51 / 255.0, 1)
ANALOG1 = (208 / 255.0, 126 / 255.0, 35 / 255.0, 1)
ANALOG2 = (208 / 255.0, 35 / 255.0, 76 / 255.0, 1)


class PromptScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Hlavní widget s pozadím
        main_widget = Widget()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá karta (slide)
        self.card_width = Window.width * 0.8
        self.card_height = Window.height * 0.7
        self.card_x = Window.width * 0.1
        self.card_y = Window.height * 0.15

        with main_widget.canvas.before:
            Color(*WHITE)
            self.card_rect = Rectangle(
                pos=(self.card_x, self.card_y), size=(self.card_width, self.card_height)
            )

        # Nadpis
        self.title_input = TextInput(
            hint_text="Kliknutím vložíte název prezentace.",
            multiline=False,
            font_size=36,
            font_name="Calibri",
            background_color=TRANSPARENT,
            hint_text_color=TEXT_COLOR,
            halign="center",
            size_hint=(None, None),
            foreground_color=BLACK,
            size=(self.card_width * 0.9, 60),
            pos=(
                self.card_x + self.card_width * 0.05,
                self.card_y + self.card_height * 0.6,
            ),
        )
        main_widget.add_widget(self.title_input)

        # Podnadpis
        self.subtitle_input = TextInput(
            hint_text="Kliknutím vložíte název autora.",
            multiline=False,
            font_size=30,
            font_name="Calibri",
            background_color=TRANSPARENT,
            hint_text_color=TEXT_COLOR,
            halign="center",
            foreground_color=BLACK,
            size_hint=(None, None),
            size=(self.card_width * 0.9, 50),
            pos=(
                self.card_x + self.card_width * 0.05,
                self.card_y + self.card_height * 0.3,
            ),
        )
        main_widget.add_widget(self.subtitle_input)

        # Tlačítko "Další krok"
        btn_width = Window.width * 0.4
        btn_height = Window.height * 0.08
        self.next_btn = Button(
            text="Další krok",
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width / 2 - btn_width / 2, Window.height * 0.05),
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=WHITE,
        )

        # Zaoblené rohy tlačítka
        with self.next_btn.canvas.before:
            Color(*RED)
            self.btn_rect = RoundedRectangle(
                pos=self.next_btn.pos,
                size=self.next_btn.size,
                radius=[
                    10,
                ],
            )
        self.next_btn.bind(
            pos=self._update_btn_rect,
            size=self._update_btn_rect,
            on_press=lambda x: setattr(self.manager, "current", "instructions"),
        )
        main_widget.add_widget(self.next_btn)

        self.add_widget(main_widget)

    def _update_bg(self, instance, value):
        self.bg_rect.size = value

    def _update_btn_rect(self, instance, value):
        self.btn_rect.pos = instance.pos
        self.btn_rect.size = instance.size


class InstructionsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Hlavní widget se šedým pozadím
        main_widget = FloatLayout()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá "slide" karta
        slide_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=20,
            spacing=15,
        )
        with slide_box.canvas.before:
            Color(*WHITE)
            self.rect = Rectangle(pos=slide_box.pos, size=slide_box.size)
        slide_box.bind(pos=self.update_rect, size=self.update_rect)

        # Nadpis
        header = Label(
            text="Nastavení instrukcí",
            font_size=30,
            font_name="Calibri",
            color=RED,
            halign="left",
            size_hint=(1, 0.1),
            text_size=(550, None),
        )
        slide_box.add_widget(header)

        slide_box.add_widget(
            Label(
                size_hint_y=None,
                height=5,
                text="__________________________________________________________________________________________",
                color=TEXT_COLOR,
            )
        )

        # TextInput pro instrukce
        self.instructions_input = TextInput(
            hint_text="Napište všechny instrukce pro umělou inteligenci…",
            multiline=True,
            font_size=20,
            font_name="Calibri",
            background_color=TRANSPARENT,
            foreground_color=BLACK,
            hint_text_color=TEXT_COLOR,
            size_hint=(1, 0.6),
            padding=(40, 10, 0, 0),
        )
        slide_box.add_widget(self.instructions_input)

        # Přidáme slide_box do main_widget
        main_widget.add_widget(slide_box)

        # Tlačítko "Další krok"
        btn_width = Window.width * 0.4
        btn_height = Window.height * 0.08
        next_btn = Button(
            text="Další krok",
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width / 2 - btn_width / 2, Window.height * 0.05),
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=WHITE,
        )
        next_btn.bind(on_press=self.save_and_next)
        main_widget.add_widget(next_btn)

        # Přidáme main_widget do screenu
        self.add_widget(main_widget)

    def update_rect(self, instance, _):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_bg(self, instance, size):
        self.bg_rect.size = size

    def save_and_next(self, instance):
        """Uloží data z textového pole a přepne na LanguageScreen"""
        self.manager.get_screen("language").instructions = self.instructions_input.text
        self.manager.current = "language"


class LanguageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instructions = ""  # Pro uložení instrukcí z předchozí obrazovky

        # Hlavní widget se šedým pozadím
        main_widget = FloatLayout()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá "slide" karta
        slide_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=20,
            spacing=10,
        )
        with slide_box.canvas.before:
            Color(*WHITE)
            self.rect = Rectangle(pos=slide_box.pos, size=slide_box.size)
        slide_box.bind(pos=self.update_rect, size=self.update_rect)

        # Nadpis
        title_label = Label(
            text="Nastavení jazyka",
            halign="left",
            font_size=30,
            font_name="Calibri",
            color=RED,
            size_hint=(1, 0.1),
            text_size=(550, None),
        )
        slide_box.add_widget(title_label)

        slide_box.add_widget(
            Label(
                size_hint_y=None,
                height=5,
                text="__________________________________________________________________________________________",
                color=TEXT_COLOR,
            )
        )
        # ScrollView s formulářem
        scroll = ScrollView(size_hint=(1, 0.9))
        content_grid = GridLayout(cols=1, size_hint_y=None, spacing=20, padding=10)
        content_grid.bind(minimum_height=content_grid.setter("height"))

        # Jazyk
        content_grid.add_widget(
            Label(
                text="Zadejte jazyk:",
                font_size=24,
                font_name="Calibri",
                halign="left",
                color=TEXT_COLOR,
                size_hint_y=None,
                height=40,
                text_size=(550, None),
            )
        )
        self.language_input = TextInput(
            hint_text="Angličtina, Čeština, Němčina, Ruština",
            multiline=False,
            font_size=20,
            halign="left",
            font_name="Calibri",
            background_color=TRANSPARENT,
            foreground_color=BLACK,
            hint_text_color=TEXT_COLOR,
            size_hint_y=None,
            height=40,
            padding=[30, 0, 0, 0],
        )
        content_grid.add_widget(self.language_input)

        # Úroveň
        content_grid.add_widget(
            Label(
                text="Úroveň jazykové dovednosti",
                font_size=24,
                font_name="Calibri",
                color=RED,
                size_hint_y=None,
                height=40,
                halign="left",
                text_size=(None, None),
            )
        )
        level_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=100,
            spacing=20,
            padding=[0, 0, 10, 0],
        )
        self.level_checkboxes = {}
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            cb_layout = BoxLayout(orientation="vertical", spacing=10)
            lbl = Label(
                text=level,
                font_size=20,
                font_name="Calibri",
                color=BLACK,
                size_hint_y=None,
                height=40,
                halign="center",
                text_size=(None, None),
            )
            cb = CheckBox(
                size_hint=(None, None),
                size=(40, 40),
                pos_hint={"center_x": 0.5},
                color=RED,
                opacity=1,
            )
            cb.bind(active=self.on_level_checkbox_active)
            self.level_checkboxes[level] = cb
            cb_layout.add_widget(lbl)
            cb_layout.add_widget(cb)
            level_box.add_widget(cb_layout)

        content_grid.add_widget(level_box)

        scroll.add_widget(content_grid)
        slide_box.add_widget(scroll)

        # Přidáme slide_box do main_widget
        main_widget.add_widget(slide_box)

        # Tlačítko "Další krok"
        btn_width = Window.width * 0.4
        btn_height = Window.height * 0.08
        next_btn = Button(
            text="Další krok",
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width / 2 - btn_width / 2, Window.height * 0.05),
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=WHITE,
        )
        next_btn.bind(
            on_press=lambda instance: setattr(self.manager, "current", "color")
        )
        main_widget.add_widget(next_btn)

        # Přidáme main_widget do screenu
        self.add_widget(main_widget)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_bg(self, instance, size):
        self.bg_rect.size = size

    def on_level_checkbox_active(self, checkbox, value):
        if value:
            # Zrušíme ostatní
            for lvl, cb in self.level_checkboxes.items():
                if cb is not checkbox:
                    cb.active = False
            # Uložíme vybranou úroveň
            self.selected_level = next(
                lvl for lvl, cb in self.level_checkboxes.items() if cb is checkbox
            )


class ColorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Hlavní widget se šedým pozadím
        main_widget = FloatLayout()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá "slide" karta
        slide_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=20,
            spacing=15,
        )
        with slide_box.canvas.before:
            Color(*WHITE)
            self.rect = Rectangle(pos=slide_box.pos, size=slide_box.size)
        slide_box.bind(pos=self.update_rect, size=self.update_rect)

        self.selected_rgb = (0.29, 0.56, 0, 1)  # Výchozí modrá

        # Nadpis
        slide_box.add_widget(
            Label(
                text="Nastavení hlavní barvy",
                font_size=28,
                font_name="Calibri",
                color=RED,
                size_hint=(1, 0.1),
                halign="left",
                text_size=(550, None),
            )
        )
        slide_box.add_widget(
            Label(
                size_hint_y=None,
                height=5,
                text="__________________________________________________________________________________________",
                color=TEXT_COLOR,
            )
        )

        # Color Picker
        self.picker = ColorPicker(size_hint=(1, 0.8))
        self.picker.bind(color=self.on_color)
        slide_box.add_widget(self.picker)

        btn_width = Window.width * 0.4
        btn_height = Window.height * 0.08
        next_btn = Button(
            text="Další krok",
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width / 2 - btn_width / 2, Window.height * 0.05),
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=WHITE,
        )
        next_btn.bind(on_press=self.next_step)
        main_widget.add_widget(slide_box)
        main_widget.add_widget(next_btn)

        self.add_widget(main_widget)

    def on_color(self, instance, value):
        self.selected_rgb = value  # rgba (0–1 float)

    def next_step(self, instance):
        self.manager.get_screen("settings").selected_rgb = self.selected_rgb
        self.manager.current = "settings"

    def _update_bg(self, instance, size):
        self.bg_rect.size = size
        self.bg_rect.pos = instance.pos

    def save_and_next(self, instance):
        """Uloží data z textového pole a přepne na LanguageScreen"""
        self.manager.get_screen("language").instructions = self.instructions_input.text
        self.manager.current = "color"

    def update_rect(self, instance, _):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_widget = FloatLayout()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá "slide" karta
        slide_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=20,
            spacing=15,
        )
        with slide_box.canvas.before:
            Color(*WHITE)
            self.rect = Rectangle(pos=slide_box.pos, size=slide_box.size)
        slide_box.bind(pos=self.update_rect, size=self.update_rect)
        # Tón
        slide_box.add_widget(
            Label(
                text="Tón prezentace:",
                font_size=24,
                font_name="Calibri",
                color=RED,
                halign="left",
                text_size=(550, None),
            )
        )
        self.tone_checkboxes = {}
        tone_box = BoxLayout(orientation="horizontal", spacing=5)
        for tone in ["Technický", "Základní", "Edukační", "Profesionální"]:
            cb = CheckBox(size_hint=(None, None), size=(30, 30), color=RED)
            cb.bind(active=self.on_tone_checkbox_active)
            lbl = Label(text=tone, font_size=20, font_name="Calibri", color=TEXT_COLOR)
            box = BoxLayout()
            box.add_widget(cb)
            box.add_widget(lbl)
            tone_box.add_widget(box)
            self.tone_checkboxes[tone] = cb
        slide_box.add_widget(tone_box)

        # Délka
        slide_box.add_widget(
            Label(
                text="Délka (minuty):",
                font_size=24,
                font_name="Calibri",
                color=RED,
                halign="left",
                text_size=(550, None),
            )
        )
        self.duration_input = TextInput(
            hint_text="Např. 5",
            input_filter="int",
            font_size=20,
            size_hint_y=None,
            height=40,
            background_color=TRANSPARENT,
            foreground_color=BLACK,
        )
        slide_box.add_widget(self.duration_input)

        # Obsah
        slide_box.add_widget(
            Label(
                text="Snímek, kde je obsah:",
                font_size=24,
                font_name="Calibri",
                color=RED,
                halign="left",
                text_size=(550, None),
            )
        )
        self.toc_checkboxes = {}
        toc_box = BoxLayout(orientation="horizontal", spacing=5)
        for option in ["Ano", "Ne"]:
            cb = CheckBox(size_hint=(None, None), size=(30, 30), color=RED)
            cb.bind(active=self.on_toc_checkbox_active)
            lbl = Label(
                text=option,
                font_size=20,
                font_name="Calibri",
                color=TEXT_COLOR,
                halign="left",
                text_size=(250, None),
            )
            box = BoxLayout()
            box.add_widget(cb)
            box.add_widget(lbl)
            toc_box.add_widget(box)
            self.toc_checkboxes[option] = cb
        slide_box.add_widget(toc_box)

        # Snímek Děkujeme
        slide_box.add_widget(
            Label(
                text="Snímek děkuji za pozornost:",
                font_size=24,
                font_name="Calibri",
                color=RED,
                halign="left",
                text_size=(550, None),
            )
        )
        self.thank_you_checkboxes = {}
        thank_you_box = BoxLayout(orientation="horizontal", spacing=5)
        for option in ["Ano", "Ne"]:
            cb = CheckBox(size_hint=(None, None), size=(30, 30), color=RED)
            cb.bind(active=self.on_thank_you_checkbox_active)
            lbl = Label(
                text=option,
                font_size=20,
                font_name="Calibri",
                color=TEXT_COLOR,
                halign="left",
                text_size=(250, None),
            )
            box = BoxLayout()
            box.add_widget(cb)
            box.add_widget(lbl)
            thank_you_box.add_widget(box)
            self.thank_you_checkboxes[option] = cb
        slide_box.add_widget(thank_you_box)

        main_widget.add_widget(slide_box)

        btn_width = Window.width * 0.4
        btn_height = Window.height * 0.08
        btn = Button(
            text="Další krok",
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width / 2 - btn_width / 2, Window.height * 0.05),
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=WHITE,
        )
        btn.bind(on_press=lambda x: setattr(self.manager, "current", "export"))
        main_widget.add_widget(btn)

        self.add_widget(main_widget)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_tone_checkbox_active(self, checkbox, value):
        if value:
            for cb in self.tone_checkboxes.values():
                if cb != checkbox:
                    cb.active = False
            self.selected_tone = next(
                k for k, v in self.tone_checkboxes.items() if v is checkbox
            )

    def on_toc_checkbox_active(self, checkbox, value):
        if value:
            for cb in self.toc_checkboxes.values():
                if cb != checkbox:
                    cb.active = False
            self.selected_toc = next(
                k for k, v in self.toc_checkboxes.items() if v is checkbox
            )

    def on_thank_you_checkbox_active(self, checkbox, value):
        if value:
            for cb in self.thank_you_checkboxes.values():
                if cb != checkbox:
                    cb.active = False
            self.selected_thank_you = next(
                k for k, v in self.thank_you_checkboxes.items() if v is checkbox
            )

    def _update_bg(self, instance, size):
        self.bg_rect.size = size


class ExportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Hlavní widget se šedým pozadím
        main_widget = FloatLayout()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá "slide" karta
        slide_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=20,
            spacing=15,
        )
        with slide_box.canvas.before:
            Color(*WHITE)
            self.rect = Rectangle(pos=slide_box.pos, size=slide_box.size)
        slide_box.bind(pos=self.update_rect, size=self.update_rect)

        # Nadpis
        slide_box.add_widget(
            Label(
                text="Závěrečný krok",
                font_size=30,
                font_name="Calibri",
                color=RED,
                size_hint=(1, 0.1),
                halign="left",
                text_size=(550, None),
            )
        )

        slide_box.add_widget(
            Label(
                size_hint_y=None,
                height=5,
                text="__________________________________________________________________________________________",
                color=TEXT_COLOR,
            )
        )

        # Text s návodem
        slide_box.add_widget(
            Label(
                text="1. Zapněte si AI (např. ChatGPT / Grok / DeepSeek / Claude).\n"
                "2. Vložte do něho vygenerovaný skript.\n"
                "3. Počkejte na Python kód.\n"
                "4. Zkopírujte jej zpět do aplikace pro generaci prezentace.",
                font_size=20,
                font_name="Calibri",
                color=TEXT_COLOR,
                halign="left",
                valign="top",
                size_hint=(1, 0.3),
                text_size=(600, None),
            )
        )

        # Výběr cesty
        slide_box.add_widget(
            Label(
                text="Cesta k uložení:",
                font_size=24,
                font_name="Calibri",
                color=TEXT_COLOR,
                size_hint_y=None,
                height=40,
            )
        )
        path_box = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=40, spacing=10
        )
        self.save_path_input = TextInput(
            hint_text="Vyberte cestu...",
            readonly=True,
            font_size=20,
            font_name="Calibri",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_COLOR,
            hint_text_color=(0.5, 0.5, 0.5, 1),
        )
        path_box.add_widget(self.save_path_input)
        choose_path_btn = Button(
            text="Vybrat",
            size_hint=(0.3, 1),
            background_color=RED,
            font_size=20,
            background_normal="",
            font_name="Calibri",
            color=WHITE,
        )
        choose_path_btn.bind(on_press=self.choose_path)
        path_box.add_widget(choose_path_btn)
        slide_box.add_widget(path_box)

        main_widget.add_widget(slide_box)

        btn_width = Window.width * 0.4
        btn_height = Window.height * 0.08
        generate_btn = Button(
            text="Vygenerovat skript do schránky",
            size_hint=(None, None),
            size=(btn_width, btn_height),
            pos=(Window.width / 2 - btn_width / 2, Window.height * 0.05),
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=WHITE,
        )

        self.status_label = Label(
            text="Zadejte údaje a klikněte na Vygenerovat skript.",
            size_hint=(1, 1.8),
            font_size=20,
            font_name="Calibri",
            color=TEXT_COLOR,
        )
        main_widget.add_widget(self.status_label)

        generate_btn.bind(on_press=self.copy_prompt)
        main_widget.add_widget(generate_btn)

        self.add_widget(main_widget)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def choose_path(self, instance):
        ps = self.manager.get_screen("prompt")
        raw_prompt = ps.title_input.text or "prezentace"
        raw_author = ps.subtitle_input.text or "autor"

        name = f"{self.sanitize(raw_prompt)}_{self.sanitize(raw_author)}.pptx"

        root = Tk()
        root.withdraw()
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pptx",
            filetypes=[("PowerPoint soubory", "*.pptx")],
            title="Vyberte umístění a název souboru",
            initialfile=name,
        )
        root.destroy()
        if output_path:
            self.save_path_input.text = output_path

    def copy_prompt(self, instance):
        # Získání všech předchozích hodnot
        ps = self.manager.get_screen("prompt")
        ins = self.manager.get_screen("instructions")
        lang = self.manager.get_screen("language")
        sett = self.manager.get_screen("settings")
        color = self.manager.get_screen("color")

        prompt = ps.title_input.text.strip()
        author = ps.subtitle_input.text.strip()
        instructions = ins.instructions_input.text.strip()
        language = lang.language_input.text.strip()
        level = getattr(lang, "selected_level", "Není potřeba")
        tone = getattr(sett, "selected_tone", "Základní")
        duration = sett.duration_input.text.strip()
        toc = getattr(sett, "selected_toc", "Ne")
        thank_you = getattr(sett, "selected_thank_you", "Ne")
        save_path = self.save_path_input.text.strip()
        primary_color = color.selected_rgb

        if not prompt or not author or not language or not duration or not save_path:
            self.status_label.text = "Zkontrolujte, že všechny údaje jsou vyplněny!"
            setattr(self.manager, "current", "prompt")
            return

        # Překlad + formatování
        level = TRANSLATIONS.get(level, level)
        tone = TRANSLATIONS.get(tone, tone).lower()
        toc = TRANSLATIONS.get(toc, toc)
        thank_you = TRANSLATIONS.get(thank_you, thank_you)
        safe_save_path = save_path.replace("\\", "/")
        thank_you_text = {
            "Čeština": "Děkujeme za pozornost",
            "Angličtina": "Thank You for Your Attention",
            "Russian": "Спасибо за внимание",
            "German": "Vielen Dank für Ihre Aufmerksamkeit",
        }.get(language, "Thank You for Your Attention")

        full_prompt = (
            "# INPUT\n"
            f"Topic: {prompt}\n"
            f"Language: {language}\n"
            f"Level: {level}\n"
            f"Author: {author}\n"
            f"Tone: {tone}\n"
            "# NOTE: 1 slide takes 45 seconds to read.\n"
            "# Do NOT count the title slide, table of contents, or thank you slide in that timing.\n"
            f"Include Table of Contents: {toc}\n"
            f"Include Thank You Slide: {thank_you}\n\n"
            "# RULES\n"
            "- Use only python-pptx version 1.0.2\n"
            "- First slide must contain only the Topic (title) and Author (subtitle)\n"
            "- Content slides must have:\n"
            "  - Max 5 bullet points per slide\n"
            "  - Max 12 words per bullet point\n"
            "- Font requirements:\n"
            "  - Use a thematic font that fits the topic\n"
            "  - Font must be natively available on Windows (no downloads)\n"
            "  - Do not use Google Fonts or fonts requiring installation\n"
            f"- Color palette: Primary color {primary_color} with 2–3 complementary colors (use RGBColor)\n"
            "  - Light background with dark text for readability\n"
            "  - Apply colors consistently to:\n"
            "    - Slide background (slide.background.fill.solid())\n"
            "    - Title and bullet text (.font.color.rgb)\n"
            "- Layout requirements:\n"
            "  - Do not add slide numbers\n"
            "  - Titles: font size ≥ 28 pt, bold, center-aligned\n"
            "  - Bullet points: font size 18–22 pt, left-aligned\n"
            "  - Leave 1/3 of slide space for images\n"
            "- Content requirements:\n"
            "  - Speaker notes must expand on bullets (60–100 words)\n"
            "  - Each note must include one real-life example or application\n"
            "  - Include References slide before conclusion\n"
            "  - Use only reliable sources\n"
            "- Image requirements:\n"
            "  - Suggest one relevant image per content slide\n"
            "  - Add image description in speaker notes or as comment\n"
            '  - Example format: "Image suggestion: [description]"\n\n'
            "# FUNCTION REQUIREMENTS\n"
            "- Script must define a callable function: create_presentation()\n"
            "- Function must return the Presentation object\n\n"
            "# INSTRUCTIONS\n"
            f"{instructions}\n"
            "- Make each slide visually appealing\n"
            "- Balance text and white space\n"
            "- Ensure consistent styling throughout\n\n"
            "# OUTPUT CODE\n"
            "Generate a Python script using python-pptx 1.0.2 that implements this structure.\n"
            "Include these components in order:\n"
            "1. Import statements\n"
            "2. Color definitions\n"
            "3. create_presentation() function\n"
            "4. Slide creation logic\n"
            "5. Save and return\n\n"
            "# SAVE INSTRUCTIONS\n"
            "Use this exact save code at the end:\n"
            "# --- Save ---\n"
            f'prs.save("{safe_save_path}")\n'
            f'print("Saved: {os.path.basename(save_path)}")\n'
            "return prs"
        )

        pyperclip.copy(full_prompt)
        self.status_label.text = (
            "Zadání zkopírováno do schránky! Vložte ho do LLM a vygenerujte skript."
        )

        setattr(self.manager, "current", "script")

    def sanitize(self, s: str) -> str:
        s = s.strip().replace(" ", "_")
        diac_map = {
            "á": "a",
            "č": "c",
            "ď": "d",
            "é": "e",
            "ě": "e",
            "í": "i",
            "ň": "n",
            "ó": "o",
            "ř": "r",
            "š": "s",
            "ť": "t",
            "ú": "u",
            "ů": "u",
            "ý": "y",
            "ž": "z",
            "Á": "A",
            "Č": "C",
            "Ď": "D",
            "É": "E",
            "Ě": "E",
            "Í": "I",
            "Ň": "N",
            "Ó": "O",
            "Ř": "R",
            "Š": "S",
            "Ť": "T",
            "Ú": "U",
            "Ů": "U",
            "Ý": "Y",
            "Ž": "Z",
        }
        return "".join(
            [diac_map.get(c, c) for c in s if c.isalnum() or c in ("_", "-")]
        )

    def _update_bg(self, instance, value):
        self.bg_rect.size = value

    def _update_btn_rect(self, instance, value):
        self.btn_rect.pos = instance.pos
        self.btn_rect.size = instance.size


class ScriptScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Hlavní widget se šedým pozadím
        main_widget = FloatLayout()
        with main_widget.canvas.before:
            Color(*GRAY)
            self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        main_widget.bind(size=self._update_bg)

        # Bílá "slide" karta
        slide_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.7),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=20,
            spacing=15,
        )
        with slide_box.canvas.before:
            Color(*WHITE)
            self.rect = Rectangle(pos=slide_box.pos, size=slide_box.size)
        slide_box.bind(pos=self.update_rect, size=self.update_rect)

        slide_box.add_widget(
            Label(
                text="Vložte skript z Groku:",
                font_size=30,
                font_name="Calibri",
                color=RED,
                size_hint=(1, 0.1),
                halign="left",
                text_size=(550, None),
            )
        )

        scroll_view_script = ScrollView(size_hint=(1, 0.8))
        self.script_input = TextInput(
            hint_text="Sem vložte Python skript pro python-pptx",
            multiline=True,
            font_size=20,
            font_name="Calibri",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_COLOR,
            hint_text_color=(0.5, 0.5, 0.5, 1),
        )
        scroll_view_script.add_widget(self.script_input)
        slide_box.add_widget(scroll_view_script)

        generate_btn = Button(
            text="Vygenerovat prezentaci",
            size_hint=(0.5, 0.1),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=RED,
            font_size=24,
            font_name="Calibri",
            color=(1, 1, 1, 1),
        )
        generate_btn.bind(on_press=self.generate_presentation)
        slide_box.add_widget(generate_btn)

        self.status_label = Label(
            text="Vložte skript a klikněte na Vygenerovat.",
            size_hint=(1, 0.1),
            font_size=20,
            font_name="Calibri",
            color=TEXT_COLOR,
        )
        slide_box.add_widget(self.status_label)

        main_widget.add_widget(slide_box)
        self.add_widget(main_widget)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def generate_presentation(self, instance):
        self.script_content = self.script_input.text.strip()

        if not self.script_content:
            self.status_label.text = (
                "Vložte prosím Python skript pro generování prezentace!"
            )
            return

        script_path = f"temp_script_{uuid.uuid4().hex}.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self.script_content)

        try:
            spec = importlib.util.spec_from_file_location("pptx_script", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["pptx_script"] = module
            spec.loader.exec_module(module)

            prs = module.create_presentation()
            if prs:
                os.remove(script_path)

                popup = Popup(
                    title="Hotovo",
                    content=Label(text="Prezentace byla úspěšně vygenerována!"),
                    size_hint=(None, None),
                    size=(500, 200),
                )
                popup.bind(on_dismiss=self.close_app)
                popup.open()

                self.status_label.text = "✅ Prezentace byla vytvořena."
            else:
                self.status_label.text = "❌ Skript nevrátil platnou prezentaci!"

        except Exception as e:
            error_trace = traceback.format_exc()

            # Uložení do schránky
            pyperclip.copy(error_trace)

            # Zobrazení popupu
            popup = Popup(
                title="Chyba při generování",
                content=Label(
                    text="⚠️ Chyba při generování prezentace!\nChyba zkopírována do schránky.\n\nVložte ji do LLM a požádejte o opravu skriptu."
                ),
                size_hint=(None, None),
                size=(600, 300),
            )
            popup.open()

            self.status_label.text = (
                "❌ Chyba: zkopírováno do schránky, vložte do LLM k opravě."
            )

        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def _update_bg(self, instance, value):
        self.bg_rect.size = value

    def _update_btn_rect(self, instance, value):
        self.btn_rect.pos = instance.pos
        self.btn_rect.size = instance.size

    def close_app(instance):
        App.get_running_app().stop()
        sys.exit()


class SlideForgeLite(App):
    def build(self):
        sm = Manager()
        sm.add_widget(PromptScreen(name="prompt"))
        sm.add_widget(InstructionsScreen(name="instructions"))
        sm.add_widget(LanguageScreen(name="language"))
        sm.add_widget(ColorScreen(name="color"))
        sm.add_widget(ScriptScreen(name="script"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(ExportScreen(name="export"))
        sm.current = "prompt"  # Začínáme s PromptScreen
        return sm


if __name__ == "__main__":
    SlideForgeLite().run()
