"""
module for the Element class. those elements make up the model
"""
from dataclasses import dataclass
from enum import Enum
import copy

from . import interact_with_rhino, geometry
from packing import packing_combinatorics
import Rhino


class ElementType(Enum):
    """
    Enum for the type of element. Can be Brep, Line or Point.
    """

    Brep = 1
    Line = 2
    Point = 3


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
    diameter: float
        The (target) diameter of the element.
    degree: int
        The degree of connectivity of the element. (2 if only connected at the ends, 3 if connected at the ends and in the middle, ...)
    locations: list
        The locations of the element's connection locations in the model. duplicates have been removed.
    """

    def __init__(self, geometry, GUID, diameter: float = None):
        self.geometry = geometry
        self.GUID = GUID
        self.diameter = diameter
        self.degree = None
        self.locations = None
        self.type = interact_with_rhino.determinate_element_type(self.geometry)

    def create_bounding_cylinder(self, radius: int = 1):
        """
        Create a cylinder that bounds the element.

        :param radius: float
            The radius of the cylinder.
        :return: Rhino.Geometry.Cylinder
            The bounding cylinder.
        """
        if self.type == ElementType.Line:
            cylinder = Rhino.Geometry.Brep.CreatePipe(
                self.geometry,
                radius,
                True,
                Rhino.Geometry.PipeCapMode.Flat,
                True,
                0.01,
                0.01,
            )[0]
        elif self.type == ElementType.Brep:
            edges = [
                self.geometry.Edges[i]
                for i in range(self.geometry.Edges.Count)
                if not self.geometry.Edges[i].IsClosed
            ]
            cylinder = Rhino.Geometry.Brep.CreatePipe(
                edges[0],
                radius,
                True,
                Rhino.Geometry.PipeCapMode.Flat,
                True,
                0.01,
                0.01,
            )[0]
        else:
            raise ValueError("The geometry of the target element is not supported.")
        return cylinder

    def __str__(self):
        return f"Element with GUID {self.GUID} and of type {self.type}"

    def allocate_trees(self, db_path: str, optimized: bool = False):
        """
        Allocate trees to the element.

        :param db_path: str
            The path to the tree database.

        :return: best_tree: Tree.tree
            The best fitting tree allocated to the element.
        :return: best_rmse: float
            The RMSE of the best fitting tree.
        """
        if self.type == ElementType.Point:
            return

        if self.locations is None:
            raise ValueError(
                "The connection locations of the element have not been computed. \n Please create the model first. the intersections are computed there."
            )
        if self.diameter is None:
            raise ValueError(
                "The diameter of the element is not set. Check the layer name of the element in Rhino."
            )
        target_diameter = self.diameter
        reference_pc_as_list = geometry.sort_points(self.locations)
        reference_skeleton = geometry.Pointcloud(reference_pc_as_list)
        if optimized:
            (
                best_tree,
                best_target,
                best_rmse,
            ) = packing_combinatorics.find_best_tree_optimized(
                reference_skeleton,
                target_diameter,
                db_path,
                return_rmse=True,
                update_database=True,
            )
        else:
            (
                best_tree,
                best_target,
                best_rmse,
            ) = packing_combinatorics.find_best_tree_unoptimized(
                reference_skeleton,
                target_diameter,
                db_path,
                return_rmse=True,
                update_database=True,
            )
        if best_tree is None:
            print("No tree found. Skiping this element.")
            return
        best_tree = copy.deepcopy(best_tree)
        return best_tree, best_rmse
