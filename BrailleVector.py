import tkinter as tk
from tkinter import filedialog, ttk, font
import UtilsLocal
import tkentrycomplete


def brailleWrapper(s, progressBar):
    if s == "" or inputText.cget('fg') == "gray":
        print("Please enter text!")
        return
    directory = filedialog.askdirectory(mustexist=True)
    if not directory:
        print("Choose a file location!")
        return
    dirname = filename.get()
    sB = UtilsLocal.textToBraille(s)
    kwargs = {}
    kwargs['mirror'] = bool(mirror.get())
    kwargs['fontSize'] = fontsizeval.get()
    kwargs['dpi'] = dpival.get()
    kwargs['marginsmm'] = marginshval.get()
    kwargs['marginsVmm'] = marginsvval.get()
    kwargs['widthmm'] = (
        paperWidthval.get() if paperTypeRadio == "custom" else paperSizes[paperSelect.get()][0])
    kwargs['heightmm'] = (
        paperHeightval.get() if paperTypeRadio == "custom" else paperSizes[paperSelect.get()][1])
    UtilsLocal.textToSVG(sB, progressBar, directory, dirname, **kwargs)

def onFocusIn(event): # pylint: disable=W0613
    # Remove placeholder text when the user focuses on the widget
    if inputText.get("1.0", "end-1c") == PLACEHOLDER_TEXT:
        inputText.delete("1.0", "end")
        inputText.config(fg="black")

def onFocusOut(event): # pylint: disable=W0613
    # Restore placeholder text if the widget is empty
    if not inputText.get("1.0", "end-1c").strip():
        inputText.insert("1.0", PLACEHOLDER_TEXT)
        inputText.config(fg="gray")

def onRadioSelection():
    if paperTypeRadio.get() == "select":
        paperWidth["state"] = "disabled"
        paperWidthLabel["state"] = "disabled"
        paperHeight["state"] = "disabled"
        paperHeightLabel["state"] = "disabled"

        paperSelect["state"] = "readonly"
        paperSelectLabel["state"] = "normal"
    else:
        paperWidth["state"] = "normal"
        paperWidthLabel["state"] = "normal"
        paperHeight["state"] = "normal"
        paperHeightLabel["state"] = "normal"

        paperSelect["state"] = "disabled"
        paperSelectLabel["state"] = "disabled"

def spinboxValidate(userInput, amin, amax):
    if  userInput.isdigit():
        if int(userInput) < int(amin) or int(userInput) > int(amax):
            print ("Out of range")
            return False
        print(userInput)
        return True
    if userInput == "":
        print(userInput)
        return True
    print("Not numeric")
    return False

def validateFilename(userInput):
    if len(userInput) > 255:
        return False
    if any(x in userInput for x in '/\\:*?<>|'):
        return False
    return True

