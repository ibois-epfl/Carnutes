"""
This module contains the class representing the abstract 3D model we want to realize with round wood.
"""

from dataclasses import dataclass
import typing
import numpy as np

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
        for i, element in enumerate(self.elements):
            if type(element.geometry) != type_of_model:
                raise ValueError(
                    "All elements in the model should be of the same type."
                )
            incident_edges_idx = self.connectivity_graph.get_connectivity_of_vertex(i)
            locations = []
            for edge_idx in incident_edges_idx:
                locations.append(self.connectivity_graph.graph.es[edge_idx]["location"])

            # removing duplicates
            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    if np.allclose(locations[i], locations[j]):
                        locations.pop(j)
                        break
            element.locations = locations
            element.degree = len(locations)

    def __str__(self):
        return "Model with {} elements".format(len(self.elements))
