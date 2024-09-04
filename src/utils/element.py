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
    def __init__(self, geometry: Rhino.Geometry.GeometryBase, GUID, diameter: float = None):
        self.geometry = geometry
        self.GUID = GUID
        self.diameter = diameter

    def create_bounding_cylinder(self, radius : int = 1):
        """
        Create a cylinder that bounds the element.

        :param radius: float
            The radius of the cylinder.
        :return: Rhino.Geometry.Cylinder
            The bounding cylinder.
        """
        if isinstance(self.geometry, Rhino.Geometry.NurbsCurve):
            cylinder = Rhino.Geometry.Brep.CreatePipe(self.geometry, radius, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
        elif isinstance(self.geometry, Rhino.Geometry.Brep):
            edges = [self.geometry.Edges[i] for i in range(self.geometry.Edges.Count) if not self.geometry.Edges[i].IsClosed]
            cylinder = Rhino.Geometry.Brep.CreatePipe(edges[0], radius, True, Rhino.Geometry.PipeCapMode.Flat, True, 0.01, 0.01)[0]
        else:
            raise ValueError("The geometry of the target element is not supported.")
        return cylinder
    
    def __str__(self):
        return "Element with GUID {}".format(self.GUID)