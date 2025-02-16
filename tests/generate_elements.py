"""
This module generates wireframe geometries to evaluate the performance of carnutes, using the database.
"""


def generate_simple_frame(n_frames: int = 10) -> list[list[list[float]]]:
    """
    Generate a simple frame with n_frames.
    it is 8m wide, 4m high.
    ```

       /\
      /__\
     /    \
    *      *
    ```
    :param n_frames: int
        The number of frames to generate. Default is 10.
    :return: list[list[list[float]]].
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    """
    elements_as_lists_of_connections = []
    for i in range(n_frames):
        base_point_left = [i, 0, 0]
        base_point_right = [i, 8, 0]
        top_point = [i, 4, 4]
        middle_left = [i, 2, 2]
        middle_right = [i, 6, 2]
        element_1 = [base_point_left, middle_left, top_point]
        element_2 = [base_point_right, middle_right, top_point]
        element_3 = [middle_left, middle_right]

        elements_as_lists_of_connections.append(element_1)
        elements_as_lists_of_connections.append(element_2)
        elements_as_lists_of_connections.append(element_3)
    return elements_as_lists_of_connections


def generate_slightly_curved_frame(n_frames: int = 10) -> list[list[list[float]]]:
    """
    Generate a slightly curved frame with n_frames.
    it is 8m wide, 4m high.

    :param n_frames: int
        The number of frames to generate. Default is 10.
    :return: list[list[list[float]]].
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    ```
    frame geometry:
      /\
     /__\
    |    |
    *    *
    ```
    """
    elements_as_lists_of_connections = []
    for i in range(n_frames):
        base_point_left = [i, 0, 0]
        base_point_right = [i, 8, 0]
        top_point = [i, 4, 4]
        middle_left = [i, 1.5, 2]
        middle_right = [i, 6.5, 2]
        element_1 = [base_point_left, middle_left, top_point]
        element_2 = [base_point_right, middle_right, top_point]
        element_3 = [middle_left, middle_right]

        elements_as_lists_of_connections.append(element_1)
        elements_as_lists_of_connections.append(element_2)
        elements_as_lists_of_connections.append(element_3)
    return elements_as_lists_of_connections


def generate_tower(n_floors: int = 10) -> list[list[list[float]]]:
    """
    Generate a tower with n_floors.

    :param n_floors: int
        The number of floors to generate. Default is 10.
    :return: list[list[list[float]]]
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    """
    pass
