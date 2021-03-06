from enum import Enum

STREAM_LENGTH = {
    "1L": 152, "1M": 128, "1Q": 104, "1H": 72,
    "2L": 272, "2M": 224, "2Q": 176, "2H": 128,
    "3L": 440, "3M": 352, "3Q": 272, "3H": 208,
    "4L": 640, "4M": 512, "4Q": 384, "4H": 288,
    "5L": 864, "5M": 688, "5Q": 496, "5H": 368,
    "6L": 1088, "6M": 864, "6Q": 608, "6H": 480,
    "7L": 1248, "7M": 992, "7Q": 704, "7H": 528,
    "8L": 1552, "8M": 1232, "8Q": 880, "8H": 688,
    "9L": 1856, "9M": 1456, "9Q": 1056, "9H": 800,
    "10L": 2192, "10M": 1728, "10Q": 1232, "10H": 976,
    "11L": 2592, "11M": 2032, "11Q": 1440, "11H": 1120,
    "12L": 2960, "12M": 2320, "12Q": 1648, "12H": 1264,
    "13L": 3424, "13M": 2672, "13Q": 1952, "13H": 1440,
    "14L": 3688, "14M": 2920, "14Q": 2088, "14H": 1576,
    "15L": 4184, "15M": 3320, "15Q": 2360, "15H": 1784,
    "16L": 4712, "16M": 3624, "16Q": 2600, "16H": 2024,
    "17L": 5176, "17M": 4056, "17Q": 2936, "17H": 2264,
    "18L": 5768, "18M": 4504, "18Q": 3176, "18H": 2504,
    "19L": 6360, "19M": 5016, "19Q": 3560, "19H": 2728,
    "20L": 6888, "20M": 5352, "20Q": 3880, "20H": 3080,
    "21L": 7456, "21M": 5712, "21Q": 4096, "21H": 3248,
    "22L": 8048, "22M": 6256, "22Q": 4544, "22H": 3536,
    "23L": 8752, "23M": 6880, "23Q": 4912, "23H": 3712,
    "24L": 9392, "24M": 7312, "24Q": 5312, "24H": 4112,
    "25L": 10208, "25M": 8000, "25Q": 5744, "25H": 4304,
    "26L": 10960, "26M": 8496, "26Q": 6032, "26H": 4768,
    "27L": 11744, "27M": 9024, "27Q": 6464, "27H": 5024,
    "28L": 12248, "28M": 9544, "28Q": 6968, "28H": 5288,
    "29L": 13048, "29M": 10136, "29Q": 7288, "29H": 5608,
    "30L": 13880, "30M": 10984, "30Q": 7880, "30H": 5960,
    "31L": 14744, "31M": 11640, "31Q": 8264, "31H": 6344,
    "32L": 15640, "32M": 12328, "32Q": 8920, "32H": 6760,
    "33L": 16568, "33M": 13048, "33Q": 9368, "33H": 7208,
    "34L": 17528, "34M": 13800, "34Q": 9848, "34H": 7688,
    "35L": 18448, "35M": 14496, "35Q": 10288, "35H": 7888,
    "36L": 19472, "36M": 15312, "36Q": 10832, "36H": 8432,
    "37L": 20528, "37M": 15936, "37Q": 11408, "37H": 8768,
    "38L": 21616, "38M": 16816, "38Q": 12016, "38H": 9136,
    "39L": 22496, "39M": 17728, "39Q": 12656, "39H": 9776,
    "40L": 23648, "40M": 18672, "40Q": 13328, "40H": 10208,
}

