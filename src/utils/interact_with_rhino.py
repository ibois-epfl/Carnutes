from . import model, warnings, geometry, element
import Rhino


def determinate_element_type(geo):
    """
    Determine the type of geometry.

    :param geo: Rhino.Geometry.GeometryBase
        The geometry to determine the type of.
    :return: element.ElementType
        The type of geometry.
    """
    return (
        element.ElementType.Brep
        if isinstance(geo, Rhino.Geometry.Brep)
        else (
            element.ElementType.Line
            if isinstance(geo, Rhino.Geometry.Curve)
            else (
                element.ElementType.Point
                if isinstance(geo, Rhino.Geometry.Point3d)
                else None
            )
        )
    )


def create_model_from_rhino_selection(max_elements: int = 100000):
    """
    Create a model from the selected breps or lines in the Rhino scene.

    :param max_elements: int
        The maximum number of elements that can be selected. Default is 100000.
    :return: model.Model
        The model created from the selected geometries.
    """

    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the breps or lines")
    go.GeometryFilter = (
        Rhino.DocObjects.ObjectType.Brep
        | Rhino.DocObjects.ObjectType.Curve
        | Rhino.DocObjects.ObjectType.Point
    )
    go.GetMultiple(1, max_elements)

    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")
        return

    converted_geometries = []

    geometries = [go.Object(i).Geometry() for i in range(go.ObjectCount)]
    if len(geometries) < 2:
        print("At least two geometries are needed to create a graph.")
        return
    for geo in geometries:
        if isinstance(geo, Rhino.Geometry.Point):
            converted_geometries.append(geo.Location)
        elif isinstance(
            geo, Rhino.Geometry.LineCurve or Rhino.Geometry.Line or Rhino.Geometry.Curve
        ):
            converted_geometries.append(geo.ToNurbsCurve())
        else:
            converted_geometries.append(geo)

    layer_ids = [
        go.Object(i).Object().Attributes.LayerIndex for i in range(go.ObjectCount)
    ]
    layer_names = [
        Rhino.RhinoDoc.ActiveDoc.Layers[layer_id].Name for layer_id in layer_ids
    ]
    elements = [
        element.Element(
            converted_geometries[i], go.Object(i).ObjectId, float(layer_names[i])
        )
        for i in range(go.ObjectCount)
    ]
    return model.Model(elements)


def select_single_element_to_replace():
    """
    Ask the user to select an element to replace with a point cloud.

    :return: Rhino.Geometry.GeometryBase
        The geometry of the selected element.
    :return: str
        The GUID of the selected element.
    """
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the element to replace with a point cloud")
    go.GeometryFilter = (
        Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Curve
    )
    go.GetMultiple(1, 1)
    element_geometry = go.Object(0).Geometry()
    element_guid = go.Object(0).ObjectId
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")
        return
    return element_geometry, element_guid
