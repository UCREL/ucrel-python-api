import nbdev.test
import nbdev

def test_all_modules() -> None:
    pass
    #nbdev.test.test_nb('./module_notebooks/00_api.ipynb')
    #nbdev.test.test_nb('./module_notebooks/01_ucrel_token.ipynb')
    #nbdev.test.test_nb('./module_notebooks/02_ucrel_doc.ipynb')

#a = nbdev.export.read_nb('./module_notebooks/api.ipynb')
#import re
#for cell in a['cells']:
#    if cell['cell_type'] == 'code':
#        print(re.match(r'^(#.+)', cell['source']))
#        if re.match(r'^(#.+)', cell['source']):
#            print('done')
#print(len(a['cells']))