#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import Rhino

from utils import meshing, conversions, interact_with_rhino


def main():
    # Select point cloud
    pointcloud = (
        interact_with_rhino.generic_object_getter(
            1,
            "Select the pointcloud you want to mesh",
            Rhino.DocObjects.ObjectType.PointSet,
        )[0]
        .Object()
        .Geometry
    )

    # Get alpha value from user
    alpha = interact_with_rhino.get_number(
        "Enter the alpha value for the meshing algorithm", 2.0
    )

    # Create mesh
    carnutes_mesh = meshing.mesh_from_rhino_pointcloud(
        pointcloud, meshing.MeshingMethod.ALPHA, alpha=alpha
    )

    # Convert Carnutes mesh to Rhino mesh
    mesh = conversions.convert_carnutes_mesh_to_rhino_mesh(carnutes_mesh)

    # Add mesh to Rhino
    Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)


if __name__ == "__main__":
    main()
