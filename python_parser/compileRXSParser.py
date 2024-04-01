import os
import subprocess

def compileRXSParser(skipExtraParam=False):
    if not skipExtraParam:
        skipExtraParam = False
    currentDir = os.getcwd()
    checkRXSParsingCoreExists(currentDir)
    print('Compiling the MATLAB parser for PicoScenes .csi file ...')
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    extraParam = ''
    if not skipExtraParam and os.path.isdir(os.path.join(os.getcwd(), '..', '..', 'utils')):
        extraParam = open(os.path.join(os.getcwd(), '..', '..', 'utils', 'compileRXSParserExtraParam')).read()
    try:
        subprocess.run(['mex', '-silent', '-DBUILD_WITH_MEX', 'CXXFLAGS="$CXXFLAGS -std=c++2a -Wno-attributes -O3"', '-I../rxs_parsing_core', 'RXSParser.cxx', '../rxs_parsing_core/*.cxx', '../rxs_parsing_core/preprocess/generated/*.cpp', extraParam], check=True)
        print('Compilation done!')
    except subprocess.CalledProcessError:
        print('Exception caught! Use verbose mode to build again.')
        subprocess.run(['mex', '-v', '-DBUILD_WITH_MEX', 'CXXFLAGS="$CXXFLAGS -std=c++2a -Wno-attributes -O3"', '-I../rxs_parsing_core', 'RXSParser.cxx', '../rxs_parsing_core/*.cxx', '../rxs_parsing_core/preprocess/generated/*.cpp', extraParam])
    os.chdir(currentDir)

def checkRXSParsingCoreExists(currentDir):
    os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'rxs_parsing_core'))
    parserDir = os.getcwd()
    allFiles = [f for f in os.listdir(parserDir) if os.path.isfile(os.path.join(parserDir, f)) and f.endswith('.cxx')]
    if not allFiles:
        os.chdir(currentDir)
        raise Exception(f'The [{parserDir}] directory is empty! That means you have NOT cloned the PicoScenes MATALB Toolbox RECURSIVELY. Please refer to page <a href = "https://gitlab.com/wifisensing/PicoScenes-MATLAB-Toolbox-Core">PicoScenes MATLAB Toolbox Core</a> on how to clone the toolbox correctly.')
    os.chdir(currentDir)