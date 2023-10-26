import cv2
import numpy as np


def encode(cover, message):

    msg_binary = ''.join(format(ord(char), '08b') for char in message)

    for i in range(len(msg_binary)):
        msg_bit = msg_binary[i]
        pixel = cover[i // cover.shape[1], i % cover.shape[1]]

        pixel[2] = int(pixel[2] / 2) * 2 + int(msg_bit)

    return cover


def decode(image, msg_length):
    CHAR_BIT_WIDTH = 8

    msg_binary_length = CHAR_BIT_WIDTH * msg_length

    msg = ''
    symbol_binary_string = ''

    for i in range(msg_binary_length):

        pixel = image[i // image.shape[1], i % image.shape[1]]

        msg_bit = pixel[2] % 2

        symbol_binary_string += str(msg_bit)

        if len(symbol_binary_string) >= CHAR_BIT_WIDTH:
            symbol_int = int(symbol_binary_string, 2)            # Convert the binary string to its base 10 integer form
            symbol = chr(symbol_int)
            symbol_binary_string = ''

            print(symbol)

            msg += symbol

    return msg

def main():

    cover = cv2.imread('cover.png')
    cv2.imshow('image', cover)

    cv2.waitKey(0)

    # closing all open windows
    cv2.destroyAllWindows()

    msg_file = open("msg.txt", "r")

    message = msg_file.read()

    steven = encode(cover, message)

    cv2.imwrite('steven.png', steven)

    decoded = decode(steven, len(message))
    print(decoded)

if __name__=='__main__':
    main()
