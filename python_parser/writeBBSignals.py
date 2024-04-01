import numpy as np

def writeBBSignals(signal, bbFileName, storageMajority, precision):
    if storageMajority is None:
        storageMajority = SignalStorageMajority.RowMajor
    
    if precision is None:
        precision = 'int16'
    
    bbFilePath = bbFileName + '.bbsignals'
    fid = open(bbFilePath, 'wb')
    fid.write(b'BB')
    fid.write(b'v2')
    fid.write(np.uint8(signal.ndim).tobytes())
    
    for i in range(signal.ndim):
        fid.write(np.uint64(signal.shape[i]).tobytes())
    
    if np.isreal(signal):
        fid.write(b'R')
    else:
        fid.write(b'C')
    
    if precision:
        if np.issubdtype(signal.dtype, np.floating) and precision.lower() == 'int16':
            signal = (signal * 32768).astype(precision)
        elif np.issubdtype(signal.dtype, np.floating) and precision.lower() == 'int8':
            signal = (signal * 256).astype(precision)
        else:
            signal = signal.astype(precision)
    
    if signal.dtype == np.float64:
        fid.write(b'D')
    elif np.issubdtype(signal.dtype, np.floating):
        fid.write(b'F')
    elif signal.dtype == np.bool:
        fid.write(b'L')
    elif signal.dtype == np.str:
        fid.write(b'C')
    elif np.issubdtype(signal.dtype, np.integer):
        typename = signal.dtype.name
        if typename[0] == 'u':
            fid.write(b'U')
        elif typename[0] == 'i':
            fid.write(b'I')
    
    if not precision:
        precision = signal.dtype.name
    
    fid.write(np.uint8(signal.itemsize * 8).tobytes())
    fid.write(np.uint8(storageMajority).tobytes())
    
    if storageMajority == SignalStorageMajority.ColumnMajor:
        if not np.isreal(signal):
            signalC = np.concatenate((np.real(signal), np.imag(signal)), axis=signal.ndim)
            signal = np.transpose(signalC, axes=(signal.ndim, *range(signal.ndim)))
        
        signal = np.reshape(signal, (-1, 1))
    else:
        if not np.isreal(signal):
            signal = np.concatenate((np.real(signal), np.imag(signal)), axis=signal.ndim)
        
        signal = np.transpose(signal, axes=np.flip(range(signal.ndim)))
        signal = np.reshape(signal, (-1, 1))
    
    fid.write(signal.tobytes())
    fid.close()

def sizeof(V):
    V = V.lower()
    if V in ['double', 'int64', 'uint64']:
        return 8
    elif V in ['single', 'int32', 'uint32']:
        return 4
    elif V in ['char', 'int16', 'uint16']:
        return 2
    elif V in ['logical', 'int8', 'uint8']:
        return 1
    else:
        raise ValueError('Class "{}" is not supported.'.format(V))