def uploadText():
    filePath = filedialog.askopenfilename()
    print("Opening: "+filePath)
    with open(filePath, "rt", encoding="utf-8") as file:
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
    frameTop.pack(fill="both", expand=True)
    separator = ttk.Separator(window, orient="horizontal")
    separator.pack(fill="x", padx=10, pady=10)
    frameBot = tk.Frame(window, height=40)
    frameBot.pack(fill="x")


    PLACEHOLDER_TEXT = "Enter your text here..."
    inputText = tk.Text(frameTop, height=10, width=30, fg="gray", wrap="word")
    inputText.pack(side="left", padx=(10,0), pady=10, fill="both", expand=True)
    inputText.insert("1.0", PLACEHOLDER_TEXT)
    inputText.bind("<FocusIn>", onFocusIn)
    inputText.bind("<FocusOut>", onFocusOut)

    scrollbar = tk.Scrollbar(frameTop, command=inputText.yview)
    scrollbar.pack(side="left", pady=10, fill="y")
    inputText.config(yscrollcommand=scrollbar.set)

    textUploadButton = tk.Button(frameTop, text="Upload Text", command=uploadText)
    textUploadButton.pack(side="top", padx=10, pady=30)

    translateButton = tk.Button(frameTop, text="Convert and Save",
            command=lambda: brailleWrapper(inputText.get("1.0", "end-1c"), loadingBar))
    translateButton.pack(side="top", padx=10)

    fileNamerLabel = tk.Label(frameTop, text="Name:")
    fileNamerLabel.pack(side="top", padx=5)
    filename = tk.StringVar(value="output")
    fileNamer = tk.Entry(frameTop, textvariable=filename, validate='key',
            validatecommand=(window.register(validateFilename), "%P"), width=17)
    fileNamer.pack(side="top", padx=10)


    fontsizeval = tk.IntVar(value=24)
    fontsize = tk.Spinbox(frameBot, width=4, textvariable=fontsizeval, from_=1, to=9999,
            increment=1, validate="key",
            validatecommand=(window.register(spinboxValidate), "%P", 1, 9999))
    fontsize.grid(row=0, column=1, pady=5)
    fontsizeLabel = tk.Label(frameBot, text= "Font Size:")
    fontsizeLabel.grid(row=0, column=0, pady=5, padx=10, sticky="e")

    dpival = tk.IntVar(value=96)
    dpi = tk.Spinbox(frameBot, width=4, textvariable=dpival, from_=1, to=9999, increment=1,
            validate="key", validatecommand=(window.register(spinboxValidate), "%P", 1, 9999))
    dpi.grid(row=1, column=1, pady=5)
    dpiLabel = tk.Label(frameBot, text= "DPI:")
    dpiLabel.grid(row=1, column=0, pady=5, padx=10, sticky="e")

    marginshval = tk.IntVar(value=25)
    marginsh = tk.Spinbox(frameBot, width=4, textvariable=marginshval, from_=0, to=9999,
            increment=1, validate="key",
            validatecommand=(window.register(spinboxValidate), "%P", 0, 9999))
    marginsh.grid(row=0, column=5, pady=5)
    marginshLabel = tk.Label(frameBot, text= "Horizontal Margins (mm):")
    marginshLabel.grid(row=0, column=2, columnspan=3, pady=5, padx=10, sticky="e")

    marginsvval = tk.IntVar(value=25)
    marginsv = tk.Spinbox(frameBot, width=4, textvariable=marginsvval, from_=0, to=9999,
            increment=1, validate="key",
            validatecommand=(window.register(spinboxValidate), "%P", 0, 9999))
    marginsv.grid(row=1, column=5, pady=5)
    marginsvLabel = tk.Label(frameBot, text= "Vertical Margins (mm):")
    marginsvLabel.grid(row=1, column=2, columnspan=3, pady=5, padx=10, sticky="e")

    fonts = font.families()
    fontDropdown = tkentrycomplete.AutocompleteCombobox(frameBot, values=fonts)
    fontDropdown.set_completion_list(fonts)
    fontDropdown.grid(row=2, column=1, columnspan=3, pady=5)
    fontLabel = tk.Label(frameBot, text= "Font:")
    fontLabel.grid(row=2, column=0, pady=5, padx=10, sticky="e")

    mirror = tk.IntVar()
    mirror.set(0)
    mirrorbox = ttk.Checkbutton(frameBot, variable=mirror)
    mirrorbox.grid(row=2, column=5, pady=5, padx=10)
    mirrorboxLabel = tk.Label(frameBot, text="Mirror?")
    mirrorboxLabel.grid(row=2, column=4, pady=5, padx=10)

    paperTypeRadio = tk.StringVar(value="select")
    radioSelect = tk.Radiobutton(frameBot, text="Preset Paper", variable=paperTypeRadio,
            value="select", command=onRadioSelection)
    radioSelect.grid(row=3, column=0, pady=5, padx=10, columnspan=2, sticky="w")
    radioCustom = tk.Radiobutton(frameBot, text="Custom Paper", variable=paperTypeRadio,
            value="custom", command=onRadioSelection)
    radioCustom.grid(row=4, column=0, pady=5, padx=10, columnspan=2, sticky="w")

    paperSelectLabel = tk.Label(frameBot, text="Type:")
    paperSelectLabel.grid(row=3, column=2, pady=5, sticky="e")
    paperSelect = ttk.Combobox(frameBot, width=3, values=list(paperSizes.keys()),  state="readonly")
    paperSelect.set(list(paperSizes.keys())[0])
    paperSelect.grid(row=3, column=3, pady=5, padx=10)

    paperWidthval = tk.IntVar(value=paperSizes["A4"][0])
    paperWidthLabel = tk.Label(frameBot, text="W (mm):")
    paperWidthLabel.grid(row=4, column=2, pady=5)
    paperWidth = tk.Spinbox(frameBot, width=4, textvariable=paperWidthval, from_=1, to=9999,
            increment=1, validate="key",
            validatecommand=(window.register(spinboxValidate), "%P", 1, 9999))
    paperWidth.grid(row=4, column=3, pady=5)

    paperHeightval = tk.IntVar(value=paperSizes["A4"][1])
    paperHeightLabel = tk.Label(frameBot, text="H (mm):")
    paperHeightLabel.grid(row=4, column=4, pady=5)
    paperHeight = tk.Spinbox(frameBot, width=4, textvariable=paperHeightval, from_=1, to=9999,
            increment=1, validate="key",
            validatecommand=(window.register(spinboxValidate), "%P", 1, 9999))
    paperHeight.grid(row=4, column=5, pady=5)

    onRadioSelection()


    loadingBar = ttk.Progressbar(window, orient="horizontal", mode="determinate")
    loadingBar.pack(fill="x", side="bottom")

    window.mainloop()