NUMBER_OF_ECC = {
    '1L': 7, '1M': 10, '1Q': 13, '1H': 17,
    '2L': 10, '2M': 16, '2Q': 22, '2H': 28,
    '3L': 15, '3M': 26, '3Q': 36, '3H': 44,
    '4L': 20, '4M': 36, '4Q': 52, '4H': 64,
    '5L': 26, '5M': 48, '5Q': 72, '5H': 88,
    '6L': 36, '6M': 64, '6Q': 96, '6H': 112,
    '7L': 40, '7M': 72, '7Q': 108, '7H': 130,
    '8L': 48, '8M': 88, '8Q': 132, '8H': 156,
    '9L': 60, '9M': 110, '9Q': 160, '9H': 192,
    '10L': 72, '10M': 130, '10Q': 192, '10H': 224,
    '11L': 80, '11M': 150, '11Q': 224, '11H': 264,
    '12L': 96, '12M': 176, '12Q': 260, '12H': 308,
    '13L': 104, '13M': 198, '13Q': 288, '13H': 352,
    '14L': 120, '14M': 216, '14Q': 320, '14H': 384,
    '15L': 132, '15M': 240, '15Q': 360, '15H': 432,
    '16L': 144, '16M': 280, '16Q': 408, '16H': 480,
    '17L': 168, '17M': 308, '17Q': 448, '17H': 532,
    '18L': 180, '18M': 338, '18Q': 504, '18H': 588,
    '19L': 196, '19M': 364, '19Q': 546, '19H': 650,
    '20L': 224, '20M': 416, '20Q': 600, '20H': 700,
    '21L': 224, '21M': 442, '21Q': 644, '21H': 750,
    '22L': 252, '22M': 476, '22Q': 690, '22H': 816,
    '23L': 270, '23M': 504, '23Q': 750, '23H': 900,
    '24L': 300, '24M': 560, '24Q': 810, '24H': 960,
    '25L': 312, '25M': 588, '25Q': 870, '25H': 1050,
    '26L': 336, '26M': 644, '26Q': 952, '26H': 1110,
    '27L': 360, '27M': 700, '27Q': 1020, '27H': 1200,
    '28L': 390, '28M': 728, '28Q': 1050, '28H': 1260,
    '29L': 420, '29M': 784, '29Q': 1140, '29H': 1350,
    '30L': 450, '30M': 812, '30Q': 1200, '30H': 1440,
    '31L': 480, '31M': 868, '31Q': 1290, '31H': 1530,
    '32L': 510, '32M': 924, '32Q': 1350, '32H': 1620,
    '33L': 540, '33M': 980, '33Q': 1440, '33H': 1710,
    '34L': 570, '34M': 1036, '34Q': 1530, '34H': 1800,
    '35L': 570, '35M': 1064, '35Q': 1590, '35H': 1890,
    '36L': 600, '36M': 1120, '36Q': 1680, '36H': 1980,
    '37L': 630, '37M': 1204, '37Q': 1770, '37H': 2100,
    '38L': 660, '38M': 1260, '38Q': 1860, '38H': 2220,
    '39L': 720, '39M': 1316, '39Q': 1950, '39H': 2310,
    '40L': 750, '40M': 1372, '40Q': 2040, '40H': 2430
}

