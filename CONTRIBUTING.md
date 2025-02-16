As this project is seen as an experiment in parallel to an architecture studio, this repo is not going to be maintained on the long term. Another repository will be opened when the long-term code is developped, as part of Damien Gilliard's PhD thesis. Therefore, any contribution made by outside people is welcome but keep in mind the "one shot" nature of this repository.

# Contributing
To contribute to this repo, open a new branch, create a pull request, push your modifications, and explain in the thread what you want to change / add.

The commit message guidelines are:
```bash
git commit -m "feat:<description>"        <--- for adding new elements, real improvements...
git commit -m "fix:<description>"         <--- for fixing (errors, typos)
```
Additionally, the `<description>` should start with "wip" if the changes commited are work in progress.

The description of the pull request should ideally contain:
- An explicit name. e.g. "improvement of registration of tree skeleton using pcl ICP registration" , and not "registration icp pcl"
- A description in a few lines of the changes made.
- A check if a test was adapted or created
- If it is linked to an issue, mark it as such in the Developmement section of the PR.
- As long as it is under development, mark it as Draft

## Pre-commits
We recommand the usage of pre-commits to make sure the code is consistently formatted:
Activate the conda environment provided with Carnutes, then hook pre-commit to git:
```bash
cd your/installation/path/to/Carnutes
conda env create -f ./environment.yml
conda activate Carnutes

pre-commit install
pre-commit run --all-files # This is simply make sure everything is well formatted, not only the files you commited to
```

# Naming convention
All code is in python
[usual python naming convention](https://peps.python.org/pep-0008/#naming-conventions)
We recommand using [pre-commit](https://pre-commit.com/). It's easy to set up and will check the code you commit and modify it to make it cleaner, before you push it.

```python
# variables:
my_variable

# functions and class methods:
my_function()

# classes:
MyClass

# constants:
MY_PI = 3.1415

# private things
_my_private_attribute
_my_private_method()
```

# Documentation
As this project is limited in time and volume, docstring are deemed sufficient for code documentation, with an additional .md file describing the general logic.

```python
class MyClass(object):
    """
    My class is amazing
    :param type something: something needed to instanciate an object of MyClass
    """
    def __init__(self, something):
        self.something = something
    def do_a_lot(self, with_little):
        """
        Does a lot using little
        :param: with_little: int
            little, with wich a lot is done
        :return: a_lot: int
            a lot done with little
        """
        a_lot = 1
        return a_lot
```
