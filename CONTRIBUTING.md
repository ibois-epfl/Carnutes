As this project is seen as an experiment in parallel to an architecture studio, this repo is not going to be maintained on the long term. Another repository will be opened when the long-term code is developped, as part of Damien Gilliard's PhD thesis. Therefore, any contribution made by outside people is welcome but keep in mind the "one shot" nature of this repository.

# Contributing
To contribute to this repo, open a new branch, create a pull request, push your modifications, and explain in the thread what you want to change / add. 

The commit message guidelines are:
```bash
git commit -m "ADD:<description>"         <--- for adding new elements
git commit -m "FIX:<description>"         <--- for fixing (errors, typos)
git commit -m "FLASH:<description>"       <--- quick checkpoint before refactoring
git commit -m "MILESTONE:<description>"   <--- for capping moment in development
git commit -m "CAP:<description>"         <--- for for less important milestones
git commit -m "UPDATE:<description>"      <--- for moddification to the same file
git commit -m "MISC:<description>"        <--- for any other reasons to be described
git commit -m "WIP:<description>"         <--- for not finished work
git commit -m "REFACTOR:<description>"    <--- for refactored code
git commit -m "MERGE:<description>"       <--- for merging operations
```

The description of the pull request should ideally contain: 
- An explicit name. e.g. "improvement of registration of tree skeleton using pcl ICP registration" , and not "registration icp pcl"
- A description in a few lines of the changes made.
- A check if a test was adapted or created
- If it is linked to an issue, mark it as such in the Developmement section of the PR.
- As long as it is under development, mark it as Draft

# Naming convention
All code is in python
[usual python naming convention](https://peps.python.org/pep-0008/#naming-conventions)

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
        :param int with_little: little, with wich a lot is done
        :return int a_lot: a lot done with little
        """
        a_lot = 1
        return a_lot
```