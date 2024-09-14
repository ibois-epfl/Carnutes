"""
Module for creating graphs from geometries.
"""

#! python 3

import typing

import utils.element as element

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
        the connectivity graph of the structure. This igraph.Graph as as edge attibutes the locations of the intersections.
    """

    def __init__(self, elements):
        if len(elements) < 2:
            raise ValueError("At least two geometries are needed to create a graph.")
        elif elements[0].type == element.ElementType.Brep:
            self.compute_brep_connectivity_graph(elements)
        else:
            self.compute_nurbs_curve_connectivity_graph(elements)
        # else:
        #     raise ValueError("Geometries must be Breps or NurbsCurve.")

    def compute_brep_connectivity_graph(self, elements: typing.List[element.Element]):
        """
        Compute the connectivity graph of the brep and stores the graph in self.graph.
        """
        n_vertices = len(elements)
        edges = []
        # igraph stores edge attributes in a dictionary. We want to store the locations of the intersections that the edge ij represents
        locations = []
        guids = []
        for i in range(n_vertices):
            guids.append(elements[i].GUID)
            for j in range(i + 1, n_vertices):
                result = Rhino.Geometry.Brep.CreateBooleanIntersection(
                    elements[i].geometry, elements[j].geometry, ABS_TOL, False
                )
                if result is not None and len(result) > 0:
                    edges.append([i, j])
                    for brep in result:
                        bounding_box = brep.GetBoundingBox(False)
                        locations.append(
                            [
                                bounding_box.Center.X,
                                bounding_box.Center.Y,
                                bounding_box.Center.Z,
                            ]
                        )
                else:
                    continue

        g = ig.Graph(
            n_vertices,
            edges,
            edge_attrs={"location": locations},
            vertex_attrs={"guid": guids},
        )
        self.graph = g

    def compute_nurbs_curve_connectivity_graph(
        self, elements: typing.List[element.Element]
    ):
        """
        Compute the connectivity graph of the Nurbs Curves.

        ::param elements: list of Rhino.Geometry.NurbsCurve
            List of Nurbs Curves.
        """
        n_vertices = len(elements)
        edges = []
        # igraph stores edge attributes in a dictionary. We want to store the locations of the intersections that the edge ij represents
        locations = []
        guids = []
        for i in range(n_vertices):
            guids.append(elements[i].GUID)
            if elements[i].type == element.ElementType.Point:
                for j in range(i + 1, n_vertices):
                    if elements[j].type == element.ElementType.Point:
                        continue
                    print(
                        "debug from line 95 in graphs.py. Location of point: ",
                        [
                            elements[i].geometry.X,
                            elements[i].geometry.Y,
                            elements[i].geometry.Z,
                        ],
                    )
                    test_intersect_1 = elements[j].geometry.GetLocalTangentPoint(
                        elements[i].geometry, 0
                    )  # returns a tuple with a boolean and a curve parameter
                    test_intersect_2 = elements[j].geometry.GetLocalTangentPoint(
                        elements[i].geometry, 1
                    )
                    if test_intersect_1[0]:
                        print("intersect")
                        edges.append([i, j])
                        locations.append(
                            [
                                elements[i].geometry.X,
                                elements[i].geometry.Y,
                                elements[i].geometry.Z,
                            ]
                        )

                    elif test_intersect_2[0]:
                        print("intersect")
                        edges.append([i, j])
                        locations.append(
                            [
                                elements[i].geometry.X,
                                elements[i].geometry.Y,
                                elements[i].geometry.Z,
                            ]
                        )

            else:
                for j in range(i + 1, n_vertices):
                    result = Rhino.Geometry.Intersect.Intersection.CurveCurve(
                        elements[i].geometry, elements[j].geometry, 5 * ABS_TOL, ABS_TOL
                    )
                    if result is not None and len(result) > 0:
                        edges.append([i, j])
                        locations.append(
                            [result[0].PointA.X, result[0].PointA.Y, result[0].PointA.Z]
                        )
                    else:
                        continue
        g = ig.Graph(
            n_vertices,
            edges,
            edge_attrs={"location": locations},
            vertex_attrs={"guid": guids},
        )
        self.graph = g

    def get_connectivity_of_vertex(self, vertex):
        """
        Get the connectivity of a vertex.

        ::param vertex: int
            The vertex for which we want to get the connectivity.

        ::return: list
            The list of vertices connected to the vertex.

        """
        return self.graph.incident(vertex)

    def __str__(self):
        return "Connectivity graph with {} vertices and {} edges".format(
            self.graph.vcount(), self.graph.ecount()
        )
