import tkinter as tk
from tkinter import filedialog
import UtilsLocal


def brailleWrapper(s):
    print(UtilsLocal.textToBraille(s))

def uploadText():
    filePath = filedialog.askopenfilename()
    print("Opening: "+filePath)
    file = open(filePath, "rt")
    s = file.read()
    inputText.delete(1.0, tk.END)
    inputText.insert(tk.END, s)

window = tk.Tk()
window.title("BrailleVector")

"""s = "Hello World!"
button = tk.Button(text="Translate to Braille", command=lambda: brailleWrapper(s))
button.pack()"""
inputText = tk.Text(window, height=10, width=30)
inputText.pack()

button = tk.Button(window, text="Upload Text", command=uploadText)
button.pack(pady=10)

window.mainloop()