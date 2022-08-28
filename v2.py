import pygame as pg
import json
import requests


def wh_to_chords(x, y, width, height):
    return x, y, x + width, y + height


def chords_to_wh(pos1, pos2):
    size = (
        abs(pos1[0] - pos2[0]),
        abs(pos1[1] - pos2[1])
    )

    start = (
        min(pos1[0], pos2[0]),
        min(pos1[1], pos2[1])
    )

    return start, size


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


# print(get_text_from_image(textImageDir))


# writes and checks values for boxes
class EditBox:
    selected_box = None
    text = ''

    @staticmethod
    def check_select_box(frame_events):
        for event in frame_events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                for i, box in enumerate(DataJson.data):
                    pos = box['bounding_box']
                    if pos['x1'] <= pg.mouse.get_pos()[0] <= pos['x2'] and \
                            pos['y1'] <= pg.mouse.get_pos()[1] <= pos['y2']:
                        print(f'"{EditBox.text}"')

                        EditBox.text = box['text']
                        EditBox.selected_box = i

            if event.type == pg.KEYDOWN and EditBox.selected_box is not None:
                if event.key == pg.K_DELETE:
                    DataJson.data.pop(EditBox.selected_box)
                    EditBox.selected_box = None
                    EditBox.text = ''

                elif event.key == pg.K_RETURN:
                    DataJson.data[EditBox.selected_box]['text'] = EditBox.text
                    EditBox.selected_box = None
                    EditBox.text = ''

                elif event.key == pg.K_BACKSPACE:
                    EditBox.text = EditBox.text[0:-1]

                else:
                    EditBox.text += event.unicode

                print(f'"{EditBox.text}"')


# makes new empty boxes
class DragCheck:
    # definitions
    drag_start = (0, 0)
    start = (0, 0)
    size = (0, 0)
    dragging = False
    draw_box_stick = False

    @staticmethod
    def check_drag(frame_events):
        for event in frame_events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
                DragCheck.dragging = True
                DragCheck.drag_start = pg.mouse.get_pos()

            if event.type == pg.MOUSEBUTTONUP and event.button == 2:
                DragCheck.dragging = False
                DragCheck.draw_box_stick = True

                DragCheck.size = (
                    abs(DragCheck.drag_start[0] - pg.mouse.get_pos()[0]),
                    abs(DragCheck.drag_start[1] - pg.mouse.get_pos()[1])
                )

                DragCheck.start = (
                    min(DragCheck.drag_start[0], pg.mouse.get_pos()[0]),
                    min(DragCheck.drag_start[1], pg.mouse.get_pos()[1])
                )

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    DragCheck.dragging = False
                    DragCheck.draw_box_stick = False

                elif event.key == pg.K_RETURN and DragCheck.draw_box_stick:
                    DragCheck.dragging = False
                    DragCheck.draw_box_stick = False
                    DataJson.data.append({"text": "",
                                          "bounding_box": {"x1": DragCheck.start[0],
                                                           "y1": DragCheck.start[1],
                                                           "x2": DragCheck.start[0] + DragCheck.size[0],
                                                           "y2": DragCheck.start[1] + DragCheck.size[1]
                                                           }})

                    # selects the new box (the new boxes pos is the las of the list)
                    EditBox.selected_box = len(DataJson.data) - 1
                    print(EditBox.selected_box)

    @staticmethod
    def draw_select_box():
        if DragCheck.dragging:
            draw_rgba_rect(game_screen, (200, 200, 255, 128),
                           pg.mouse.get_pos(),
                           DragCheck.drag_start,
                           outline_width=1, outline_color=(0, 100, 255))

        elif DragCheck.draw_box_stick:
            draw_rgba_rect(game_screen, (200, 200, 255, 128),
                           (DragCheck.start[0] + DragCheck.size[0],
                            DragCheck.start[1] + DragCheck.size[1]),
                           DragCheck.drag_start,
                           outline_width=1, outline_color=(0, 100, 255))


