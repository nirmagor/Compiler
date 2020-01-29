import os
import sys
from re import *


class JackTokenizer:
    # curr_file_name = ""

    keyword_list = {"class", "constructor", "function", "method", "field",
                    "static",
                    "var", "int", "char", "boolean", "void", "true", "false",
                    "null",
                    "false", "let", "do", "if", "else", "while", "return", "this"}

    symbol_list = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                   '/', '&',
                   '|', '<', '>', '=', '~'}

    def __init__(self, inputFile):
        self.inputPath = inputFile
        self.file = open(inputFile, 'r')
        self.lines = self.file.readlines()
        self.file.close()
        # self.findEndBlock = False
        self.inStringFlag = False
        self.inCommentFlag = False
        self.dontGetIn = False

        self.tokens = list()
        self.goThroughLines()
        self.currIndex = 0
        self.token = self.tokens[self.currIndex]






    def hasMoreTokens(self):
        if self.currIndex == len(self.tokens):
            return False
        else:
            return True

    def advance(self):
        self.currIndex += 1
        self.token = self.tokens[self.currIndex]

    def tokenType(self):
        if self.token in JackTokenizer.keyword_list:
            return "KEYWORD"
        elif self.token in JackTokenizer.symbol_list:
            return "SYMBOL"
        elif match("^[0-9]+", self.token):
            return "INT_CONST"
        elif match("^[\"].*[\"]$", self.token):
            return "STRING_CONST"
        elif match("^[^0-9]+.*", self.token):
            return "IDENTIFIER"
        else:
            print("ruti and nir you've got an error")

    def keyWord(self):
        return self.token

    def symbol(self):
        return self.token

    def identifier(self):
        return self.token

    def intVal(self):
        return self.token

    def stringVal(self):
        return self.token

    def makeOneSpace(self, line):

        flag = False
        found_first_space = False
        if search("^\s+", line) and search("^\s+", line).end() != len(
                line):
            line = line[search("^\s+", line).end():]
        st_list = list(line)
        for i in range(len(line)):

            if st_list[i] == '\"':
                flag = not flag

            if not flag:
                if st_list[i] == ' ' and not found_first_space:
                    found_first_space = True
                    continue
                elif st_list[i] == ' ' and found_first_space:
                    st_list[i] = ''
                else:
                    found_first_space = False
        if st_list:
            if st_list[-1] == " ":
                st_list[-1] = ''
        return ''.join(st_list)



    def splitBySpace(self, line):
        start_index = 0
        lst = list()
        st_list = list(line)
        flag = False
        for i in range(len(line)):

            if st_list[i] == '\"':
                flag = not flag

            if not flag:
                if st_list[i] == ' ' or len(line) - 1 == i:
                    if len(line) - 1 == i and st_list[i] != ' ':
                        i = i + 1
                    lst.append(line[start_index:i])
                    start_index = i + 1
        return lst





    def relevantLines(self, line):
        newline = ""
        for index in range(len(line)):
            char = line[index]
            if not self.inStringFlag:
                if not self.inCommentFlag:

                    if match("(/\*)",line[index: index +2]):
                        self.inCommentFlag = True
                        continue
                    elif match("//",line[index: index +2]) and not self.dontGetIn:
                        break
                else:
                    if match("\*/",line[index:index+2]):
                        self.inCommentFlag = False
                        self.dontGetIn = True
                        continue
            if not self.inCommentFlag:
                if self.dontGetIn:
                    self.dontGetIn = False
                    newline += " "
                    continue
                if self.inStringFlag and char == '\t':
                    char = ' '
                if char == '\"':
                    self.inStringFlag = not self.inStringFlag
                newline += char
                continue

        return newline





    def processLine(self, line):
        line = line.replace("\r\n", "")
        line = line.replace("\n", "")

        line = self.relevantLines(line)
        res = ""
        flag = False
        for i in range(len(line)):
            if not flag and line[i] in JackTokenizer.symbol_list:
                res += " " + line[i] + " "
            elif line[i] == '\"':
                flag = not flag
                res += line[i]
            else:
                res += line[i]
        return self.makeOneSpace(res)

    def goThroughLines(self):
        for index in range(len(self.lines)):
            self.lines[index] = self.processLine(self.lines[index])
        for index in range(len(self.lines)):
            self.lines[index] = self.lines[index].replace("\t","")
            if match("^[\s]*[\t]*$", self.lines[index]):
                pass
            else:
                splited = self.splitBySpace(self.lines[index])
                for token in splited:
                    self.tokens.append(token)

    def revealNext(self):
        if self.currIndex + 1 < len(self.tokens):
            return self.tokens[self.currIndex + 1]
        else:
            return None

    def revealTwoNext(self):
        if self.currIndex + 2 < len(self.tokens):
            return self.tokens[self.currIndex + 2]
        else:
            return None

    def getToken(self):
        return self.token
