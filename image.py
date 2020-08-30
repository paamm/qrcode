from typing import List, Tuple

import numpy
from PIL import Image

from constants import EC_LEVEL, ALIGNMENT_POSITIONS
import encoding


class QRImage:
    def __init__(self, version: int, error_correction: EC_LEVEL, message: str):
        self.size = version * 4 + 17
        self.version = version
        self.ecl = error_correction
        self.message = message

        # Create 2 arrays with correct size based on the version in the parameters
        self.array = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        self.unmasked = [[-1 for _ in range(self.size)] for _ in range(self.size)]

        # Compute the codewords for the message
        self.data = encoding.generate_codewords(message, version, error_correction)
        # Create the qr code
        self.__draw_initial__()  # drawing the static modules (finder patterns, etc)
        self.write_data()

        # Image and whether we need to regen it or not before showing it (when changing version, etc.. is implemented)
        self.image = self.__generate_image__()
        self.need_regen: bool = False

    def __draw_initial__(self):

        def draw_timing_patterns():
            # As defined in 7.3.4
            # Vertical pattern
            for y in range(self.size):
                self.unmasked[y][6] = (y + 1) % 2

            # Horizontal pattern
            for x in range(self.size):
                self.unmasked[6][x] = (x + 1) % 2

        def draw_finder_patterns():
            # As defined in 7.3.2
            x_offset = [0, self.size - 7, 0]
            y_offset = [0, 0, self.size - 7]

            for pattern in range(3):
                for x in range(7):
                    for y in range(7):
                        color = 0

                        if x in [0, 6] or y in [0, 6]:  # in outer pattern
                            color = 1
                        elif x not in [1, 5] and y not in [1, 5]:  # not in middle pattern (in inner pattern)
                            color = 1

                        self.unmasked[y + y_offset[pattern]][x + x_offset[pattern]] = color

        def draw_spacing_and_format():
            # top left
            for x in range(9):
                self.unmasked[7][x] = 0
                self.unmasked[8][x] = x == 6  # doesn't overwrite existing timing pattern
            for y in range(9):
                self.unmasked[y][7] = 0
                self.unmasked[y][8] = y == 6

            #top right
            for x in range(self.size - 8, self.size):
                self.unmasked[7][x] = 0
                self.unmasked[8][x] = 0
            for y in range(9):
                self.unmasked[y][self.size - 8] = 0

            #bottom left
            for y in range(self.size - 8, self.size):
                self.unmasked[y][7] = 0
                self.unmasked[y][8] = 0
            for x in range(9):
                self.unmasked[self.size - 8][x] = x == 8  # write the format black module

        def draw_alignment_patterns():
            pos = ALIGNMENT_POSITIONS[self.version]

            for pair in pos:
                x_offset, y_offset = pair
                for x in range(5):
                    for y in range(5):
                        if x in [0, 4] or y in [0, 4] or x == y == 2:
                            # outer square or inner dot
                            self.unmasked[y + y_offset][x + x_offset] = 1
                        else:
                            self.unmasked[y + y_offset][x + x_offset] = 0

        def draw_version_information():
            table = [""] * 7 + [
                "000111110010010100",
                "001000010110111100",
                "001001101010011001",
                "001010010011010011",  # v10
                "001011101111110110",
                "001100011101100010",
                "001101100001000111",
                "001110011000001101",
                "001111100100101000",  # v15
                "010000101101111000",
                "010001010001011101",
                "010010101000010111",
                "010011010100110010",
                "010100100110100110",  # v20
                "010101011010000011",
                "010110100011001001",
                "010111011111101100",
                "011000111011000100",
                "011001000111100001",  # v25
                "011010111110101011",
                "011011000010001110",
                "011100110000011010",
                "011101001100111111",
                "011110110101110101",  # v30
                "011111001001010000",
                "100000100111010101",
                "100001011011110000",
                "100010100010111010",
                "100011011110011111",  # v35
                "100100101100001011",
                "100101010000101110",
                "100110101001100100",
                "100111010101000001",
                "101000110001101001",  # v40
            ]

            version_info = table[self.version]

            # top right
            x = y = 0
            for i in range(len(version_info)):
                self.unmasked[y + 5][self.size + x - 9] = int(version_info[i])

                if x == -2:
                    x = 0
                    y -= 1
                else:
                    x -= 1

            # bottom left
            x = y = 0
            for i in range(len(version_info)):
                self.unmasked[self.size + y - 9][x + 5] = int(version_info[i])

                if y == - 2:
                    y = 0
                    x -= 1
                else:
                    y -= 1

        draw_timing_patterns()
        draw_finder_patterns()
        draw_spacing_and_format()
        if self.version > 1:
            draw_alignment_patterns()  # not needed for version 1
        if self.version >= 7:
            draw_version_information()

    def write_data(self):
        def top(x: int) -> int:
            """
            Returns the max height you can write to for the specified x coordinate.
            :param x: The current column
            :return: The max height (inclusive) accessible.
            """
            if x >= self.size - 8 or x <= 8:
                # under the finder patterns
                return 9
            else:
                return 0

        def bottom(x: int) -> int:
            return self.size - 1 if x > 8 else self.size - 9

        def going_up(x: int) -> bool:
            """Returns true for up, false for down"""
            # An enum would be better, but since it would only be used once, didn't create it
            if x <= 6:
                # Before vertical timing pattern
                return (x // 2) % 2 != 0
            else:
                # After vertical timing pattern
                return ((x + 1) // 2) % 2 == 0

        def next_move(x: int, y: int) -> Tuple[int, int]:
            # initial
            if x is None and y is None:
                return self.size - 1, self.size - 1

            if x > 6:
                # normal section
                if going_up(x):
                    if x % 2 == 0:
                        # Going left
                        return x - 1, y
                    else:
                        if y == top(x):
                            if x == 7:
                                # Edge-case: corner of vertical timing and top-left position pattern
                                return x - 2, y
                            else:
                                # Normal case
                                return x - 1, y

                        # Going up, check not at horizontal timing pattern
                        if y == 7:
                            # below pattern
                            return x + 1, y - 2
                        else:
                            return x + 1, y - 1
                else:
                    # Downward
                    if x % 2 == 0:
                        # Going left
                        return x - 1, y
                    else:
                        # Going down
                        if y == bottom(x):
                            if x == 9:
                                # Edge-case: next to bottom left position pattern, weird jump
                                return 8, self.size - 9
                            else:
                                # Normal case
                                return x - 1, y

                        # Check if not at horizontal timing pattern
                        if y == 5:
                            # above pattern
                            return x + 1, y + 2
                        else:
                            return x + 1, y + 1
            else:
                # Left-most section
                if going_up(x):
                    if x % 2 == 1:
                        # going left
                        return x - 1, y
                    else:
                        # going up
                        if y == top(x):
                            return x - 1, y
                        else:
                            return x + 1, y - 1
                    pass
                else:
                    # going down
                    if x % 2 == 1:
                        # going left
                        return x - 1, y
                    else:
                        # going down
                        if y == bottom(x):
                            return x - 1, y
                        else:
                            return x + 1, y + 1

        def new_next_move(x: int, y: int) -> Tuple[int, int]:
            if x is None and y is None:
                # initial
                return self.size - 1, self.size - 1

            # edge-case: transition between normal zone and left zone
            if y == 0 and x == 7:
                return 5, 0

            if x >= 7:
                # normal zone
                up = ((x + 1) // 2) % 2 == 0

                if up:
                    if x % 2 == 0:
                        # going left
                        return x - 1, y
                    else:
                        # going up right
                        if y == 0:
                            # already at top, switch lane
                            return x - 1, y
                        else:
                            return x + 1, y - 1
                else:
                    # down
                    if x % 2 == 0:
                        # going left
                        return x - 1, y
                    else:
                        # going down right
                        if y == self.size - 1:
                            # bottom, switch lane
                            return x - 1, y
                        else:
                            return x + 1, y + 1

            else:
                # left-most zone
                up = x in [2, 3]

                if up:
                    if x % 2 == 1:
                        # going left
                        return x - 1, y
                    else:
                        # up-right
                        if y == 0:
                            # top
                            return x - 1, y
                        else:
                            return x + 1, y - 1
                else:
                    # down
                    if x % 2 == 1:
                        return x - 1, y
                    else:
                        if y == self.size - 1:
                            return x - 1, y
                        else:
                            return x + 1, y + 1

        x = y = None

        for i in range(len(self.data)):
        # for i in range(3000):
            x, y = new_next_move(x, y)

            while self.unmasked[y][x] != -1:  # if not -1, has been written to (most likely alignment pattern)
                x, y = new_next_move(x, y)

            # self.unmasked[y][x] = int(self.data[i])

        self.__write_best_mask__()

    def __write_best_mask__(self):
        def is_protected(x: int, y: int) -> bool:
            if x == 6 or y == 6:
                # Timing pattern
                return True
            if x <= 8 and y <= 8 or x >= (self.size - 8) and y <= 8 or x <= 8 and y >= (self.size - 8):
                # Finder pattern
                return True

            if self.version > 1:
                positions = ALIGNMENT_POSITIONS[self.version]
                for position in positions:
                    x_pos, y_pos = position
                    if x_pos <= x <= x_pos + 4 and y_pos <= y <= y_pos + 4:
                        return True
            if self.version >= 7:
                # version info section
                if x <= 5 and y >= self.size - 11 or x >= self.size - 11 and y <= 5:
                    return True

        def mask_pattern(pattern: int) -> List[List[int]]:
            masked_array = [row[:] for row in self.unmasked]  # deep copy
            self.__write_format_information__(masked_array, pattern)

            for x in range(self.size):
                for y in range(self.size):
                    if not is_protected(x, y):
                        if pattern == 0:
                            masked_array[y][x] ^= ((y + x) % 2 == 0)
                        elif pattern == 1:
                            masked_array[y][x] ^= (y % 2 == 0)
                        elif pattern == 2:
                            masked_array[y][x] ^= (x % 3 == 0)
                        elif pattern == 3:
                            masked_array[y][x] ^= ((y + x) % 3 == 0)
                        elif pattern == 4:
                            masked_array[y][x] ^= (((y // 2) + (x // 3)) % 2 == 0)
                        elif pattern == 5:
                            masked_array[y][x] ^= ((y * x) % 2 + (y * x) % 3 == 0)
                        elif pattern == 6:
                            masked_array[y][x] ^= (((y * x) % 2 + (y * x) % 3) % 2 == 0)
                        elif pattern == 7:
                            masked_array[y][x] ^= (((y + x) % 2 + (y * x) % 3) % 2 == 0)
            return masked_array

        # initialize values by computing mask 0, loop for mask 1-7
        # self.array = mask_pattern(0)
        self.array = self.unmasked
        lowest_score = self.__calculate_mask_score__(self.array)

        for mask in range(1, 8):
            masked = mask_pattern(mask)
            score = self.__calculate_mask_score__(masked)
            if score < lowest_score:
                lowest_score = score
                # self.array = masked

    def __write_format_information__(self, array: List[List[int]], mask_pattern: int):
        # Using hardcoded table since there is no real reason to actually compute the format bits each time
        table = dict({
            "L": [
                "111011111000100", "111001011110011", "111110110101010", "111100010011101",
                "110011000101111", "110001100011000", "110110001000001", "110100101110110"
            ],
            "M": [
                "101010000010010", "101000100100101", "101111001111100", "101101101001011",
                "100010111111001", "100000011001110", "100111110010111", "100101010100000"
            ],
            "Q": [
                "011010101011111", "011000001101000", "011111100110001", "011101000000110",
                "010010010110100", "010000110000011", "010111011011010", "010101111101101"
            ],
            "H": [
                "001011010001001", "001001110111110", "001110011100111", "001100111010000",
                "000011101100010", "000001001010101", "000110100001100", "000100000111011"
            ]
        })

        info = table[self.ecl.name][mask_pattern]

        i = 0
        for x in range(9):
            if x != 6:
                array[8][x] = int(info[i])
                i += 1

        for y in range(7, -1, -1):
            if y != 6:
                array[y][8] = int(info[i])
                i += 1

        i = 0
        for y in range(self.size - 1, self.size - 8, -1):
            array[y][8] = int(info[i])
            i += 1

        for x in range(self.size - 8, self.size):
            array[8][x] = int(info[i])
            i += 1

        # dark module
        array[self.size - 8][8] = 1

    def __calculate_mask_score__(self, array: List[List[int]]) -> int:
        def colored_rows() -> int:
            score = 0
            for y in range(self.size):
                x = 0
                color = array[y][x]
                current_length = 1
                x += 1
                while x < self.size:
                    if array[y][x] == color:
                        current_length += 1
                    else:
                        if current_length >= 5:
                            score += 3 + (current_length - 5)
                        current_length = 1
                        color = array[y][x]
                    x += 1

                # need to check again after the loop in case the last module is part of a group
                if current_length >= 5:
                    score += 3 + (current_length - 5)

            return score

        def colored_cols() -> int:
            score = 0
            for x in range(self.size):
                y = 0
                color = array[y][x]
                current_length = 1
                y += 1
                while y < self.size:
                    if array[y][x] == color:
                        current_length += 1
                    else:
                        if current_length >= 5:
                            score += 3 + (current_length - 5)
                        current_length = 1
                        color = array[y][x]
                    y += 1
                # need to check again after the loop in case the last module is part of a group
                if current_length >= 5:
                    score += 3 + (current_length - 5)
            return score

        def colored_boxes() -> int:
            score = 0
            for y in range(self.size - 1):
                for x in range(self.size - 1):
                    if array[y][x] == array[y][x + 1] == array[y + 1][x] == array[y + 1][x + 1]:
                        score += 3
            return score

        def finder_pattern() -> int:
            score = 0
            pad_before = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]
            pad_after = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]

            for row in array:
                for i in range(self.size - 11):
                    sub_row = row[i:i + 11]
                    if sub_row in [pad_before, pad_after]:
                        # pattern match
                        score += 40

            for i in range(self.size):
                col = [row[i] for row in array]
                for j in range(self.size - 11):
                    sub_col = col[j:j + 11]
                    if sub_col in [pad_before, pad_after]:
                        score += 40

            return score

        def color_proportion() -> int:
            black_modules = 0
            for x in range(self.size):
                for y in range(self.size):
                    black_modules += array[y][x]

            proportion = (black_modules * 100) / (self.size ** 2)  # proportion in %

            i = 0
            while not ((50 - 5 * (i + 1)) <= proportion <= (50 + 5 * (i + 1))):
                # 0 if 45 <= x <= 55, 1 if 40 <= x <= 50, etc...
                i += 1

            return i * 10

        return colored_rows() + colored_cols() + colored_boxes() + finder_pattern() + color_proportion()

    def __generate_image__(self):
        np_array = [[255 if i != 1 else 0 for i in row] for row in self.array]

        # Upscaling
        # TODO remove / implement better
        np_array = numpy.kron(np_array, numpy.ones((20, 20)))

        return Image.fromarray(np_array.astype(numpy.uint8), mode='L')

    def show_image(self):
        if self.need_regen:
            self.image = self.__generate_image__()
        self.image.show()

    def save_image(self, filename="qr"):
        if self.need_regen:
            self.image = self.__generate_image__()
        filename += ".png"
        self.image.save(filename)
