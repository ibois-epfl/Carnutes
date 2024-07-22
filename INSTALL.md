To use this tool (we avoid the term plugin, as it isn't a proper plugin), you need to follow those two steps. This solution is not very elegant but is adapted to the time available for this project 🏃‍♀️‍➡️. 

# 3-step install:
1)  To avoid conflicts we have run into, we propose to setup a conda environment. To do so, assuming you have conda installed (we can recommand to download [anaconda](https://www.anaconda.com/download/)), open a terminal, cd' yourself to the Carnutes folder, and run
```bash
conda env create -f environment.yml
conda activate Carnutes
```
Hopefully in a few weeks, it will be again possible to only rely on the
`# r:` tactic, but it currently makes Rhino8 crash 😢

2)  Add the src folder with the codes to the "scripts" folder of Rhino. (At every new release, the old files must be deleted). Please note that the Library (MacOS) and AppData (Windows) folders are "hidden folders". On MacOS press command+shift+. to reveal the hidden folders. On Windows 10 or 11, [see this link](https://support.microsoft.com/en-us/windows/view-hidden-files-and-folders-in-windows-97fbc472-c603-9d90-91d0-1166d1d9f4b5#WindowsVersion=Windows_11) 

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

3) Drag-and-drop the .rhc container file ( [Download link](https://github.com/ibois-epfl/Carnutes/raw/main/Carnutes.rhc) ). This file contains the metadata that creates the "Carnutes" toolbar tab with all the buttons calling the different scripts.

This solution is inelegant but corresponds to the developement time allocated to this project. If you know a better way, create an issue and tell me how to improve it 😇. The main issues are that a proper version tracking is inexistant, and installation is not super user friendly.

# Dependencies
There is no need to install dependencies as they are all installed in the conda environment "Carnutes"

The dependencies are nevertheless listed here: 

- [numpy](https://numpy.org/) for basic mathematics
- [i-graph](https://igraph.org/) for connectivity of elements
- [open3d](https://www.open3d.org/) for basic point cloud IO
- [ZODB](https://zodb.org/en/latest/) for the database of tree trunks


# Create your own database
To create your own database with another dataset, you can activate the conda environment (assuming you have [Conda](https://docs.conda.io/projects/conda/en/latest/index.html) installed on your computer), by running the following commands from the Carnutes root directory:

```bash
conda env create -f environment.yml
conda activate database_creation
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