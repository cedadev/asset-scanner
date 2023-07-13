# encoding: utf-8
"""


Configuration
-------------

.. code-block:: yaml

    item_descriptions:
        root_directory: /path/to/root/descriptions

"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from datetime import datetime

from stac_generator.core.collection_describer import CollectionDescription
from stac_generator.core.generator import BaseGenerator
from stac_generator.core.utils import dict_merge
from stac_generator.types.generators import GeneratorType

LOGGER = logging.getLogger(__name__)


class CollectionGenerator(BaseGenerator):

    TYPES = GeneratorType.COLLECTION

    def run_id_extraction_methods(
        self, body: dict, description: CollectionDescription, **kwargs: dict
    ) -> dict:
        """
        Extract the raw facets from the listed extraction methods

        :param body: Dict of current extracted data
        :param description: CollectionDescription
        :return: dictionary containing ids
        """

        ids = {}
        collection_description = description.collection

        if collection_description and collection_description.id:
            collection_id_description = collection_description.id

        else:
            collection_id_description = self.DEFAULT_ID_EXTRACTION_METHODS[
                "collection_id"
            ]

        ids["collection_id"] = self._run_extraction_method(
            collection_id_description, body, **kwargs
        )

    def _process(self, uri: str, **kwargs) -> None:
        """
        Method to outline the processing pipeline for an asset

        :param uri:

        :return:
        """

        # Get dataset description file
        description = self.collection_descriptions.get_description(uri, **kwargs)

        body = {}

        body = self.run_extraction_methods(uri, body, description, **kwargs)

        ids = self.run_id_extraction_methods(body, description, **kwargs)

        data = self.map(uri, ids, body, description, **kwargs)

        self.output(data, description=description, **kwargs)
