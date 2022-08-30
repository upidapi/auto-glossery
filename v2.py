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
                   'detectOrientation': False,
                   }
        with open(filename, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image',
                              files={filename: f},
                              data=payload,
                              )

        DataJson.data = r.content.decode()
        return DataJson.data

    @staticmethod
    def get_data_form_json():
        with open("sample.json") as jsonFile:
            json_object = json.load(jsonFile)
            jsonFile.close()

        # extracts
        DataJson.data = json.loads(json_object)

    @staticmethod
    def save_data_to_jason():
        json_object = json.dumps(DataJson.data, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def get_next_line() -> dict:
        lines = DataJson.data["ParsedResults"][0]["TextOverlay"]["Lines"]
        for line in lines:
            yield line

    @staticmethod
    def get_next_word() -> dict:
        for line in DataJson.get_next_line():
            words = line["Words"]
            for word in words:
                yield word


# # writes and checks values for boxes
# class EditBox:
#     selected_box = None
#     text = ''
#
#     @staticmethod
#     def check_select_box(frame_events):
#         for event in frame_events:
#             if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
#                 for i, box in enumerate(DataJson.data):
#                     pos = box['bounding_box']
#                     if pos['x1'] <= pg.mouse.get_pos()[0] <= pos['x2'] and \
#                             pos['y1'] <= pg.mouse.get_pos()[1] <= pos['y2']:
#                         print(f'"{EditBox.text}"')
#
#                         EditBox.text = box['text']
#                         EditBox.selected_box = i
#
#             if event.type == pg.KEYDOWN and EditBox.selected_box is not None:
#                 if event.key == pg.K_DELETE:
#                     DataJson.data.pop(EditBox.selected_box)
#                     EditBox.selected_box = None
#                     EditBox.text = ''
#
#                 elif event.key == pg.K_RETURN:
#                     DataJson.data[EditBox.selected_box]['text'] = EditBox.text
#                     EditBox.selected_box = None
#                     EditBox.text = ''
#
#                 elif event.key == pg.K_BACKSPACE:
#                     EditBox.text = EditBox.text[0:-1]
#
#                 else:
#                     EditBox.text += event.unicode
#
#                 print(f'"{EditBox.text}"')
#
#
# # makes new empty boxes
# class DragCheck:
#     # definitions
#     drag_start = (0, 0)
#     start = (0, 0)
#     size = (0, 0)
#     dragging = False
#     draw_box_stick = False
#
#     @staticmethod
#     def check_drag(frame_events):
#         for event in frame_events:
#             if event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
#                 DragCheck.dragging = True
#                 DragCheck.drag_start = pg.mouse.get_pos()
#
#             if event.type == pg.MOUSEBUTTONUP and event.button == 2:
#                 DragCheck.dragging = False
#                 DragCheck.draw_box_stick = True
#
#                 DragCheck.size = (
#                     abs(DragCheck.drag_start[0] - pg.mouse.get_pos()[0]),
#                     abs(DragCheck.drag_start[1] - pg.mouse.get_pos()[1])
#                 )
#
#                 DragCheck.start = (
#                     min(DragCheck.drag_start[0], pg.mouse.get_pos()[0]),
#                     min(DragCheck.drag_start[1], pg.mouse.get_pos()[1])
#                 )
#
#             if event.type == pg.KEYDOWN:
#                 if event.key == pg.K_ESCAPE:
#                     DragCheck.dragging = False
#                     DragCheck.draw_box_stick = False
#
#                 elif event.key == pg.K_RETURN and DragCheck.draw_box_stick:
#                     DragCheck.dragging = False
#                     DragCheck.draw_box_stick = False
#                     DataJson.data.append({"text": "",
#                                           "bounding_box": {"x1": DragCheck.start[0],
#                                                            "y1": DragCheck.start[1],
#                                                            "x2": DragCheck.start[0] + DragCheck.size[0],
#                                                            "y2": DragCheck.start[1] + DragCheck.size[1]
#                                                            }})
#
#                     # selects the new box (the new boxes pos is the las of the list)
#                     EditBox.selected_box = len(DataJson.data) - 1
#                     print(EditBox.selected_box)
#
#     @staticmethod
#     def draw_select_box():
#         if DragCheck.dragging:
#             draw_rgba_rect(game_screen, (200, 200, 255, 128),
#                            pg.mouse.get_pos(),
#                            DragCheck.drag_start,
#                            outline_width=1, outline_color=(0, 100, 255))
#
#         elif DragCheck.draw_box_stick:
#             draw_rgba_rect(game_screen, (200, 200, 255, 128),
#                            (DragCheck.start[0] + DragCheck.size[0],
#                             DragCheck.start[1] + DragCheck.size[1]),
#                            DragCheck.drag_start,
#                            outline_width=1, outline_color=(0, 100, 255))


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
        for line in DataJson.get_next_line():
            start, size = chords_to_wh(BoundingBox.get_word_line_size(line))
            draw_rgba_rect(game_screen, (200, 200, 255, 128), start, size,
                           outline_width=1, outline_color=(0, 100, 255))

    @staticmethod
    def draw_word():
        # may look a bit of, it's because of rounding errors when drawing
        for line in DataJson.get_next_line():
            words = line["Words"]

            # gets and draws the bounding box for each word
            for word in words:
                draw_rgba_rect(game_screen, (200, 200, 255, 128),
                               (word["Left"], word["Top"]),
                               (word["Width"], word["Height"]),
                               outline_width=1, outline_color=(0, 100, 255))


class EditInput:
    @staticmethod
    def check_click_word(frame_events, button=1):
        for event in frame_events:
            # checks if you pressed x mouse button
            if event.type == pg.MOUSEBUTTONDOWN and event.button == button:
                # checks if you clicked a word
                for word in DataJson.get_next_word():
                    button_size = wh_to_chords((word["Left"], word["Top"], word["Width"], word["Height"]))
                    if button_click_check(button_size):
                        return word

    @staticmethod
    def check_click_line(frame_events, button=1):
        for event in frame_events:
            # checks if you pressed x mouse button
            if event.type == pg.MOUSEBUTTONDOWN and event.button == button:
                for line in DataJson.get_next_line():
                    # checks if you clicked a line
                    button_size = BoundingBox.get_word_line_size(line)
                    if button_click_check(button_size):
                        return line

    # @staticmethod
    # def select_box(frame_events, check_lines=True, check_words=True):
    #     for event in frame_events:
    #         # checks if you pressed right mouse button
    #         if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
    #             word_data = EditInput.check_click_word()
    #             line_data = EditInput.check_click_line()
    #             if word_data is not None and check_words:
    #                 return word_data["WordText"]
    #             elif line_data is not None and check_lines:
    #                 return line_data["LineText"]


def get_image(select_image="spa_text_glossary_perfect"):
    test_images = {
        "eng_text_page": r"C:\Users\videw\Downloads\book page.jpg",
        "spa_text_glossary_rotated": r"C:\Users\videw\Downloads\IMG_2439.jpg",
        "spa_text_glossary_perfect": r"C:\Users\videw\Downloads\IMG_2438.jpg",
        "spa_text_glossary_inprefect": r"C:\Users\videw\Downloads\IMG_2421.png"
    }

    image = Image.open(test_images[select_image])
    image.thumbnail((1000, 1000))

    new_image = False
    if new_image:
        image.save('selected_image.jpg')
        DataJson.ocr_space_file('selected_image.jpg', language='spa')
        DataJson.save_data_to_jason()


def check_exit(frame_events):
    for event in frame_events:
        if event.type == pg.QUIT:
            pg.quit()
            # DataJson.save_data_to_jason()
            quit()


class Other:
    mode = 0

    @staticmethod
    def change_mode(frame_events):
        for event in frame_events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RIGHT:
                    Other.mode += 1
                    Other.mode = Other.mode % 4
                if event.key == pg.K_LEFT:
                    Other.mode -= 1
                    Other.mode = Other.mode % 4
                print(Other.mode)


    @staticmethod
    def draw_inp_mode(frame_events):
        temp_word = EditInput.check_click_word(frame_events, button=1)
        temp_line = EditInput.check_click_word(frame_events, button=1)

        if Other.mode == 1:
            BoundingBox.draw_word()
            if temp_word is not None:
                print(temp_word["WordText"])

        if Other.mode == 2:
            BoundingBox.draw_word_line()
            if temp_line is not None:
                print(temp_line["LineText"])

        if Other.mode == 3:
            BoundingBox.draw_word()
            BoundingBox.draw_word_line()
            if temp_word is not None:
                print(temp_word["WordText"])
            if temp_line is not None:
                print(temp_line["LineText"])



def event_loop():
    frame_events = pg.event.get()

    check_exit(frame_events)
    Other.change_mode(frame_events)

    Other.draw_inp_mode(frame_events)

    # DragCheck.check_drag(frame_events)

    # print(EditBox.selected_box)


def main():
    global game_screen
    global text_image_dir
    text_image_dir = 'selected_image.jpg'

    # the pygame initiation proses
    pg.init()
    pg_text_img = pg.image.load(text_image_dir)
    game_screen = pg.display.set_mode(pg_text_img.get_size())
    pg.display.set_caption('Maze')
    clock = pg.time.Clock()

    # loads, process and fetches the text from the input image
    get_image()

    DataJson.get_data_form_json()

    while True:
        game_screen.fill((255, 255, 255))
        game_screen.blit(pg_text_img, (0, 0))

        # DragCheck.draw_select_box()


        event_loop()
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
