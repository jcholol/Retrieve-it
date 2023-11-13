# ImageViewer.py
# Program to start evaluating an image in python
from operator import truediv
from tkinter import *
from tkinter import Tk, Frame, Checkbutton, BooleanVar
import math
import os
from turtle import clear
from PixInfo import PixInfo
from PIL import Image, ImageTk
from statistics import stdev
from copy import deepcopy
import numpy

# Main app.


class ImageViewer(Frame):

    # Constructor.
    def __init__(self, master, pixInfo):

        Frame.__init__(self, master)
        self.master = master
        self.pixInfo = pixInfo
        self.resultWin = None

        self.colorCode = pixInfo.get_colorCode()
        self.intenCode = pixInfo.get_intenCode()
        self.relevanceFb = []
        ccCopy = deepcopy(self.colorCode)
        intCopy = deepcopy(self.intenCode)
        for i in range(100):
            temp = []
            ccSize = ccCopy[i].pop(0)
            intenSize = intCopy[i].pop(0)
            temp.append(ccSize)
            temp += intCopy[i] + ccCopy[i]
            self.relevanceFb.append(temp)
        # print("hello: ", self.relevanceFb)
        self.normalizedFB = []
        self.ccDistance = []
        self.intenDistance = []
        self.sortedTup = []
        self.total_pages = 0
        self.current_page = 0
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()
        self.currentMethod = ""
        self.relevanceQuery = set()

        # Create Main frame.
        mainFrame = Frame(master)
        mainFrame.pack()

        # Create Picture chooser frame.
        listFrame = Frame(mainFrame)
        listFrame.pack(side=LEFT)

        # Create Control frame.
        controlFrame = Frame(mainFrame)
        controlFrame.pack(side=RIGHT)

        # Create Preview frame.
        previewFrame = Frame(mainFrame,
                             width=self.xmax+45, height=self.ymax)
        previewFrame.pack_propagate(0)
        previewFrame.pack(side=RIGHT)

        # Create Search Frame at the top.
        searchFrame = Frame(mainFrame)
        searchFrame.pack(side=TOP, fill=X)

        search_label = Label(listFrame, text="Search:")
        search_label.pack(side=TOP, anchor="nw")

        # Create Results frame.
        self.resultsFrame = Frame(self.resultWin)
        self.resultsFrame.pack(side=BOTTOM)

        self.canvas = Canvas(self.resultsFrame, bg='black',
                             width=self.xmax * 4, height=(self.ymax + 20) * 5)
        self.canvas.pack()

        # Create Page Label
        self.page_label = Label(self.resultsFrame, text="No Image Loaded")
        self.page_label.pack(side=BOTTOM)

        # Create the search entry and bind a function to handle search
        self.search_entry = Entry(listFrame)
        self.search_entry.pack(side=TOP, fill=X)
        self.search_entry.bind("<KeyRelease>", self.highlight_searched_item)

        self.b1 = Button(controlFrame, text="Color-Code Method",
                         padx=10, width=20,
                         command=lambda: self.find_distance(method='CC'))
        self.b1.grid(row=1, sticky=E)

        b2 = Button(controlFrame, text="Intensity Method",
                    padx=10, width=20,
                    command=lambda: self.find_distance(method='inten'))
        b2.grid(row=2, sticky=E)
        b3 = Button(controlFrame, text="Intensity + ColorCode w/ RF",
                    padx=10, width=20,
                    command=lambda: self.find_distance(method='RF'))
        b3.grid(row=3, sticky=E)

        b3 = Button(controlFrame, text="RFQuery",
                    padx=5, width=5,
                    command=lambda: self.find_distance(method='NF'))
        b3.grid(row=4, sticky=E)

        self.image_relevance = [BooleanVar() for _ in self.imageList]

        # Create Prev, Next, and Reset Buttons
        self.prev_button = Button(
            self.resultsFrame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=LEFT, padx=50)

        self.reset_button = Button(
            self.resultsFrame,
            text="Reset Image", command=self.reset_page)
        self.reset_button.pack(side=LEFT, padx=20)

        self.next_button = Button(
            self.resultsFrame, text="Next", command=self.next_page)
        self.next_button.pack(side=RIGHT, padx=20)

        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(listFrame,
                            yscrollcommand=self.listScrollbar.set,
                            selectmode=BROWSE,
                            bg="black",
                            height=10)
        for i in range(len(self.imageList)):
            name = self.imageList[i].filename.replace("images/", "")
            self.list.insert(i, name)
        self.list.pack(side=TOP, fill=BOTH)
        self.list.activate(0)
        self.list.bind('<<ListboxSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.list.yview)

        # Layout Preview.
        self.selectImg = Label(previewFrame,
                               image=self.photoList[0])
        self.selectImg.pack(side="top", fill="both", expand=True)

        # Create the relevance feedback button

        self.create_main_frame()

    def highlight_searched_item(self, event):
        search_term = self.search_entry.get().lower()
        for i in range(self.list.size()):
            item = self.list.get(i).lower()
            if search_term and search_term in item:
                self.list.itemconfig(i, {'bg': 'blue'})
                self.list.see(i)
            else:
                self.list.itemconfig(i, {'bg': 'black'})

    def update_page_label(self):
        self.page_label.config(
            text="Page: " + str(self.current_page + 1) + "/" + str(self.total_pages))

    # Create the main frame with Picture Listbox and Control Frame
    def create_main_frame(self):
        self.canvas.delete(ALL)
        mainFrame = Frame(self.master)
        mainFrame.pack()
    # Handle the "Color-Code" button click

    def update_preview(self, event):
        i = self.list.curselection()[0]
        self.selectImg.configure(
            image=self.photoList[int(i)])

    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses the comparison method of the passed
    # binList
    def find_distance(self, method):
        self.ccDistance = []
        self.intenDistance = []
        self.rFDistance = []
        self.nFDistance = []
        selectedPhotoIndex = self.list.curselection()[0]

        if method == "CC":
            self.relevanceQuery = set()
            self.currentMethod = "CC"
            # print("colorC: ", self.colorCode)
            aPixelSize = self.colorCode[selectedPhotoIndex][0]

            for i in range(100):
                distance = 0
                for j in range(65):
                    bPixelSize = self.colorCode[i][0]
                    distance += abs((self.colorCode[selectedPhotoIndex][j] / aPixelSize) -
                                    (self.colorCode[i][j] / bPixelSize))
                self.ccDistance.append([distance, i])
            # print(self.ccDistance)
            self.ccDistance = sorted(self.ccDistance)
            updateResults = []
            for val, i in self.ccDistance:
                updateResults.append(
                    (self.imageList[i].filename, self.photoList[i], i))
            self.update_results(updateResults)
            self.update_page_label()
        elif method == "inten":
            self.relevanceQuery = set()
            self.currentMethod = "inten"
            # find the distance between A and B 100 images
            aPixelSize = self.intenCode[selectedPhotoIndex][0]
            for i in range(100):
                distance = 0
                for j in range(26):
                    bPixelSize = self.intenCode[i][0]
                    distance += abs((self.intenCode[selectedPhotoIndex][j] / aPixelSize) -
                                    (self.intenCode[i][j] / bPixelSize))
                self.intenDistance.append([distance, i])
            self.intenDistance = sorted(self.intenDistance)
            updateResults = []
            for val, i in self.intenDistance:
                updateResults.append(
                    (self.imageList[i].filename, self.photoList[i], i))
            self.update_results(updateResults)
            self.update_page_label()
        elif method == "RF":
            # initial query, no updated weights
            self.relevanceQuery = set()
            self.currentMethod = "RF"
            orgFeature = []
            for i in range(100):
                rows = []
                aPixelSize = self.relevanceFb[i][0]
                for j in range(90):
                    temp = self.relevanceFb[i][j] / aPixelSize
                    temp = round(temp, 9)
                    rows.append(temp)
                orgFeature.append(rows)
            avg = []
            std = []
            for i in range(90):
                columns = []
                for j in range(100):
                    columns.append(orgFeature[j][i])

                std.append(round(stdev(columns), 9))
                avg.append(round(sum(columns) / len(columns), 9))

            weight = [1/89] * 90
            for i in range(100):
                rows = []
                for j in range(90):
                    tempSTD = std[j]
                    minimum = max(std)
                    if tempSTD == 0.0:
                        rows.append(0)
                        continue
                    rows.append(
                        round(((orgFeature[i][j] - avg[j]) / tempSTD), 9))
                self.normalizedFB.append(rows)
            
            aPixelSize = self.relevanceFb[selectedPhotoIndex][0]
            for i in range(100):
                distance = 0.0
                for j in range(90):
                    bPixelSize = self.relevanceFb[i][0]
                    distance += weight[j] * abs((self.normalizedFB[selectedPhotoIndex][j] / aPixelSize) -
                                                (self.normalizedFB[i][j] / bPixelSize))
                self.rFDistance.append([distance, i])
            self.rFDistance = sorted(self.rFDistance)
            # print(self.rFDistance)
            updateResults = []
            for val, i in self.rFDistance:
                updateResults.append(
                    (self.imageList[i].filename, self.photoList[i], i))
            self.update_results(updateResults)
            self.update_page_label()
        elif method == "NF":
            self.currentMethod = "RF"
            aPixelSize = self.relevanceFb[selectedPhotoIndex][0]
            queryNorm = []
            for i in self.relevanceQuery:
                queryNorm.append(self.normalizedFB[i])

            avg = []
            std = []
            # find avg and stdev of new query
            for i in range(90):
                columns = []
                for j in range(len(queryNorm)):
                    columns.append(queryNorm[j][i])
                std.append(round(stdev(columns), 9))
                avg.append(round(sum(columns) / len(columns), 9))

            weight = [0.0] * 90
            # find std edge case and weight
            for i in range(len(std)):
                minimum = max(std)
                if std[i] == 0.0:
                    if avg[i] == 0.0:
                        continue
                    for j in range(len(std)):
                        if std[j] != 0:
                            minimum = min(minimum, std[j])
                    std[i] = 0.5 * minimum
                weight[i] = round((1 / std[i]), 9)

            weightSum = round(sum(weight), 9)

            normalizedWeight = []
            for i in range(len(weight)):
                normWeight = weight[i] / weightSum
                normalizedWeight.append(round(normWeight, 9))

            aPixelSize = self.relevanceFb[selectedPhotoIndex][0]
            for i in range(100):
                distance = 0.0
                for j in range(90):
                    bPixelSize = self.relevanceFb[i][0]
                    distance += weight[j] * abs((self.normalizedFB[selectedPhotoIndex][j] / aPixelSize) -
                                                (self.normalizedFB[i][j] / bPixelSize))
                self.nFDistance.append([distance, i])

            self.nFDistance = sorted(self.nFDistance)

            updateResults = []
            for val, i in self.nFDistance:
                updateResults.append(
                    (self.imageList[i].filename, self.photoList[i], i))
            self.update_results(updateResults)
            self.update_page_label()
            # Create the results based on the sorted Distance

    def update_results(self, sortedTup):
        self.sortedTup = sortedTup
        cols = 4
        rows = 5
        items_per_page = cols * rows
        self.total_pages = math.ceil(len(sortedTup) / items_per_page)

        # Calculate the current page based on class attribute
        current_page = self.current_page

        # Calculate the range of items to display on the current page
        start_index = current_page * items_per_page
        end_index = (current_page + 1) * items_per_page

        # Initialize the canvas
        self.canvas.delete(ALL)
        self.canvas.config(
            bg='black',
            width=self.xmax * cols,
            height=(self.ymax + 20) * rows,
            scrollregion=(0, 0, self.xmax * cols, (self.ymax + 20) * rows)
        )
        self.canvas.pack()

        photoRemain = sortedTup[start_index:end_index]

        rowPos = 0
        colPos = 0

        margin = 10

        for (filename, img, i) in photoRemain:
            # Open the image using Image.open
            img = Image.open(filename)

            # Calculate the aspect-ratio-preserving dimensions to fit within the squares
            target_width = self.xmax - 2 * margin
            target_height = self.ymax - 2 * margin
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height

            if aspect_ratio > 1:
                # Landscape image
                target_height = int(target_width / aspect_ratio) + 15
            else:
                # Portrait or square image
                target_width = int(target_height * aspect_ratio)

            img = img.resize((target_width, target_height), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            link = Label(self.canvas, text=filename, image=img,
                         height=self.xmax, width=self.ymax, borderwidth=2, relief="solid")
            link.image = img
            link.pack(side=LEFT, expand=YES)
            # def handler(f=filename): return self.inspect_pic(f)
            # link.config(command=handler)
            if self.currentMethod == "RF":
                self.canvas.create_window(
                    colPos,
                    rowPos,
                    anchor=NW,
                    window=link,
                    width=self.xmax,
                    height=self.ymax
                )
                # Create a label for the text with a transparent background
                name = filename.replace("images/", "")
                label = Label(self.canvas, text=name, font=(
                    "Helvetica", 9), fg="black", bg='white')
                label.place(x=colPos + self.xmax // 2, y=rowPos +
                            self.ymax - 8, anchor="center")

                checkVar = BooleanVar()
                toggle = Checkbutton(
                    self.canvas, text="Relevant", variable=checkVar, command=lambda i=i: self.relevance_pic(i))
                toggle.configure(font=(
                    "Helvetica", 9))
                toggle.place(x=colPos + self.xmax // 2, y=rowPos +
                             self.ymax + 13, anchor="center")
            else:
                self.canvas.create_window(
                    colPos,
                    rowPos,
                    anchor=NW,
                    window=link,
                    width=self.xmax,
                    height=self.ymax + 20
                )
                # Create a label for the text with a transparent background
                name = filename.replace("images/", "")
                label = Label(self.canvas, text=name, font=(
                    "Helvetica", 9), fg="black", bg='white')
                label.place(x=colPos + self.xmax / 2, y=rowPos +
                            self.ymax + 10, anchor="center")
            colPos += self.xmax
            if colPos >= self.xmax * cols:
                colPos = 0
                rowPos += self.ymax + 20
        self.current_page = current_page

    # Define the previous, next, reset page functions
    def prev_page(self):
        if self.sortedTup:
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = 0
            self.update_results(self.sortedTup)
            self.update_page_label()

    def next_page(self):
        if self.sortedTup:
            self.current_page += 1
            if self.current_page >= self.total_pages:
                self.current_page = self.total_pages - 1
            self.update_results(self.sortedTup)
            self.update_page_label()

    def reset_page(self):
        self.canvas.delete(ALL)
        self.page_label.config(text="No Images Loaded")
        self.sortedTup = []
        for widget in self.canvas.winfo_children():
            widget.destroy()

    # Open the picture with the default operating system image
    # viewer.
    def inspect_pic(self, filename):
        command = str('open ' + os.getcwd() + '/' + filename)
        os.system(command)

    def relevance_pic(self, index):
        # print("index: ", index)
        self.relevanceQuery.add(index)


if __name__ == '__main__':
    root = Tk()
    root.title('Image Analysis Tool')

    window_width = 800
    window_height = root.winfo_screenheight()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    pixInfo = PixInfo(root)
    imageViewer = ImageViewer(root, pixInfo)
    app = Frame(root)
    app.pack()

    root.mainloop()
