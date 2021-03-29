# UCREL Python API
> Python API to the <a href='http://ucrel-api.lancaster.ac.uk/'>UCREL Tool Chain.</a>


<p align="center">
    <a href="https://colab.research.google.com/github/UCREL/ucrel-python-api/blob/main/module_notebooks/index.ipynb" target="_blank">
        <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab">
    </a>
</p>
<p align="center">
    <a href="https://github.com/UCREL/ucrel-python-api/blob/main/LICENSE"> <img alt="License" src="https://img.shields.io/github/license/ucrel/ucrel-python-api?color=orange"></a>
</p>

<p align="center">
    <a href="https://pypi.org/project/ucrel_api/"> <img alt="PyPi" src="https://img.shields.io/pypi/v/ucrel_api"> </a>
    <a href="https://pypi.org/project/ucrel_api/"> <img alt="Supported Python Versions" src="https://img.shields.io/pypi/pyversions/ucrel_api"> </a>
</p>

## Install

`pip install ucrel_api`

```python
%%capture
# If you are running this in Google Colab:
! pip install ucrel_api
```

## Examples

### Connecting to the API

You can connect to the public [UCREL Tool Chain](http://ucrel-api.lancaster.ac.uk/) like so:

```python
from ucrel_api.api import UCREL_API

api = UCREL_API('a.moore@lancaster.ac.uk', 'http://ucrel-api.lancaster.ac.uk')
```

As shown it requires an email address and server address, of which the server address in this case is the address of the public UCREL Tool Chain. The email address is only used to detect misuse of the public UCREL Tool Chain. Please be kind to this public server, UCREL provides it free of charge and is not intended for extremely large numbers of repeated submission from the same site. 

### USAS

Once we have an API insance we can use it to call the [USAS tagger](http://ucrel-api.lancaster.ac.uk/usas/tagger.html):

```python
text_to_process = ('Hope you have a nice day. '
                   'Works with SGML entities e.g. 5 > 4.'
                   'Also with MWE like New York.')
ucrel_doc = api.usas(text_to_process)
for index, sentence in enumerate(ucrel_doc.sentences):
    print(f'Sentence {index}')
    for token in sentence:
        print(token)
    if index == 0 or index == 1:
        print('\n')
```

    Sentence 0
    UCREL Token: Hope	Lemma: hope	POS tag: VV0	USAS tag: X2.6+
    UCREL Token: you	Lemma: you	POS tag: PPY	USAS tag: Z8mf
    UCREL Token: have	Lemma: have	POS tag: VH0	USAS tag: A9+
    UCREL Token: a	Lemma: a	POS tag: AT1	USAS tag: Z5
    UCREL Token: nice	Lemma: nice	POS tag: JJ	USAS tag: O4.2+
    UCREL Token: day	Lemma: day	POS tag: NNT1	USAS tag: T1.3
    UCREL Token: .	Lemma: PUNC	POS tag: .
    
    
    Sentence 1
    UCREL Token: Works	Lemma: works	POS tag: NN	USAS tag: I4/H1c
    UCREL Token: with	Lemma: with	POS tag: IW	USAS tag: Z5
    UCREL Token: SGML	Lemma: sgml	POS tag: NP1	USAS tag: Z99
    UCREL Token: entities	Lemma: entity	POS tag: NN2	USAS tag: O2
    UCREL Token: e.g.	Lemma: e.g.	POS tag: REX	USAS tag: A4.1
    UCREL Token: 5	Lemma: 5	POS tag: MC	USAS tag: N1
    UCREL Token: >	Lemma: >	POS tag: FO	USAS tag: Z99
    UCREL Token: 4	Lemma: 4	POS tag: MC	USAS tag: N1
    UCREL Token: .	Lemma: PUNC	POS tag: .
    
    
    Sentence 2
    UCREL Token: Also	Lemma: also	POS tag: RR	USAS tag: N5++
    UCREL Token: with	Lemma: with	POS tag: IW	USAS tag: Z5
    UCREL Token: MWE	Lemma: mwe	POS tag: NP1	USAS tag: Z99
    UCREL Token: like	Lemma: like	POS tag: II	USAS tag: Z5
    UCREL Token: New	Lemma: new	POS tag: NP1	USAS tag: Z2	MWE tag: 2.2.1
    UCREL Token: York	Lemma: york	POS tag: NP1	USAS tag: Z2	MWE tag: 2.2.2
    UCREL Token: .	Lemma: PUNC	POS tag: .


The return of the `UCREL_API.usas` api call is a `UCREL_Doc` instance, the `UCREL_Doc` instance is made up of `UCREL_Token`s. The USAS tagger provides both token level attributes and sentence segmentation as shown above.

## Development

If you would like to develop on this library. Clone the repository and then install the regular requirements and the development requirements using:

``` bash
pip install -e .[dev]
```

[The `-e` is an editable flag](http://codumentary.blogspot.com/2014/11/python-tip-of-year-pip-install-editable.html) meaning that if you change anything in the library locally Python will keep track on those changes.

### Package is created with nbdev

**Note** as it is created with nbdev the code and documentation is generated from the notebooks that are within the [./module_notebooks folder](./module_notebooks).

**Note** need to run the following once: `nbdev_install_git_hooks`: ["This will set up git hooks which will remove metadata from your notebooks when you commit, greatly reducing the chance you have a conflict."](https://nbdev.fast.ai/tutorial.html#Install-git-hooks-to-avoid-and-handle-conflicts)

The main workflow is the following:

1. Edit the notebook(s) you want within [./module_notebooks folder.](./module_notebooks) **The README is generated from the [./module_notebooks/index.ipynb file.](./module_notebooks/index.ipynb)**
2. Run `nbdev_build_lib` to convert the notebook(s) into a Python module, which in this case will go into the [./ucrel_api folder](./ucrel_api). **Note** if you created a function in one python module and want to use it in another module then you will need to run `nbdev_build_lib` first, as that python module code needs to be transfered from the [./module_notebooks folder.](./module_notebooks) into the [./ucrel_api folder](./ucrel_api).
3. Create the documentation using `nbdev_build_docs`.
4. **Optionally** if you created tests run them using `make test`. When you do add tests in the notebooks you will need to import the function from the module and not rely on the function already expressed in the notebook, this is to ensure that code coverage is calculated correctly.
5. **Optionally** if you would like to see the documentation locally see the [sub-section below.](#local-documentation)
6. Git add the relevant notebook(s), python module code, and documentation.

### Local documentation

The documentation can be ran locally via a docker container. The easiest way to run this container is through the make command:

``` bash
make docker_docs_serve
```

**NOTE** This documentation does not update automatically, so it requires re-running this make command each time you want to see an updated version of the documentation.

### PYPI Package release

To release an updated version of the package:

1. Change the version number in [./settings.ini](./settings.ini)
2. Build the library using `nbdev_build_lib`
3. Then make the package and upload it to PYPI using `make release`

## Acknowledgement

The work has been funded by the [UCREL research centre at Lancaster University](http://ucrel.lancs.ac.uk/).
