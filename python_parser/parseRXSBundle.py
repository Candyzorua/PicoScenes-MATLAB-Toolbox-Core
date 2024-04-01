import numpy as np
import read_rxs_log

def parseRXSBundle(rxsBundleFilePathOrRxsCells, maxRxSLogNumber=np.iinfo(np.int32).max):
    if isinstance(rxsBundleFilePathOrRxsCells, str):
        rxs_cells = read_rxs_log(rxsBundleFilePathOrRxsCells, maxRxSLogNumber)
    elif isinstance(rxsBundleFilePathOrRxsCells, list):
        rxs_cells = rxsBundleFilePathOrRxsCells

    if not rxs_cells:
        rxsBundles = []
        return rxsBundles

    rtt_num = [len(x) for x in rxs_cells]
    rtt_outlierIndex = np.where(rtt_num != np.median(rtt_num))[0]
    tones_num = [x[0].CSI.NumTones * (x[0].CSI.NumTx + x[0].CSI.NumESS) * x[0].CSI.NumRx * x[0].CSI.NumCSI for x in rxs_cells]
    tones_outlierIndex = np.where(tones_num != np.median(tones_num))[0]
    outlierIndex = np.unique(np.concatenate((rtt_outlierIndex, tones_outlierIndex)))
    if len(outlierIndex) < len(rxs_cells) * 0.05:
        rxs_cells = [x for i, x in enumerate(rxs_cells) if i not in outlierIndex]

    rxs_struct_array = np.concatenate(rxs_cells, axis=1).T
    rxsBundles = [structRecursiveMerge(rxs_struct_array[:, i]) for i in range(rxs_struct_array.shape[1])]

    return rxsBundles

def structRecursiveMerge(structArray):
    mergedStruct = {}
    fieldNames = structArray.dtype.names
    numElement = structArray.shape[0]
    for fieldName in fieldNames:
        nameString = fieldName

        try:
            if not np.isscalar(structArray[nameString][0]) and np.issubdtype(structArray[nameString][0].dtype, np.number):
                mergedData = np.concatenate([x[nameString].reshape(1, -1) for x in structArray]).ravel()
            else:
                mergedData = np.concatenate([x[nameString] for x in structArray])
        except Exception as e:
            print(f'structRecursiveMerge fails on data merging for the field: {nameString}')
            raise e
        numColumn = mergedData.size // numElement

        if np.issubdtype(mergedData.dtype, np.number) and mergedData.ndim == 1:
            mergedData = mergedData.reshape(numElement, numColumn)
        elif np.issubdtype(mergedData.dtype, np.object):
            mergedData = structRecursiveMerge(mergedData)
        elif isinstance(mergedData, list):
            mergedData = np.array(mergedData).T

        mergedStruct[nameString] = mergedData

    return mergedStruct