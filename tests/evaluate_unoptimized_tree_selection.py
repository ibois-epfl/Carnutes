#! python3

# r: numpy==1.26.4
# r: open3d==0.18.0
# r: ZODB==6.0
# r: igraph==0.11.6

import os, sys, csv, argparse

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + "/..")
sys.path.append(current_dir + "/../src/Carnutes")
sys.path.append(current_dir)

import generate_elements
from packing import packing_combinatorics
from utils import geometry
from reset_database import main as reset_database

import numpy as np


def evaluate_unoptimized_tree_selection(
    type: str, n_frames: int, reference_diameter: float
):
    """
    we generate a number of frames, apply the tree selection, and evaluate the performance according to two metrics:
    - The number of trees used and their degree of use (% of the tree that is used)
    - The mean RMSE of the fitting over all the frames
    """

    csv_file_elementwise = open("unoptimized_tree_selection_elementwise.csv", mode="w")
    csv_file_treewise = open("unoptimized_tree_selection_treewise.csv", mode="w")
    csv_writer_elementwise = csv.writer(
        csv_file_elementwise, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    csv_writer_treewise = csv.writer(
        csv_file_treewise, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    csv_writer_elementwise.writerow(["Frame", "Degree of use", "Mean RMSE"])
    csv_writer_treewise.writerow(
        ["Tree", "number of elements", "length used", "initial tree length"]
    )

    tree_number_usage = {}
    tree_length_usage = {}
    tree_initial_length = {}

    RMSEs = []

    db_path = (
        os.path.dirname(os.path.realpath(__file__))
        + "/../src/Carnutes/database/tree_database.fs"
    )
    if type == "simple_frame":
        list_of_elements_locations = generate_elements.generate_simple_frame(
            n_frames=n_frames
        )
    elif type == "scissor_truss":
        list_of_elements_locations = generate_elements.generate_scissor_truss(
            n_frames=n_frames
        )
    elif type == "symmetrical_portal":
        list_of_elements_locations = generate_elements.generate_symmetrical_portal(
            n_frames=n_frames
        )
    elif type == "asymmetrical_portal":
        list_of_elements_locations = generate_elements.generate_asymmetrical_portal(
            n_frames=n_frames
        )
    elif type == "tower":
        list_of_elements_locations = generate_elements.generate_tower(n_floors=n_frames)

    for element_locations in list_of_elements_locations:
        element_length = np.linalg.norm(
            np.asarray(element_locations[0]) - np.asarray(element_locations[-1])
        )
        print(f"Element length: {element_length}")
        element_pc = geometry.Pointcloud(element_locations)
        (
            best_tree,
            best_target,
            best_rmse,
            best_init_rotation,
        ) = packing_combinatorics.find_best_tree_unoptimized(
            element_pc,
            reference_diameter=reference_diameter,
            database_path=db_path,
            return_rmse=True,
            update_database=True,
        )
        if best_tree is None:
            csv_writer_elementwise.writerow([element_locations, "Failed", "Failed"])
            print("No tree found. Skiping this element.")
            continue
        tree_length = best_tree.height
        if best_tree.id not in tree_initial_length:
            tree_initial_length[best_tree.id] = tree_length
        csv_writer_elementwise.writerow(
            [element_locations, element_length / tree_length, best_rmse]
        )
        print(f"Best tree: {best_tree}")
        print(f"Best RMSE: {best_rmse}")
        RMSEs.append(best_rmse)
        if best_tree.id not in tree_number_usage and best_tree != None:
            tree_number_usage[best_tree.id] = 1
            tree_length_usage[best_tree.id] = element_length
        else:
            tree_number_usage[best_tree.id] += 1
            tree_length_usage[best_tree.id] += element_length

    for tree_id in tree_number_usage:
        csv_writer_treewise.writerow(
            [
                tree_id,
                tree_number_usage[tree_id],
                tree_length_usage[tree_id],
                tree_initial_length[tree_id],
            ]
        )
    csv_file_elementwise.close()
    csv_file_treewise.close()

    mean_RMSE = np.mean(RMSEs)
    mean_RMSE = np.round(mean_RMSE, 4)
    with open("rmse_result.txt", "w") as f:
        f.write(f"{mean_RMSE}")

    mean_tree_usage = np.mean(
        [
            tree_length_usage[tree_id] / tree_initial_length[tree_id]
            for tree_id in tree_number_usage
        ]
    )
    mean_tree_usage = np.round(mean_tree_usage, 4)
    mean_tree_usage = mean_tree_usage * 100
    with open("tree_usage_result.txt", "w") as f:
        f.write(f"{mean_tree_usage}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Evaluate the unoptimized tree selection algorithm."
    )
    parser.add_argument(
        "--reference_diameter",
        "-d",
        type=float,
        default=0.3,
        help="The reference diameter of the trees, expressed in meters.",
    )
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        default="simple_frame",
        help="The type of frame to generate. Choose between simple_frame, scissor_truss, symmetrical_portal, asymmetrical_portal, tower.",
    )
    parser.add_argument(
        "--n_frames",
        "-n",
        type=int,
        default=1,
        help="The number of frames to generate.",
    )

    args = parser.parse_args()
    reference_diameter = args.reference_diameter
    type = args.type
    n_frames = args.n_frames

    if (
        type != "simple_frame"
        and type != "scissor_truss"
        and type != "symmetrical_portal"
        and type != "asymmetrical_portal"
        and type != "tower"
    ):
        print(
            "Invalid type. Please choose between simple_frame, scissor_truss, symmetrical_portal, asymmetrical_portal, tower"
        )
        sys.exit(1)

    reset_database(
        voxel_size=0.03,
        working_dir=os.path.dirname(os.path.realpath(__file__)) + "/../src/Carnutes",
    )
    evaluate_unoptimized_tree_selection(type, n_frames, reference_diameter)
    print("Evaluation done.")
    sys.exit(0)
