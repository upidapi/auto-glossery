import pygame as pg
import json
import requests
from PIL import Image


def wh_to_chords(wh) -> tuple[int, int, int, int]:
    x, y, width, height = wh
    return int(x), int(y), int(x + width), int(y + height)


def chords_to_wh(chords: list[int, int, int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    x1, y1, x2, y2 = chords
    size = (
        abs(x1 - x2),
        abs(y1 - y2)
    )

    start = (
        min(x1, x2),
        min(y1, y2)
    )

    return start, size


def button_click_check(button_size, click_pos=None) -> bool:
    if click_pos is None:
        click_pos = pg.mouse.get_pos()

    x1, y1, x2, y2 = button_size

    if x1 <= click_pos[0] <= x2 and y1 <= click_pos[1] <= y2:
        return True
    return False


def draw_rgba_rect(surface, color, start, size, outline_width=0, outline_color=(0, 0, 0)):
    # drawing a rect with alpha
    select_rect = pg.Surface(size)  # the size of your rect
    select_rect.set_alpha(color[3])  # alpha level
    select_rect.fill((color[0], color[1], color[2]))  # this fills the entire surface

    surface.blit(select_rect, start)  # (0,0) are the top-left coordinates

    # draws the outline
    pg.draw.rect(surface, outline_color, start + size, outline_width)


class Listener:
    class Text:
        text = ''

        @staticmethod
        def save_text_input(frame_event):
            for event in frame_event:
                if event.type == pg.KEYDOWN:
                    print('hello')

                    # Check for backspace
                    if event.key == pg.K_BACKSPACE:
                        print(2)

                        # get text input from 0 to -1 i.e. end.
                        Listener.Text.text = Listener.Text.text[:-1]

                    # Unicode standard is used for string
                    # formation
                    else:
                        character = event.unicode
                        allowed_characters = '1234567890abcdefghijklmnopqrstuvwxyzåäöñè ,.()!?'
                        if character in allowed_characters:
                            Listener.Text.text += event.unicode

        @staticmethod
        def get_text():
            return Listener.Text.text

        @staticmethod
        def set_text(text=''):
            return_text = Listener.Text.text
            Listener.Text.text = text
            return return_text

    class Mouse:
        listeners = []

        def __init__(self, button, *, on_click_word, on_click_line, on_click_only_line):
            self.button = button
            self.on_click_word = on_click_word
            self.on_click_line = on_click_line
            self.on_click_only_line = on_click_only_line

            Listener.Mouse.listeners.append(self)

        @staticmethod
        def check_click_word(frame_events, button=1):
            for event in frame_events:
                # checks if you pressed x mouse button
                if event.type == pg.MOUSEBUTTONDOWN and event.button == button:
                    # checks if you clicked a word
                    for i, line in enumerate(DataJson.data):
                        words = line["Words"]
                        for j, word in enumerate(words):
                            button_size = wh_to_chords((word["Left"], word["Top"], word["Width"], word["Height"]))
                            if button_click_check(button_size):
                                return {'word': word, 'index': {'word': j, 'line': i}}

        @staticmethod
        def check_click_line(frame_events, button=1):
            for event in frame_events:
                # checks if you pressed x mouse button
                if event.type == pg.MOUSEBUTTONDOWN and event.button == button:
                    for i, line in enumerate(DataJson.data):
                        # checks if you clicked a line
                        button_size = BoundingBox.get_word_line_size(line)
                        if button_click_check(button_size):
                            return {'line': line, 'index': i}

        def combine(self, frame_events):
            word = Listener.Mouse.check_click_word(frame_events, self.button)
            line = Listener.Mouse.check_click_line(frame_events, self.button)
            if line and word:
                self.on_click_line(line)
            elif word:
                self.on_click_word(word)
            elif line:
                self.on_click_only_line(line)

        @classmethod
        def listen(cls, frame_events):
            for obj in cls.listeners:
                obj.combine(frame_events)

# noinspection PyTypeChecker
class DataJson:
    data = []

    @staticmethod
    def ocr_space_file(filename, language='eng'):
        """ OCR.space API request with local file.
            Python3.5 - not tested on 2.7
        :param filename: Your file path & name.
        :param language: Language code to be used in OCR.
                        List of available language codes can be found on https://ocr.space/OCRAPI
                        Defaults to 'en'.
        :return: Result in JSON format.
        """

        api_key = "K85003833988957"

        payload = {'isOverlayRequired': True,
                   'apikey': api_key,
                   'language': language,
                   'scale': True
                   }
        with open(filename, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image',
                              files={filename: f},
                              data=payload,
                              )

        # decode
        return_data = r.content.decode()
        # from json-str to python-array
        return_data = json.loads(return_data)
        # remove unnecessary data
        DataJson.data = return_data["ParsedResults"][0]["TextOverlay"]["Lines"]

        DataJson.save_data_to_jason()

    @staticmethod
    def get_data():
        with open("sample.json") as jsonFile:
            # converts json-document to python-array
            DataJson.data = json.load(jsonFile)
            jsonFile.close()

    @staticmethod
    def save_data_to_jason():
        # converts python-array to json-document with indent 4
        json_object = json.dumps(DataJson.data, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def get_image(select_image="spa_text_glossary_perfect"):
        test_images = {
            "eng_text_page": r"C:\Users\videw\Downloads\book page.jpg",
            "spa_text_glossary_rotated": r"C:\Users\videw\Downloads\IMG_2439.jpg",
            "spa_text_glossary_perfect": r"C:\Users\videw\Downloads\IMG_2438.jpg",
            "spa_text_glossary_inprefect": r"C:\Users\videw\Downloads\IMG_2421.png"
        }

        image = Image.open(test_images[select_image])
        image.thumbnail((1000, 1000))

        new_image = True
        if new_image:
            image.save('selected_image.jpg')
            DataJson.ocr_space_file('selected_image.jpg', language='spa')
            DataJson.save_data_to_jason()

    @staticmethod
    def get_next_word() -> dict:
        for line in DataJson.data:
            words = line["Words"]
            for word in words:
                yield word

    @staticmethod
    def get_index(thing):
        for i, line in enumerate(DataJson.data):
            if thing == line:
                # returns is as a tuple
                return {'line_index': i, 'type': 'line'}
            for j, word in enumerate(DataJson.data):
                if thing == word:
                    return {'line_index': i, 'word_index': j, 'type': 'word'}

    @staticmethod
    def get_selected(thing=None):
        if EditInput.selected_word is None or thing == 'line':
            return DataJson.data[EditInput.selected_line]
        else:
            return DataJson.data[EditInput.selected_line]["Words"][EditInput.selected_word]


class BoundingBox:
    @staticmethod
    def get_word_line_size(line):
        min_chords = [1_000_000, 1_000_000, 0, 0]
        words = line["Words"]
        for word in words:
            chords = wh_to_chords((word["Left"], word["Top"], word["Width"], word["Height"]))
            # gets the min/max chords of chords to get the bounding box
            min_chords[0] = min(min_chords[0], chords[0])
            min_chords[1] = min(min_chords[1], chords[1])
            min_chords[2] = max(min_chords[2], chords[2])
            min_chords[3] = max(min_chords[3], chords[3])

        return min_chords

    @staticmethod
    def draw_word_line():
        # may look a bit of, it's because of rounding errors when drawing
        for line in DataJson.data:
            start, size = chords_to_wh(BoundingBox.get_word_line_size(line))
            draw_rgba_rect(game_screen, (200, 200, 255, 128), start, size,
                           outline_width=1, outline_color=(0, 100, 255))

    @staticmethod
    def draw_word():
        # may look a bit of, it's because of rounding errors when drawing
        for line in DataJson.data:
            words = line["Words"]

            # gets and draws the bounding box for each word
            for word in words:
                draw_rgba_rect(game_screen, (200, 200, 255, 128),
                               (word["Left"], word["Top"]),
                               (word["Width"], word["Height"]),
                               outline_width=1, outline_color=(0, 100, 255))


class EditInput:
    @staticmethod
    def sort_text(line):
        line["Words"].sort(key=lambda i: i["Left"])
        text = ''
        for word in line['Words']:
            text += (word["WordText"] + ' ')

        return text.strip()

    selected_line = None
    selected_word = None

    @staticmethod
    # used for deleting a thing
    def delete(frame_events, select):
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.key == pg.K_DELETE:
                if select == 'word':
                    # noinspection PyTypeChecker
                    del DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]
                elif select == 'line':
                    # noinspection PyTypeChecker
                    del DataJson.data[EditInput.selected_line]

                # unselect
                EditInput.selected_word = None
                EditInput.selected_line = None

    @staticmethod
    # used for saving the edits to a word
    def edit(frame_events):
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                # noinspection PyTypeChecker
                DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]['WordText']\
                    = Listener.Text.get_text()

                # unselect
                EditInput.selected_word = None
                EditInput.selected_line = None

    @staticmethod
    def draw_words(selected):
        if selected is None:
            # draw it normally
            for line in DataJson.data:
                img = font.render(line["LineText"], True, (0, 0, 0))
                game_screen.blit(img, BoundingBox.get_word_line_size(line)[0:2])

        else:
            for i, line in enumerate(DataJson.data):
                # normal line
                if i != EditInput.selected_line:
                    img = font.render(line["LineText"], True, (0, 0, 0))
                    game_screen.blit(img, BoundingBox.get_word_line_size(line)[0:2])
                else:
                    # draws the selected thing in red
                    if selected == 'line':
                        # draws the selected line red
                        # noinspection PyTypeChecker
                        text = DataJson.get_selected('line')["LineText"]
                        img = font.render(text, True, (255, 0, 0))
                        # the first two items of the returned list is the lines x and y pos
                        pos = BoundingBox.get_word_line_size(DataJson.get_selected('line'))[0:2]
                        game_screen.blit(img, pos)

                    elif selected == 'word':
                        # draws the selected word red
                        # the first two items of the returned list is the lines x and y pos
                        line_pos_x, line_pos_y = BoundingBox.get_word_line_size(line)[0:2]

                        line["Words"].sort(key=lambda x: x["Left"])
                        for word in line["Words"]:
                            # only draw the selected word in red
                            if word == DataJson.get_selected():
                                # adds a space to account for the space between words
                                img = font.render(Listener.Text.get_text() + ' ', True, (255, 0, 0))

                            else:
                                # adds a space to account for the space between words
                                img = font.render((word['WordText'] + ' '), True, (0, 0, 0))

                            # use the lines y pos to make sure the words are aligned
                            pos = line_pos_x, line_pos_y
                            game_screen.blit(img, pos)

                            # add the width to the x pos so that the next word starts at the end of the last
                            line_pos_x += img.get_size()[0]

    @staticmethod
    def get_last_selected(frame_events):
        # checks the last clicked word / line
        word_line = EditInput.check_click_line(frame_events, button=1)
        if word_line is not None:
            EditInput.selected_line = word_line['index']
            EditInput.selected_word = None

        word_data = EditInput.check_click_word(frame_events, button=1)
        if word_data is not None:
            EditInput.selected_line = word_data['index']['line']
            EditInput.selected_word = word_data['index']['word']

        # if you press esc unselect the current thing
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                EditInput.selected_line = None
                EditInput.selected_word = None

    @staticmethod
    def selection_action(frame_events, select):
        game_screen.fill((255, 255, 255))
        EditInput.get_last_selected(frame_events)

        # checks if you have selected a thing
        if EditInput.selected_word is not None and (select == 'word' or select == 'both'):
            # noinspection PyTypeChecker
            Listener.Text.set_text(DataJson.get_selected()['WordText'])
            EditInput.edit(frame_events)

            EditInput.delete(frame_events, EditInput.selected_word)

            EditInput.draw_words('word')

        elif EditInput.selected_line is not None and (select == 'line' or select == 'both'):
            EditInput.delete(frame_events, EditInput.selected_line)

            EditInput.draw_words('line')

        else:
            EditInput.draw_words(None)


def check_exit(frame_events):
    for event in frame_events:
        if event.type == pg.QUIT:
            pg.quit()
            # DataJson.save_data_to_jason()
            quit()


class Other:
    draw_mode = 0
    draw_text = False
    ctrl_pressed = False

    @staticmethod
    def change_mode(frame_events):
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.key == pg.K_LCTRL:
                Other.ctrl_pressed = True
            if event.type == pg.KEYUP and event.key == pg.K_LCTRL:
                Other.ctrl_pressed = False

            if event.type == pg.KEYDOWN and Other.ctrl_pressed:
                # display modes
                if event.key == pg.K_RIGHT:
                    Other.draw_mode += 1
                    Other.draw_mode = Other.draw_mode % 4
                if event.key == pg.K_LEFT:
                    Other.draw_mode -= 1
                    Other.draw_mode = Other.draw_mode % 4
                if event.key == pg.K_s:
                    Other.draw_text = not Other.draw_text

    @staticmethod
    def draw_inp_mode(frame_events):
        temp_word = EditInput.check_click_word(frame_events, button=1)
        temp_line = EditInput.check_click_line(frame_events, button=1)

        if Other.draw_mode == 1:
            BoundingBox.draw_word()
            if temp_word is not None:
                print(temp_word["word"]["WordText"])

        if Other.draw_mode == 2:
            BoundingBox.draw_word_line()
            if temp_line is not None:
                print(temp_line["line"]["LineText"])

        if Other.draw_mode == 3:
            BoundingBox.draw_word()
            BoundingBox.draw_word_line()
            if temp_word is not None:
                print(temp_word["word"]["WordText"])
            elif temp_line is not None:
                print(temp_line["line"]["LineText"])

    @staticmethod
    def draw_text_on_image():
        if Other.draw_text:
            game_screen.fill((255, 255, 255))
            # for word in DataJson.get_next_word():
            #     img = font.render(word["WordText"], True, (255, 0, 0))
            #     game_screen.blit(img, (word["Left"], word["Top"]))
            #     # font.render_to(game_screen, (word["Left"], word["Top"]), word["WordText"], (0, 0, 0),
            #     #                size=word["Height"])
            for line in DataJson.data:
                img = font.render(line["LineText"], True, (0, 0, 0))
                game_screen.blit(img, BoundingBox.get_word_line_size(line)[0:2])


def event_loop():
    frame_events = pg.event.get()

    check_exit(frame_events)

    Other.change_mode(frame_events)

    Listener.Text.save_text_input(frame_events)

    EditInput.selection_action(frame_events, 'both')

    Other.draw_inp_mode(frame_events)

    # print(Listener.text)


def main():
    # noinspection PyGlobalUndefined
    global game_screen
    # noinspection PyGlobalUndefined
    global text_image_dir
    # noinspection PyGlobalUndefined
    global font

    text_image_dir = 'selected_image.jpg'

    # loads, process and fetches the text from the input image
    # DataJson.get_image("spa_text_glossary_perfect")
    DataJson.get_data()
    # the pygame initiation proses
    pg.init()
    pg_text_img = pg.image.load(text_image_dir)
    game_screen = pg.display.set_mode(pg_text_img.get_size())
    pg.display.set_caption('Maze')
    clock = pg.time.Clock()

    font = pg.font.SysFont('Helvatical bold', 24)

    while True:
        game_screen.fill((255, 255, 255))
        game_screen.blit(pg_text_img, (0, 0))

        # DragCheck.draw_select_box()

        event_loop()
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
