import drawsvg
import pybrl as brl


def textToBraille(str):
    return brl.toUnicodeSymbols(brl.translate(str), flatten=True)

def textToSVG(str, mirror=False):
    pass

if __name__ == "__main__":
    print(brl.toUnicodeSymbols(brl.translate(input("Enter: ")), flatten=True))