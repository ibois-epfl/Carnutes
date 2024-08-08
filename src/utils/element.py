"""
module for the Element class. those elements make up the model
"""
from dataclasses import dataclass

import Rhino

@dataclass
class Element(object):
    """
    Class representing an element in the model.

    Attributes:
    -----------
    geometry: Rhino.Geometry.GeometryBase
        The geometry of the element.
    GUID: str
        The GUID of the element in the ActiveDoc.
    """
    def __init__(self, geometry: Rhino.Geometry.GeometryBase, GUID):
        self.geometry = geometry
        self.GUID = GUID