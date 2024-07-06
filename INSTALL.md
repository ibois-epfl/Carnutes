To use this tool (we avoid the term plugin, as it isn't a proper plugin), you need to follow those two steps. This solution is not very elegant but is adapted to the time available for this project. 

1)  Add the content of the folder with the codes to the "scripts" folder of Rhino. 

MacOS:
```
/Users/<your_username>/Library/Application support/McNeel/Rhinoceros/Scripts
```

NB: The naming of "Library" varies in function of the system language. For example if our OS is in French, replace "Library" with "Bibliothèque"...

Windows:

```
C:\Users\<your_username>\AppData\Roaming\McNeel\Rhinoceros\8.0\scripts
```

2) Drag-and-drop the .rhc container file. This file contains the metadata that creates the "Carnutes" toolbar tab with all the buttons calling the different scripts.

It is inelegant but corresponds to the developement time allocated to this project.

## Commands
To have buttons to click on, without developping a proper plugin, we can create macros that call a python script. Those macros are saved with the .3dm file, so the solution founnd here is to push on the repository a .3dm file with the macros already set up. It is thus recommanded to use the .3dm file provided in the repository, if you are not familiar with Macros in Rhino.
## scripts

For Rhino to find the scripts