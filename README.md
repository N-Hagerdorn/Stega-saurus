# Stega-saurus
Simple steganography project for ECCS 4431 - Theory of Computation

Run main.py in the terminal or IDE of your choice and follow the prompts in the terminal.

If it appears that the program has halted, check if a new window has opened to show an image.
These windows sometimes open in a minimized state or behind the terminal window, and the program will not continue until the image window is closed.

The file msg.png is encoded with the message contained in msg.txt using the key 0
It can be decoded by choosing the decode option, entering "msg.png" for the file name, and entering "0" for the key.

When encoding, there is an option to add noise to the image. This is to account for low-noise image backgrounds like the white background of cover.png
Adding noise is a WIP feature and takes a long time for images as large as cover.png. Please be patient when using it.

"smallcover.png" exists to demonstrate what happens when one attempts to encode a message that is too long into a small cover file (an error message is printed)
