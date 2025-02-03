"""
This module contains functions to display warnings and messages to the user.
"""

import Rhino


def basic_message(message: str):
    """
    Display a warning message to the user when no object is selected.
    """
    Rhino.UI.Dialogs.ShowMessage(message, "Small message")


def layer_names_not_numbers():
    """
    Display a warning message to the user when the layer names are not numbers.
    """
    Rhino.UI.Dialogs.ShowMessage(
        "Layer names must be the target diameter of the element. The units are meters. \n Please rename the layers accordingly, for example 0.300, 0.200.",
        "ooopsi",
        Rhino.UI.ShowMessageButton.OK,
        Rhino.UI.ShowMessageIcon.Hand,
    )
