import tkinter as tk
from tkinter import filedialog, ttk
import UtilsLocal


def brailleWrapper(s, loadingBar):
    sB = UtilsLocal.textToBraille(s)
    UtilsLocal.textToSVG(sB, loadingBar)

def on_focus_in(event):
    # Remove placeholder text when the user focuses on the widget
    if inputText.get("1.0", "end-1c") == placeholder_text:
        inputText.delete("1.0", "end")
        inputText.config(fg="black")

def on_focus_out(event):
    # Restore placeholder text if the widget is empty
    if not inputText.get("1.0", "end-1c").strip():
        inputText.insert("1.0", placeholder_text)
        inputText.config(fg="gray")

def uploadText():
    filePath = filedialog.askopenfilename()
    print("Opening: "+filePath)
    file = open(filePath, "rt")
    s = file.read()
    inputText.delete(1.0, tk.END)
    inputText.insert(tk.END, s)
    inputText.config(fg="black")

if __name__ == "__main__":

    paperSizes = {
        "A4": (210, 297), # In mm
        "A3": (297, 420),

        "B4": (250, 353),
        "B5": (176, 250)
    }

    window = tk.Tk()
    window.title("BrailleVector")


    frameTop = tk.Frame(window, height=20)
    frameTop.pack(fill="x", pady=10)
    separator = ttk.Separator(window, orient="horizontal")
    separator.pack(fill="x", padx=10, pady=10)
    frameBot = tk.Frame(window, height=20)
    frameBot.pack(fill="x", pady=10)

    placeholder_text = "Enter your text here..."
    inputText = tk.Text(frameTop, height=10, width=30, fg="gray")
    inputText.pack(side="left", padx=10, pady=10)
    inputText.insert("1.0", placeholder_text)
    inputText.bind("<FocusIn>", on_focus_in)
    inputText.bind("<FocusOut>", on_focus_out)

    textUploadButton = tk.Button(frameTop, text="Upload Text", command=uploadText)
    textUploadButton.pack(side="top", padx=10, pady=30)

    translateButton = tk.Button(frameTop, text="Translate to Braille", command=lambda: brailleWrapper(inputText.get("1.0", "end-1c"), loadingBar))
    translateButton.pack(side="top", padx=10)

    loadingBar = ttk.Progressbar(window, orient="horizontal", mode="determinate")
    loadingBar.pack(fill="x")

    window.mainloop()