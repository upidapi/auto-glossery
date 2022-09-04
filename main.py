import pygame as pg
import json
import requests
from PIL import Image
import listeners
import draw


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


def left_only_line(inp):
    EditInput.selected_line = inp['index']
    EditInput.selected_word = None


def left_word(inp):
    EditInput.selected_line = inp['index']['line']
    EditInput.selected_word = inp['index']['word']
    print('rer')


left_click = listeners.Mouse(button=1, on_click_only_line=left_only_line, on_click_word=left_word)


# class BoundingBox:
#     @staticmethod
#     def get_word_line_size(line):
#         min_chords = [1_000_000, 1_000_000, 0, 0]
#         words = line["Words"]
#         for word in words:
#             chords = wh_to_chords((word["Left"], word["Top"], word["Width"], word["Height"]))
#             # gets the min/max chords of chords to get the bounding box
#             min_chords[0] = min(min_chords[0], chords[0])
#             min_chords[1] = min(min_chords[1], chords[1])
#             min_chords[2] = max(min_chords[2], chords[2])
#             min_chords[3] = max(min_chords[3], chords[3])
#
#         return min_chords
#
#     @staticmethod
#     def draw_word_line():
#         # may look a bit of, it's because of rounding errors when drawing
#         for line in DataJson.data:
#             start, size = chords_to_wh(BoundingBox.get_word_line_size(line))
#             draw_rgba_rect(game_screen, (200, 200, 255, 128), start, size,
#                            outline_width=1, outline_color=(0, 100, 255))
#
#     @staticmethod
#     def draw_word():
#         # may look a bit of, it's because of rounding errors when drawing
#         for line in DataJson.data:
#             words = line["Words"]
#
#             # gets and draws the bounding box for each word
#             for word in words:
#                 draw_rgba_rect(game_screen, (200, 200, 255, 128),
#                                (word["Left"], word["Top"]),
#                                (word["Width"], word["Height"]),
#                                outline_width=1, outline_color=(0, 100, 255))


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
                    = listeners.Text.get_text()

                # unselect
                EditInput.selected_word = None
                EditInput.selected_line = None

    @staticmethod
    def get_last_selected(frame_events):
        # checks the last clicked word / line
        listeners.Mouse.listen(frame_events, DataJson.data)

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
            listeners.Text.set_text(DataJson.get_selected()['WordText'])
            EditInput.edit(frame_events)

            EditInput.delete(frame_events, EditInput.selected_word)

            draw.draw_words('word', game_screen, DataJson.data, (EditInput.selected_line, EditInput.selected_word))

        elif EditInput.selected_line is not None and (select == 'line' or select == 'both'):
            EditInput.delete(frame_events, EditInput.selected_line)

            draw.draw_words('line', game_screen, DataJson.data, (EditInput.selected_line, EditInput.selected_word))

        else:
            draw.draw_words(None, game_screen, DataJson.data, (EditInput.selected_line, EditInput.selected_word))


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

def event_loop():
    frame_events = pg.event.get()

    check_exit(frame_events)

    Other.change_mode(frame_events)

    listeners.Text.save_text_input(frame_events)

    EditInput.selection_action(frame_events, 'both')

    draw.draw_inp_mode(Other.draw_mode, game_screen, DataJson.data)

    # print(listeners.text)


def main():
    # noinspection PyGlobalUndefined
    global game_screen
    # noinspection PyGlobalUndefined
    global text_image_dir
    # noinspection PyGlobalUndefined

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

    while True:
        game_screen.fill((255, 255, 255))
        game_screen.blit(pg_text_img, (0, 0))

        # DragCheck.draw_select_box()

        event_loop()
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
