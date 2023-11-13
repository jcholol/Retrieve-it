# PixInfo.py
# Program to start evaluating an image in python

from code import interact
from PIL import Image, ImageTk
import glob
import os
import math


# Pixel Info class.
class PixInfo:

    # Constructor.
    def __init__(self, master):

        self.master = master
        self.imageList = []
        self.photoList = []
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []

        # Add each image (for evaluation) into a list,
        # and a Photo from the image (for the GUI) in a list.
        for infile in glob.glob('images/*.jpg'):

            file, ext = os.path.splitext(infile)
            im = Image.open(infile)

            # Resize the image for thumbnails.
            imSize = im.size
            x = int(imSize[0]/3.2)
            y = int(imSize[1]/3.2)
            imResize = im.resize((x, y), Image.LANCZOS)
            photo = ImageTk.PhotoImage(imResize)

            # Find the max height and width of the set of pics.
            if x > self.xmax:
                self.xmax = x
            if y > self.ymax:
                self.ymax = y

            # Add the images to the lists.
            self.imageList.append(im)
            self.photoList.append(photo)

        # Create a list of pixel data for each image and add it
        # to a list.
        for im in self.imageList[:]:

            pixList = list(im.getdata())
            CcBins, InBins = self.encode(pixList)
            self.colorCode.append(CcBins)
            self.intenCode.append(InBins)

    # Bin function returns an array of bins for each
    # image, both Intensity and Color-Code methods.

    def encode(self, pixlist):

        # 2D array initilazation for bins, initialized
        # to zero.
        CcBins = [0]*65
        InBins = [0]*26
        InBins[0] = len(pixlist)
        CcBins[0] = len(pixlist)

        intensity = 0
        for i in range(len(pixlist)):
            j = 0
            r = pixlist[i][j]
            g = pixlist[i][j + 1]
            b = pixlist[i][j + 2]
            intensity = (0.299 * r) + (0.587 * g) + (0.114 * b)
            hIndex = int((intensity // 10) + 1)
            if hIndex == 26:
                InBins[hIndex - 1] += 1
            else:
                InBins[hIndex] += 1

            ccR = format(r, '08b')[:2]
            ccG = format(g, '08b')[:2]
            ccB = format(b, '08b')[:2]
            colorCode = ccR + ccG + ccB
            # print("ColorCode :", colorCode)
            decimal = int(colorCode, 2)
            # print("Decimal :", decimal)
            CcBins[decimal + 1] += 1

        # Return the list of binary digits, one digit for each
        # pixel.
        return CcBins, InBins

    # Accessor functions:

    def get_imageList(self):
        return self.imageList

    def get_photoList(self):
        return self.photoList

    def get_xmax(self):
        return self.xmax

    def get_ymax(self):
        return self.ymax

    def get_colorCode(self):
        return self.colorCode

    def get_intenCode(self):
        return self.intenCode
