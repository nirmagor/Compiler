
class VMWriter:

    SegmentDict = dict()
    SegmentDict["CONST"] = "constant"
    SegmentDict["ARG"] = "argument"
    SegmentDict["LOCAL"] = "local"
    SegmentDict["THIS"] = "this"
    SegmentDict["THAT"] = "that"
    SegmentDict["STATIC"] = "static"
    SegmentDict["POINTER"] = "pointer"
    SegmentDict["TEMP"] = "temp"
    ArithmeticDict = dict()
    ArithmeticDict["ADD"] = "add"
    ArithmeticDict["SUB"] = "sub"
    ArithmeticDict["NEG"] = "neg"
    ArithmeticDict["EQ"] = "eq"
    ArithmeticDict["GT"] = "gt"
    ArithmeticDict["LT"] = "lt"
    ArithmeticDict["AND"] = "and"
    ArithmeticDict["OR"] = "or"
    ArithmeticDict["NOT"] = "not"
    ArithmeticDict["MUL"] = "call Math.multiply 2"
    ArithmeticDict["DIV"] = "call Math.divide 2"


    def __init__(self, outputFile):

        self.vmFile = open(outputFile, 'w')

    def writePush(self, segment, index):

        self.vmFile.write("push " + self.SegmentDict[segment] + " " + str(index) + "\n")

    def writePop(self, segment, index):

        self.vmFile.write("pop " + self.SegmentDict[segment] + " " + str(index) + "\n")

    def writeArithmetic(self, command):

        self.vmFile.write(self.ArithmeticDict[command]+ "\n")

    def writeLabel(self, label):

        self.vmFile.write("label " + label + "\n")

    def writeGoTo(self, label):

        self.vmFile.write("goto " + label + "\n")

    def writeIf(self, label):

        self.vmFile.write("if-goto " + label + "\n")

    def writeCall(self, name, nArgs):

        self.vmFile.write("call " + name + " " + str(nArgs) + "\n")

    def writeFunction(self, name, nLocals):

        self.vmFile.write("function " + name + " " + str(nLocals) + "\n")

    def writeReturn(self):

        self.vmFile.write("return\n")

    def writeString(self, string):
        length = len(string)
        self.writePush("CONST", length)
        self.writeCall("String.new", 1)
        for char in string:
            self.writePush("CONST", ord(char))
            self.writeCall("String.appendChar", 2)

    def close(self):
        self.vmFile.close()


