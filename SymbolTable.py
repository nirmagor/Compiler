from re import *


class SymbolTable:

    CLASS_KIND = 0

    def __init__(self):

        self.classTable = dict()

    def startSubroutine(self):

        self.subroutineTable = dict()

    def define(self, name, type, kind):


        if self.__kindIdentifier(kind) == self.CLASS_KIND:
            relevantTable = self.classTable
        else:
            relevantTable = self.subroutineTable
        relevantTable[name] = (name, type, kind, self.varCount(kind))

    def varCount(self, kind):
        counter = 0

        if self.__kindIdentifier(kind) == self.CLASS_KIND:
            relevantSynbolTable = self.classTable
        else:
            relevantSynbolTable = self.subroutineTable
        for key in relevantSynbolTable:
            if match(kind, relevantSynbolTable[key][2]):
                counter += 1
        return counter

    def kindOf(self, name):

        if name in self.subroutineTable:
            return self.subroutineTable[name][2]
        elif name in self.classTable:
            return self.classTable[name][2]
        else:
            return None

    def typeOf(self, name):

        if name in self.subroutineTable:
            return self.subroutineTable[name][1]
        elif name in self.classTable:
            return self.classTable[name][1]
        else:
            return None

    def indexOf(self, name):
        releventTable = self.subroutineTable
        kind = self.kindOf(name)
        if kind:
            if self.__kindIdentifier(kind) == self.CLASS_KIND:
                releventTable = self.classTable
            return releventTable[name][3]
        else:
            return -1


    def __kindIdentifier(self, kind):

        if match("(STATIC|FIELD)",kind):
            return 0
        else:
            return 1

