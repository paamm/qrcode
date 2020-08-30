import re
from typing import List

from constants import DATA_MODE, EC_LEVEL, CCI_LENGTH, STREAM_LENGTH, NUMBER_OF_ECC, REMAINDER_BITS, EC_SHORT, EC_LONG
import rs


def optimal_data_mode(data: str) -> DATA_MODE:
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
                # digit
                encoded[i] = int(char)
            elif 65 <= value <= 90:
                # letter
                encoded[i] = value - 55
            else:
                # remaining chars
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
        encoded = []
        for char in data.encode("iso8859"):
            encoded.append(char)
        return encoded


def convert_to_binary(data: List[int], mode: DATA_MODE, version: int, ec: EC_LEVEL) -> str:
    binary_stream = ""
    if mode == DATA_MODE.Numeric:
        # Group data in groups of 3 digits
        for i in range(0, len(data), 3):
            group = int("".join([str(i) for i in data[i:i+3]]))  # converts the list of digits to an int
            length = len(str(group))
            if length == 3:
                # 3 digits
                binary_stream += "{0:010b}".format(group)
            elif length == 2:
                # 2 digits
                binary_stream += "{0:07b}".format(group)
            else:
                # 1 digits
                binary_stream += "{0:04b}".format(group)
    elif mode == DATA_MODE.Alphanumeric:
        # Group data in groups of 2 chars
        for i in range(0, len(data), 2):
            group = data[i:i+2]
            if len(group) == 2:
                # normal group of 2 chars, convert from pseudo-base 45 to base 10 to binary
                number = group[0] * 45 + group[1]
                binary_stream += "{0:011b}".format(number)
            else:
                # group of 1 digit, use 6-bit binary
                binary_stream += "{0:06b}".format(group[0])
    elif mode == DATA_MODE.Byte:
        # Characters already in 0-255 range, just convert to 8-bit binary
        for char in data:
            binary_stream += "{0:08b}".format(char)

    # add CCI
    cci = "{0:0b}".format(len(data))
    cci = "0" * (CCI_LENGTH.get(mode)[version] - len(cci)) + cci  # pad start with 0s to get the correct length
    binary_stream = cci + binary_stream

    # add mode
    binary_stream = "{0:04b}".format(mode.value) + binary_stream

    # add terminator byte (4 bits or less if data is already filling near the limit
    # converting 2 vars to string: ie. 1 and M to "1M"
    empty_space = STREAM_LENGTH.get(str(version) + ec.name) - len(binary_stream)
    pad_length = 4 if empty_space > 4 else empty_space
    binary_stream += "0" * pad_length

    # add bit-padding (fill up last codeword)
    missing = 8 - (len(binary_stream) % 8)
    missing = 0 if missing == 8 else missing  # if 8 bits are "missing", already multiple of 8 so no padding needed
    binary_stream += "0" * missing

    # add byte-padding (fill stream up to full size)
    words = ["11101100", "00010001"]
    i = 0
    while len(binary_stream) < STREAM_LENGTH.get(str(version) + ec.name):
        binary_stream += words[i]
        i ^= 1  # xoring i with 1 to alternate between first and second padding word

    return binary_stream


def generate_codewords(data: str, version: int, ec: EC_LEVEL) -> str:
    data_mode = optimal_data_mode(data)
    encoded_data = encode(data, data_mode)
    binary_stream = convert_to_binary(encoded_data, data_mode, version, ec)

    ec_short = EC_SHORT.get(str(version) + ec.name)
    ec_long = EC_LONG.get(str(version) + ec.name)
    total_blocks = ec_short + ec_long

    blocks: List[str] = []
    ec_blocks: List[str] = []

    short_length = len(binary_stream) // total_blocks
    long_length = 0
    if ec_long > 0:
        short_length = short_length - (short_length % 8)
        long_length = short_length + 8

    ecc_amount = NUMBER_OF_ECC.get(str(version) + ec.name) // total_blocks

    for i in range(ec_short):
        # Short blocks
        block = binary_stream[short_length * i:short_length * (i + 1)]
        codewords = [block[j:j+8] for j in range(0, len(block), 8)]
        msg_poly = rs.message_poly(codewords)
        gen_poly = rs.rs_generator_poly(ecc_amount)
        rs_codewords = rs.gf_polynomial_division(msg_poly, gen_poly)
        rs_codewords = ["{0:08b}".format(k) for k in rs_codewords]  # convert base10 ecc to binary
        blocks.append(block)
        ec_blocks.append("".join(rs_codewords))

    offset = ec_short * short_length
    for i in range(ec_long):
        # Long blocks
        block = binary_stream[offset + long_length * i:offset + long_length * (i + 1)]
        codewords = [block[j:j + 8] for j in range(0, len(block), 8)]
        msg_poly = rs.message_poly(codewords)
        gen_poly = rs.rs_generator_poly(ecc_amount)
        rs_codewords = rs.gf_polynomial_division(msg_poly, gen_poly)
        rs_codewords = ["{0:08b}".format(k) for k in rs_codewords]  # convert base10 ecc to binary
        blocks.append(block)
        ec_blocks.append("".join(rs_codewords))

    final_stream = ""

    i = 0
    while i < len(blocks[0]):  # interleave the different blocks
        for block in blocks:
            final_stream += block[i:i+8]
        i += 8

    # add the remaining bits from the long blocks
    while i < len(blocks[-1]):
        for block in blocks[ec_short:]:  # only loop through long blocks
            final_stream += block[i:i+8]
        i += 8

    # add ec bits
    for i in range(0, ecc_amount * 8, 8):
        for block in ec_blocks:
            final_stream += block[i:i+8]

    # add remainder bits if needed to have enough bits to write to every module
    final_stream += "0" * REMAINDER_BITS[version]

    return final_stream

