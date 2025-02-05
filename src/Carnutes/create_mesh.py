
#! python3
# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import Rhino
import open3d as o3d
import rhinoscriptsyntax as rs
import numpy as np

print(o3d.__version__)

def main():
    pcd_guid = rs.GetObjects("Select pointclouds", rs.filter.pointcloud)
    if not pcd_guid:
        print("No point cloud selected.")
        return

    pcd = rs.coercegeometry(pcd_guid[0])
    if not pcd:
        print("Failed to coerce geometry.")
        return

    pcd_o3d = o3d.geometry.PointCloud()
    pcd_as_list = []
    for i in range(pcd.Count):
        pcd_as_list.append([pcd[i].Location.X, pcd[i].Location.Y, pcd[i].Location.Z])

    # Convert pcd_as_list to numpy array
    pcd_as_np = np.array(pcd_as_list)

    # Convert numpy array to open3d pointcloud
    pcd_o3d.points = o3d.utility.Vector3dVector(pcd_as_np)
    
    # Estimate normals
    pcd_o3d.estimate_normals()

    # Create mesh
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd_o3d, depth=9, width=0, scale=1.1, linear_fit=False)[0:2]
    print("Mesh created from point cloud Poisson")
    print(mesh)

    #create mesh from point cloud alpha shape
    
    #mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd_o3d, alpha=2)
    
    print(mesh)
    #print mesh faces number
    #print(mesh.triangles)
    
    #visualize the mesh
    #o3d.visualization.draw_geometries([mesh])

    # save the mesh
    #o3d.io.write_triangle_mesh("mesh.ply", mesh)

    # Decimate mesh
    #mesh = mesh.simplify_quadric_decimation(1000)
 
    # Convert mesh to rhino mesh
    vertices = np.asarray(mesh.vertices)

    #convert vertices to list
    vertices = vertices.tolist()

    
    faces = np.asarray(mesh.triangles)  # Ensure faces are integers
    #convert faces to list
    faces = faces.tolist() 

    # convert the mesh to rhino mesh
    rhino_mesh = Rhino.Geometry.Mesh()
    for vertex in vertices:
        rhino_mesh.Vertices.Add(vertex[0], vertex[1], vertex[2])
    for face in faces:
        rhino_mesh.Faces.AddFace(int(face[0]), int(face[1]), int(face[2]))
    
    #is valid mesh
    print(rhino_mesh.IsValid)
    print(rhino_mesh.Faces.Count)
    # Add mesh to rhino
    Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(rhino_mesh)

if __name__ == "__main__":
    main()