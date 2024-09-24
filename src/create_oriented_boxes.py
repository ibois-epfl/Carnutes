#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import Rhino
import scriptcontext as sc

from utils import interact_with_rhino
from utils.element import ElementType


def main():
    model = interact_with_rhino.create_model_from_rhino_selection()

    for i in range(len(model.elements)):
        if model.elements[i].type != ElementType.Line:
            continue
        intersection_idx = model.connectivity_graph.get_connectivity_of_vertex(i)
        for j in intersection_idx:
            connection = model.connectivity_graph.graph.es[j]
            connection_location = connection["location"]
            element_1_id = connection.source
            element_1 = model.elements[element_1_id]
            element_2_id = connection.target
            element_2 = model.elements[element_2_id]
            if (
                element_1.type == ElementType.Point
                or element_2.type == ElementType.Point
            ):
                continue
            rh_connection_location = Rhino.Geometry.Point3d(
                connection_location[0], connection_location[1], connection_location[2]
            )
            element_1_length_parameter = element_1.geometry.ClosestPoint(
                rh_connection_location
            )[1]
            element_2_length_parameter = element_2.geometry.ClosestPoint(
                rh_connection_location
            )[1]
            first_direction = element_1.geometry.TangentAt(element_1_length_parameter)
            second_direction = element_2.geometry.TangentAt(element_2_length_parameter)
            plane = Rhino.Geometry.Plane(
                rh_connection_location, first_direction, second_direction
            )
            interval = Rhino.Geometry.Interval(-0.3, 0.3)
            box = Rhino.Geometry.Box(plane, interval, interval, interval)
            mesh = Rhino.Geometry.Mesh.CreateFromBox(box, 1, 1, 1)
            sc.doc.Objects.AddMesh(mesh)


if __name__ == "__main__":
    main()
