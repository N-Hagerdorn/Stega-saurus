import numpy as np

class StegEncoder:

    # Use a pattern that is very unlikely to occur naturally in the pixels of an image as an end flag
    # to tell the decoder when the end of the message is reached
    MESSAGE_END_FLAG = '\1\1'

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
        Convert a raw key string into a binary string for encoding and decoding data
        :param raw_key:             An ASCII key string used to generate a unique, reproducible binary key string
        :return:                    The binary key string produced by hashing the original key string
        """

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

            msg_bit = msg_binary[0]
            msg_binary = msg_binary[1:]

            # Get the next pixel from the image
            # Since pixel_idx is indexing a 2D list,
            # use integer division to find the appropriate row number and modulus to find the column number
            pixel = cover[pixel_idx // cover.shape[1], pixel_idx % cover.shape[1]]

            # Encode into only the red channel (this will eventually change to use all channels)
            pixel[2] = int(pixel[2] / 2) * 2 + int(msg_bit)

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
        symbol = ''
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

            if pixel_idx >= rows * cols:
                return None

            pixel = image[pixel_idx // image.shape[1], pixel_idx % image.shape[1]]

            message_bit = pixel[2] % 2

            symbol_binary_string += str(message_bit)

            if len(symbol_binary_string) >= CHAR_BIT_WIDTH:
                symbol_int = int(symbol_binary_string, 2)  # Convert the binary string to its base 10 integer form
                symbol = chr(symbol_int)
                symbol_binary_string = ''

                message += symbol
                if message[-2:] == StegEncoder.MESSAGE_END_FLAG:
                    break

        return message[:-len(StegEncoder.MESSAGE_END_FLAG)]

    @staticmethod
    def fuzz(image, degree):

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
