import importlib, sys
try:
    m = importlib.import_module('metadata.MICROBIAL_GROUPING')
    MG = getattr(m, 'MICROBIAL_GROUPING', None)
    if MG is None:
        print('MICROBIAL_GROUPING not found in module')
        sys.exit(2)
    print('Imported MICROBIAL_GROUPING OK, keys:', list(MG.keys())[:20])
except Exception as e:
    print('Import error:', repr(e))
    sys.exit(1)
