import os
import warnings
import read_rxs_log
import parseRXSBundle

def opencsi(filePath):
    _, fileName, extension = os.path.splitext(filePath)
    bundleValidName = fileName

    print('Start parsing PicoScenes CSI file:', fileName, extension)

    cells = read_rxs_log(filePath)
    try:
        bundle = parseRXSBundle(cells)
        if isscalar(bundle):
            bundle[0].BundleName = bundleValidName
        else:
            if len(bundle) == 2:
                bundle[0].BundleName = bundleValidName + '.backward'
                bundle[1].BundleName = bundleValidName + '.forward'
        mergeAcrossCells = True
    except:
        warnings.off('backtrace')
        warnings.warn('The bundled parsing stage of [' + fileName + extension + '] fails. The extracted data returns in the basic cell form. See the document <a href = "https://ps.zpj.io/matlab.html#structures-of-the-picoscenes-tx-and-rx-frames">The Raw Parsing & Bundled Parsing</a> for more information.')
        warnings.on('backtrace')
        bundle = cells
        mergeAcrossCells = False

    if bundle and mergeAcrossCells and 'RXSBundle' in globals() and 'RTRXSBundle' in globals():
        try:
            bundle = [RXSBundle(x) for x in bundle]
            if len(bundle) == 2:
                bundle = RTRXSBundle(bundle)
        except:
            warnings.warn('failed to convert raw bundles to RXSBundle. The extracted data returns in the merged format.')

    globals()[bundleValidName] = bundle
    globals()['latest'] = bundle
    print(bundleValidName)

    currentDir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))  # change the working directory to the folder of this file.
    path2ProtocolHandler = os.path.join(os.getcwd(), '..', '..', 'utils', 'ProtocolHandler')
    if os.path.isdir(path2ProtocolHandler):
        protocolList = [file for file in os.listdir(path2ProtocolHandler) if file.endswith('.m')]
        for file in protocolList:
            _, mName = os.path.splitext(file)
            eval(mName + '("' + bundleValidName + '")')

    os.chdir(currentDir)

    if not nargout:
        bundle = []
    return bundle, bundleValidName