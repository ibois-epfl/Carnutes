![basic geometry test](https://github.com/ibois-epfl/Carnutes/actions/workflows/test_geo_basics.yml/badge.svg)
![RMSE in meters](https://img.shields.io/badge/RMSE-0.0173-c7a8ad)
![Tree Usage in percent ](https://img.shields.io/badge/Tree_Usage-63.31-c7a8ad)

# Carnutes🌳

🪵 In Asterix & Obelix, the Carnutes forest is where druids present their latest crazy inventions to their peers 🪵

<p align="center"> <img src="./assets/images/Carnutes_illustration_17_09_2024.png" height="400" />

This repo contains the code produced as part of the studio Weinand, the architecture studio directed by Prof. Yves Weinand, and Assist. Dr. Agathe Mignon at IBOIS, EPFL (Switzerland), taught to 3rd bachelor and 1st master students.

This code is also a preparation to the research package 3 of Damien Gilliard's PhD thesis. This preparation work aims at finding out what the needs are in the context of roundwood architecture design, through the practice. By collaborating closely with the students through  a series of workshops, design needs will be identified, and the code will be improved and adapted accordingly.

Lastly, this repository is a quick python experiment, has been swiftly developed, and is not meant as a final product. It is made public for transparency purposes.

[! Warning:  This repo is under active development, but the main branch should work fine at any point]

## Goal

 This project enables the students to:
- Dispose of a database of simple tree trunks geometries. ✅
- Match the tree trunk geometries with an 3D sketch of an architectural design. ✅

For this, the following functions are planned:

- Practical:
    - Allocate trees automatically and orient given cylinder model ❌
    - Allocate trees automatically and orient given wireframe model ✅
    - Allocate trees manually and orient given cylinder model ❌
    - Allocate trees manually and orient given wireframe model ✅
    - Create locally oriented bounding box of overlap to assist students to experiment with their own joinery ❌
    - reset the database to original state ✅

- Graphical:
    - Draw connectivity Graphs of 3D models ✅
    - Joint mapping (must be clarified)
    - Highlight difference between initial model and model with tree trunks (once the right tree trunks are selected):
        - using wireframe data ❌
        - using cylinder data ❌

<p align="center">
    <img src="./assets/images/07_09_2024_demo_Carnutes.gif" height="400" />

<p align="center">
    <img src="./assets/images/05_09_2024_Carnutes_eval.png" height="400" >

# Install and use
This tool is intended to be used in Rhino 8.
See the [INSTALL.md](./INSTALL.md) for installation instructions, and the [CONTRIBUTING.md](./CONTRIBUTING.md) for minimal contribution guidelines. This repo contains a small .3dm to easily test Carnutes.
 # Timeline
 ```mermaid
gantt
    title Roadmap to publication: first draft milestone is 16 october
    dateFormat  YY-MM-DD
    excludes weekends
    section Patches and improvements
    Cylinder pipeline finalization                          :a1, 2024-09-30, 3d
    Create mesh from point cloud                            :a2, after a1, 1d
    Keep track of volumetric overlaps                       :a3, after a2, 3d
    section Evaluation
    Data creation pipeline for evaluation                   :b1, after a1, 3d
    Creation of final 3d models for evaluation              :b2, after b1, 1d
    Evaluation of fitting; rmse                             :b3, after b2, 1d
    Evaluation of tree usage                                :b4, after b3, 2d
    Evaluation of overlaps                                  :b5, after b3, 2d
    section Writing
    First draft                                             :crit, milestone, 2024-10-16,1d
    Introduction and state of the art finalization          :c1, 2024-09-30, 3d
    Outline of evaluation pipeline                          :c2, after b1, 2d
    Evaluation-results                                      :c3, after b4, 1d
    Evaluation-discussion                                   :c4, after c3, 1d
    Conclusion                                              :c5, after c4, 1d

 ```
