# Compiler
This project introduce the Jack language compiler.
The project featured string parsing, and understanding the LL2 grammar of an object oriented language.


Project Files:
1. JackCompiler.py : responsible for taking JACK files and calling the compilation engine.
2. CompilationEngine.py: using the JackTokenizer, SymbolTable and the VMWriter to take a token (or several), keep track of the scope's variables and write a VM code to the compatibles VM files. 
3.JackTokenizer.py: generates tokens out of a given JACK file. 
4.SymbolTable.py: creates a table of variables and objects for a subroutine and for the JACK class.
5.VMWriter.py: responisble for generating the VM code.

Project's flow: 

JACK file/s -> JackCompiler -> CompilationEngine -> VM files

