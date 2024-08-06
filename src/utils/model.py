"""
This module contains the class representing the abstract 3D model we want to realize with round wood.
"""

from dataclasses import dataclass

from utils import graphs

@dataclass
class Model(object):
    """
    Class representing the abstract 3D model we want to realize with round wood.

    Attributes:
    -----------
    model: list
        List of elements in the model. Each element is an object of the Element class.
    graph: graphs.ConnectivityGraph
        The connectivity graph of the model. Object of the ConnectivityGraph class.
    """
    def __init__(self, elements):
        self.elements = elements
        geo_elements = [element.geometry for element in elements]
        self.connectivity_graph = graphs.ConnectivityGraph(geo_elements)
        type_of_model = type(self.elements[0])
        for element in self.elements:
            if type(element) != type_of_model:
                raise ValueError("All elements in the model should be of the same type.")
    
    def __str__(self):
        return "Model with {} elements".format(len(self.elements))
    
@dataclass
class Element(object):
    """
    Class representing an element in the model.

    Attributes:
    -----------
    geometry: Rhino.Geometry.GeometryBase
        The geometry of the element.
    guid: str
        The GUID of the element in the ActiveDoc.
    """
    def __init__(self, geometry, guid):
        self.geometry = geometry
        self.GUID = guid
        

    
            
