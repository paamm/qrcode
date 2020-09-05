import re
from typing import List

from constants import DATA_MODE, EC_LEVEL, CCI_LENGTH, STREAM_LENGTH, NUMBER_OF_ECC, REMAINDER_BITS, EC_SHORT, EC_LONG
import rs


def optimal_data_mode(data: str) -> DATA_MODE:
    """
    Analyses a string and returns the best data mode (kanji not implemented)

    :param data: The string to analyze
    :return: Enum of the best mode to use
    """
    numeric_regex = r"^\d+$"
    alphanum_regex = r"^[A-Z0-9 $%*+\-./:]+$"

    if re.match(numeric_regex, data):
        return DATA_MODE.Numeric
    elif re.match(alphanum_regex, data):
        return DATA_MODE.Alphanumeric

    # check that we can encode in iso8859 (if not, exit program until ECI is implemented)
    try:
        data.encode("iso8859")
        return DATA_MODE.Byte
    except UnicodeEncodeError:
        print("Error: Invalid character(s) in string")
        exit(1)


def encode(data: str, mode: DATA_MODE = None) -> List[int]:
    """
    Encodes a string using a specific mode

    :param data: The string to encode
    :param mode: The mode to use. If not specified, will determine best mode based on the contents of data
    :return: A list of ints containing the converted characters from the data string
    """
    if mode is None:
        mode = optimal_data_mode(data)

    if mode == DATA_MODE.Numeric:
        return list(data)  # can just convert to list since numeric mode doesn't change digits
    elif mode == DATA_MODE.Alphanumeric:
        encoded = [0] * len(data)
        for i in range(len(data)):
            char = data[i]
            value = ord(char)
            if 48 <= value <= 57:
                # digits keep same value, convert string to int
                encoded[i] = int(char)
            elif 65 <= value <= 90:
                # letters are mapped in a way that A-Z = 10-35
                encoded[i] = value - 55
            else:
                # remaining chars with no easy mapping
                if char == " ":
                    encoded[i] = 36
                elif char == "$":
                    encoded[i] = 0
                elif char == "%":
                    encoded[i] = 38
                elif char == "*":
                    encoded[i] = 39
                elif char == "+":
                    encoded[i] = 40
                elif char == "-":
                    encoded[i] = 41
                elif char == ".":
                    encoded[i] = 42
                elif char == "/":
                    encoded[i] = 43
                elif char == ":":
                    encoded[i] = 44

        return encoded
    elif mode == DATA_MODE.Byte:
        return list(data.encode("iso8859"))


def _convert_to_binary(data: List[int], mode: DATA_MODE, version: int, ec: EC_LEVEL) -> str:
    """
    Convert encoded data to binary data with mode and character count indicators

    :param data: The encoded data formatted as a list of integers
    :param mode: The data mode to use
    :param version: The QR version to use
    :param ec: The error correction level to use
    :return: The binary data as a string
    """

    binary_data = ""

    # Group data and convert to binary
    if mode == DATA_MODE.Numeric:
        # Group data in groups of 3 digits
        for i in range(0, len(data), 3):
            group = int("".join([str(i) for i in data[i:i+3]]))  # converts the list of digits to an int
            length = len(str(group))
            if length == 3:
                # 3 digits
                binary_data += "{0:010b}".format(group)
            elif length == 2:
                # 2 digits
                binary_data += "{0:07b}".format(group)
            else:
                # 1 digits
                binary_data += "{0:04b}".format(group)
    elif mode == DATA_MODE.Alphanumeric:
        # Group data in groups of 2 chars
        for i in range(0, len(data), 2):
            group = data[i:i+2]
            if len(group) == 2:
                # normal group of 2 chars, convert from pseudo-base 45 to base 10 to binary
                number = group[0] * 45 + group[1]
                binary_data += "{0:011b}".format(number)
            else:
                # group of 1 digit, use 6-bit binary
                binary_data += "{0:06b}".format(group[0])
    elif mode == DATA_MODE.Byte:
        # Characters already in 0-255 range, just convert to 8-bit binary
        for char in data:
            binary_data += "{0:08b}".format(char)

    # add CCI
    cci = "{0:0b}".format(len(data))
    cci = "0" * (CCI_LENGTH.get(mode)[version] - len(cci)) + cci  # pad start with 0s to get required CCI length
    binary_data = cci + binary_data

    # add data mode to start of string
    binary_data = "{0:04b}".format(mode.value) + binary_data

    # add terminator byte (4 bits or less if less than 4 bits available based on version) at end of string
    # accessing specific value in dictionary by combining version and EC level (1 and "M" -> "1M")
    empty_space = STREAM_LENGTH.get(str(version) + ec.name) - len(binary_data)
    pad_length = 4 if empty_space > 4 else empty_space
    binary_data += "0" * pad_length

    # add bit-padding (fill up last codeword)
    missing = 8 - (len(binary_data) % 8)
    missing = 0 if missing == 8 else missing  # if 8 bits are "missing", already multiple of 8 so no padding needed
    binary_data += "0" * missing

    # add byte-padding (fill string up to full size)
    words = ["11101100", "00010001"]
    i = 0
    while len(binary_data) < STREAM_LENGTH.get(str(version) + ec.name):
        binary_data += words[i]
        i ^= 1  # xoring i with 1 to alternate between first and second padding word

    return binary_data


