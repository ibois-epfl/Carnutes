#! python 3
#r: igraph

import Rhino
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
        Compute the connectivity graph of the brep.
        """
        n_vertices = len(self.model)
        edges = []
        for i in range(n_vertices):
            for j in range(i+1,n_vertices):
                result = Rhino.Geometry.Brep.CreateBooleanIntersection(self.model[i], self.model[j], Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance, False)
                if len(result) > 0:    
                    edges.append([i,j])
        g = ig.Graph(n_vertices, edges)
        self.graph = g
    
    def compute_polyline_connectivity_graph(self):
        """
        Compute the connectivity graph of the polyline.
        """
        self.graph = ig.Graph()