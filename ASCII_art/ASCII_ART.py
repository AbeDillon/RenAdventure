import sys
import string
import time
from PIL import Image, ImageChops, ImageOps, ImageStat


class AAGenerator():
    """
    an object that generates ASCII art versions of images
    """

    def __init__(self, width=52, height=26, font="WINCMD10x20", grayWeight=0.2):
        """

        """
        self.textWidth = width
        self.textHeight = height
        self.font = font
        self.rasterFont = Image.open(self.font + ".png")
        self.printableChars = string.printable[:-5]
        self.charWidth = self.rasterFont.size[0]/len(self.printableChars)
        self.charHeight = self.rasterFont.size[1]
        self.grayWeight = grayWeight
        self.charImages = self.getCharImages()



    def getCharImages(self):
        """
        constructs a dictionary with keys = printable character, vals = raster image of that character
        """

        maxWhite = 0

        charImages = {}
        for i, char in enumerate(self.printableChars):
            minX = i*self.charWidth
            minY = 0
            maxX = minX + self.charWidth
            maxY = self.charHeight
            charImage = self.rasterFont.crop((minX, minY, maxX, maxY))
            charImage = charImage.convert("L")
            stat = ImageStat.Stat(charImage)
            grayVal = stat.mean[0]
            if grayVal > maxWhite:
                maxWhite = grayVal
            charImages[char] = charImage.convert("L")

        for char, charImage in charImages.iteritems():

            stat = ImageStat.Stat(charImage)
            grayVal = stat.mean[0]/maxWhite * 255

            blackVal = int(grayVal * self.grayWeight)
            blackImage = ImageChops.constant(charImage, blackVal)

            whiteVal = int(grayVal + (255 - grayVal)*(1.0 - self.grayWeight))
            whiteImage = ImageChops.constant(charImage, whiteVal)

            charImage = ImageChops.lighter(charImage, blackImage)
            charImage = ImageChops.darker(charImage, whiteImage)

            charImages[char] = charImage

        return charImages

    def prepImage(self):
        """

        """
        # Resize
        W = self.charWidth * self.textWidth
        H = self.charHeight * self.textHeight
        self.image = ImageOps.fit(self.image, (W, H), Image.BICUBIC, 0, (0.5, 0.5))

        # convert to B&W
        self.image = self.image.convert("L")

        # Invert
        #self.image = ImageOps.invert(self.image)

        # Correct contrast
        self.image = ImageOps.autocontrast(self.image)
        #self.image = ImageOps.equalize(self.image)
        # Highlight edges
        #self.hilightEdges()
        #self.image = ImageOps.equalize(self.image)

        #self.image.show()

    def hilightEdges(self):
        """

        """
        img = self.image.copy()
        img = ImageOps.equalize(img)
        xneg = ImageChops.difference(img, img.offset(-1,0))
        xpos = ImageChops.difference(img, img.offset(1,0))
        yneg = ImageChops.difference(img, img.offset(0,-1))
        ypos = ImageChops.difference(img, img.offset(0,1))
        xmax = ImageChops.lighter(xneg, xpos)
        ymax = ImageChops.lighter(yneg, ypos)
        xymax = ImageChops.lighter(xmax,ymax)

        xymax.show()
        xymax = ImageOps.autocontrast(xymax)
        xymax.show()
        xymax = ImageOps.posterize(xymax, 3)
        xymax = ImageOps.equalize(xymax)
        xymax.show()
        xymax = ImageOps.posterize(xymax, 2)
        xymax.show()
        self.image.show()
        self.image = ImageChops.screen(self.image, xymax)
        self.image.show()


    def render(self, image):
        """

        """
        if type(image) == type(str()):
            image = Image.open(image)
        self.image = image.copy()
        self.prepImage()

        outText = [["" for c in range(self.textWidth)] for l in range(self.textHeight)]
        for j in range(self.textHeight):
            for i in range(self.textWidth):
                char = self.charMatch(i,j)
                outText[j][i] = char

            outText[j] = "".join(outText[j])

        outText = "\n".join(outText)

        return outText


    def charMatch(self, i, j):
        """

        """
        minX = i*self.charWidth
        minY = j*self.charHeight
        maxX = minX + self.charWidth
        maxY = minY + self.charHeight

        imageSection = self.image.crop((minX,minY,maxX,maxY))
        mindiff = 256

        bestChar = None

        for char, img in self.charImages.iteritems():

            diff = ImageChops.difference(imageSection, img)
            stat = ImageStat.Stat(diff)
            if stat.mean[0] < mindiff:
                mindiff = stat.mean[0]
                bestChar = char

        return bestChar

def main(filenames):
    """

    """
    ag = AAGenerator()
    for name in filenames:

        t = time.time()
        print ag.render(name) + "\n"
        print str(time.time() - t)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        filenames = ["Ackbar.jpeg", "KW.png", "Lilwayne.jpg", "FM.jpg", "Troll.jpg"]
    main(filenames)