from general_funcs import *


class Text:
    text = ''

    @staticmethod
    def save_text_input(frame_event):
        for event in frame_event:
            if event.type == pg.KEYDOWN:

                # Check for backspace
                if event.key == pg.K_BACKSPACE:

                    # get text input from 0 to -1 i.e. end.
                    Text.text = Text.text[:-1]

                # Unicode standard is used for string
                # formation
                else:
                    character = event.unicode
                    allowed_characters = '1234567890abcdefghijklmnopqrstuvwxyzåäöñè ,.()!?'
                    if character in allowed_characters:
                        Text.text += event.unicode

    @staticmethod
    def get_text():
        return Text.text

    @staticmethod
    def set_text(text=''):
        return_text = Text.text
        Text.text = text
        return return_text


class Mouse:
    listeners = []

    def __init__(self, button, on_click_word=None, on_click_line=None, on_click_only_line=None):
        self.button = button
        self.on_click_word = on_click_word
        self.on_click_line = on_click_line
        self.on_click_only_line = on_click_only_line

        Mouse.listeners.append(self)

    @staticmethod
    def check_click_word(frame_events, data, button=1):
        for event in frame_events:
            # checks if you pressed x mouse button
            if event.type == pg.MOUSEBUTTONDOWN and event.button == button:
                # checks if you clicked a word
                for i, line in enumerate(data):
                    words = line["Words"]
                    for j, word in enumerate(words):
                        button_size = wh_to_chords((word["Left"], word["Top"], word["Width"], word["Height"]))
                        if button_click_check(button_size):
                            return {'word': word, 'index': {'word': j, 'line': i}}

    @staticmethod
    def check_click_line(frame_events, data, button=1):
        for event in frame_events:
            # checks if you pressed x mouse button
            if event.type == pg.MOUSEBUTTONDOWN and event.button == button:
                for i, line in enumerate(data):
                    # checks if you clicked a line
                    button_size = get_word_line_size(line)
                    if button_click_check(button_size):
                        return {'line': line, 'index': i}

    def check_click(self, frame_events, data):
        word = Mouse.check_click_word(frame_events, data, self.button)
        line = Mouse.check_click_line(frame_events, data, self.button)
        if line and word:
            if self.on_click_word:
                self.on_click_word(word)
        elif word:
            if self.on_click_line:
                self.on_click_line(line)
        elif line:
            if self.on_click_only_line:
                self.on_click_only_line(line)

    @classmethod
    def listen(cls, frame_events, data):
        for obj in cls.listeners:
            obj.check_click(frame_events, data)


def listen(frame_events, data):
    Text.save_text_input(frame_events)
    Mouse.listen(frame_events, data)
