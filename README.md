# Carnutes🌳
🪵 Where druids experiment in the forest 🪵

as part of the studio Weinand, The architecture studio of Prof. Weinand, Assist. Agathe Mignon at IBOIS, EPFL (Switzerland), taught to 3rd bachelor and 1st master students.

This code is also a preparation to the research package 3 of Damien Gilliard's PhD thesis. This preparation work aims at finding out what the needs are in the context of roundwood architecture design, through the practice. By collaborating closely with the students through  a series of workshops, design needs will be identified, and the code will be improved and adapted accordingly.

Lastly, this repository is a quick python experiment, has been swiftly developed, and is not meant as a final product. It is made public for transparency purposes.

## Goal

 The goal of this project is to provide a tool to help druids to experiment with their magic in the forest. 

More precisely, the tool must enable the druids to:
- Dispose of a database of simple tree trunks geometries
- Match the tree trunk geometries with an 3D sketch of an architectural design.
- Generate architectural drawings with the tree trunk geometries.

For this, the following functions are planned:

- Practical:
    - Select trees automatically and orient given cylinder model
    - Select trees automatically and orient given wireframe model
    - Select trees manually and orient given cylinder model
    - Select trees manually and orient given wireframe model

- Graphical:
    - Draw connectivity Graphs of 3D models
    - Joint mapping (must be clarified)
    - Highlight difference between initial model and model with tree trunks (once the right tree trunks are selected):
        - using wireframe data (must be clarified)
        - using cylinder data
# Install and use
This tool is intended to be used in Rhino 8.
See the [INSTALL.md](./INSTALL.md) for installation instructions, and the [CONTRIBUTING.md](./CONTRIBUTING.md) for minimal contribution guidelines

# 4 workshops will be held within the Studio:

### 🌲S1: digitalisation of the real world 
(LiDAR, photogrammetry, ...) a little bit of theory.

-> The students can scan a tree and gain knowledge on how we can transfer the real world into the digital world.

### 🌲S2: Intro to the tools 
Manipulate tree trunk geometries and graphical representation: introduction to the tools offered, first anticipatory feed-back of students. Improved code (within time constrains) given to students for the next workshop.

-> The students learn to manipulate tree trunk geometries easily: translation and rotation. To start with, a simple 3D sketch is provided to the students. The students learn the basics of the proposed tools. They get out of this workshop with the ability to manipulate tree trunk geometries and to represent them graphically.

### 🌲S3: / 
NO DIGITAL WORKSHOP, but the students come up with their own 3D sketches model of what their design could look like. How do the small pieces fit together? What are the material constraints? What are the geometrical possibilities? How do the pieces join together ? Some or all these question are addressed by the students.


### 🌲S4: Presentation, feed-back and improvement. 
Small presentation of each student (1 screen shot of the work done), feed-back. Improvement of the tools are asked to Damien. Improved code (within time constrains) given to students for the next workshop. Some choices might be necessary, 

-> The students learn to critically analyse their needs and formulate the need for improvement. They also learn new graphical representation tools

### 🌲S5: Presentation, feed-back and improvement.
Small presentation of each student (1 screen shot of the work done), feed-back. Improvement of the tools are asked to Damien. Improved code (within time constrains) given to students for the next week.

-> The students present the new applications / adaptations of the tool.

## Development timetable

```mermaid
gantt
    title Development TimeTable
    dateFormat  YYYY-MM-DD
    section development
    Database of simple tree trunks      : 2024-07-08, 5d
    Graphs for connectivity of 3D models: 2024-07-15, 5d
    Wireframe tree matching             : 2024-07-22, 5d
    Cylinder tree matching              : 2024-07-29, 5d
    Joint mapping and joinery           : 2024-08-05, 5d
    Integration in Rhino UI             : 2024-08-12, 5d
```

