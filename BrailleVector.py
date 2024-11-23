import tkinter as tk
from tkinter import filedialog, ttk, font
import UtilsLocal
import tkentrycomplete


def brailleWrapper(s, loadingBar):
    filedialog.askdirectory()
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

def spinboxValidate(user_input):
    if  user_input.isdigit():
        if int(user_input) <= 0 or int(user_input) > 2000:
            print ("Out of range")
            return False
        print(user_input)
        return True
    elif user_input == "":
        print(user_input)
        return True
    else:
        print("Not numeric")
        return False

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
    frameTop.pack(fill="x")
    separator = ttk.Separator(window, orient="horizontal")
    separator.pack(fill="x", padx=10, pady=10)
    frameBot = tk.Frame(window, height=40)
    frameBot.pack(fill="x")


    placeholder_text = "Enter your text here..."
    inputText = tk.Text(frameTop, height=10, width=30, fg="gray")
    inputText.pack(side="left", padx=10, pady=10)
    inputText.insert("1.0", placeholder_text)
    inputText.bind("<FocusIn>", on_focus_in)
    inputText.bind("<FocusOut>", on_focus_out)

    textUploadButton = tk.Button(frameTop, text="Upload Text", command=uploadText)
    textUploadButton.pack(side="top", padx=10, pady=30)

    translateButton = tk.Button(frameTop, text="Convert and Save", command=lambda: brailleWrapper(inputText.get("1.0", "end-1c"), loadingBar))
    translateButton.pack(side="top", padx=10)


    fontsize = tk.Spinbox(frameBot, width=3, value=12, from_=1, to=2000, increment=1, validate="key", validatecommand=(window.register(spinboxValidate), "%P"))
    fontsize.grid(row=0, column=1, pady=5)
    fontsizeLabel = tk.Label(frameBot, text= "Font Size:")
    fontsizeLabel.grid(row=0, column=0, pady=5, padx=10)

    dpi = tk.Spinbox(frameBot, width=3, value=96, from_=1, to=2000, increment=1, validate="key", validatecommand=(window.register(spinboxValidate), "%P"))
    dpi.grid(row=1, column=1, pady=5)
    dpiLabel = tk.Label(frameBot, text= "DPI:")
    dpiLabel.grid(row=1, column=0, pady=5, padx=10)

    marginsh = tk.Spinbox(frameBot, width=3, value=25, from_=0, to=2000, increment=1, validate="key", validatecommand=(window.register(spinboxValidate), "%P"))
    marginsh.grid(row=0, column=5, pady=5)
    marginshLabel = tk.Label(frameBot, text= "Horizontal Margins (mm):")
    marginshLabel.grid(row=0, column=2, columnspan=3, pady=5, padx=10)

    marginsv = tk.Spinbox(frameBot, width=3, value=25, from_=0, to=2000, increment=1, validate="key", validatecommand=(window.register(spinboxValidate), "%P"))
    marginsv.grid(row=1, column=5, pady=5)
    marginsvLabel = tk.Label(frameBot, text= "Vertical Margins (mm):")
    marginsvLabel.grid(row=1, column=2, columnspan=3, pady=5, padx=10)

    fonts = font.families()
    fontDropdown = tkentrycomplete.AutocompleteCombobox(frameBot, values=fonts)
    fontDropdown.set_completion_list(fonts)
    fontDropdown.grid(row=2, column=1, columnspan=3, pady=5)
    fontLabel = tk.Label(frameBot, text= "Font:")
    fontLabel.grid(row=2, column=0, pady=5, padx=10)

    mirror = tk.IntVar()
    mirror.set(0)
    mirrorbox = ttk.Checkbutton(frameBot, variable=mirror)
    mirrorbox.grid(row=2, column=5, pady=5, padx=10)
    mirrorboxLabel = ttk.Label(frameBot, text="Mirror?")
    mirrorboxLabel.grid(row=2, column=4, pady=5, padx=10)


    loadingBar = ttk.Progressbar(window, orient="horizontal", mode="determinate")
    loadingBar.pack(fill="x")

    window.mainloop()