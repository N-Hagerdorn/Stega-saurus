import numpy as np


class StegEncoder:
    """
    StegEncoder class

    A set of methods to perform steganography - encoding a concealed message into an image to avoid detection.
    Performs encoding, decoding, key generation, and other necessary actions for steganography.
    """

    # Use a pattern that is very unlikely to occur naturally in the pixels of an image as an end flag
    # to tell the decoder when the end of the message is reached
    MESSAGE_END_FLAG = '\0END'

    @staticmethod
    def stringToBinary(ascii_string):
        """
        Convert an ASCII string into a corresponding binary string.

        :param ascii_string:        A string of ASCII characters
        :return:                    A binary string consisting of th ASCII codes of the input string's characters
        """

        return ''.join(format(ord(char), '08b') for char in ascii_string)

    @staticmethod
    def keyToBinaryKey(raw_key):
        """
        Convert a raw key string into a binary string for encoding and decoding data.

        :param raw_key:             An ASCII key string used to generate a unique, reproducible binary key string
        :return:                    The binary key string produced by hashing the original key string
        """

        # hash method produces a fixed-length output from which to generate the key string
        # The output of the hash is numeric, so it can be turned into an ASCII string and then
        # converted to binary without risk of invalid (UNICODE) symbols
        return StegEncoder.stringToBinary(str(hash(raw_key)))

    @staticmethod
    def encode(cover, message, key='10'):
        """
        Encode a plaintext message into a cover image using a binary key.

        :param cover:               The cover image into which the message will be encoded
        :param message:             An ASCII string to encode into the cover image
        :param key:                 A binary key string which defines the pattern of pixels to be encoded into
        :return:                    The cover image with the message encoded into it
        """

        msg_binary = StegEncoder.stringToBinary(message + StegEncoder.MESSAGE_END_FLAG)

        # Calculate the number of elements (monochrome pixels) in the cover image
        img_dims = cover.shape
        img_element_count = np.prod(img_dims)

        # Calculate the number of elements needed to encode the binary message using the given key
        key_space_efficiency = key.count('1') / len(key)
        needed_space = len(msg_binary) / key_space_efficiency

        # If there isn't enough space in the cover image, don't even try to encode the message
        if needed_space > img_element_count:
            raise IndexError('Cover image is not large enough to store the message with this key')

        key_idx = -1
        pixel_idx = -1
        while len(msg_binary) > 0:
            pixel_idx += 1
            key_idx += 1

            # If the end of the key is reached,
            # start again at the beginning to create the illusion of an infinite keystream
            if key_idx >= len(key):
                key_idx = 0

            # When the key is 0, do not encode into the current pixel
            if key[key_idx] == '0':
                continue

            # Get the next 3 bits of the message, or as many as there are left if there are fewer than 3
            msg_bits = msg_binary

            NUM_COLOR_CHANNELS = 3
            if len(msg_binary) > NUM_COLOR_CHANNELS:
                msg_bits = msg_binary[0:NUM_COLOR_CHANNELS]
                msg_binary = msg_binary[NUM_COLOR_CHANNELS:]
            else:
                msg_binary = ''

            # Get the next pixel from the image
            # Since pixel_idx is indexing a 2D list,
            # use integer division to find the appropriate row number and modulus to find the column number
            pixel = cover[pixel_idx // cover.shape[1], pixel_idx % cover.shape[1]]

            # Encode into each channel of the pixel
            for channel_idx in range(len(msg_bits)):
                pixel[channel_idx] = int(pixel[channel_idx] / 2) * 2 + int(msg_bits[channel_idx])

        return cover

    @staticmethod
    def decode(image, key='10'):
        """
        Decode a plaintext message from an encoded image using a binary key.

        :param image:               The image in which the message is encoded
        :param key:                 The binary key which defines the pattern of pixels which contain the message
        :return:                    The plaintext message that was encoded in the image
        """

        CHAR_BIT_WIDTH = 8          # Using ASCII characters, which are 8-bit

        symbol_binary_string = ''
        message = ''

        rows, cols, channels = image.shape

        key_idx = -1
        pixel_idx = -1

        while True:
            pixel_idx += 1
            key_idx += 1

            # If the end of the key is reached,
            # start again at the beginning to create the illusion of an infinite keystream
            if key_idx >= len(key):
                key_idx = 0

            # When the key is 0, the corresponding pixel has no data, so skip it
            if key[key_idx] == '0':
                continue

            # If the end of the image is reached before breaking out of the loop,
            # there is no message to be decoded with the given key
            if pixel_idx >= rows * cols:
                return None

            pixel = image[pixel_idx // image.shape[1], pixel_idx % image.shape[1]]

            # Get the least significant bits of each color channel of the pixel
            message_bits = [0, 0, 0]
            for channel_idx in range(len(pixel)):
                message_bits[channel_idx] = pixel[channel_idx] % 2

            symbol_binary_string += ''.join(str(bit) for bit in message_bits)

            # Once enough bits have been collected to make a character, process them into a character
            if len(symbol_binary_string) >= CHAR_BIT_WIDTH:

                # Process the first 8 bits in the binary string and save any excess for the next symbol
                excess_bits = ''
                if len(symbol_binary_string) > CHAR_BIT_WIDTH:
                    excess_bits = symbol_binary_string[CHAR_BIT_WIDTH:]
                symbol_int = int(symbol_binary_string[0:CHAR_BIT_WIDTH], 2)  # Convert the binary string to its base 10 integer form
                symbol_binary_string = excess_bits
                message += chr(symbol_int)

                if message.endswith(StegEncoder.MESSAGE_END_FLAG):
                    break

        return message[:-len(StegEncoder.MESSAGE_END_FLAG)]

    @staticmethod
    def noisify(image, degree):
        """
        Add background noise to an image to help conceal a hidden message.

        :param image:               The image to which noise will be added
        :param degree:              The degree of noise to add to the image
        :return:                    The noisified image
        """

        # Degree indicates the number of bits of the 8-bit pixel to randomize, so it must be in the range [0, 8]
        if degree < 0:
            degree = 0
        if degree > 8:
            degree = 8

        # Since the randomization is applied to the least significant n bits, it is helpful to know 2^n
        val = pow(2, degree)

        rows, cols, channels = image.shape

        for row in image:

            # Make enough random numbers for each channel of each pixel in the row
            rns = list(np.random.randint(low=0, high=val - 1, size=cols * channels))
            rand_idx = 0

            for pixel in row:
                for channel_idx in range(len(pixel)):

                    # Integer division and re-multiplication results in rounding off the least significant bits
                    # Add back a random amount to introduce noise into the least significant bits
                    pixel[channel_idx] = (pixel[channel_idx] // val) * val + rns[rand_idx]
                    rand_idx += 1

        return image
