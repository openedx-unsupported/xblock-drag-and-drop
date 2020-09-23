# Imports ###########################################################

import os
from setuptools import setup


# Functions #########################################################

def package_data(pkg, root_list):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in root_list:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


# Main ##############################################################

setup(
    name='xblock-drag-and-drop',
    version='0.1',
    description='XBlock - Drag-and-Drop',
    packages=['drag_and_drop'],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': 'drag-and-drop = drag_and_drop:DragAndDropBlock',
    },
    package_data=package_data("drag_and_drop", ["static", "templates", "public"]),
)
