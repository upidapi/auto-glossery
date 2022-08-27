import pygame as pg
import json
import requests


def draw_rgba_rect(surface, color, start, end, outline_width=0, outline_color=(0, 0, 0)):
    size = (
        abs(start[0] - end[0]),
        abs(start[1] - end[1])
    )

    start = (
        min(start[0], end[0]),
        min(start[1], end[1])
    )

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
    def get_text_from_image(image_dir):
        image_file_descriptor = open(image_dir, 'rb')
        files = {'image': image_file_descriptor}

        api_url = 'https://api.api-ninjas.com/v1/imagetotext'

        headers = {
            "X-Api-Key": "yhS5vPsCpXpS44xc7Lk8Sw==hIbaqsxzX7p3I17L"
        }

        response = requests.post(api_url, files=files, headers=headers).text

        json_object = json.dumps(response, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

        return response

    @staticmethod
    def ocr_space_file(filename, language='spa'):
        """ OCR.space API request with local file.
            Python3.5 - not tested on 2.7
        :param filename: Your file path & name.
        :param overlay: Is OCR.space overlay required in your response.
                        Defaults to False.
        :param api_key: OCR.space API key.
                        Defaults to 'helloworld'.
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
    def get_text_from_image_space(image):
        api_url = 'https://api.ocr.space/parse/image'
        api_key = "K85003833988957"
        payload = {
            "apikey": api_key,
            "isOverlayRequired": True,
            "language": "spa",
        }

        response = requests.post(api_url,
                                 files={image},
                                 data=payload)

        json_object = json.dumps(response, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

        return response


    @staticmethod
    def get_data_form_json():
        with open("sample.json") as jsonFile:
            json_object = json.load(jsonFile)
            jsonFile.close()

        DataJson.data = json.loads(json_object)

    @staticmethod
    def save_data_to_jason():
        json_object = json.dumps(DataJson.data, indent=4)
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)


print(DataJson.data)

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


def draw_text_box():
    for box in DataJson.data:
        pos = box['bounding_box']
        draw_rgba_rect(game_screen, (200, 200, 255, 128), (pos['x1'], pos['y1']), (pos['x2'], pos['y2']),
                       outline_width=1, outline_color=(0, 100, 255))


def check_exit(frame_events):
    for event in frame_events:
        if event.type == pg.QUIT:
            pg.quit()
            # DataJson.save_data_to_jason()
            quit()


def event_loop():
    frame_events = pg.event.get()

    check_exit(frame_events)
    EditBox.check_select_box(frame_events)
    DragCheck.check_drag(frame_events)

    # print(EditBox.selected_box)


def main():
    textImageDir = r"C:\Users\videw\Downloads\IMG_2421.png"

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

        DragCheck.draw_select_box()
        draw_text_box()

        event_loop()
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    # main()
    DataJson.ocr_space_file(r"C:\Users\videw\Downloads\IMG_2421.png")
    DataJson.save_data_to_jason()
    print(DataJson.data)
