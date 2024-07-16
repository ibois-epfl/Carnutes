"""
This module contains the class representing the abstract 3D model we want to realize with round wood.
"""

from utils import graphs

class Model(object):
    """
    Class representing the abstract 3D model we want to realize with round wood.

    Attributes:
    -----------
    model: list
        List of geometries in the model. Can be Breps or PolylineCurve.
    graph: graphs.ConnectivityGraph
        The connectivity graph of the model. Object of the ConnectivityGraph class.
    """
    def __init__(self, elements):
        self.elements = elements
        self.connectivity_graph = graphs.ConnectivityGraph(self.elements)
        type_of_model = type(self.elements[0])
        for element in self.elements:
            if type(element) != type_of_model:
                raise ValueError("All elements in the model should be of the same type.")
            
