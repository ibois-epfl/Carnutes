"""
dummy function to test the bones of the project
this one creates a graph from the selected breps or lines and draws a graph of the connected elements in the rhino scene
"""
#! python 3
# r: igraph

import System.Drawing

import Rhino
import scriptcontext as sc

from utils import graphs

# Create a new layer
layer_name = "Layer_for_connectivity_graph"
layer_index = sc.doc.Layers.Add(layer_name, System.Drawing.Color.FromArgb(255, 50, 255, 50))
sc.doc.Layers.SetCurrentLayerIndex(layer_index, True)

attributes = Rhino.DocObjects.ObjectAttributes()
attributes.LayerIndex = layer_index
attributes.ObjectColor = System.Drawing.Color.FromArgb(255, 100, 100, 100)

    
def main():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the breps or lines")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Curve
    go.GetMultiple(1, 1000)
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")

    geometries = [go.Object(i).Geometry() for i in range(go.ObjectCount)]
    g = graphs.ConnectivityGraph(geometries)
    centers = g.compute_brep_connectivity_graph()
    for edge in g.graph.get_edgelist():
        sc.doc.Objects.AddLine(g.model[edge[0]].GetBoundingBox(False).Center, g.model[edge[1]].GetBoundingBox(False).Center, attributes)

    # sc.doc.Objects.AddPoints(centers)
    print("Graph created with {} vertices and {} edges".format(g.graph.vcount(), g.graph.ecount())) 

if __name__ == "__main__":
    main()
