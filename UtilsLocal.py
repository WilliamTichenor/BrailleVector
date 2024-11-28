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

def replaceLast(string, old, new):
    # Find the last occurrence of the substring
    pos = string.rfind(old)
    if pos != -1:  # If the substring is found
        # Replace the last occurrence
        string = string[:pos] + new + string[pos + len(old):]
    return string

def textToSVG(s, feedback, directory, dirname,
            mirror=False, fontSize=24, dpi=96,
            marginsmm=25, marginsVmm=25, widthmm=210, heightmm=297):
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

    newdirname = dirname
    i = 1
    while os.path.exists(directory+os.path.sep+newdirname):
        print(newdirname+" exists")
        newdirname = dirname+f"({i})"
        i+=1
    os.mkdir(directory+os.path.sep+newdirname)

    s=s.strip()
    s=s.replace("\n"," ") # Re-add newlines, fix super-long word infinitly wrapping
    totalLen=len(s)
    news = ""
    savedline = ""
    pagenum = 1

    server, thread = startServer(port)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            while s:
                if savedline:
                    news = savedline
                    savedline = ""
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
                        feedback.master.update_idletasks()
                        break
                    line = newline
                    s = s[index+1:]
                # Test (news + line.strip()+"\n") HERE to see if we need a new page!
                # if we do, save the new line! then make the page and restart.
                # if we dont, append it to news then make page and restart

                d = dw.Drawing(width, height, origin=(0,0), font_family="courCustom")
                d.append(dw.Text((news+line.strip()+"\n"), font_size=fontSize, x=0, y=marginsV))
                d.append_css(styleCompact)
                svgs = d.as_svg()
                svgs = svgs.replace('<text ', '<text id="myText" ')
                svgs = replaceLast(svgs, '<text ', '<text id="myText" ')
                svgHtml = "<!DOCTYPE html><html><body>"+svgs+"</body></html>"
                page.set_content(svgHtml)
                textHeight = page.evaluate("""
                    () => {
                        const text = document.getElementById('myText');
                        const bbox = text.getBoundingClientRect();
                        return bbox.bottom;
                    }
                """)
                if textHeight > height-marginsV or not s:
                    #save line!
                    savedline = line.strip()+"\n"
                    if not s:
                        news+=line.strip()+"\n"
                    # Only reach this point if the new line WONT fit, or s is empty!
                    d = dw.Drawing(width, height, origin=(0,0), font_family="courCustom")
                    # Mark top right corner
                    if mirror:
                        e = dw.Group(transform=f"scale(-1, 1) translate({-1*width}, 0)")
                        e.append(dw.Text(news, font_size=fontSize, x=margins, y=marginsV))
                        e.append(dw.Line(width-50, 0, width, 50, stroke='black'))
                        d.append(e)
                    else:
                        d.append(dw.Text(news, font_size=fontSize, x=margins, y=marginsV))
                        d.append(dw.Line(width-50, 0, width, 50, stroke='black'))

                    d.append_css(style)
                    d.save_svg(directory + os.path.sep + newdirname + os.path.sep +
                            dirname + str(pagenum) + ".svg")
                    pagenum+=1
                    news = ""
                    if not s:
                        break
                    continue
                news+=line.strip()+"\n" # only run this if the new line will fit!
            browser.close()
    finally:
        stopServer(server, thread)

    feedback["value"]=100
    return 0
