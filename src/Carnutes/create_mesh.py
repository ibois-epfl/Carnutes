#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import Rhino

from utils import meshing
from utils import interact_with_rhino


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
    # Create mesh
    mesh = meshing.mesh_from_rhino_pointcloud(
        pointcloud, meshing.MeshingMethod.ALPHA, to_rhino=True
    )

    # Add mesh to Rhino
    Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)


if __name__ == "__main__":
    main()