ALIGNMENT_POSITIONS = [
    None, None,
    [(16, 16)],  # v2
    [(20, 20)],
    [(24, 24)],
    [(28, 28)],
    [(32, 32)],
    [(4, 20), (20, 36), (20, 20), (20, 4), (36, 36), (36, 20)],
    [(4, 22), (22, 40), (22, 22), (22, 4), (40, 40), (40, 22)],
    [(4, 24), (24, 44), (24, 24), (24, 4), (44, 44), (44, 24)],
    [(4, 26), (26, 48), (26, 26), (26, 4), (48, 48), (48, 26)],  # v10
    [(4, 28), (28, 52), (28, 28), (28, 4), (52, 52), (52, 28)],
    [(4, 30), (30, 56), (30, 30), (30, 4), (56, 56), (56, 30)],
    [(4, 32), (32, 60), (32, 32), (32, 4), (60, 60), (60, 32)],
    [(4, 44), (4, 24), (24, 64), (24, 44), (24, 24), (24, 4), (44, 64), (44, 44), (44, 24), (44, 4), (64, 64), (64, 44), (64, 24)],
    [(4, 48), (4, 26), (24, 68), (24, 48), (24, 26), (24, 4), (46, 68), (46, 48), (46, 26), (46, 4), (68, 68), (68, 48), (68, 26)],  # v15
    [(4, 52), (4, 28), (24, 72), (24, 52), (24, 28), (24, 4), (48, 72), (48, 52), (48, 28), (48, 4), (72, 72), (72, 52), (72, 28)],
    [(4, 52), (4, 28), (28, 76), (28, 52), (28, 28), (28, 4), (52, 76), (52, 52), (52, 28), (52, 4), (76, 76), (76, 52), (76, 28)],
    [(4, 56), (4, 30), (28, 80), (28, 56), (28, 30), (28, 2), (54, 80), (54, 56), (54, 30), (54, 2), (82, 80), (82, 56), (82, 30)],
    [(4, 60), (4, 32), (28, 84), (28, 60), (28, 32), (28, 4), (56, 84), (56, 60), (56, 32), (56, 4), (84, 84), (84, 60), (84, 32)],
    [(4, 60), (4, 32), (32, 88), (32, 60), (32, 32), (32, 4), (60, 88), (60, 60), (60, 32), (60, 4), (88, 88), (88, 60), (88, 32)],  # v20
    [(4, 70), (4, 44), (4, 26), (26, 92), (26, 70), (26, 44), (26, 26), (26, 4), (52, 92), (52, 70), (52, 44), (52, 26), (52, 4), (70, 92), (70, 70), (70, 44), (70, 26), (70, 4), (92, 92), (92, 70), (92, 44), (92, 26)],
    [(4, 76), (4, 52), (4, 28), (24, 96), (24, 76), (24, 52), (24, 28), (24, 4), (48, 96), (48, 76), (48, 52), (48, 28), (48, 4), (72, 96), (72, 76), (72, 52), (72, 28), (72, 4), (96, 96), (96, 76), (96, 52), (96, 28)],
    [(4, 76), (4, 52), (4, 28), (28, 100), (28, 76), (28, 52), (28, 28), (28, 4), (52, 100), (52, 76), (52, 52), (52, 28), (52, 4), (76, 100), (76, 76), (76, 52), (76, 28), (76, 4), (100, 100), (100, 76), (100, 52), (100, 28)],
    [(4, 82), (4, 56), (4, 30), (26, 104), (26, 82), (26, 56), (26, 30), (26, 4), (52, 104), (52, 82), (52, 56), (52, 30), (52, 4), (78, 104), (78, 82), (78, 56), (78, 30), (78, 4), (104, 104), (104, 82), (104, 56), (104, 30)],
    [(4, 82), (4, 56), (4, 30), (30, 108), (30, 82), (30, 56), (30, 30), (30, 4), (56, 108), (56, 82), (56, 56), (56, 30), (56, 4), (82, 108), (82, 82), (82, 56), (82, 30), (82, 4), (108, 108), (108, 82), (108, 56), (108, 30)],  # v25
    [(4, 88), (4, 60), (4, 32), (28, 112), (28, 88), (28, 60), (28, 32), (28, 4), (56, 112), (56, 88), (56, 60), (56, 32), (56, 4), (84, 112), (84, 88), (84, 60), (84, 32), (84, 4), (112, 112), (112, 88), (112, 60), (112, 32)],
    [(4, 88), (4, 60), (4, 32), (32, 116), (32, 88), (32, 60), (32, 32), (32, 4), (60, 116), (60, 88), (60, 60), (60, 32), (60, 4), (88, 116), (88, 88), (88, 60), (88, 32), (88, 4), (116, 116), (116, 88), (116, 60), (116, 32)],
    [(4, 100), (4, 76), (4, 52), (4, 28), (24, 120), (24, 100), (24, 76), (24, 52), (24, 28), (24, 4), (48, 120), (48, 100), (48, 76), (48, 52), (48, 28), (48, 4), (72, 120), (72, 100), (72, 76), (72, 52), (72, 28), (72, 4), (96, 120), (96, 100), (96, 76), (96, 52), (96, 28), (96, 4), (120, 120), (120, 100), (120, 76), (120, 52), (120, 28)],
    [(4, 100), (4, 76), (4, 52), (4, 28), (28, 124), (28, 100), (28, 76), (28, 52), (28, 28), (28, 4), (52, 124), (52, 100), (52, 76), (52, 52), (52, 28), (52, 4), (76, 124), (76, 100), (76, 76), (76, 52), (76, 28), (76, 4), (100, 124), (100, 100), (100, 76), (100, 52), (100, 28), (100, 4), (124, 124), (124, 100), (124, 76), (124, 52), (124, 28)],
    [(4, 108), (4, 82), (4, 56), (4, 30), (24, 128), (24, 108), (24, 82), (24, 56), (24, 30), (24, 4), (50, 128), (50, 108), (50, 82), (50, 56), (50, 30), (50, 4), (76, 128), (76, 108), (76, 82), (76, 56), (76, 30), (76, 4), (102, 128), (102, 108), (102, 82), (102, 56), (102, 30), (102, 4), (128, 128), (128, 108), (128, 82), (128, 56), (128, 30)],  # v30
    [(4, 108), (4, 82), (4, 56), (4, 30), (28, 132), (28, 108), (28, 82), (28, 56), (28, 30), (28, 4), (54, 132), (54, 108), (54, 82), (54, 56), (54, 30), (54, 4), (80, 132), (80, 108), (80, 82), (80, 56), (80, 30), (80, 4), (106, 132), (106, 108), (106, 82), (106, 56), (106, 30), (106, 4), (132, 132), (132, 108), (132, 82), (132, 56), (132, 30)],
    [(4, 108), (4, 82), (4, 56), (4, 30), (32, 136), (32, 108), (32, 82), (32, 56), (32, 30), (32, 4), (58, 136), (58, 108), (58, 82), (58, 56), (58, 30), (58, 4), (84, 136), (84, 108), (84, 82), (84, 56), (84, 30), (84, 4), (110, 136), (110, 108), (110, 82), (110, 56), (110, 30), (110, 4), (136, 136), (136, 108), (136, 82), (136, 56), (136, 30)],
    [(4, 116), (4, 88), (4, 60), (4, 32), (28, 140), (28, 116), (28, 88), (28, 60), (28, 32), (28, 4), (56, 140), (56, 116), (56, 88), (56, 60), (56, 32), (56, 4), (84, 140), (84, 116), (84, 88), (84, 60), (84, 32), (84, 4), (112, 140), (112, 116), (112, 88), (112, 60), (112, 32), (112, 4), (140, 140), (140, 116), (140, 88), (140, 60), (140, 32)],
    [(4, 116), (4, 88), (4, 60), (4, 32), (32, 144), (32, 116), (32, 88), (32, 60), (32, 32), (32, 4), (60, 144), (60, 116), (60, 88), (60, 60), (60, 32), (60, 4), (88, 144), (88, 116), (88, 88), (88, 60), (88, 32), (88, 4), (116, 144), (116, 116), (116, 88), (116, 60), (116, 32), (116, 4), (144, 144), (144, 116), (144, 88), (144, 60), (144, 32)],
    [(4, 124), (4, 100), (4, 76), (4, 52), (4, 28), (28, 148), (28, 124), (28, 100), (28, 76), (28, 52), (28, 28), (28, 4), (52, 148), (52, 124), (52, 100), (52, 76), (52, 52), (52, 28), (52, 4), (76, 148), (76, 124), (76, 100), (76, 76), (76, 52), (76, 28), (76, 4), (100, 148), (100, 124), (100, 100), (100, 76), (100, 52), (100, 28), (100, 4), (124, 148), (124, 124), (124, 100), (124, 76), (124, 52), (124, 28), (124, 4), (148, 148), (148, 124), (148, 100), (148, 76), (148, 52), (148, 28)],  # v35
    [(4, 134), (4, 98), (4, 82), (4, 56), (4, 30), (22, 152), (22, 134), (22, 98), (22, 82), (22, 56), (22, 30), (22, 4), (58, 152), (58, 134), (58, 98), (58, 82), (58, 56), (58, 30), (58, 4), (74, 152), (74, 134), (74, 98), (74, 82), (74, 56), (74, 30), (74, 4), (100, 152), (100, 134), (100, 98), (100, 82), (100, 56), (100, 30), (100, 4), (126, 152), (126, 134), (126, 98), (126, 82), (126, 56), (126, 30), (126, 4), (152, 152), (152, 134), (152, 98), (152, 82), (152, 56), (152, 30)],
    [(4, 134), (4, 108), (4, 82), (4, 56), (4, 30), (26, 156), (26, 134), (26, 108), (26, 82), (26, 56), (26, 30), (26, 4), (52, 156), (52, 134), (52, 108), (52, 82), (52, 56), (52, 30), (52, 4), (78, 156), (78, 134), (78, 108), (78, 82), (78, 56), (78, 30), (78, 4), (104, 156), (104, 134), (104, 108), (104, 82), (104, 56), (104, 30), (104, 4), (130, 156), (130, 134), (130, 108), (130, 82), (130, 56), (130, 30), (130, 4), (156, 156), (156, 134), (156, 108), (156, 82), (156, 56), (156, 30)],
    [(4, 134), (4, 108), (4, 82), (4, 56), (4, 30), (30, 160), (30, 134), (30, 108), (30, 82), (30, 56), (30, 30), (30, 4), (56, 160), (56, 134), (56, 108), (56, 82), (56, 56), (56, 30), (56, 4), (82, 160), (82, 134), (82, 108), (82, 82), (82, 56), (82, 30), (82, 4), (108, 160), (108, 134), (108, 108), (108, 82), (108, 56), (108, 30), (108, 4), (134, 160), (134, 134), (134, 108), (134, 82), (134, 56), (134, 30), (134, 4), (160, 160), (160, 134), (160, 108), (160, 82), (160, 56), (160, 30)],
    [(4, 144), (4, 116), (4, 88), (4, 60), (4, 32), (24, 164), (24, 144), (24, 116), (24, 88), (24, 60), (24, 32), (24, 4), (52, 164), (52, 144), (52, 116), (52, 88), (52, 60), (52, 32), (52, 4), (80, 164), (80, 144), (80, 116), (80, 88), (80, 60), (80, 32), (80, 4), (108, 164), (108, 144), (108, 116), (108, 88), (108, 60), (108, 32), (108, 4), (136, 164), (136, 144), (136, 116), (136, 88), (136, 60), (136, 32), (136, 4), (164, 164), (164, 144), (164, 116), (164, 88), (164, 60), (164, 32)],
    [(4, 144), (4, 116), (4, 88), (4, 60), (4, 32), (28, 168), (28, 144), (28, 116), (28, 88), (28, 60), (28, 32), (28, 4), (56, 168), (56, 144), (56, 116), (56, 88), (56, 60), (56, 32), (56, 4), (84, 168), (84, 144), (84, 116), (84, 88), (84, 60), (84, 32), (84, 4), (112, 168), (112, 144), (112, 116), (112, 88), (112, 60), (112, 32), (112, 4), (140, 168), (140, 144), (140, 116), (140, 88), (140, 60), (140, 32), (140, 4), (168, 168), (168, 144), (168, 116), (168, 88), (168, 60), (168, 32)],  # v40
]