def generate_codewords(data: str, version: int, ec: EC_LEVEL) -> str:
    """
    Generates the codewords (data and EC) based on the provided arguments.

    :param data: Message to encode
    :param version: QR version
    :param ec: Error correction level
    :raise ValueError: if the data string is too long for the specified version and EC level
    :return: String of codeblocks in binary
    """

    data_mode = optimal_data_mode(data)
    encoded_data = encode(data, data_mode)
    binary_data = _convert_to_binary(encoded_data, data_mode, version, ec)

    # Check if data is too long for specified version and EC level
    max_length = STREAM_LENGTH.get(str(version) + ec.name)
    if len(binary_data) > max_length:
        raise ValueError("The message to encode is too large for the specified version and EC level.")

    # Retrieve constants for version and EC level
    ec_short = EC_SHORT.get(str(version) + ec.name)
    ec_long = EC_LONG.get(str(version) + ec.name)
    total_blocks = ec_short + ec_long

    blocks: List[str] = []
    ec_blocks: List[str] = []

    # Calculate block length
    short_length = len(binary_data) // total_blocks
    long_length = 0
    if ec_long > 0:
        # If there are long blocks, round short_length down to nearest multiply of 8 and add 1 byte to long_length
        short_length = short_length - (short_length % 8)
        long_length = short_length + 8

    # Divide the total amount of ecc codewords needed by the number of blocks to get # of ecc codewords per block
    ecc_amount = NUMBER_OF_ECC.get(str(version) + ec.name) // total_blocks

    # TODO refactor next two loops in one function in rs.py? rs.create_ecc_block()?
    for i in range(ec_short):
        # Short blocks
        # Generates the Reed-Solomon EC codewords and adds them to the ec_blocks list
        block = binary_data[short_length * i:short_length * (i + 1)]  # get sublist that is 'short_length' long
        codewords = [block[j:j+8] for j in range(0, len(block), 8)]
        msg_poly = rs.message_poly(codewords)
        gen_poly = rs.rs_generator_poly(ecc_amount)
        rs_codewords = rs.gf_polynomial_division(msg_poly, gen_poly)
        rs_codewords = ["{0:08b}".format(k) for k in rs_codewords]  # convert base10 ecc to binary
        blocks.append(block)
        ec_blocks.append("".join(rs_codewords))

    offset = ec_short * short_length  # create an offset to start reading after the data already read in short blocks
    for i in range(ec_long):
        # Long blocks
        block = binary_data[offset + long_length * i:offset + long_length * (i + 1)]
        codewords = [block[j:j + 8] for j in range(0, len(block), 8)]
        msg_poly = rs.message_poly(codewords)
        gen_poly = rs.rs_generator_poly(ecc_amount)
        rs_codewords = rs.gf_polynomial_division(msg_poly, gen_poly)
        rs_codewords = ["{0:08b}".format(k) for k in rs_codewords]  # convert base10 ecc to binary
        blocks.append(block)
        ec_blocks.append("".join(rs_codewords))

    final_stream = ""

    i = 0
    # The data from different blocks needs to be interleaved, meaning if we had 4 blocks, stream would look like:
    # A1, B1, C1, D1, A2, B2, C2, D2, ...
    while i < len(blocks[0]):  # interleave up to length of short block (first block is always short block)
        for block in blocks:
            final_stream += block[i:i+8]  # append byte, not bit
        i += 8

    # if there are long blocks, finish the interleaving using only data from long blocks
    # ie: A1, B1, C1, D1, C2, D2 if A, B are short and C, D are long
    while i < len(blocks[-1]):  # last block is either short and we don't loop, or it is long and we loop until end.
        for block in blocks[ec_short:]:  # get sublist of blocks list to only use long blocks
            final_stream += block[i:i+8]
        i += 8

    # Interleave the same way but with ECCs. Loop is simpler since EC blocks all have same length
    for i in range(0, ecc_amount * 8, 8):  # increase i by 8 to add data byte by byte instead of bit by bit
        for block in ec_blocks:
            final_stream += block[i:i+8]

    # add remainder bits if needed
    final_stream += "0" * REMAINDER_BITS[version]

    return final_stream
