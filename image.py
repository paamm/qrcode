from typing import List, Tuple, Union

import numpy
from PIL import Image

from constants import EC_LEVEL, ALIGNMENT_POSITIONS
import encoding


class QRImage:
    def __init__(self, version: int, ec_level: Union[EC_LEVEL, str], message: str):
        """
        Create a QRImage object with the given arguments.

        :param version: The QR version to use
        :param ec_level: The error correction level to use
        :param message: The message to write to the QR code
        """
        self._size = version * 4 + 17
        self._version = version
        self._message = message

        # Cast ec_level to EC_LEVEL enum if needed
        if type(ec_level) is str:
            self._ecl = EC_LEVEL[ec_level]
        else:
            self._ecl = ec_level

        # Create 2 arrays with correct size based on the version
        self._array = [[-1 for _ in range(self._size)] for _ in range(self._size)]
        self._unmasked = [[-1 for _ in range(self._size)] for _ in range(self._size)]

        # Compute the codewords for the message
        self._data = encoding.generate_codewords(self._message, self._version, self._ecl)

        # Create the qr code
        self._draw_initial()  # drawing the static modules (finder patterns, etc)
        self._write_data()  # draw the data and apply masking

        # Create the PIL image
        self._image = self._generate_image()
        self._need_regen: bool = False

    def _draw_initial(self):
        """
        Writes the static patterns to the unmasked array
        """

        def draw_timing_patterns():
            # As defined in 7.3.4
            # Vertical pattern
            for y in range(self._size):
                self._unmasked[y][6] = (y + 1) % 2

            # Horizontal pattern
            for x in range(self._size):
                self._unmasked[6][x] = (x + 1) % 2

        def draw_finder_patterns():
            # As defined in 7.3.2
            x_offset = [0, self._size - 7, 0]
            y_offset = [0, 0, self._size - 7]

            for pattern in range(3):
                for x in range(7):
                    for y in range(7):
                        color = 0

                        if x in [0, 6] or y in [0, 6]:  # in outer pattern
                            color = 1
                        elif x not in [1, 5] and y not in [1, 5]:  # not in middle pattern (in inner pattern)
                            color = 1

                        self._unmasked[y + y_offset[pattern]][x + x_offset[pattern]] = color

        def draw_spacing_and_format():
            # top left
            for x in range(9):
                self._unmasked[7][x] = 0
                self._unmasked[8][x] = x == 6  # doesn't overwrite existing timing pattern
            for y in range(9):
                self._unmasked[y][7] = 0
                self._unmasked[y][8] = y == 6

            # top right
            for x in range(self._size - 8, self._size):
                self._unmasked[7][x] = 0
                self._unmasked[8][x] = 0
            for y in range(9):
                self._unmasked[y][self._size - 8] = 0

            # bottom left
            for y in range(self._size - 8, self._size):
                self._unmasked[y][7] = 0
                self._unmasked[y][8] = 0
            for x in range(9):
                self._unmasked[self._size - 8][x] = x == 8  # write the format black module

        def draw_alignment_patterns():
            pos = ALIGNMENT_POSITIONS[self._version]

            for pair in pos:
                x_offset, y_offset = pair
                for x in range(5):
                    for y in range(5):
                        if x in [0, 4] or y in [0, 4] or x == y == 2:
                            # outer square or inner dot
                            self._unmasked[y + y_offset][x + x_offset] = 1
                        else:
                            self._unmasked[y + y_offset][x + x_offset] = 0

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

            version_info = table[self._version]

            # top right
            x = y = 0
            for i in range(len(version_info)):
                self._unmasked[y + 5][self._size + x - 9] = int(version_info[i])

                if x == -2:
                    x = 0
                    y -= 1
                else:
                    x -= 1

            # bottom left
            x = y = 0
            for i in range(len(version_info)):
                self._unmasked[self._size + y - 9][x + 5] = int(version_info[i])

                if y == - 2:
                    y = 0
                    x -= 1
                else:
                    y -= 1

        draw_timing_patterns()
        draw_finder_patterns()
        draw_spacing_and_format()
        if self._version > 1:
            draw_alignment_patterns()  # not needed for version 1
        if self._version >= 7:
            draw_version_information()

    def get_version(self) -> int:
        return self._version

    def set_version(self, new_version: int):
        """
        Set a new version for the instance

        :param new_version: The new version to use
        :raise ValueError: if the current message is too long for the instance's error correction level and new version
        """
        self._version = new_version
        self._size = self._version * 4 + 17

        # Recreate array and unmasked since new version means new size
        self._array = [[-1 for _ in range(self._size)] for _ in range(self._size)]
        self._unmasked = [[-1 for _ in range(self._size)] for _ in range(self._size)]

        # regen encoded data with new version
        self._data = encoding.generate_codewords(self._message, self._version, self._ecl)
        self._need_regen = True  # Set need_regen to True to only generate image when requested for the first time.
        self._write_data()

    def get_error_correction_level(self) -> EC_LEVEL:
        return self._ecl

    def set_error_correction_level(self, new_ecl: Union[EC_LEVEL, str]):
        """
        Set a new error correction level for the instance

        :param new_ecl: The new error correction level to use
        :raise ValueError: if the current message is too long for the instance's version and new error correction level
        """
        if type(new_ecl) is str:
            self._ecl = EC_LEVEL[new_ecl]  # Cast to enum
        else:
            self._ecl = new_ecl

        self._data = encoding.generate_codewords(self._message, self._version, self._ecl)
        self._need_regen = True
        self._write_data()

    def get_message(self) -> str:
        return self._message

    def set_message(self, new_msg: str):
        """
        Set a new message for the instance

        :param new_msg: The new message to use
        :raise ValueError: if the new message is too long for the instance's version and error correction level
        """
        self._message = new_msg
        self._data = encoding.generate_codewords(self._message, self._version, self._ecl)
        self._need_regen = True
        self._write_data()

    def _write_data(self):
        """
        Write the contents of _data to the _unmasked matrix
        """

        def next_move(x: int, y: int) -> Tuple[int, int]:
            """
            Calculates the new position based on the current one.

            :param x: The current x position
            :param y: The current y position
            :return: A tuple containing the new x and y coordinates
            """
            if x is None and y is None:
                # initial
                return self._size - 1, self._size - 1

            # edge-case: transition between normal zone and left zone
            if y == 0 and x == 7:
                return 5, 0

            if x >= 7:
                # normal zone
                up = ((x + 1) // 2) % 2 == 0  # boolean checking if we're moving up

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
                        if y == self._size - 1:
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
                        if y == self._size - 1:
                            return x - 1, y
                        else:
                            return x + 1, y + 1

        x = y = None

        for i in range(len(self._data)):
            x, y = next_move(x, y)

            while self._unmasked[y][x] != -1:  # if not -1, has been written to (static pattern)
                x, y = next_move(x, y)  # go to next position until we're not in a static pattern anymore

            self._unmasked[y][x] = int(self._data[i])  # write bit to current position

        self._write_best_mask()  # Find the optimal mask for the unmasked matrix

    def _write_best_mask(self):
        """
        Reads the _unmasked matrix to determine the best mask and writes the masked matrix to _array
        """

        def is_protected(x: int, y: int) -> bool:
            """
            Checks if we can make changes to the coordinates
            :param x: The x coordinate
            :param y: The y coordinate
            :return: True if it is protected, false if it is not and we can make changes
            """
            if x == 6 or y == 6:
                # Timing pattern
                return True
            if x <= 8 and y <= 8 or x >= (self._size - 8) and y <= 8 or x <= 8 and y >= (self._size - 8):
                # Finder pattern
                return True

            if self._version > 1:
                # Alignment pattern
                positions = ALIGNMENT_POSITIONS[self._version]
                for position in positions:
                    x_pos, y_pos = position
                    if x_pos <= x <= x_pos + 4 and y_pos <= y <= y_pos + 4:
                        return True
            if self._version >= 7:
                # version info section
                if x <= 5 and y >= self._size - 11 or x >= self._size - 11 and y <= 5:
                    return True

        def mask_pattern(pattern: int) -> List[List[int]]:
            masked_array = [row[:] for row in self._unmasked]  # deep copy
            self._write_format_information(masked_array, pattern)

            if pattern == 0:
                def pattern_formula(x, y): return (y + x) % 2 == 0
            elif pattern == 1:
                def pattern_formula(x, y): return y % 2 == 0
            elif pattern == 2:
                def pattern_formula(x, y): return x % 3 == 0
            elif pattern == 3:
                def pattern_formula(x, y): return (y + x) % 3 == 0
            elif pattern == 4:
                def pattern_formula(x, y): return ((y // 2) + (x // 3)) % 2 == 0
            elif pattern == 5:
                def pattern_formula(x, y): return (y * x) % 2 + (y * x) % 3 == 0
            elif pattern == 6:
                def pattern_formula(x, y): return ((y * x) % 2 + (y * x) % 3) % 2 == 0
            elif pattern == 7:
                def pattern_formula(x, y): return ((y + x) % 2 + (y * x) % 3) % 2 == 0
            else:
                raise ValueError("Illegal mask pattern")  # technically should not be called

            # Xor the unmasked array with the pattern formula to get a masked matrix
            for x in range(self._size):
                for y in range(self._size):
                    if not is_protected(x, y):  # check coordinates aren't static pattern, if not, proceed
                        masked_array[y][x] ^= pattern_formula(x, y)
            return masked_array

        # initialize values by computing mask 0, loop for mask 1-7
        self._array = mask_pattern(0)
        self._array = self._unmasked
        lowest_score = self._calculate_mask_score(self._array)

        for mask in range(1, 8):
            masked = mask_pattern(mask)
            score = self._calculate_mask_score(masked)
            if score < lowest_score:
                lowest_score = score
                self._array = masked

    def _write_format_information(self, array: List[List[int]], mask_pattern: int):
        # Using hardcoded table since there is only a few options and computing the bits would be time consuming.
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

        info = table[self._ecl.name][mask_pattern]

        # Write the format information as described in Figure 19

        i = 0
        # left horizontal
        for x in range(9):
            if x != 6:
                array[8][x] = int(info[i])
                i += 1

        # top vertical
        for y in range(7, -1, -1):
            if y != 6:
                array[y][8] = int(info[i])
                i += 1

        i = 0
        # bottom vertical
        for y in range(self._size - 1, self._size - 8, -1):
            array[y][8] = int(info[i])
            i += 1

        # right horizontal
        for x in range(self._size - 8, self._size):
            array[8][x] = int(info[i])
            i += 1

        # dark module
        array[self._size - 8][8] = 1

    def _calculate_mask_score(self, array: List[List[int]]) -> int:
        """
        Calculates the mask score of the array

        :param array: The array to use in the calculation
        :return: The overall mask score of the array
        """

        def colored_rows() -> int:
            """
            Checks for groups of 5+ adjacent modules in rows
            """
            score = 0
            for y in range(self._size):
                x = 0
                color = array[y][x]
                current_length = 1
                x += 1
                while x < self._size:
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
            """
            Checks for groups of 5+ adjacent modules in columns
            """
            score = 0
            for x in range(self._size):
                y = 0
                color = array[y][x]
                current_length = 1
                y += 1
                while y < self._size:
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
            """
            Checks for 2x2 blocks of same color modules
            """
            score = 0
            for y in range(self._size - 1):
                for x in range(self._size - 1):
                    if array[y][x] == array[y][x + 1] == array[y + 1][x] == array[y + 1][x + 1]:
                        score += 3
            return score

        def finder_pattern() -> int:
            """
            Checks for patterns of dark:light:dark:dark:dark:light:dark (similar to finder pattern)
            """
            score = 0
            pad_before = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]
            pad_after = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]

            for row in array:
                for i in range(self._size - 11):
                    sub_row = row[i:i + 11]
                    if sub_row in [pad_before, pad_after]:
                        # pattern match
                        score += 40

            for i in range(self._size):
                col = [row[i] for row in array]
                for j in range(self._size - 11):
                    sub_col = col[j:j + 11]
                    if sub_col in [pad_before, pad_after]:
                        score += 40

            return score

        def color_proportion() -> int:
            """
            Checks if the proportion of black and white modules are near 50%
            """
            black_modules = 0
            for x in range(self._size):
                for y in range(self._size):
                    black_modules += array[y][x]

            proportion = (black_modules * 100) / (self._size ** 2)  # proportion in %

            i = 0
            while not ((50 - 5 * (i + 1)) <= proportion <= (50 + 5 * (i + 1))):
                # 0 if 45 <= x <= 55, 1 if 40 <= x <= 50, etc...
                i += 1

            return i * 10

        return colored_rows() + colored_cols() + colored_boxes() + finder_pattern() + color_proportion()

    def _generate_image(self) -> Image:
        """
        Creates a PIL image object from the _array variable
        """
        np_array = [[255 if i != 1 else 0 for i in row] for row in self._array]

        # Upscaling
        # TODO remove / implement better
        np_array = numpy.kron(np_array, numpy.ones((20, 20)))

        return Image.fromarray(np_array.astype(numpy.uint8), mode='L')

    def get_image(self) -> Image:
        """
        Returns the representation of the QR code as an image

        :return: A PIL Image object
        """
        if self._need_regen:
            self._image = self._generate_image()
        return self._image
