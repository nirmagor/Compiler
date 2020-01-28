import sys
import CompilationEngine
import os


def main():
    path=os.path.abspath(sys.argv[1])
    if os.path.isdir(path):
        files=os.listdir(path)
        for file in files:
            file=path+"/"+file
            if file.endswith("jack"):
                handleFile(file)
    elif path.endswith(".jack"): # a single file
        handleFile(path)

def handleFile(path):
    outputPath=path.replace(".jack",".xml")
    file=open(path,'r')
    outFile=open(outputPath,'w')
    compilation =CompilationEngine.CompilationEngine(file.readlines(),outFile)
    compilation.compileClass()
    file.close()
    outFile.close()

if (__name__ == "__main__"):
    main()