class BoundingBox:
    @staticmethod
    def draw_word_line():
        # may look a bit of, it's because of rounding errors when drawing
        lines = DataJson.data["ParsedResults"][0]["TextOverlay"]["Lines"]
        for line in lines:
            len_to_start_x = 1_000_000
            len_to_start_y = 1_000_000
            x = 1_000_000
            y = 1_000_000
            height = 0
            width = 0

            words = line["Words"]

            # gets the bounding box for the line of words
            for word in words:
                x = min(x, word["Left"])
                y = min(y, word["Top"])

                # + word["Left"] adds the length of the last word
                width = max(width, word["Width"] + word["Left"])
                height = max(height, word["Height"] + word["Top"])

                len_to_start_x = min(len_to_start_x, word["Left"])
                len_to_start_y = min(len_to_start_y, word["Top"])

            # - len_to_start_x removes the length from 0 -> the leftmost word
            draw_rgba_rect(game_screen, (200, 200, 255, 128),
                           (x, y),
                           (width - len_to_start_x,
                            height - len_to_start_y),
                           outline_width=1, outline_color=(0, 100, 255))

    @staticmethod
    def draw_word():
        # may look a bit of, it's because of rounding errors when drawing
        lines = DataJson.data["ParsedResults"][0]["TextOverlay"]["Lines"]
        for line in lines:
            words = line["Words"]

            # gets and draws the bounding box for each word
            for word in words:
                draw_rgba_rect(game_screen, (200, 200, 255, 128),
                               (word["Left"], word["Top"]),
                               (word["Width"], word["Height"]),
                               outline_width=1, outline_color=(0, 100, 255))


saved = {
    "Lines": [
        {
            "LineText": "vas a",
            "Words": [
                {
                    "WordText": "vas",
                    "Left": 61.0,
                    "Top": 3.0,
                    "Height": 12.0,
                    "Width": 29.0
                },
                {
                    "WordText": "a",
                    "Left": 94.0,
                    "Top": 5.0,
                    "Height": 11.0,
                    "Width": 12.0}
            ],
            "MaxHeight": 12.0,
            "MinTop": 3.0},
        {
            "LineText": "(el) mediodía",
            "Words": [
                {
                    "WordText": "(el)",
                    "Left": 59.0,
                    "Top": 30.0,
                    "Height": 20.0,
                    "Width": 26.0
                },
                {"WordText": "mediodía",
                 "Left": 91.0,
                 "Top": 34.0,
                 "Height": 19.0,
                 "Width": 80.0
                 }
            ],
            "MaxHeight": 20.0,
            "MinTop": 30.0}
    ]
}
saved = {
    "ParsedResults": [
        {
            "TextOverlay": {
                "Lines": [
                    {
                        "Words": [
                            {
                                "WordText": "Word 1",
                                "Left": 106,
                                "Top": 91,
                                "Height": 9,
                                "Width": 11
                            },
                            {
                                "WordText": "Word 2",
                                "Left": 121,
                                "Top": 90,
                                "Height": 13,
                                "Width": 51
                            }

                        ],
                        "MaxHeight": 13,
                        "MinTop": 90
                    },

                ],
                "HasOverlay": True,
                "Message": None
            },
            "FileParseExitCode": "1",
            "ParsedText": "This is a sample parsed result",

            "ErrorMessage": None,
            "ErrorDetails": None
        },
        {
            "TextOverlay": None,
            "FileParseExitCode": -10,
            "ParsedText": None,

            "ErrorMessage": "...error message (if any)",
            "ErrorDetails": "...detailed error message (if any)"
        }

    ],
    "OCRExitCode": "2",
    "IsErroredOnProcessing": False,
    "ErrorMessage": None,
    "ErrorDetails": None,
    "SearchablePDFURL": "https://.....",
    "ProcessingTimeInMilliseconds": "3000"
}


def check_exit(frame_events):
    for event in frame_events:
        if event.type == pg.QUIT:
            pg.quit()
            # DataJson.save_data_to_jason()
            quit()


def event_loop():
    frame_events = pg.event.get()

    check_exit(frame_events)
    # EditBox.check_select_box(frame_events)
    # DragCheck.check_drag(frame_events)

    # print(EditBox.selected_box)


def main():
    textImageDir = r"C:\Users\videw\Downloads\book page.jpg"

    global game_screen
    pg.init()

    pg_text_img = pg.image.load(textImageDir)
    game_screen = pg.display.set_mode(pg_text_img.get_size())
    pg.display.set_caption('Maze')
    clock = pg.time.Clock()

    # DataJson.get_text_from_image(textImageDir)
    DataJson.get_data_form_json()
    print(DataJson.data)
    while True:
        game_screen.fill((255, 255, 255))
        game_screen.blit(pg_text_img, (0, 0))

        # DragCheck.draw_select_box()
        # BoundingBox.draw_word_line()
        BoundingBox.draw_word()

        event_loop()
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    # DataJson.get_text_from_image(textImageDir)
    main()
    # DataJson.ocr_space_file(r"C:\Users\videw\Downloads\book page.jpg")
    # DataJson.save_data_to_jason()
    print(DataJson.data)

    print(DataJson.data)
