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

    Attributes:
    ----------
    graph: igraph.Graph
        the connectivity graph of the structure
    """
    def __init__(self,elements):
        if  len(elements) < 2:
            raise ValueError("At least two geometries are needed to create a graph.")
        elif isinstance(elements[0], Rhino.Geometry.Brep):
            self.compute_brep_connectivity_graph(elements)
        elif isinstance(elements[0], Rhino.Geometry.NurbsCurve):
            self.compute_nurbs_curve_connectivity_graph(elements)
        else:
            raise ValueError("Geometries must be Breps or NurbsCurve.")

    def compute_brep_connectivity_graph(self, elements):
        """
        Compute the connectivity graph of the brep and stores the graph in self.graph.
        returns: list[Point3d] 
            the centers of the bounding boxes of the intersections
        """
        n_vertices = len(elements)
        edges = []
        centers = []
        for i in range(n_vertices):
            for j in range(i+1,n_vertices):
                result = Rhino.Geometry.Brep.CreateBooleanIntersection(elements[i], elements[j], ABS_TOL, False)
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
    
    def compute_nurbs_curve_connectivity_graph(self, elements):
        """
        Compute the connectivity graph of the Nurbs Curves.
        returns: list[Point3d]
            the intersection points
        """
        n_vertices = len(elements)
        edges = []
        centers = []
        for i in range(n_vertices):
            for j in range(i+1,n_vertices):
                result = Rhino.Geometry.Intersect.Intersection.CurveCurve(elements[i], elements[j], ABS_TOL, ABS_TOL)
                if result is not None and len(result) > 0:
                    edges.append([i,j])
                    for intersection in result:
                        centers.append(intersection.PointA)
                else:
                    continue
        g = ig.Graph(n_vertices, edges)
        self.graph = g
        return centers