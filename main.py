"""
Author: Nathan Hagerdorn
Date: 6 November 2023

Main and supporting methods for the ECCS 4431 Steganography project.
"""

import cv2
from stegEncoder import StegEncoder as steve


def encodeRoutine():
    """
    Encode a secret message from a text file into a given image file.

    :return:                    Boolean. Whether the message was successfully encoded.
    """

    # Get the cover image
    cover_filename = input('Please enter the filename of the cover image (including the file extension): ')
    cover = cv2.imread(cover_filename)
    if cover is None:
        print('\nError: No such image file was found...\n')
        return False

    # Show the cover image if the user so desires
    if input('Would you like to see the cover image before encoding? Y or N: ').upper() == 'Y':
        print('Press any key to close the image...')

        # Show the image, wait for a key to be pressed, and close the image window when a key is pressed
        cv2.imshow('image', cover)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Add noise to the cover image if the user so desires
    if input('Would you like to add noise to the cover image before encoding? Y or N: ').upper() == 'Y':
        try:
            degree = int(input('Enter the degree of noise you would like to add (0-8): '))
            print('Adding noise... this will take a few seconds...')
            steve.noisify(cover, degree)

        except ValueError as e:
            print('\nError: ' + str(e) + '...\n')
            return False

    # Get the message from the message text file
    msg_filename = input('Enter the name of the file containing the message to encode: ')
    try:
        msg_file = open(msg_filename, 'r')

    except FileNotFoundError as e:
        print('\nError: '+ str(e) + '...\n')
        return False

    message = msg_file.read()

    # Get the encoding key from the user
    key_raw = input('Please enter the key you would like to use to encode the message: ')
    key = steve.keyToBinaryKey(key_raw)

    # Encode the message into the cover image
    try:
        encoded_img = steve.encode(cover, message, key=key)
    except IndexError as e:
        print('\nError: ' + str(e) + '...\n')
        return False

    # Save the encoded image
    encoded_img_filename = msg_filename.split('.')[0] + '.png'
    cv2.imwrite(encoded_img_filename, encoded_img)

    print('Coded image saved as ' + encoded_img_filename)

    # Show the encoded image
    cv2.imshow('image', encoded_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return True


def decodeRoutine():
    """
    Routine to decode a secret message from an image.

    :return:                    Boolean. Whether a message was successfully decoded.
    """

    # Get the encoded image
    image_filename = input('Please enter the filename of the coded image (including the file extension): ')
    image = cv2.imread(image_filename)

    if image is None:
        print('\nError: No such image file was found...\n')
        return False

    # Show the image if the user so desires
    if input('Would you like to see the image? Y or N: ').upper() == 'Y':
        print('Press any key to close the image...')
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Get the decoding key from the user
    key_raw = input('Please enter the key to decode the message: ')
    key = steve.keyToBinaryKey(key_raw)

    # decode will return None if no message is found in the image
    # This occurs when the key is invalid or the image is corrupted
    message = steve.decode(image, key=key)
    if message is None:
        return False

    # Print and save the secret message
    print('START OF MESSAGE\n\n' + message + '\n\nEND OF MESSAGE')

    msg_filename = input('Enter the name of the file you want the decoded message to be written to: ')
    try:
        msg_file = open(msg_filename, 'w')
        msg_file.write(message)
        print('Decoded message written to ' + msg_filename)

    except OSError as e:
        print('\nError: ' + str(e) + '...\n')

    return True


def main():
    """
    Main method to run the steganography program.

    :return:                    None
    """

    # Run the program in a loop
    while True:

        match input('Would you like to encode (E), decode (D), or quit (Q)?: ').upper():
            case 'E':
                encodeRoutine()
            case 'D':
                decodeRoutine()
            case 'Q':
                break
            case _:
                print('Invalid choice, please try again\n')


# Run main
if __name__ == '__main__':
    main()
