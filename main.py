import pygame as pg
import json
import requests
from PIL import Image
import listeners
import draw
from general_funcs import get_word_line_size, chords_to_wh


# noinspection PyTypeChecker
class DataJson:
    data = []

    @staticmethod
    def ocr_space_file(filename, language='eng'):
        """ OCR.space API request with local file.
            Python3.5 - not tested on 2.7
        :param filename: Your file path & name.
        param language: Language code to be used in OCR.
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


def left_only_line(inp):
    EditInput.selected_line = inp['index']
    EditInput.selected_word = None


def left_word(inp):
    EditInput.selected_line = inp['index']['line']
    EditInput.selected_word = inp['index']['word']

    # noinspection PyTypeChecker
    text = DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]['WordText']
    listeners.Text.set_text(text)


def middle_line(inp):
    if EditInput.selected_line and EditInput.selected_line != inp["index"]:
        EditInput.combine_lines(inp["index"], EditInput.selected_line)


middle_click = listeners.Mouse(button=2, on_click_line=middle_line)
left_click = listeners.Mouse(button=1, on_click_only_line=left_only_line, on_click_word=left_word)


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
            if event.type == pg.KEYDOWN and event.key == pg.K_MINUS:
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
                data = DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]
                text_img = font.render((listeners.Text.get_text()), True, (0, 0, 0))

                data["Width"], data["Height"] = text_img.get_size()
                # noinspection PyTypeChecker
                DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]['WordText']\
                    = listeners.Text.get_text()
                # noinspection PyTypeChecker
                DataJson.data[EditInput.selected_line]['LineText']\
                    = EditInput.sort_text(DataJson.data[EditInput.selected_line])
                # unselect
                EditInput.selected_word = None
                EditInput.selected_line = None
                listeners.Text.set_text('')

    @staticmethod
    def new_word(frame_events):
        for event in frame_events:
            # event.button == 2 is the middle mouse button
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                x, y = pg.mouse.get_pos()
                data = {
                    "LineText": "",
                    "Words": [
                        {
                            "WordText": "",
                            "Left": x,
                            "Top": y,
                            "Height": 0,
                            "Width": 0
                        }
                    ],
                    "MaxHeight": 0,
                    "MinTop": y
                }

                DataJson.data.append(data)

                EditInput.selected_line = len(DataJson.data) - 1
                EditInput.selected_word = 0

    # noinspection PyTypeChecker
    @staticmethod
    def combine_lines(l1_index, l2_index):
        rough_merge = {
            "LineText": "",

            "Words": DataJson.data[l1_index]["Words"] + DataJson.data[l2_index]["Words"],
            "MaxHeight": 0,
            "MinTop": 0
        }

        space = font.render(' ', True, (0, 0, 0))
        space_size = space.get_size()[0]

        l1_size = get_word_line_size(DataJson.data[l1_index])
        l2_size = get_word_line_size(DataJson.data[l2_index])

        l1_text = DataJson.data[l1_index]["LineText"]
        l2_text = DataJson.data[l2_index]["LineText"]

        # noinspection PyTypeChecker
        def la_lb(switch):
            print(l1_size, l2_size)
            if switch:
                rough_merge["LineText"] = l1_text + ' ' + l2_text

                for word in DataJson.data[l2_index]["Words"]:
                    word["Left"] += (l1_size[2] - l1_size[0] + space_size)
                    word["Top"] -= (l2_size[1] - l1_size[1])
            else:
                rough_merge["LineText"] = l2_text + l1_text

                for word in DataJson.data[l1_index]["Words"]:
                    word["Left"] += (l2_size[2] - l2_size[0] + space_size)
                    word["Top"] -= (l1_size[1] - l2_size[1])

        # if the words x pos difference is smaller than x combine by y pos otherwise combine by x pos
        if abs(l1_size[0] - l2_size[0]) < 10:
            # if the y pos of l1 is smaller than l2
            if l1_size[1] < l2_size[1]:
                print(1)
                la_lb(True)
            else:
                print(2)
                la_lb(False)

        else:
            if l1_size[0] < l2_size[0]:
                print(3)
                la_lb(True)

            else:
                print(4)
                la_lb(False)

        print(rough_merge["LineText"])
        _, rough_merge["MinTop"], _, rough_merge["MaxHeight"] = get_word_line_size(rough_merge)

        # delete the one with the higher index first so the others index doesn't change
        # noinspection PyTypeChecker
        del DataJson.data[max(l1_index, l2_index)]
        # noinspection PyTypeChecker
        del DataJson.data[min(l1_index, l2_index)]

        DataJson.data.append(rough_merge)

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
            text = DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]['WordText']
            EditInput.edit(frame_events)

            EditInput.delete(frame_events, 'word')

            draw.draw_words('word', game_screen, DataJson.data, (EditInput.selected_line, EditInput.selected_word))

        elif EditInput.selected_line is not None and (select == 'line' or select == 'both'):
            EditInput.delete(frame_events, 'line')

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
    def change_draw_box_mode(frame_events):
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


    # @staticmethod
    # def change_edit_mode(frame_events, next):
    #     # add missing words, remove unnecessary words
    #     # hit box post-processing, word post-processing, edit words
    #     # combine lines if they are supposed to be in the same word
    #     # combine translation and word into a full glossary
    #
    #     edit_mode = -1
    #
    #     def select_line(inp):
    #         EditInput.selected_line = inp['index']
    #         EditInput.selected_word = None
    #
    #     def select_word(inp):
    #         EditInput.selected_line = inp['index']['line']
    #         EditInput.selected_word = inp['index']['word']
    #
    #         # noinspection PyTypeChecker
    #         text = DataJson.data[EditInput.selected_line]['Words'][EditInput.selected_word]['WordText']
    #         listeners.Text.set_text(text)
    #
    #     def combine_lines(inp):
    #         if EditInput.selected_line and EditInput.selected_line != inp["index"]:
    #             EditInput.combine_lines(inp["index"], EditInput.selected_line)
    #
    #     for event in frame_events:
    #         if event.type == pg.KEYDOWN and pg.key == pg.K_RETURN and Other.ctrl_pressed or next:
    #             edit_mode += 1
    #
    #             if edit_mode == 0:
    #                 pg.display.set_caption('add/remove words')
    #                 left_click = listeners.Mouse(button=1, on_click_word=left_word)
    #
    #             if edit_mode == 1:
    #                 pg.display.set_caption('edit words')
    #
    #
    #     if edit_mode == 0:
    #         EditInput.new_word(frame_events)




def event_loop():
    frame_events = pg.event.get()

    check_exit(frame_events)

    # Other.change_edit_mode(frame_events)

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
    global font

    text_image_dir = 'selected_image.jpg'
    font = pg.font.SysFont('Helvatical bold', 24)

    # loads, process and fetches the text from the input image
    # DataJson.get_image("spa_text_glossary_perfect")
    DataJson.get_data()
    # the pygame initiation proses
    pg.init()
    pg_text_img = pg.image.load(text_image_dir)
    game_screen = pg.display.set_mode(pg_text_img.get_size())
    pg.display.set_caption('add/remove words')
    clock = pg.time.Clock()

    print(get_word_line_size(DataJson.data[0]))
    print(DataJson.data[0]["LineText"])

    while True:
        game_screen.fill((255, 255, 255))
        game_screen.blit(pg_text_img, (0, 0))

        # DragCheck.draw_select_box()

        event_loop()
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
