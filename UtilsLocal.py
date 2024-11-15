import drawsvg as dw
import pybrl as brl
from PIL import ImageFont, Image, ImageDraw


def textToBraille(s):
    return brl.toUnicodeSymbols(brl.translate(s), flatten=True)

def mmToPx(mm, dpi):
    return mm*dpi/25.4

def textToSVG(s, mirror=False):
    fontName = "bin/cour.ttf"

    fontFile = open("bin/courText.txt")
    s64 = fontFile.read()
    fontFile.close()
    style = """
    @font-face {
        font-family: courCustom;
        src: url("""+s64+""")
    }
    """
    
    fontSize = 24
    dpi = 96
    margins = mmToPx(15, dpi)
    rightMarginBonus = 0 # Depending on the svg viewer/conversions/other nonsense, the auto text wrapping may break down. Change this to tune the margins!
    charSizeBonus = 1.1 # same purpose as above: increase predicted size of characters by this factor
    paperSizes = {
        "A4": (210, 297), # In mm
        "A3": (297, 420),

        "B4": (250, 353),
        "B5": (176, 250)
    }
    width = mmToPx(paperSizes["A4"][0],dpi)
    height = mmToPx(paperSizes["A4"][1],dpi)
    font = ImageFont.truetype(fontName, fontSize)
    charLen = font.getlength("⠻")*charSizeBonus

    """
    #bounding box testing (This works for real! just need to physically draw the line to check its size)
    image = Image.new("RGBA", (1000, 200), (255, 255, 255, 0))
    render = ImageDraw.Draw(image)
    render.text((0, 0), "⠻⠻", font=font, fill="black")
    testbb1 = image.getbbox()
    print("⠻: "+str(testbb1[2]-testbb1[0]))

    image = Image.new("RGBA", (1000, 200), (255, 255, 255, 0))
    render = ImageDraw.Draw(image)
    render.text((0, 0), "ww", font=font, fill="black")
    testbb1 = image.getbbox()
    print("w: "+str(testbb1[2]-testbb1[0]))
    """


    """
    # Cairo Testing 1
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
    context = cairo.Context(surface)

    # Set the font face and size
    context.select_font_face("Courier New")
    context.set_font_size(fontSize)

    # Measure the text width and height
    (_, _, width2, _, _, _) = context.text_extents("abcde")

    print(f"Text width: {width2}")
    """

    """
    # line length by character length
    charsPerLine = math.floor((width-(margins*2)-rightMarginBonus)/charLen)
    s=s.replace("\n"," ")

    news = ""
    while (len(s)>charsPerLine):
        index = s.rfind(" ", 0, charsPerLine)
        news+=s[0:index]+"\n"
        s = s[index+1:]
    s=news
    print(s)
    """
    s=s.strip()
    s=s.replace("\n"," ") # Current issues: does not preserve newlines, super long words will not wrap
    news = ""
    while s:
        line = ""
        while True:
            index = s.find(" ")
            if index == -1:
                line+=s
                s = ""
                break
            newline = line+s[:index+1]

            image = Image.new("RGBA", (int(width), int(height)), (255, 255, 255, 0))
            render = ImageDraw.Draw(image)
            render.text((0, 0), newline, font=font, fill="black")
            bb = image.getbbox()

            if (bb[2]-bb[0]) > (width-(margins*2)): break
            else: 
                line = newline
                s = s[index+1:]
        news+=line.strip()+"\n"
    s=news
    print(s)


    d = dw.Drawing(width, height, origin=(0,0), font_family="courCustom")
    # Mark top right corner
    if mirror:
        e = dw.Group(transform="scale(-1, 1) translate({}, 0)".format(-1*width))
        e.append(dw.Text(s, font_size=fontSize, x=margins, y=60))
        e.append(dw.Line(width-50, 0, width, 50))
        d.append(e)
    else:
        d.append(dw.Text(s, font_size=fontSize, x=margins, y=60))
        d.append(dw.Line(width-50, 0, width, 50, stroke='black'))

    d.append_css(style)
    d.save_svg("test.svg")
    d.as_svg
    # d.save_png("test.png")

if __name__ == "__main__":
    #print(brl.toUnicodeSymbols(brl.translate(input("Enter: ")), flatten=True))
    textToSVG("⠠⠭ ⠴ ⠮ ⠆⠌ ⠷ ⠞⠊⠍⠑⠎ ⠭ ⠴ ⠮ ⠺⠕⠗⠌ ⠷ ⠞⠊⠍⠑⠎ ⠭ ⠴ ⠮ ⠁⠛⠑ ⠷ ⠺⠊⠎⠙⠕⠍ ⠭ ⠴ ⠮ ⠁⠛⠑ ⠷ ⠋⠕⠕⠇⠊⠩⠝⠑⠎⠎ ⠭ ⠴ ⠮ ⠑⠏⠕⠡ ⠷ ⠆⠑⠇⠊⠋ ⠭ ⠴ ⠮ ⠑⠏⠕⠡ ⠷ ⠔⠉⠗⠫⠥⠇⠊⠞⠽ ⠭ ⠴ ⠮ ⠎⠂⠎⠕⠝ ⠷ ⠠⠇⠊⠣⠞ ⠭ ⠴ ⠮ ⠎⠂⠎⠕⠝ ⠷ ⠠⠙⠜⠅⠝⠑⠎⠎ ⠭ ⠴ ⠮ ⠎⠏⠗⠬ ⠷ ⠓⠕⠏⠑ ⠭ ⠴ ⠮ ⠺⠔⠞⠻ ⠷ ⠙⠑⠎⠏⠁⠊⠗ ⠺⠑ ⠓⠁⠙ ⠑⠧⠻⠽⠹⠬ ⠆⠑⠿ ⠥ ⠺⠑ ⠓⠁⠙ ⠝⠕⠹⠬ ⠆⠑⠿ ⠥ ⠺⠑ ⠛⠛ ⠁⠇⠇ ⠛⠕⠬ ⠙⠊⠗⠑⠉⠞ ⠋⠋ ⠠⠓⠂⠧⠢ ⠺⠑ ⠛⠛ ⠁⠇⠇ ⠛⠕⠬ ⠙⠊⠗⠑⠉⠞ ⠮ ⠕⠮⠗ ⠺⠁⠽⠔ ⠩⠕⠗⠞ ⠮ ⠏⠻⠊⠕⠙ ⠴ ⠎ ⠋⠜ ⠇⠊⠅⠑ ⠮ ⠏⠗⠑⠎⠢⠞ ⠏⠻⠊⠕⠙ ⠞ ⠎⠕⠍⠑ ⠷ ⠊⠞⠎ ⠝⠕⠊⠎⠊⠑⠌ ⠁⠥⠹⠕⠗⠊⠞⠊⠑⠎ ⠔⠎⠊⠌⠫ ⠕⠝ ⠊⠞⠎ ⠆⠬ ⠗⠑⠉⠑⠊⠧⠫ ⠿ ⠛⠕⠕⠙ ⠕⠗ ⠿ ⠑⠧⠊⠇ ⠔ ⠮ ⠎⠥⠏⠻⠇⠁⠞⠊⠧⠑ ⠙⠑⠛⠗⠑⠑ ⠷ ⠉⠕⠍⠏⠜⠊⠎⠕⠝ ⠕⠝⠇⠽ It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way--in short, the period was so far like the present period, that some of its noisiest authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only.")