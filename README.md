# UCREL Python API
> Python API to the <a href='http://ucrel-api.lancaster.ac.uk/'>UCREL Tool Chain.</a>


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
