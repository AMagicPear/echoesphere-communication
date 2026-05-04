music_notes_pixels_map: dict[str, set[int]] = {
    "waterdrop": {0, 1, 2, 3, 4, 5, 6, 57, 58, 59, 60, 61, 62, 63},
    "crossing": {9, 10, 11, 12, 13, 14, 54, 53, 52, 51, 50, 49},
    "tide": {17, 18, 19, 20, 21, 22, 23, 46, 45, 44, 43, 42, 41},
    "breeze": {25, 26, 27, 28, 29, 30, 31, 32, 38, 37, 36, 35, 34, 33},
}

music_notes_colors: dict[str, tuple[int, int, int]] = {
    "waterdrop": (0x61, 0xCC, 0xE7),
    "crossing": (0x7C, 0x67, 0xEC),
    "tide": (0x55, 0x7E, 0xF1),
    "breeze": (0x57, 0xEE, 0x8C),
}
