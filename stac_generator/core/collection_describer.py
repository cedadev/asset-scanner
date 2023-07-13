# encoding: utf-8
"""
Collection Description
======================
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Python imports
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import yaml

# 3rd Party Imports
from directory_tree import DatasetNode
from pydantic import BaseModel

# Package imports
from stac_generator.core.utils import load_description_files

LOGGER = logging.getLogger(__name__)


class Category(BaseModel):
    """Category label model."""

    label: str
    regex: str


class STACModel(BaseModel):
    """Collections processor description model."""

    id: dict = {}
    extraction_methods: List[dict] = []
    post_extraction_methods: List[dict] = []


class CollectionDescription(BaseModel):
    """Top level container for CollectionDescriptions."""

    paths: list

    asset: Optional[STACModel]
    item: Optional[STACModel]
    collection: Optional[STACModel]

    categories: List[Category] = []

    def __repr__(self):
        return yaml.dump(self.dict())


class CollectionDescriptions:
    """
    Holds references to all the description files and handles loading, merging
    and returning an :py:obj:`ItemDescription`
    """

    def __init__(
        self, root_path: Optional[str] = None, filelist: Optional[list] = None
    ):
        """

        :param root_path: Path to the root of the yaml store
        :param filelist: Can supply a set of yml files to load. If present, root_path is ignored.
        """

        self.tree = DatasetNode()

        self._build_tree(root_path, filelist)

    def _build_tree(self, root_path: str, files: List[Path]) -> None:
        """
        Loads the yaml files from the root path and builds the dataset tree
        with references to the yaml files.

        :param root_path: Path at the top of the yaml file tree
        :param files: list of files to open.
        """

        if not files:
            files = load_description_files(root_path)

        if not files:
            LOGGER.error(
                "No description files found. "
                "Check the path in your configuration. Exiting..."
            )
            exit()

        for file in files:
            with open(file, encoding="utf-8") as reader:
                data = yaml.safe_load(reader)

                for dataset in data.get("paths", []):
                    # Strip trailing slash. Needed to make sure tree search works
                    if dataset != "/":
                        dataset = dataset.rstrip("/")

                    LOGGER.info(
                        "Adding file %s to path %s in description tree", file, dataset
                    )
                    self.tree.add_child(dataset, description_file=file.as_posix())

    def get_description(self, filepath: str, **kwargs) -> CollectionDescription:
        """
        Get the merged description for the given file path.
        This gets all the description files along the path
        and merges them from top down so that more generic
        descriptions are overridden.
        e.g.

        files describing ``/badc`` will be overridden by files
        which describe ``/badc/faam/data``

        dict values are overridden by more specific files and
        arrays are appended to, with duplicates ignored.

        .. note::
            For remote filepaths (e.g. https://... or gs://) a ``/``
            character will be pre-pended. This is to enable the lookup
            to pass as the root node of the tree is ``/``.

        :param filepath: Path for which to retrieve the description
        """

        if "description_path" in kwargs:
            filepath = kwargs.get("description_path")

        elif not filepath[0] == "/":
            filepath = f"/{filepath}"

        nodes = self.tree.search_all(filepath)
        description_files = [node.description_file for node in nodes]

        config_description = self.load_config(*description_files)

        return CollectionDescription(**config_description)

    @lru_cache(100)
    def load_config(self, *args: str) -> dict:
        """

        :param args: each arg is a filepath to a description file
        :return: dictionary containing the merged properties of all the matching nodes
        """
        base_dict = {}
        for file in args:
            with open(file, encoding="utf-8") as reader:
                base_dict = self.description_merge(base_dict, yaml.safe_load(reader))

        return base_dict

    def methods_merge(self, base_methods: list, override_methods: list) -> list:
        """
        merge sections from two description

        :param base_section: methods of the base description
        :param override_section: methods of the more specific description
        """
        base_method_dict = {
            base_method["method"]: base_method for base_method in base_methods
        }

        for method in override_methods:

            method_name = method["method"]

            if method_name == "default" and "default" in base_method_dict:

                base_method_dict["default"]["inputs"]["defaults"] = {
                    **base_method_dict["default"]["inputs"]["defaults"],
                    **method["inputs"]["defaults"],
                }

                base_methods.append(base_method_dict["default"])

            else:

                base_methods.append(method)

        return base_methods

    def section_merge(self, base_section: dict, override_section: dict) -> dict:
        """
        merge sections from two description

        :param base_section: methods of the base description
        :param override_section: methods of the more specific description
        """
        if "id" in override_section:
            base_section["id"] = override_section.pop("id")

        for methods_name, methods in override_section.items():
            base_section[methods_name] = self.methods_merge(
                base_section[methods_name], methods
            )

        return base_section

    def description_merge(self, *args) -> dict:
        """
        merge multiple descriptions into one

        :params: List of descriptions
        """
        descriptions = list(args)

        if len(descriptions) == 1:
            return descriptions[0]

        # Make a copy of the root description
        description = descriptions.pop(0)

        for next_description in descriptions:
            if "paths" in next_description:
                description["paths"] = next_description.pop("paths")

            for section_name, section in next_description.items():
                if section_name in description:
                    description[section_name] = self.section_merge(
                        description[section_name], section
                    )
                else:
                    description[section_name] = section

        return description


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root", help="root from which to load all the yaml description files"
    )
    parser.add_argument("path", help="path to retrieve description for")

    arguments = parser.parse_args()

    collection_descriptions = CollectionDescriptions(arguments.root)

    collection_description = collection_descriptions.get_description(arguments.path)

    print(collection_description)
