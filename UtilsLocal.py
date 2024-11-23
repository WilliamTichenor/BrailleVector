import drawsvg as dw
import pybrl as brl
from playwright.sync_api import sync_playwright
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading


class CORSSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        """Add CORS headers to the response."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

def start_server(port):
    server = TCPServer(("localhost", port), CORSSimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Serving at http://localhost:{port}")
    return server, thread

def stop_server(server, thread):
    if server:
        server.shutdown()
        server.server_close()
        thread.join()
        print("Server stopped.")

def textToBraille(s):
    return brl.toUnicodeSymbols(brl.translate(s), flatten=True)

def mmToPx(mm, dpi):
    return mm*dpi/25.4

def textToSVG(s, feedback, mirror=False, fontSize=24, dpi=96, marginsmm=15, marginsVmm=15, widthmm=210, heightmm=297):
    feedback["value"]=0
    PORT = 8000
    fontFile = open("bin/courText.txt")
    s64 = fontFile.read()
    fontFile.close()
    style = """
    @font-face {
        font-family: courCustom;
        src: url("""+s64+""")
    }
    """
    fontPath = f"http://localhost:{PORT}/bin/cour.ttf"
    print(fontPath)
    styleCompact = """
    @font-face {
        font-family: courCustom;
        src: url('"""+fontPath+"""')
    }
    """
    
    margins = mmToPx(marginsmm, dpi)
    marginsV = mmToPx(marginsVmm, dpi)
    
    width = mmToPx(widthmm,dpi)
    height = mmToPx(heightmm,dpi)

    s=s.strip()
    s=s.replace("\n"," ") # TODO: Re-add newlines, fix super-long word infinitly wrapping
    totalLen=len(s)
    news = ""

    server, thread = start_server(PORT)
    try:
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
                    d.append_css(styleCompact)
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

                    if textWidth > (width-(margins*2)): 
                        feedback["value"]=(totalLen-len(s))*100/totalLen
                        break
                    else: 
                        line = newline
                        s = s[index+1:]
                news+=line.strip()+"\n"
            browser.close()
    finally:
        stop_server(server, thread)
    s=news
    print(s)


    d = dw.Drawing(width, height, origin=(0,0), font_family="courCustom")
    # Mark top right corner
    if mirror:
        e = dw.Group(transform="scale(-1, 1) translate({}, 0)".format(-1*width))
        e.append(dw.Text(s, font_size=fontSize, x=margins, y=marginsV))
        e.append(dw.Line(width-50, 0, width, 50))
        d.append(e)
    else:
        d.append(dw.Text(s, font_size=fontSize, x=margins, y=marginsV))
        d.append(dw.Line(width-50, 0, width, 50, stroke='black'))

    d.append_css(style)
    d.save_svg("test.svg")
    feedback["value"]=100


if __name__ == "__main__":
    #print(brl.toUnicodeSymbols(brl.translate(input("Enter: ")), flatten=True))
    textToSVG("⠠⠭ ⠴ ⠮ ⠆⠌ ⠷ ⠞⠊⠍⠑⠎ ⠭ ⠴ ⠮ ⠺⠕⠗⠌ ⠷ ⠞⠊⠍⠑⠎ ⠭ ⠴ ⠮ ⠁⠛⠑ ⠷ ⠺⠊⠎⠙⠕⠍ ⠭ ⠴ ⠮ ⠁⠛⠑ ⠷ ⠋⠕⠕⠇⠊⠩⠝⠑⠎⠎ ⠭ ⠴ ⠮ ⠑⠏⠕⠡ ⠷ ⠆⠑⠇⠊⠋ ⠭ ⠴ ⠮ ⠑⠏⠕⠡ ⠷ ⠔⠉⠗⠫⠥⠇⠊⠞⠽ ⠭ ⠴ ⠮ ⠎⠂⠎⠕⠝ ⠷ ⠠⠇⠊⠣⠞ ⠭ ⠴ ⠮ ⠎⠂⠎⠕⠝ ⠷ ⠠⠙⠜⠅⠝⠑⠎⠎ ⠭ ⠴ ⠮ ⠎⠏⠗⠬ ⠷ ⠓⠕⠏⠑ ⠭ ⠴ ⠮ ⠺⠔⠞⠻ ⠷ ⠙⠑⠎⠏⠁⠊⠗ ⠺⠑ ⠓⠁⠙ ⠑⠧⠻⠽⠹⠬ ⠆⠑⠿ ⠥ ⠺⠑ ⠓⠁⠙ ⠝⠕⠹⠬ ⠆⠑⠿ ⠥ ⠺⠑ ⠛⠛ ⠁⠇⠇ ⠛⠕⠬ ⠙⠊⠗⠑⠉⠞ ⠋⠋ ⠠⠓⠂⠧⠢ ⠺⠑ ⠛⠛ ⠁⠇⠇ ⠛⠕⠬ ⠙⠊⠗⠑⠉⠞ ⠮ ⠕⠮⠗ ⠺⠁⠽⠔ ⠩⠕⠗⠞ ⠮ ⠏⠻⠊⠕⠙ ⠴ ⠎ ⠋⠜ ⠇⠊⠅⠑ ⠮ ⠏⠗⠑⠎⠢⠞ ⠏⠻⠊⠕⠙ ⠞ ⠎⠕⠍⠑ ⠷ ⠊⠞⠎ ⠝⠕⠊⠎⠊⠑⠌ ⠁⠥⠹⠕⠗⠊⠞⠊⠑⠎ ⠔⠎⠊⠌⠫ ⠕⠝ ⠊⠞⠎ ⠆⠬ ⠗⠑⠉⠑⠊⠧⠫ ⠿ ⠛⠕⠕⠙ ⠕⠗ ⠿ ⠑⠧⠊⠇ ⠔ ⠮ ⠎⠥⠏⠻⠇⠁⠞⠊⠧⠑ ⠙⠑⠛⠗⠑⠑ ⠷ ⠉⠕⠍⠏⠜⠊⠎⠕⠝ ⠕⠝⠇⠽ It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way--in short, the period was so far like the present period, that some of its noisiest authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only.")
    #textToSVG("testing!")
    #textToSVG("supercalifragilisticexpialidocioussupercalifragilisticexpialidocious!")