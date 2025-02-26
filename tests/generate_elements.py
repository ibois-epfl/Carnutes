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


def generate_scissor_truss(n_frames: int = 10) -> list[list[list[float]]]:
    """
    Generate a scissor truss with n_frames.
    it is 8m wide, 4m high.

    :param n_frames: int
        The number of frames to generate. Default is 10.
    :return: list[list[list[float]]].
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    ```
    frame geometry:
           /|\
          / | \
         /  |  \
        /   |   \
       /____|____\
      /    / \    \
     /  /       \  \
    //             \\
    ```
    """
    elements_as_lists_of_connections = []
    for i in range(n_frames):
        base_point_left = [i, 0, 0]
        base_point_right = [i, 8, 0]
        top_point = [i, 4, 4]
        middle_left = [i, 2, 2]
        middle_right = [i, 6, 2]
        middle_bottom = [i, 4, 1.75]
        element_1 = [base_point_left, middle_left, top_point]
        element_2 = [base_point_right, middle_right, top_point]
        element_3 = [base_point_left, middle_bottom, middle_right]
        element_4 = [base_point_right, middle_bottom, middle_left]
        element_5 = [top_point, middle_bottom]

        elements_as_lists_of_connections.append(element_1)
        elements_as_lists_of_connections.append(element_2)
        elements_as_lists_of_connections.append(element_3)
        elements_as_lists_of_connections.append(element_4)
        elements_as_lists_of_connections.append(element_5)

    return elements_as_lists_of_connections


def generate_symmetrical_portal(n_frames: int = 10) -> list[list[list[float]]]:
    """
    Generate a symmetrical portal with n_frames.
    it is 8m wide, 4m high.

    :param n_frames: int
        The number of frames to generate. Default is 10.
    :return: list[list[list[float]]].
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    ```
    frame geometry:

               /\
         /           \
       / \  /     \  / \
      /  /           \  \
     / /               \ \
    //                   \\
    """
    elements_as_lists_of_connections = []

    for i in range(n_frames):
        base_point_left = [i, 0, 0]
        base_point_right = [i, 8, 0]
        top_point = [i, 4, 4]
        top_left = [i, 1, 3.5]
        top_right = [i, 7, 3.5]
        lower_left = [i, 1.5, 2.5]
        lower_right = [i, 6.5, 2.5]
        element_1 = [base_point_left, lower_left, top_point]
        element_2 = [base_point_right, lower_right, top_point]
        element_3 = [lower_left, top_left]
        element_4 = [lower_right, top_right]
        element_5 = [base_point_left, top_left]
        element_6 = [base_point_right, top_right]
        element_7 = [top_left, top_point]
        element_8 = [top_right, top_point]

        elements_as_lists_of_connections.append(element_1)
        elements_as_lists_of_connections.append(element_2)
        elements_as_lists_of_connections.append(element_3)
        elements_as_lists_of_connections.append(element_4)
        elements_as_lists_of_connections.append(element_5)
        elements_as_lists_of_connections.append(element_6)
        elements_as_lists_of_connections.append(element_7)
        elements_as_lists_of_connections.append(element_8)

    return elements_as_lists_of_connections


def generate_asymmetrical_portal(n_frames: int = 10) -> list[list[list[float]]]:
    """
    Generate an asymmetrical portal with n_frames.
    it is 8m wide, 3m high.

    :param n_frames: int
        The number of frames to generate. Default is 10.
    :return: list[list[list[float]]].
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    ```
    frame geometry:


                         _____________
                   /    \            /
            /            \      /
     _______________________/
    |                     |
    |                     |
    |                     |
    """
    elements_as_lists_of_connections = []

    for i in range(n_frames):
        column_left_lower = [i, 0, 0]
        column_right_lower = [i, 5, 0]
        column_left_upper = [i, 0, 2]
        column_right_upper = [i, 5, 2]
        top_left = [i, 4.5, 3]
        top_right = [i, 8, 3]

        element_1 = [column_left_lower, column_left_upper]
        element_2 = [column_right_lower, column_right_upper, top_left]
        element_3 = [column_left_upper, column_right_upper, top_right]
        element_4 = [column_left_lower, top_left, top_right]

        elements_as_lists_of_connections.append(element_1)
        elements_as_lists_of_connections.append(element_2)
        elements_as_lists_of_connections.append(element_3)
        elements_as_lists_of_connections.append(element_4)

    return elements_as_lists_of_connections


def generate_tower(n_floors: int = 10) -> list[list[list[float]]]:
    """
    Generate n towers 8m high.

    :param n_floors: int
        The number of floors to generate. Default is 10.
    :return: list[list[list[float]]]
        a list of elements, each element is a list of 3 points, each point is a list of 3 floats.
    """

    elements_as_lists_of_connections = []

    for i in range(n_floors):
        step = 6 * i
        point_1_level_0 = [step, 0, 0]
        point_2_level_0 = [step, 4, 0]
        point_3_level_0 = [step + 4, 4, 0]
        point_4_level_0 = [step + 4, 0, 0]
        point_1_level_1 = [step - 0.828, 2, 4]
        point_2_level_1 = [step + 2, 4 + 0.828, 4]
        point_3_level_1 = [step + 4.828, 2, 4]
        point_4_level_1 = [step + 2, -0.828, 4]
        point_1_level_2 = [step, 4, 8]
        point_2_level_2 = [step + 4, 4, 8]
        point_3_level_2 = [step + 4, 0, 8]
        point_4_level_2 = [step, 0, 8]

        element_1 = [point_1_level_0, point_1_level_1, point_1_level_2]
        element_2 = [point_2_level_0, point_2_level_1, point_2_level_2]
        element_3 = [point_3_level_0, point_3_level_1, point_3_level_2]
        element_4 = [point_4_level_0, point_4_level_1, point_4_level_2]
        element_5 = [point_1_level_0, point_2_level_0]
        element_6 = [point_2_level_0, point_3_level_0]
        element_7 = [point_3_level_0, point_4_level_0]
        element_8 = [point_4_level_0, point_1_level_0]
        element_9 = [point_1_level_1, point_2_level_1]
        element_10 = [point_2_level_1, point_3_level_1]
        element_11 = [point_3_level_1, point_4_level_1]
        element_12 = [point_4_level_1, point_1_level_1]
        element_13 = [point_1_level_2, point_2_level_2]
        element_14 = [point_2_level_2, point_3_level_2]
        element_15 = [point_3_level_2, point_4_level_2]
        element_16 = [point_4_level_2, point_1_level_2]

        elements_as_lists_of_connections.append(element_1)
        elements_as_lists_of_connections.append(element_2)
        elements_as_lists_of_connections.append(element_3)
        elements_as_lists_of_connections.append(element_4)
        elements_as_lists_of_connections.append(element_5)
        elements_as_lists_of_connections.append(element_6)
        elements_as_lists_of_connections.append(element_7)
        elements_as_lists_of_connections.append(element_8)
        elements_as_lists_of_connections.append(element_9)
        elements_as_lists_of_connections.append(element_10)
        elements_as_lists_of_connections.append(element_11)
        elements_as_lists_of_connections.append(element_12)
        elements_as_lists_of_connections.append(element_13)
        elements_as_lists_of_connections.append(element_14)
        elements_as_lists_of_connections.append(element_15)
        elements_as_lists_of_connections.append(element_16)

    return elements_as_lists_of_connections
