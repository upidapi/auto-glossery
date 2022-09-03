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


# # noinspection PyTypeChecker
# class SimplifiedDataFetch:
#     # get modify or delete data from the master data in a pythonic way
#     def __init__(self):
#         with open("sample.json") as jsonFile:
#             json_object = json.load(jsonFile)
#             jsonFile.close()
#
#         self.data = json.loads(json_object)
#
#     # ["ParsedResults"][0]["TextOverlay"]["Lines"][index]['Words'][EditInput.selected_word['word']]['WordText']
#     # format:
#     # "a" is a key for the dict
#     # i and j are indexes from lists
#     # data[i: int]                 ->                            lines[i]
#     # data[i: int,         a: str] -> line[j]               from lines[i]
#     # data[i: int, j: int]         ->              words[j] from lines[i]
#     # data[i: int, j: int, a: str] -> word[a] from words[j] from lines[i]
#
#     def __getitem__(self, index):
#         if type(index) is int:
#             return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][index]
#
#         elif type(index[1]) is str:
#             return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][index[0]][index[1]]
#
#         elif type(index[1]) is int:
#             if len(index) == 2:
#                 return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][index[0]]['Words'][index[1]]
#
#             else:
#                 return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][index[0]]['Words'][index[1]][index[2]]
#
#     def __delitem__(self, key):
#         if type(key) is int:
#             return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key]
#
#         elif type(key[1]) is str:
#             return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key[0]][key[1]]
#
#         elif type(key[1]) is int:
#             if len(key) == 2:
#                 return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key[0]]['Words'][key[1]]
#
#             else:
#                 return self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key[0]]['Words'][key[1]][key[2]]
#
#     def __setitem__(self, key, value):
#         if type(key) is int:
#             self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key] = value
#
#         elif type(key[1]) is str:
#             self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key[0]][key[1]] = value
#
#         elif type(key[1]) is int:
#             if len(key) == 2:
#                 self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key[0]]['Words'][key[1]] = value
#
#             else:
#                 self.data["ParsedResults"][0]["TextOverlay"]["Lines"][key[0]]['Words'][key[1]][key[2]] = value


class Listener:
    listener = []

    text = ''

    @staticmethod
    def save_text_input(frame_event):
        for event in frame_event:
            if event.type == pg.KEYDOWN and EditInput.typing:

                # Check for backspace
                if event.key == pg.K_BACKSPACE:

                    # get text input from 0 to -1 i.e. end.
                    EditInput.new_text = EditInput.new_text[:-1]

                # Unicode standard is used for string
                # formation
                else:
                    character = event.unicode
                    allowed_characters = '1234567890abcdefghijklmnopqrstuvwxyzåäöñè ,.()!?'
                    if character in allowed_characters:
                        Listener.text += event.unicode

    @staticmethod
    def get_text():
        return Listener.text

    @staticmethod
    def set_text(text=''):
        text = Listener.text
        Listener.text = text
        return text


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
    def get_next_line() -> dict:
        for line in DataJson.data:
            yield line

    @staticmethod
    def get_next_word() -> dict:
        for line in DataJson.data:
            words = line["Words"]
            for word in words:
                yield word

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

    @staticmethod
    def delete(frame_events, selected_line, selected_word):
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.KEY == pg.K_DELETE:
                # noinspection PyTypeChecker
                del DataJson.data[selected_line]['Words'][selected_word]

    @staticmethod
    def edit(frame_events, selected_line, selected_word):
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.KEY == pg.K_RETURN:
                # noinspection PyTypeChecker
                DataJson.data[selected_line]['Words'][selected_word]['WordText'] = Listener.get_text()

    text_top_pos = [0, 0]
    typing = False
    select_line = False

    @staticmethod
    def selection_action(frame_events, select):
        selected_line = None
        selected_word = None

        # checks the last clicked word / line
        word_data = EditInput.check_click_word(frame_events, button=1)
        if word_data is not None:
            EditInput.selected_word = word_data['index']

        word_data = EditInput.check_click_line(frame_events, button=1)
        if word_data is not None:
            EditInput.selected_word = word_data['index']

        # if you press esc unselect the current word
        for event in frame_events:
            if event.type == pg.KEYDOWN and event.KEY == pg.K_ESCAPE:
                selected_line = None
                selected_word = None

        if selected_word is not None and select == 'word':
            EditInput.edit(frame_events, selected_line, selected_word)
            EditInput.delete(frame_events, selected_line, selected_word)

        elif selected_line is not None and select == 'line':
            EditInput.delete(frame_events, selected_line, selected_word)

    @staticmethod
    def make_new_word(frame_events):
        if EditInput.select_line:
            for event in frame_events:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    img = font.render(Listener.get_text(), True, (0, 0, 0))
                    size = img.get_size()

                    DataJson.data.append(
                        {
                            "LineText": Listener.get_text(),
                            "Words": [
                                {
                                    "WordText": Listener.get_text(),
                                    "Left": EditInput.text_top_pos[0],
                                    "Top": EditInput.text_top_pos[1],
                                    "Height": size[1],
                                    "Width": size[0]
                                }
                            ],
                            "MaxHeight": size[1],
                            "MinTop": size[0]
                        },
                    )
                    EditInput.select_line = False
                    Listener.set_text()

            line_data = EditInput.check_click_line(frame_events, button=2)
            if line_data is not None:
                img = font.render(Listener.get_text(), True, (0, 0, 0))
                size = img.get_size()
                line_data['line']["Words"].append({
                    "WordText": Listener.get_text(),
                    "Left": EditInput.text_top_pos[0],
                    "Top": EditInput.text_top_pos[1],
                    "Height": size[1],
                    "Width": size[0]
                })
                DataJson.data[line_data['index']] = line_data
                line_data['line']['LineText'] = EditInput.sort_text(line_data['line'])

                EditInput.select_line = False
                Listener.set_text()

        else:
            for event in frame_events:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
                    EditInput.typing = True
                    EditInput.text_top_pos = pg.mouse.get_pos()

                if event.type == pg.KEYDOWN and EditInput.typing:

                    if event.key == pg.K_RETURN:
                        EditInput.select_line = True
                        EditInput.typing = False

                    elif event.key == pg.K_ESCAPE:
                        EditInput.typing = False
                        Listener.set_text()

    @staticmethod
    def draw_new_word():
        if EditInput.typing:
            img = font.render(Listener.get_text(), True, (0, 0, 0))
            game_screen.blit(img, EditInput.text_top_pos)
        if EditInput.select_line:
            img = font.render(Listener.get_text(), True, (255, 0, 0))
            game_screen.blit(img, EditInput.text_top_pos)


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
            for line in DataJson.get_next_line():
                img = font.render(line["LineText"], True, (0, 0, 0))
                game_screen.blit(img, BoundingBox.get_word_line_size(line)[0:2])


def event_loop():
    frame_events = pg.event.get()

    Listener.save_text_input(frame_events)
    check_exit(frame_events)
    Other.change_mode(frame_events)

    Other.draw_inp_mode(frame_events)
    Other.draw_text_on_image()
    # DragCheck.check_drag(frame_events)
    EditInput.make_new_word(frame_events)
    EditInput.draw_new_word()
    # print(EditBox.selected_box)


def main():
    global game_screen
    global text_image_dir
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
