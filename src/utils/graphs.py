"""
Module for creating graphs from geometries.
"""

#! python 3
#r: igraph
#r: numpy

import Rhino

import numpy as np
import igraph as ig

ABS_TOL = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance

class ConnectivityGraph(object):
    """
    Connectivity graph of the structure.
    Handles PolylineCurves and Breps
    """
    def __init__(self,elements):
        self.elements = elements
        if  len(elements) < 2:
            raise ValueError("At least two geometries are needed to create a graph.")
        elif type(elements[0]) == Rhino.Geometry.Brep:
            self.compute_brep_connectivity_graph()
        elif type(elements[0]) == Rhino.Geometry.PolylineCurve:
            self.compute_polyline_connectivity_graph()
        else:
            raise ValueError("Geometries must be Breps or PolylineCurves.")

    def compute_brep_connectivity_graph(self):
        """
        Compute the connectivity graph of the brep and stores the graph in self.graph.
        returns: list[Point3d] 
            the centers of the bounding boxes of the intersections
        """
        matrix_of_intersections = np.triu(np.ones((len(self.elements),len(self.elements))),1)
        print(matrix_of_intersections)
        n_vertices = len(self.elements)
        edges = []
        centers = []
        for i in range(n_vertices):
            for j in range(i+1,n_vertices):
                result = Rhino.Geometry.Brep.CreateBooleanIntersection(self.elements[i], self.elements[j], ABS_TOL, False)
                if result is not None and len(result) > 0:    
                    edges.append([i,j])
                    for brep in result:
                        bounding_box = brep.GetBoundingBox(False)
                        centers.append(bounding_box.Center)
                else:
                    continue

                    
        g = ig.Graph(n_vertices, edges)
        self.graph = g
        return centers
    
    def compute_polyline_connectivity_graph(self):
        """
        Compute the connectivity graph of the polyline.
        """
        self.graph = ig.Graph()