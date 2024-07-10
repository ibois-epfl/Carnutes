#! python 3
import Rhino
from utils import graphs
    
def main():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select the breps or lines")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Brep | Rhino.DocObjects.ObjectType.Curve
    go.GetMultiple(1, 1000)
    if go.CommandResult() != Rhino.Commands.Result.Success:
        print("No object selected.")

    geometries = [go.Object(i).Geometry() for i in range(go.ObjectCount)]
    g = graphs.ConnectivityGraph(geometries)
    g.compute_brep_connectivity_graph()
    print("Graph created with {} vertices and {} edges".format(g.graph.vcount(), g.graph.ecount())) 

if __name__ == "__main__":
    main()
