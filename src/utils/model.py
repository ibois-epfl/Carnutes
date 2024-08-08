"""
This module contains the class representing the abstract 3D model we want to realize with round wood.
"""

from dataclasses import dataclass
import typing

from utils import graphs, element

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
    def __init__(self, elements: typing.List[element.Element]):
        self.elements = elements
        self.connectivity_graph = graphs.ConnectivityGraph(elements)
        type_of_model = type(self.elements[0].geometry)
        for element in self.elements:
            if type(element.geometry) != type_of_model:
                raise ValueError("All elements in the model should be of the same type.")
    
    def __str__(self):
        return "Model with {} elements".format(len(self.elements))
    