import numpy as np

def openbbsignals(filePath, *args):
    if len(args) == 0:
        skipLength = 0
        readLength = np.inf
    else:
        skipLength = args[0]
        readLength = args[1]
    
    fileName, extension = os.path.splitext(filePath)
    validName = matlab.lang.makeValidName(fileName)
    print('Loading PicoScenes SDR baseband signal file: ' + fileName + extension)
    bb_signal = loadBasebandSignalFile(filePath, skipLength, readLength)
    globals()[validName] = bb_signal
    print('Loaded variable name: ' + validName)

def loadBasebandSignalFile(bbFilePath, skipLength, readLength):
    fid = open(bbFilePath, 'rb')
    fileHeader = np.fromfile(fid, dtype=np.uint8, count=2).tobytes().decode('utf-8')
    bbFileVersion = np.fromfile(fid, dtype=np.uint8, count=2).tobytes().decode('utf-8')
    numDimensions = np.fromfile(fid, dtype=np.uint8, count=1)[0]
    dimensions = np.ones(numDimensions, dtype=np.int32)
    
    if ord(bbFileVersion[1]) - 48 == 1:
        for i in range(numDimensions):
            dimensions[i] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    elif ord(bbFileVersion[1]) - 48 == 2:
        for i in range(numDimensions):
            dimensions[i] = np.fromfile(fid, dtype=np.int64, count=1)[0]
    
    isComplexMatrix = np.fromfile(fid, dtype=np.uint8, count=1)[0] == ord('C')
    typeChar = np.fromfile(fid, dtype=np.uint8, count=1)[0]
    typeBits = np.fromfile(fid, dtype=np.uint8, count=1)[0]
    majority = SignalStorageMajority(np.fromfile(fid, dtype=np.uint8, count=1)[0])
    
    if any(fileHeader != 'BB') or (any(bbFileVersion != 'v1') and any(bbFileVersion != 'v2')):
        raise ValueError(' ** incompatible .bbsignals file format! **')
    
    if typeChar == ord('D'):
        precision = 'float'
    elif typeChar == ord('F'):
        precision = 'float'
    elif typeChar == ord('U'):
        precision = 'uint'
    elif typeChar == ord('I'):
        precision = 'int'
    elif typeChar == ord('L'):
        precision = 'uint'
    
    precision = precision + str(typeBits) + '=>' + precision
    
    skipBytes = typeBits * skipLength / 8 * 2**isComplexMatrix * dimensions[1]
    readBytes = readLength * 2**isComplexMatrix * dimensions[1]
    fid.seek(skipBytes, 1)
    data = np.fromfile(fid, dtype=precision, count=readBytes)
    corruptedLength = np.remainder(data.size, 2**isComplexMatrix * dimensions[1])
    data = data[:data.size - corruptedLength]
    
    if data.dtype == np.int16:
        data = data.astype(float) / 32768
    elif data.dtype == np.int8:
        data = data.astype(float) / 256
    
    if isComplexMatrix:
        data = data.reshape(-1, 2)
        data = data[:, 0] + 1j * data[:, 1]
    
    if dimensions[0] < 0: # streaming file
        dimensions[0] = data.size / np.prod(dimensions[1:])
    
    if majority == SignalStorageMajority.ColumnMajor and dimensions[1] > 1:
        data = data.reshape(dimensions)
    elif majority == SignalStorageMajority.RowMajor and dimensions[1] > 1:
        data = data.reshape(np.flip(dimensions))
        data = np.transpose(data, np.arange(data.ndim)[::-1])
    
    return data