EC_SHORT = {
    '1L': 1, '1M': 1, '1Q': 1, '1H': 1,
    '2L': 1, '2M': 1, '2Q': 1, '2H': 1,
    '3L': 1, '3M': 1, '3Q': 2, '3H': 2,
    '4L': 1, '4M': 2, '4Q': 2, '4H': 4,
    '5L': 1, '5M': 2, '5Q': 2, '5H': 2,
    '6L': 2, '6M': 4, '6Q': 4, '6H': 4,
    '7L': 2, '7M': 4, '7Q': 2, '7H': 4,
    '8L': 2, '8M': 2, '8Q': 4, '8H': 4,
    '9L': 2, '9M': 3, '9Q': 4, '9H': 4,
    '10L': 2, '10M': 4, '10Q': 6, '10H': 6,
    '11L': 4, '11M': 1, '11Q': 4, '11H': 3,
    '12L': 2, '12M': 6, '12Q': 4, '12H': 7,
    '13L': 4, '13M': 8, '13Q': 8, '13H': 12,
    '14L': 3, '14M': 4, '14Q': 11, '14H': 11,
    '15L': 5, '15M': 5, '15Q': 5, '15H': 11,
    '16L': 5, '16M': 7, '16Q': 15, '16H': 3,
    '17L': 1, '17M': 10, '17Q': 1, '17H': 2,
    '18L': 5, '18M': 9, '18Q': 17, '18H': 2,
    '19L': 3, '19M': 3, '19Q': 17, '19H': 9,
    '20L': 3, '20M': 3, '20Q': 15, '20H': 15,
    '21L': 4, '21M': 17, '21Q': 17, '21H': 19,
    '22L': 2, '22M': 17, '22Q': 7, '22H': 34,
    '23L': 4, '23M': 4, '23Q': 11, '23H': 16,
    '24L': 6, '24M': 6, '24Q': 11, '24H': 30,
    '25L': 8, '25M': 8, '25Q': 7, '25H': 22,
    '26L': 10, '26M': 19, '26Q': 28, '26H': 33,
    '27L': 8, '27M': 22, '27Q': 8, '27H': 12,
    '28L': 3, '28M': 3, '28Q': 4, '28H': 11,
    '29L': 7, '29M': 21, '29Q': 1, '29H': 19,
    '30L': 5, '30M': 19, '30Q': 15, '30H': 23,
    '31L': 13, '31M': 2, '31Q': 42, '31H': 23,
    '32L': 17, '32M': 10, '32Q': 10, '32H': 19,
    '33L': 17, '33M': 14, '33Q': 29, '33H': 11,
    '34L': 13, '34M': 14, '34Q': 44, '34H': 59,
    '35L': 12, '35M': 12, '35Q': 39, '35H': 22,
    '36L': 6, '36M': 6, '36Q': 46, '36H': 2,
    '37L': 17, '37M': 29, '37Q': 49, '37H': 24,
    '38L': 4, '38M': 13, '38Q': 48, '38H': 42,
    '39L': 20, '39M': 40, '39Q': 43, '39H': 10,
    '40L': 19, '40M': 18, '40Q': 34, '40H': 20
}

