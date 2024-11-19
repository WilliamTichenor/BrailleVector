import drawsvg as dw
import pybrl as brl
from playwright.sync_api import sync_playwright


def textToBraille(s):
    return brl.toUnicodeSymbols(brl.translate(s), flatten=True)

def mmToPx(mm, dpi):
    return mm*dpi/25.4

def textToSVG(s, mirror=False):
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
    paperSizes = {
        "A4": (210, 297), # In mm
        "A3": (297, 420),

        "B4": (250, 353),
        "B5": (176, 250)
    }
    width = mmToPx(paperSizes["A4"][0],dpi)
    height = mmToPx(paperSizes["A4"][1],dpi)

    s=s.strip()
    s=s.replace("\n"," ") # TODO: Re-add newlines, fix super-long word infinitly wrapping
    news = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        while s:
            line = ""
            while True:
                index = s.find(" ")
                if index == -1:
                    line+=s
                    s = ""
                    break
                newline = line+s[:index+1]

                # Test the size of newline!
                
                # Playwright browser test method
                d = dw.Drawing(width, height, origin=(0,0), font_family="courCustom")
                d.append(dw.Text(newline, font_size=fontSize, x=0, y=0))
                d.append_css(style)
                svgs = d.as_svg()
                svgs = svgs.replace('<text ', '<text id="myText" ')
                svg_html = "<!DOCTYPE html><html><body>"+svgs+"</body></html>"
                page.set_content(svg_html)
                textWidth = page.evaluate("""
                    () => {
                        const text = document.getElementById('myText');
                        const bbox = text.getBBox();
                        return bbox.width;
                    }
                """)

                if textWidth > (width-(margins*2)): break
                else: 
                    line = newline
                    s = s[index+1:]
            news+=line.strip()+"\n"
        browser.close()
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


if __name__ == "__main__":
    #print(brl.toUnicodeSymbols(brl.translate(input("Enter: ")), flatten=True))
    textToSVG("⠠⠭ ⠴ ⠮ ⠆⠌ ⠷ ⠞⠊⠍⠑⠎ ⠭ ⠴ ⠮ ⠺⠕⠗⠌ ⠷ ⠞⠊⠍⠑⠎ ⠭ ⠴ ⠮ ⠁⠛⠑ ⠷ ⠺⠊⠎⠙⠕⠍ ⠭ ⠴ ⠮ ⠁⠛⠑ ⠷ ⠋⠕⠕⠇⠊⠩⠝⠑⠎⠎ ⠭ ⠴ ⠮ ⠑⠏⠕⠡ ⠷ ⠆⠑⠇⠊⠋ ⠭ ⠴ ⠮ ⠑⠏⠕⠡ ⠷ ⠔⠉⠗⠫⠥⠇⠊⠞⠽ ⠭ ⠴ ⠮ ⠎⠂⠎⠕⠝ ⠷ ⠠⠇⠊⠣⠞ ⠭ ⠴ ⠮ ⠎⠂⠎⠕⠝ ⠷ ⠠⠙⠜⠅⠝⠑⠎⠎ ⠭ ⠴ ⠮ ⠎⠏⠗⠬ ⠷ ⠓⠕⠏⠑ ⠭ ⠴ ⠮ ⠺⠔⠞⠻ ⠷ ⠙⠑⠎⠏⠁⠊⠗ ⠺⠑ ⠓⠁⠙ ⠑⠧⠻⠽⠹⠬ ⠆⠑⠿ ⠥ ⠺⠑ ⠓⠁⠙ ⠝⠕⠹⠬ ⠆⠑⠿ ⠥ ⠺⠑ ⠛⠛ ⠁⠇⠇ ⠛⠕⠬ ⠙⠊⠗⠑⠉⠞ ⠋⠋ ⠠⠓⠂⠧⠢ ⠺⠑ ⠛⠛ ⠁⠇⠇ ⠛⠕⠬ ⠙⠊⠗⠑⠉⠞ ⠮ ⠕⠮⠗ ⠺⠁⠽⠔ ⠩⠕⠗⠞ ⠮ ⠏⠻⠊⠕⠙ ⠴ ⠎ ⠋⠜ ⠇⠊⠅⠑ ⠮ ⠏⠗⠑⠎⠢⠞ ⠏⠻⠊⠕⠙ ⠞ ⠎⠕⠍⠑ ⠷ ⠊⠞⠎ ⠝⠕⠊⠎⠊⠑⠌ ⠁⠥⠹⠕⠗⠊⠞⠊⠑⠎ ⠔⠎⠊⠌⠫ ⠕⠝ ⠊⠞⠎ ⠆⠬ ⠗⠑⠉⠑⠊⠧⠫ ⠿ ⠛⠕⠕⠙ ⠕⠗ ⠿ ⠑⠧⠊⠇ ⠔ ⠮ ⠎⠥⠏⠻⠇⠁⠞⠊⠧⠑ ⠙⠑⠛⠗⠑⠑ ⠷ ⠉⠕⠍⠏⠜⠊⠎⠕⠝ ⠕⠝⠇⠽ It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way--in short, the period was so far like the present period, that some of its noisiest authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only.")
    #textToSVG("testing!")