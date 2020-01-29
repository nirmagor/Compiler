from JackTokenizer import *
from re import *
from VMWriter import *
from SymbolTable import *


class CompilationEngine:
    op_list = ["+" , "-" , "*" , "/" , "&" , "|" , "<" , ">" , "="]
    un_op_list = ["-" , "~"]

    un_op_dic = {"-": "NEG", "~":"NOT"}
    kind_dic = {"VAR":"LOCAL", "ARG":"ARG", "STATIC":"STATIC", "FIELD":"THIS"}
    op_dic = {"+": "ADD", "-":"SUB", "=":"EQ", ">":"GT", "<":"LT", "|":"OR", "&":"AND", "*":"MUL", "/":"DIV"}
    special_chars = dict()
    special_chars["<"] = "&lt;"
    special_chars[">"] = "&gt;"
    # special_chars['\"'] = "&quot;"
    special_chars["&"] = "&amp;"
    INDENT = "  "

    def __init__(self , inputFile , outputFile):
        # self.outFile = outputFile
        self.tokenizer = JackTokenizer(inputFile)
        self.vmwriter = VMWriter(outputFile)
        self.outFile = outputFile
        self.currToken = ""
        self.tabber = ""

        self.argumentsCounter = 0


    def compileClass(self):
        self.symbolTable = SymbolTable()
        self.currToken = self.tokenizer.getToken()
        # assuming first token is keyword class
        self.__advanceToken()
        # assuming next token is the class name
        self.thisType = self.currToken
        self.__advanceToken()
        # assuming next token is '{'
        if match("^[^}]+",self.tokenizer.revealNext()):
            self.compileClassVarDec()
            self.compileSubroutine()
        # assuming next token is '}'
        self.__advanceToken()
        self.vmwriter.close()

    def compileClassVarDec(self):

        while match("^(static|field)",self.tokenizer.revealNext()):
            # we know next token is static or field
            self.__advanceToken()
            kind = self.currToken.upper()
            # we assume this will be type of the var
            self.__advanceToken()
            typeVar = self.currToken
            while match("[^;]+", self.tokenizer.revealNext()):
                if match("[,]", self.tokenizer.revealNext()):
                    self.__advanceToken()
                # we assume this will be the var name
                self.__advanceToken()
                name = self.currToken
                self.symbolTable.define(name, typeVar, kind)
            self.__advanceToken()


    def compileSubroutine(self):
        while match("(constructor|function|method)", self.tokenizer.revealNext()):
            self.ifCounter = 0
            self.whileCounter = 0
            self.symbolTable.startSubroutine()
            self.__advanceToken()
            self.subroutineKind = self.currToken
            if match("method",self.currToken):
                self.symbolTable.define("this", self.thisType, "ARG")

            self.__advanceToken()
            self.subroutineType = self.currToken
            # assuming this will be subroutine name
            self.__advanceToken()
            self.subroutineName = self.currToken
            # assuming this will be '('
            self.__advanceToken()
            self.compileParameterList()
            # assuming this will be ')'
            self.__advanceToken()
            self.compileSubroutineBody()




    def compileParameterList(self):

        while match("[^)]+", self.tokenizer.revealNext()):
            self.__advanceToken()
            typeArg = self.currToken
            # assuming this will be var name
            self.__advanceToken()
            nameArg = self.currToken
            self.symbolTable.define(nameArg, typeArg, "ARG")
            if match("[,]",self.tokenizer.revealNext()):
                self.__advanceToken()

    def compileSubroutineBody(self):
        if match("[{]",self.tokenizer.revealNext()):
            self.__advanceToken()
        if match("[^}]+", self.tokenizer.revealNext()):
            self.compileVarDec()
            nLocal = self.symbolTable.varCount("VAR")
            self.vmwriter.writeFunction(self.thisType + '.' + self.subroutineName, nLocal)
            if match("method",self.subroutineKind):
                self.vmwriter.writePush("ARG", 0)
                self.vmwriter.writePop("POINTER", 0)
            elif match("constructor", self.subroutineKind):
                fieldCounter = self.symbolTable.varCount("FIELD")
                self.vmwriter.writePush("CONST", fieldCounter)
                self.vmwriter.writeCall("Memory.alloc", 1)
                self.vmwriter.writePop("POINTER", 0)
            self.compileStatements()
        # assuming this will be '}'
        self.__advanceToken()

    def compileVarDec(self):

        while match("var", self.tokenizer.revealNext()):

            self.__advanceToken()
            kind = self.currToken.upper()
            # assuming this will be type
            self.__advanceToken()
            typeVar = self.currToken
            while match("[^;]+", self.tokenizer.revealNext()):
                if match("[,]", self.tokenizer.revealNext()):
                    self.__advanceToken()
                # assuming this will be the var name
                self.__advanceToken()
                nameVar = self.currToken
                self.symbolTable.define(nameVar, typeVar, kind)
            # assuming this will be ;
            self.__advanceToken()


    def compileStatements(self):
        while match("(let|do|if|while|return)", self.tokenizer.revealNext()):
            if match("(let)", self.tokenizer.revealNext()):
                self.compileLet()
            elif match("(do)", self.tokenizer.revealNext()):
                self.compileDo()
            elif match("(if)", self.tokenizer.revealNext()):
                self.compileIf()
            elif match("(while)", self.tokenizer.revealNext()):
                self.compileWhile()
            elif match("(return)", self.tokenizer.revealNext()):
                self.compileReturn()

    def subRoutineCall(self):
        numArg = 0
        # identifier was advanced already
        name = self.currToken
        remember = 0
        if match("[.]", self.tokenizer.revealNext()):
            if self.symbolTable.kindOf(name):
                kind = self.kind_dic[self.symbolTable.kindOf(name)]
                index = self.symbolTable.indexOf(name)
                self.vmwriter.writePush(kind, index)
                remember += 1
                name = self.symbolTable.typeOf(name)
            # assuming this will be '.'
            self.__advanceToken()
            name += self.currToken
            # assuming this will be subroutineName
            self.__advanceToken()
            name += self.currToken
        else:
            self.vmwriter.writePush("POINTER", 0)
            remember += 1
            name = self.thisType + '.' + name
        #assuming this will be '('
        self.__advanceToken()
        numArg = self.compileExpressionList()
        self.vmwriter.writeCall(name, numArg + remember)
        #assuming this will be ')'
        self.__advanceToken()


    

    def compileDo(self):  # 'do' subroutineCall ';'
        self.__advanceToken()
        #assuming this will be varName/className/subroutineName
        self.__advanceToken()
        self.subRoutineCall()
        # assuming this will be ;
        self.vmwriter.writePop("TEMP", 0)
        self.__advanceToken()


    def compileLet(self):
        self.__advanceToken()
        # assuming this will be var name
        self.__advanceToken()
        name = self.currToken
        kind = self.kind_dic[self.symbolTable.kindOf(name)]
        index = self.symbolTable.indexOf(name)
        arrayExp = False
        if match("[[]", self.tokenizer.revealNext()):
            arrayExp = True
            self.__advanceToken()
            self.compileExpression()
            self.vmwriter.writePush(kind, index)
            self.vmwriter.writeArithmetic("ADD")
            # assuming this will be ']'
            self.__advanceToken()
        # assuming this will be '='
        self.__advanceToken()
        self.compileExpression()
        if arrayExp:
            self.vmwriter.writePop("TEMP", 0)
            self.vmwriter.writePop("POINTER", 1)
            self.vmwriter.writePush("TEMP", 0)
            self.vmwriter.writePop("THAT", 0)
        else:
            self.vmwriter.writePop(kind, index)
        # assuming this will be ;
        self.__advanceToken()


    def compileWhile(self):  # 'while' '(' 'expression' ')' '{' 'statments' '}'
        currWhile = self.whileCounter
        self.whileCounter += 1
        self.__advanceToken()
        self.vmwriter.writeLabel("WHILE_EXP" + str(currWhile) )
        #assuming this will be '('
        self.__advanceToken()
        self.compileExpression()
        #assuming this will be ')'
        self.__advanceToken()
        self.vmwriter.writeArithmetic("NOT")
        self.vmwriter.writeIf("WHILE_END" + str(currWhile))
        #assuming this will be '{'
        self.__advanceToken()
        self.compileStatements()
        #assuming this will be '}'
        self.__advanceToken()
        self.vmwriter.writeGoTo("WHILE_EXP" + str(currWhile))
        self.vmwriter.writeLabel("WHILE_END" + str(currWhile))



    def compileReturn(self):  # 'return' expression? ';'
        self.__advanceToken()
        if match("[^;]+",self.tokenizer.revealNext()):
            self.compileExpression()
        # assuming this will be ;
        if match("void", self.subroutineType):
            self.vmwriter.writePush("CONST", 0)
        self.vmwriter.writeReturn()
        self.__advanceToken()


    def compileIf(self):  # if ( exprssion ) { statments } (else { statments }) ?
        curr_if = self.ifCounter
        self.ifCounter += 1
        self.__advanceToken()
        # assuming this will be '('
        self.__advanceToken()
        self.compileExpression()
        # assuming this will be ')'
        self.__advanceToken()
        self.vmwriter.writeIf("IF_TRUE" + str(curr_if))
        self.vmwriter.writeGoTo("IF_FALSE" + str(curr_if))
        self.vmwriter.writeLabel("IF_TRUE" + str(curr_if))
        # assuming this will be '{'
        self.__advanceToken()
        self.compileStatements()
        # assuming this will be '}'
        self.__advanceToken()

        if match("(else)", self.tokenizer.revealNext()):
            self.vmwriter.writeGoTo("IF_END" + str(curr_if))
            self.vmwriter.writeLabel("IF_FALSE" + str(curr_if))
            self.__advanceToken()
            # assuming this will be '{'
            self.__advanceToken()
            self.compileStatements()
            #assuming this will be '}'
            self.__advanceToken()
            self.vmwriter.writeLabel("IF_END" + str(curr_if))
        else:
            self.vmwriter.writeLabel("IF_FALSE" + str(curr_if))

    def compileExpression(self):
        relevantOp = None
        counter = 0
        while match("[^,)}\];]+",self.tokenizer.revealNext()):
            self.compileTerm()
            if counter != 0:
                self.vmwriter.writeArithmetic(self.op_dic[relevantOp])
            if self.tokenizer.revealNext() in self.op_list:
                self.__advanceToken()
                relevantOp = self.currToken
            counter += 1



    def compileTerm(self):
        self.__advanceToken()
        if match("KEYWORD", self.tokenizer.tokenType()):
            if match("(false|null)", self.currToken):
                self.vmwriter.writePush("CONST", 0)
            elif match("true", self.currToken):
                self.vmwriter.writePush("CONST", 0)
                self.vmwriter.writeArithmetic("NOT")
            else:
                self.vmwriter.writePush("POINTER", 0)
        elif match("STRING_CONST", self.tokenizer.tokenType()):
            constString = self.currToken.replace('\"', "")
            constString = constString.replace('\t', "\\t")
            constString = constString.replace('\b', "\\b")
            constString = constString.replace('\r', "\\r")
            constString = constString.replace('\n', "\\n")
            self.vmwriter.writeString(constString)
        elif match("INT_CONST", self.tokenizer.tokenType()):
            self.vmwriter.writePush("CONST", int(self.currToken))
        elif match("IDENTIFIER", self.tokenizer.tokenType()):
            if match("[\[]", self.tokenizer.revealNext()):
                name = self.currToken
                kind = self.kind_dic[self.symbolTable.kindOf(name)]
                index = self.symbolTable.indexOf(name)
                self.__advanceToken()
                self.compileExpression()
                self.vmwriter.writePush(kind, index)
                self.vmwriter.writeArithmetic("ADD")
                self.vmwriter.writePop("POINTER", 1)
                self.vmwriter.writePush("THAT", 0)
                #assuming this will be ']'
                self.__advanceToken()
            elif match("([.]|[(])",self.tokenizer.revealNext()):
                self.subRoutineCall()
            else:
                seg = self.kind_dic[self.symbolTable.kindOf(self.currToken)]
                index = self.symbolTable.indexOf(self.currToken)
                self.vmwriter.writePush(seg , index)

        elif match("SYMBOL", self.tokenizer.tokenType()):
            if match("[(]", self.currToken):
                self.compileExpression()
                #assuming this will be ')'
                self.__advanceToken()
            else:
                un_op = self.currToken
                self.compileTerm()
                self.vmwriter.writeArithmetic(self.un_op_dic[un_op])

                


    def compileExpressionList(self):
        argsCount = 0
        while match("[^)]+", self.tokenizer.revealNext()):
            if match("[,]",self.tokenizer.revealNext()):
                self.__advanceToken()
            self.compileExpression()
            argsCount += 1
        return argsCount


    def __advanceToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            self.currToken = self.tokenizer.getToken()
