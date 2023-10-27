import cv2
from stegEncoder import StegEncoder as steve


def encodeRoutine():

    cover_filename = input('Please enter the filename of the cover image (including the file extension): ')
    cover = cv2.imread(cover_filename)

    if input('Would you like to see the cover image before encoding? Y or N: ').upper() == 'Y':
        print('Press any key to close the image...')
        cv2.imshow('image', cover)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if input('Would you like to add noise to the cover image before encoding? Y or N: ').upper() == 'Y':
        degree = int(input('Enter the degree of noise you would like to add (0-8): '))
        print('Adding noise... this will take a few seconds...')
        steve.fuzz(cover, degree)

    msg_filename = input('Enter the name of the file containing the message to encode: ')
    msg_file = open(msg_filename, 'r')
    message = msg_file.read()

    key_raw = input('Please enter the key you would like to use to encode the message: ')
    key = steve.keyToBinaryKey(key_raw)

    encoded_img = steve.encode(cover, message, key=key)
    encoded_img_filename = msg_filename.split('.')[0] + '.png'

    cv2.imwrite(encoded_img_filename, encoded_img)
    print('Coded image saved as ' + encoded_img_filename)

    cv2.imshow('image', encoded_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def decodeRoutine():

    image_filename = input('Please enter the filename of the coded image (including the file extension): ')
    image = cv2.imread(image_filename)

    if input('Would you like to see the image? Y or N: ').upper() == 'Y':
        print('Press any key to close the image...')
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    key_raw = input('Please enter the key to decode the message: ')
    key = steve.keyToBinaryKey(key_raw)

    message = steve.decode(image, key=key)

    # decode will return None if no message is found in the image
    # This occurs when the key is invalid or the image is corrupted
    if message is None:
        return False

    print('START OF MESSAGE\n\n' + message + '\n\nEND OF MESSAGE')

    msg_filename = input('Enter the name of the file you want the decoded message to be written to: ')
    msg_file = open(msg_filename, 'w')

    msg_file.write(message)
    print('Decoded message written to ' + msg_filename)


def main():

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


if __name__ == '__main__':
    main()
