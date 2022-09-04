from general_funcs import *
import listeners

pg.init()
font = pg.font.SysFont('Helvatical bold', 24)


def draw_rgba_rect(surface, color, start, size, outline_width=0, outline_color=(0, 0, 0)):
    # drawing a rect with alpha
    select_rect = pg.Surface(size)  # the size of your rect
    select_rect.set_alpha(color[3])  # alpha level
    select_rect.fill((color[0], color[1], color[2]))  # this fills the entire surface

    surface.blit(select_rect, start)  # (0,0) are the top-left coordinates

    # draws the outline
    pg.draw.rect(surface, outline_color, start + size, outline_width)


def draw_line_box(surface, data):
    # may look a bit of, it's because of rounding errors when drawing
    for line in data:
        start, size = chords_to_wh(get_word_line_size(line))
        draw_rgba_rect(surface, (200, 200, 255, 128), start, size,
                       outline_width=1, outline_color=(0, 100, 255))


def draw_word_box(surface, data):
    # may look a bit of, it's because of rounding errors when drawing
    for line in data:
        words = line["Words"]

        # gets and draws the bounding box for each word
        for word in words:
            draw_rgba_rect(surface, (200, 200, 255, 128),
                           (word["Left"], word["Top"]),
                           (word["Width"], word["Height"]),
                           outline_width=1, outline_color=(0, 100, 255))


def draw_words(selected_type, surface, data, selected_data):
    selected_line, selected_word = selected_data

    # selected_data = {selected_line: i, selected_word: j,
    if selected_type is None:
        # draw it normally
        for line in data:
            img = font.render(line["LineText"], True, (0, 0, 0))
            surface.blit(img, get_word_line_size(line)[0:2])

    else:
        for i, line in enumerate(data):
            # normal line
            if i != selected_line:
                img = font.render(line["LineText"], True, (0, 0, 0))
                surface.blit(img, get_word_line_size(line)[0:2])
            else:
                # draws the selected thing in red
                if selected_type == 'line':
                    # draws the selected line red
                    # noinspection PyTypeChecker
                    line_data = data[selected_line]
                    text = line_data["LineText"]
                    img = font.render(text, True, (255, 0, 0))
                    # the first two items of the returned list is the lines x and y pos
                    pos = get_word_line_size(line_data)[0:2]
                    surface.blit(img, pos)

                elif selected_type == 'word':
                    # draws the selected word red
                    # the first two items of the returned list is the lines x and y pos
                    line_pos_x, line_pos_y = get_word_line_size(line)[0:2]

                    line["Words"].sort(key=lambda x: x["Left"])
                    for word in line["Words"]:
                        # only draw the selected word in red
                        if word == data[selected_line]['Words'][selected_word]:
                            # adds a space to account for the space between words
                            img = font.render(listeners.Text.get_text() + ' ', True, (255, 0, 0))

                        else:
                            # adds a space to account for the space between words
                            img = font.render((word['WordText'] + ' '), True, (0, 0, 0))

                        # use the lines y pos to make sure the words are aligned
                        pos = line_pos_x, line_pos_y
                        surface.blit(img, pos)

                        # add the width to the x pos so that the next word starts at the end of the last
                        line_pos_x += img.get_size()[0]


def draw_inp_mode(mode, surface, data):
    if mode == 1:
        draw_word_box(surface, data)

    if mode == 2:
        draw_line_box(surface, data)

    if mode == 3:
        draw_word_box(surface, data)
        draw_line_box(surface, data)
                        