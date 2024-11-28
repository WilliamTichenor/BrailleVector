from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket
import threading
import os
import drawsvg as dw
import pybrl as brl
from playwright.sync_api import sync_playwright


class CORSSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        """Add CORS headers to the response."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

def startServer(port):
    server = TCPServer(("localhost", port), CORSSimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Serving at http://localhost:{port}")
    return server, thread

def stopServer(server, thread):
    if server:
        server.shutdown()
        server.server_close()
        thread.join()
        print("Server stopped.")

def textToBraille(s):
    return brl.toUnicodeSymbols(brl.translate(s), flatten=True)

def mmToPx(mm, dpi):
    return mm*dpi/25.4

def textToSVG(s, feedback, directory, dirname,
            mirror=False, fontSize=24, dpi=96,
            marginsmm=25, marginsVmm=25, widthmm=210, heightmm=297):
    print(mirror)
    print(fontSize)
    print(dpi)
    print(marginsmm)
    print(marginsVmm)
    print(widthmm)
    print(heightmm)
    feedback["value"]=0
    feedback.master.update_idletasks()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', 0))
        port = sock.getsockname()[1]
    with open("bin/courText.txt", encoding="utf-8") as fontFile:
        s64 = fontFile.read()
    style = """
    @font-face {
        font-family: courCustom;
        src: url("""+s64+""")
    }
    """
    fontPath = f"http://localhost:{port}/bin/cour.ttf"
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
    s=s.replace("\n"," ") # Re-add newlines, fix super-long word infinitly wrapping
    totalLen=len(s)
    news = ""

    server, thread = startServer(port)
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
                    svgHtml = "<!DOCTYPE html><html><body>"+svgs+"</body></html>"
                    page.set_content(svgHtml)
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
                    line = newline
                    s = s[index+1:]
                news+=line.strip()+"\n"
            browser.close()
    finally:
        stopServer(server, thread)
    s=news
    print(s)


    d = dw.Drawing(width, height, origin=(0,0), font_family="courCustom")
    # Mark top right corner
    if mirror:
        e = dw.Group(transform=f"scale(-1, 1) translate({-1*width}, 0)")
        e.append(dw.Text(s, font_size=fontSize, x=margins, y=marginsV))
        e.append(dw.Line(width-50, 0, width, 50, stroke='black'))
        d.append(e)
    else:
        d.append(dw.Text(s, font_size=fontSize, x=margins, y=marginsV))
        d.append(dw.Line(width-50, 0, width, 50, stroke='black'))

    d.append_css(style)
    newdirname = dirname
    i = 1
    while os.path.exists(directory+os.path.sep+newdirname):
        print(newdirname+" exists")
        newdirname = dirname+f"({i})"
        i+=1
    os.mkdir(directory+os.path.sep+newdirname)
    d.save_svg(directory+os.path.sep+newdirname+os.path.sep+dirname+".svg")
    feedback["value"]=100
    return 0
