import os
import struct
import time
from python_parser.compileRXSParser import compileRXSParser

def read_rxs_log(filename, maxCSINumber=None):
    if maxCSINumber is None:
        maxCSINumber = float('inf')

    if not os.path.exists('RXSParser.mex'):
        compileRXSParser()

    if not os.path.exists('RXSParser.mex'):
        raise Exception('RXSParser compilation fails')

    ticStart = time.time()
    with open(filename, 'rb') as fp:
        resultBatchSize = 10000
        results = [None] * resultBatchSize
        count = 0

        while True:
            segmentLength_bytes = fp.read(4)
            if not segmentLength_bytes:
                break
            segmentLength = struct.unpack('I', segmentLength_bytes)[0] + 4
            fp.seek(-4, os.SEEK_CUR)
            bytes = fp.read(segmentLength)
            csi_entry = RXSParser(bytes)
            for i in range(len(csi_entry)):
                csi_entry[i]['MPDU'] = [csi_entry[i]['MPDU']]
            if not csi_entry:
                continue

            # if ParserPreference.getPreference().skipBasebandSignals:
            #     csi_entry = [{k: v for k, v in entry.items() if k != 'BasebandSignals'} for entry in csi_entry]

            if count == len(results):
                results.extend([None] * resultBatchSize)
            results[count] = csi_entry
            count += 1

            if count > maxCSINumber:
                break

    results = results[:count]
    print(f'{len(results)} PicoScenes frames are decoded in {time.time() - ticStart} seconds.')

