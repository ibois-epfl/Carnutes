"""
This module contains the conversion utilities, and should only be imported by the final Carnutes functions.
"""

import Rhino
import utils.geometry as geometry


def convert_carnutes_mesh_to_rhino_mesh(
    carnutes_mesh: geometry.Mesh,
) -> Rhino.Geometry.PointCloud:
    """
    Convert a Carnutes mesh to a Rhino.Geometry.Mesh.

    :param carnutes_pc: Carnutes mesh
        The Carnutes mesh to convert.

    :return: Rhino.Geometry.Mesh
        The converted Rhino.Geometry.Mesh.
    """
    rhino_mesh = Rhino.Geometry.Mesh()
    for i in range(len(carnutes_mesh.vertices)):
        rhino_mesh.Vertices.Add(
            Rhino.Geometry.Point3f(
                carnutes_mesh.vertices[i][0],
                carnutes_mesh.vertices[i][1],
                carnutes_mesh.vertices[i][2],
            )
        )
    for i in range(len(carnutes_mesh.faces)):
        rhino_mesh.Faces.AddFace(
            int(carnutes_mesh.faces[i][0]),
            int(carnutes_mesh.faces[i][1]),
            int(carnutes_mesh.faces[i][2]),
        )
    return rhino_mesh
