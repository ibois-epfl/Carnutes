#! python 3
#r: igraph
#r: numpy

import Rhino

import numpy as np
import igraph as ig

class ConnectivityGraph(object):
    """
    Connectivity graph of the structure.
    Handles PolylineCurves and Breps
    """
    def __init__(self,model):
        self.model = model
        if  len(model) < 2:
            raise ValueError("At least two geometries are needed to create a graph.")
        elif type(model[0]) == Rhino.Geometry.Brep:
            self.compute_brep_connectivity_graph()
        elif type(model[0]) == Rhino.Geometry.PolylineCurve:
            self.compute_polyline_connectivity_graph()
        else:
            raise ValueError("Geometries must be Breps or PolylineCurves.")

    def compute_brep_connectivity_graph(self):
        """
        Compute the connectivity graph of the brep and stores the graph in self.graph.
        returns: list[Point3d] 
            the centers of the bounding boxes of the intersections
        """
        matrix_of_intersections = np.triu(np.ones((len(self.model),len(self.model))),1)
        print(matrix_of_intersections)
        n_vertices = len(self.model)
        edges = []
        centers = []
        for i in range(n_vertices):
            for j in range(i+1,n_vertices):
                result = Rhino.Geometry.Brep.CreateBooleanIntersection(self.model[i], self.model[j], Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance, False)
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