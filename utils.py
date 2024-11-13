import drawsvg as dw
import pybrl as brl
from PIL import ImageFont
import math


def textToBraille(s):
    return brl.toUnicodeSymbols(brl.translate(s), flatten=True)

def mmToPx(mm, dpi):
    return mm*dpi/25.4

def textToSVG(s, mirror=False):
    fontSize = 24
    margins = 20
    dpi = 96
    paperSizes = {
        "A4": (210, 297), #In mm
        "A3": (297, 420),

        "B4": (250, 353),
        "B5": (176, 250)
    }
    width = mmToPx(paperSizes["A4"][0],dpi)
    height = mmToPx(paperSizes["A4"][1],dpi)
    font = ImageFont.truetype("cour.ttf", fontSize)
    charLen = font.getlength("⠻")
    charsPerLine = math.floor((width-margins)/charLen)-1
    s=s.replace("\n"," ")

    news = ""
    while (len(s)>charsPerLine):
        index = s.rfind(" ", 0, charsPerLine)
        news+=s[0:index]+"\n"
        s = s[index+1:]
    s=news
    print(s)


    d = dw.Drawing(width, height, origin=(0,0), font_family="Courier New") #Switch this to monospace if possible! May not matter, but online viewers are being strange.

    d.append(dw.Text(s, font_size=fontSize, x=margins, y=60))
    d.save_svg("test.svg")

if __name__ == "__main__":
    #print(brl.toUnicodeSymbols(brl.translate(input("Enter: ")), flatten=True))
    textToSVG("Lorem ipsum odor amet, consectetuer adipiscing elit. Mauris himenaeos varius tincidunt quam vehicula. Facilisis placerat dictumst dictum mollis nisl dictum accumsan. Augue vulputate porttitor est porta, blandit tempor nullam felis. Diam sem dictumst placerat ornare efficitur. Sociosqu mattis nec placerat erat dignissim leo velit nisi. Maecenas arcu vitae netus, iaculis inceptos consequat. Torquent lacus enim volutpat fusce vel facilisis malesuada diam. Platea rhoncus dapibus luctus montes, sapien nostra enim. Malesuada ex laoreet dignissim facilisi venenatis per morbi primis.")