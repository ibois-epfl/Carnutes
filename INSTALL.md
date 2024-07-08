To use this tool (we avoid the term plugin, as it isn't a proper plugin), you need to follow those two steps. This solution is not very elegant but is adapted to the time available for this project 🏃‍♀️‍➡️. 

# 2-step install:

1)  Add the content of the Carnutes folder with the codes to the "scripts" folder of Rhino. (At every new release, the old files must be deleted)

MacOS:
```
/Users/<your_username>/Library/Application support/McNeel/Rhinoceros/8.0/scripts
```

NB: For unexplicable reasons, in the GUI, Apple changes the naming of "Library" in function of the system language, but not on the terminal. For example if our OS is in French and you want to find the folder using the "Finder", replace "Library" with "Bibliothèque"...

Windows:

```
C:\Users\<your_username>\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts
```

2) Drag-and-drop the .rhc container file in Rhino. This file contains the metadata that creates the "Carnutes" toolbar tab with all the buttons calling the different scripts.

This solution is inelegant but corresponds to the developement time allocated to this project. If you know a better way, create an issue and tell me how to improve it 😇. The main issues are that a proper version tracking is inexistant, and installation is not super user friendly.

# DEPS
There is no need to install dependencies (in this case pip packages) yourself, as they are all included as requirement at the beginning of the .py files. This means that the python version shipped with Rhino will install the pip package automatically. For example, for [i-graph](https://igraph.org/) :

```python
#! python 3
#r: igraph

import igraph as ig

"""
code using the igraph library 
"""
```

The dependencies are nevertheless listed here: 

- [i-graph](https://igraph.org/) for connectivity of elements
