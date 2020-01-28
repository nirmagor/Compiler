from JackTokenizer import *
from re import *


class CompilationEngine:
    op_list = ["+" , "-" , "*" , "/" , "&" , "|" , "<" , ">" , "="]

    un_op_list = ["-" , "~"]
    special_chars = dict()
    special_chars["<"] = "&lt;"
    special_chars[">"] = "&gt;"
    # special_chars['\"'] = "&quot;"
    special_chars["&"] = "&amp;"
    INDENT = "  "

    def __init__(self , inputFile , outputFile):
        self.outFile = outputFile
        self.tokenizer = JackTokenizer(inputFile)
        self.currToken = ""
        self.tabber = ""

    def compileClass(self):
        self.outFile.write(self.tabber +"<class>\n")
        self.tabber += self.INDENT
        self.currToken = self.tokenizer.getToken()
        # assuming first token is keyword class
        self.__writeKeyword()
        self.__advanceToken()
        # assuming next token is the class name
        self.__writeIdentifier()
        self.__advanceToken()
        # assuming next token is '{'
        self.__writeSymbol()
        if match("^[^}]+",self.tokenizer.revealNext()):
            self.compileClassVarDec()
            self.compileSubroutine()
        # assuming next token is '}'
        self.__advanceToken()
        self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</class>\n")

    def compileClassVarDec(self):

        while match("^(static|field)",self.tokenizer.revealNext()):
            self.outFile.write(self.tabber +"<classVarDec>\n")
            self.tabber += self.INDENT
            # we know next token is static or field
            self.__advanceToken()
            self.__writeKeyword()
            # we assume this will be type of the var
            self.__advanceToken()
            if match("(int|char|boolean)",self.currToken):
                self.__writeKeyword()
            else:
                self.__writeIdentifier()
            while match("[^;]+", self.tokenizer.revealNext()):
                if match("[,]", self.tokenizer.revealNext()):
                    self.__advanceToken()
                    self.__writeSymbol()
                # we assume this will be the var name
                self.__advanceToken()
                self.__writeIdentifier()
            self.__advanceToken()
            self.__writeSymbol()
            self.tabber = self.tabber[:-2]
            self.outFile.write(self.tabber +"</classVarDec>\n")


    def compileSubroutine(self):
        while match("(constructor|function|method)", self.tokenizer.revealNext()):
            self.outFile.write(self.tabber +"<subroutineDec>\n")
            self.tabber += self.INDENT
            self.__advanceToken()
            self.__writeKeyword()
            if match("(void|int|boolean|char)", self.tokenizer.revealNext()):
                self.__advanceToken()
                self.__writeKeyword()
            else:
                self.__advanceToken()
                self.__writeIdentifier()
            # assuming this will be subroutine name
            self.__advanceToken()
            self.__writeIdentifier()
            # assuming this will be '('
            self.__advanceToken()
            self.__writeSymbol()
            self.compileParameterList()
            # assuming this will be ')'
            self.__advanceToken()
            self.__writeSymbol()
            self.compileSubroutineBody()
            self.tabber = self.tabber[:-2]
            self.outFile.write(self.tabber +"</subroutineDec>\n")



    def compileParameterList(self):
        self.outFile.write(self.tabber +"<parameterList>\n")
        self.tabber += self.INDENT
        while match("[^)]+", self.tokenizer.revealNext()):
            if match("(int|boolean|char)", self.tokenizer.revealNext()):
                self.__advanceToken()
                self.__writeKeyword()
            else:
                self.__advanceToken()
                self.__writeIdentifier()
            # assuming this will be var name
            self.__advanceToken()
            self.__writeIdentifier()
            if match("[,]",self.tokenizer.revealNext()):
                self.__advanceToken()
                self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</parameterList>\n")

    def compileSubroutineBody(self):
        self.outFile.write(self.tabber +"<subroutineBody>\n")
        self.tabber += self.INDENT
        if match("[{]",self.tokenizer.revealNext()):
            self.__advanceToken()
            self.__writeSymbol()
        if match("[^}]+", self.tokenizer.revealNext()):
            self.compileVarDec()
            self.compileStatements()
        # assuming this will be '}'
        self.__advanceToken()
        self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</subroutineBody>\n")

    def compileVarDec(self):

        while match("var", self.tokenizer.revealNext()):
            self.outFile.write(self.tabber +"<varDec>\n")
            self.tabber += self.INDENT
            self.__advanceToken()
            self.__writeKeyword()
            # assuming this will be type
            if match("(int|boolean|char)", self.tokenizer.revealNext()):
                self.__advanceToken()
                self.__writeKeyword()
            else:
                self.__advanceToken()
                self.__writeIdentifier()
            while match("[^;]+", self.tokenizer.revealNext()):
                if match("[,]", self.tokenizer.revealNext()):
                    self.__advanceToken()
                    self.__writeSymbol()
                self.__advanceToken()
                self.__writeIdentifier()
            # assuming this will be ;
            self.__advanceToken()
            self.__writeSymbol()
            self.tabber = self.tabber[:-2]
            self.outFile.write(self.tabber +"</varDec>\n")

    def compileStatements(self):
        self.outFile.write(self.tabber +"<statements>\n")
        self.tabber += self.INDENT
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
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</statements>\n")

    def subRoutineCall(self):
        # identifier was advanced already
        if match("[.]", self.tokenizer.revealNext()):
            # assuming this will be '.'
            self.__advanceToken()
            self.__writeSymbol()
            # assuming this will be subroutineName
            self.__advanceToken()
            self.__writeIdentifier()
        #assuming this will be '('
        self.__advanceToken()
        self.__writeSymbol()
        self.compileExpressionList()
        #assuming this will be ')'
        self.__advanceToken()
        self.__writeSymbol()
    

    def compileDo(self):  # 'do' subroutineCall ';'
        self.outFile.write(self.tabber +"<doStatement>\n")
        self.tabber += self.INDENT
        self.__advanceToken()
        self.__writeKeyword()
        #assuming this will be varName/className/subroutineName
        self.__advanceToken()
        self.__writeIdentifier()
        self.subRoutineCall()
        # assuming this will be ;
        self.__advanceToken()
        self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</doStatement>\n")

    def compileLet(self):
        self.outFile.write(self.tabber +"<letStatement>\n")
        self.tabber += self.INDENT
        self.__advanceToken()
        self.__writeKeyword()
        # assuming this will be var name
        self.__advanceToken()
        self.__writeIdentifier()
        if match("[[]", self.tokenizer.revealNext()):
            self.__advanceToken()
            self.__writeSymbol()
            self.compileExpression()
            # assuming this will be ']'
            self.__advanceToken()
            self.__writeSymbol()
        # assuming this will be '='
        self.__advanceToken()
        self.__writeSymbol()
        self.compileExpression()
        # assuming this will be ;
        self.__advanceToken()
        self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</letStatement>\n")

    def compileWhile(self):  # 'while' '(' 'expression' ')' '{' 'statments' '}'
        self.outFile.write(self.tabber +"<whileStatement>\n")
        self.tabber += self.INDENT
        self.__advanceToken()
        self.__writeKeyword()
        #assuming this will be '('
        self.__advanceToken()
        self.__writeSymbol()
        self.compileExpression()
        #assuming this will be ')'
        self.__advanceToken()
        self.__writeSymbol()
        #assuming this will be '{'
        self.__advanceToken()
        self.__writeSymbol()
        self.compileStatements()
        #assuming this will be '}'
        self.__advanceToken()
        self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber + "</whileStatement>\n")

    def compileReturn(self):  # 'return' expression? ';'
        self.outFile.write(self.tabber +"<returnStatement>\n")
        self.tabber += self.INDENT
        self.__advanceToken()
        self.__writeKeyword()
        if match("[^;]+",self.tokenizer.revealNext()):
            self.compileExpression()
        # assuming this will be ;
        self.__advanceToken()
        self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</returnStatement>\n")

    def compileIf(self):  # if ( exprssion ) { statments } (else { statments }) ?
        self.outFile.write(self.tabber +"<ifStatement>\n")
        self.tabber += self.INDENT
        self.__advanceToken()
        self.__writeKeyword()
        # assuming this will be '('
        self.__advanceToken()
        self.__writeSymbol()
        self.compileExpression()
        # assuming this will be ')'
        self.__advanceToken()
        self.__writeSymbol()
        # assuming this will be '{'
        self.__advanceToken()
        self.__writeSymbol()
        self.compileStatements()
        # assuming this will be '};
        self.__advanceToken()
        self.__writeSymbol()
        if match("(else)", self.tokenizer.revealNext()):
            self.__advanceToken()
            self.__writeKeyword()
            # assuming this will be '{'
            self.__advanceToken()
            self.__writeSymbol()
            self.compileStatements()
            #assuming this will be '}'
            self.__advanceToken()
            self.__writeSymbol()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</ifStatement>\n")

    def compileExpression(self):
        counter = 0
        while match("[^,)}\];]+",self.tokenizer.revealNext()):
            if counter == 0:
                self.outFile.write(self.tabber +"<expression>\n")
                self.tabber += self.INDENT
                counter = 1
            self.outFile.write(self.tabber +"<term>\n")
            self.tabber += self.INDENT
            self.compileTerm()
            self.tabber = self.tabber[:-2]
            self.outFile.write(self.tabber +"</term>\n")
            if self.tokenizer.revealNext() in self.op_list:
                self.__advanceToken()
                self.__writeSymbol()
        if counter != 0:
            self.tabber = self.tabber[:-2]
            self.outFile.write(self.tabber +"</expression>\n")

    def compileTerm(self):
        self.__advanceToken()
        if match("KEYWORD", self.tokenizer.tokenType()):
            self.__writeKeyword()
        elif match("STRING_CONST", self.tokenizer.tokenType()):
            self.__writeStringConstant()
        elif match("INT_CONST", self.tokenizer.tokenType()):
            self.__writeIntConstant()
        elif match("IDENTIFIER", self.tokenizer.tokenType()):
            self.__writeIdentifier()
            if match("[\[]", self.tokenizer.revealNext()):
                self.__advanceToken()
                self.__writeSymbol()
                self.compileExpression()
                #assuming this will be ']'
                self.__advanceToken()
                self.__writeSymbol()
            elif match("([.]|[(])",self.tokenizer.revealNext()):
                self.subRoutineCall()
        elif match("SYMBOL", self.tokenizer.tokenType()):
            self.__writeSymbol()
            if match("[(]", self.currToken):
                self.compileExpression()
                #assuming this will be ')'
                self.__advanceToken()
                self.__writeSymbol()
            else:
                self.outFile.write(self.tabber +"<term>\n")
                self.tabber += self.INDENT
                self.compileTerm()
                self.tabber = self.tabber[:-2]
                self.outFile.write(self.tabber +"</term>\n")
                


    def compileExpressionList(self):
        self.outFile.write(self.tabber +"<expressionList>\n")
        self.tabber += self.INDENT
        while match("[^)]+", self.tokenizer.revealNext()):
            if match("[,]",self.tokenizer.revealNext()):
                self.__advanceToken()
                self.__writeSymbol()
            self.compileExpression()
        self.tabber = self.tabber[:-2]
        self.outFile.write(self.tabber +"</expressionList>\n")

    def __writeSymbol(self):
        token = self.currToken
        if self.currToken in CompilationEngine.special_chars:
            token = CompilationEngine.special_chars[self.currToken]
        self.outFile.write(self.tabber +"<symbol> " + token + " </symbol>\n")

    def __writeIdentifier(self):
        self.outFile.write(self.tabber +"<identifier> " + self.currToken + " </identifier>\n")

    def __writeKeyword(self):
        self.outFile.write(self.tabber +"<keyword> " + self.currToken + " </keyword>\n")

    def __writeStringConstant(self):
        token = self.currToken
        token = self.currToken.replace("\"", "")
        self.outFile.write(self.tabber +"<stringConstant> " + token + " </stringConstant>\n")

    def __writeIntConstant(self):
        self.outFile.write(self.tabber +"<integerConstant> " + self.currToken + " </integerConstant>\n")

    def __advanceToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            self.currToken = self.tokenizer.getToken()