EC_LONG = {
    '1L': 0, '1M': 0, '1Q': 0, '1H': 0,
    '2L': 0, '2M': 0, '2Q': 0, '2H': 0,
    '3L': 0, '3M': 0, '3Q': 0, '3H': 0,
    '4L': 0, '4M': 0, '4Q': 0, '4H': 0,
    '5L': 0, '5M': 0, '5Q': 2, '5H': 2,
    '6L': 0, '6M': 0, '6Q': 0, '6H': 0,
    '7L': 0, '7M': 0, '7Q': 4, '7H': 1,
    '8L': 0, '8M': 2, '8Q': 2, '8H': 2,
    '9L': 0, '9M': 2, '9Q': 4, '9H': 4,
    '10L': 2, '10M': 1, '10Q': 2, '10H': 2,
    '11L': 0, '11M': 4, '11Q': 4, '11H': 8,
    '12L': 2, '12M': 2, '12Q': 6, '12H': 4,
    '13L': 0, '13M': 1, '13Q': 4, '13H': 4,
    '14L': 1, '14M': 5, '14Q': 5, '14H': 5,
    '15L': 1, '15M': 5, '15Q': 7, '15H': 7,
    '16L': 1, '16M': 3, '16Q': 2, '16H': 13,
    '17L': 5, '17M': 1, '17Q': 15, '17H': 17,
    '18L': 1, '18M': 4, '18Q': 1, '18H': 19,
    '19L': 4, '19M': 11, '19Q': 4, '19H': 16,
    '20L': 5, '20M': 13, '20Q': 5, '20H': 10,
    '21L': 4, '21M': 0, '21Q': 6, '21H': 6,
    '22L': 7, '22M': 0, '22Q': 16, '22H': 0,
    '23L': 5, '23M': 14, '23Q': 14, '23H': 14,
    '24L': 4, '24M': 14, '24Q': 16, '24H': 2,
    '25L': 4, '25M': 13, '25Q': 22, '25H': 13,
    '26L': 2, '26M': 4, '26Q': 6, '26H': 4,
    '27L': 4, '27M': 3, '27Q': 26, '27H': 28,
    '28L': 10, '28M': 23, '28Q': 31, '28H': 31,
    '29L': 7, '29M': 7, '29Q': 37, '29H': 26,
    '30L': 10, '30M': 10, '30Q': 25, '30H': 25,
    '31L': 3, '31M': 29, '31Q': 1, '31H': 28,
    '32L': 0, '32M': 23, '32Q': 35, '32H': 35,
    '33L': 1, '33M': 21, '33Q': 19, '33H': 46,
    '34L': 6, '34M': 23, '34Q': 7, '34H': 1,
    '35L': 7, '35M': 26, '35Q': 14, '35H': 41,
    '36L': 14, '36M': 34, '36Q': 10, '36H': 64,
    '37L': 4, '37M': 14, '37Q': 10, '37H': 46,
    '38L': 18, '38M': 32, '38Q': 14, '38H': 32,
    '39L': 4, '39M': 7, '39Q': 22, '39H': 67,
    '40L': 6, '40M': 31, '40Q': 34, '40H': 61
}


class EC_LEVEL(Enum):
    L = "01"
    M = "00"
    Q = "11"
    H = "10"


class DATA_MODE(Enum):
    Numeric = 1
    Alphanumeric = 2
    Byte = 4


CCI_LENGTH = {
    DATA_MODE.Numeric: [0] + [10] * 9 + [12] * 17 + [14] * 14,
    DATA_MODE.Alphanumeric: [0] + [9] * 9 + [11] * 17 + [13] * 14,
    DATA_MODE.Byte: [0] + [8] * 9 + [16] * 17 + [16] * 14
}

REMAINDER_BITS = [0] + [0] + [7] * 5 + [0] * 7 + [3] * 7 + [4] * 7 + [3] * 7 + [0] * 6
