To use this tool (we avoid the term plugin, as it isn't a proper plugin), you need to follow those two steps. This solution is not very elegant but is adapted to the time available for this project 🏃‍♀️‍➡️. 

# 2-step install:
1) Add the src folder with the codes to the "scripts" folder of Rhino. (At every new release, the old files must be deleted). Please note that the Library (MacOS) and AppData (Windows) folders are "hidden folders". On MacOS press command+shift+. to reveal the hidden folders. On Windows 10 or 11, [see this link](https://support.microsoft.com/en-us/windows/view-hidden-files-and-folders-in-windows-97fbc472-c603-9d90-91d0-1166d1d9f4b5#WindowsVersion=Windows_11) 

Note that the "script" folder in the "8.0" folder might be missing, in which case you have to create it, respecting the exact spelling.

MacOS path:
```
/Users/<your_username>/Library/Application support/McNeel/Rhinoceros/8.0/scripts
```

NB: For unexplicable reasons, in the GUI, Apple changes the naming of "Library" in function of the system language, but not on the terminal. For example if our OS is in French and you want to find the folder using the "Finder", replace "Library" with "Bibliothèque"...

Windows path:

```
C:\Users\<your_username>\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts
```

For each `function_<>.py`, change the `admin` by your user name. This step is particularly not elegant, but until pip packages via Rhino are not resolved, this is the way to go if you want to avoid creating a fully fledged plugin. 

2) Drag-and-drop the .rhc container file ( [Download link](https://github.com/ibois-epfl/Carnutes/raw/main/Carnutes.rhc) ). This file contains the metadata that creates the "Carnutes" toolbar tab with all the buttons calling the different scripts.

This solution is inelegant but corresponds to the developement time allocated to this project. If you know a better way, create an issue and tell me how to improve it 😇. The main issues are that a proper version tracking is inexistant, and installation is not super user friendly.

# Dependencies
There is no need to install dependencies as they are all installed automatically using the `# r: <package>`

The dependencies are nevertheless listed here: 

- [numpy (1.26.4)](https://numpy.org/) for basic mathematics. Note that [numpy 2.0.0 is not compatible with open3d 0.18.0](https://github.com/isl-org/Open3D/issues/6840)
- [i-graph (0.11.6)](https://igraph.org/) for connectivity of elements
- [open3d (0.18.0)](https://www.open3d.org/) for basic point cloud IO
- [ZODB (6.0)](https://zodb.org/en/latest/) for the database of tree trunks


# Create your own database
To create your own database with another dataset, you can activate the conda environment (assuming you have [Conda](https://docs.conda.io/projects/conda/en/latest/index.html) installed on your computer), by running the following commands from the Carnutes root directory:

```bash
conda env create -f environment.yml
conda activate Carnutes
```

Navigate to the src directory: 

```bash
cd src
```

And run the python script with: 

MacOS:

```bash
/Users/<your_username>/anaconda3/envs/database_creation/bin/python database_creator.py
```

Windows: 

```bash
C:\Users\<your_username>\anaconda3\envs\database_creation\python.exe .\database_creator.py
```