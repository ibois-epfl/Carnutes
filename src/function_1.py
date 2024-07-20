"""
dummy function to test the bones of the project
this one creates a graph from the selected breps or lines and draws a graph of the connected elements in the rhino scene
"""
#! python 3
# r: igraph

import System.Drawing

import Rhino
import scriptcontext as sc

from utils.model import Model, Element

# Create a new layer into which we output the graph
layer_name = "Layer_for_connectivity_graph"
layer_index = sc.doc.Layers.Add(layer_name, System.Drawing.Color.FromArgb(255, 50, 255, 50))
sc.doc.Layers.SetCurrentLayerIndex(layer_index, True)

attributes = Rhino.DocObjects.ObjectAttributes()
attributes.LayerIndex = layer_index
attributes.ObjectColor = System.Drawing.Color.FromArgb(255, 100, 100, 100)

def get_geometries():
    """
    Just a small utility function to get the geometries from the Rhino scene
    """
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the breps or lines")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Curve
    go.GetMultiple(1, 1000)
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")
    geometries = [go.Object(i).Geometry() for i in range(go.ObjectCount)]
    return geometries
def main():
    # Get the geometries from the Rhino scene
    geometries = get_geometries()
    if len(geometries) < 2:
        print("At least two geometries are needed to create a graph.")
        return
    
    if isinstance(geometries[0], Rhino.Geometry.LineCurve):
        geometries = [geo.ToNurbsCurve() for geo in geometries]
        print("LineCurves converted to NurbsCurves")
    elif isinstance(geometries[0], Rhino.Geometry.Line):
        geometries = [geo.ToNurbsCurve() for geo in geometries]
        print("Lines converted to NurbsCurves")
    elif isinstance(geometries[0], Rhino.Geometry.Curve):
        geometries = [geo.ToNurbsCurve() for geo in geometries]
        print("Curves converted to NurbsCurve")

    # Create the model
    elements = [Element(geometries[i], i) for i in range(len(geometries))]
    abstract_model = Model(elements)
    for edge in abstract_model.connectivity_graph.graph.get_edgelist():
        sc.doc.Objects.AddLine(abstract_model.elements[edge[0]].geometry.GetBoundingBox(False).Center, abstract_model.elements[edge[1]].geometry.GetBoundingBox(False).Center, attributes)

    print("Graph created with {} vertices and {} edges".format(abstract_model.connectivity_graph.graph.vcount(), abstract_model.connectivity_graph.graph.ecount())) 

if __name__ == "__main__":
    main()
