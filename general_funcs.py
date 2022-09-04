import pygame as pg


def wh_to_chords(wh) -> tuple[int, int, int, int]:
    x, y, width, height = wh
    return int(x), int(y), int(x + width), int(y + height)


def chords_to_wh(chords: list[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = chords
    size = (
        abs(x1 - x2),
        abs(y1 - y2)
    )

    start = (
        min(x1, x2),
        min(y1, y2)
    )

    return start[0], start[1], size[0], size[1]


def button_click_check(button_size, click_pos=None) -> bool:
    if click_pos is None:
        click_pos = pg.mouse.get_pos()

    x1, y1, x2, y2 = button_size

    if x1 <= click_pos[0] <= x2 and y1 <= click_pos[1] <= y2:
        return True
    return False


def get_word_line_size(line):
    min_chords = [1_000_000, 1_000_000, 0, 0]
    words = line["Words"]
    for word in words:
        chords = wh_to_chords((word["Left"], word["Top"], word["Width"], word["Height"]))
        # gets the min/max chords of chords to get the bounding box
        min_chords[0] = min(min_chords[0], chords[0])  # x1
        min_chords[1] = min(min_chords[1], chords[1])  # y1
        min_chords[2] = max(min_chords[2], chords[2])  # x2
        min_chords[3] = max(min_chords[3], chords[3])  # y2

    return min_chords
