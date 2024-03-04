
*******
Recipes
*******

.. toctree::
    :hidden:

    building_a_workflow


These documents describe how to process the files within a dataset and extract facets.
These documents are aggregated along the branch with the information lower in the tree taking
precendence.
Having multiple files at different points in the tree allow for a narrowing of information.
i.e. A default set at a higher level, if not overwritten, will exist at all points down the tree.

Example Recipe
==============

This file applies to all files listed under: ``/badc/faam/data``.

It uses the regex processor to match a regex pattern to
extract a date. This is then passed to the ISO Date post-processor which converts
the date into the ISO8601 format.

The second, extracts platform and flight number from the filepath.
No pre or post processing is done in this case.

.. code-block:: yaml

    paths:
      - /badc/faam/data
    type: item
    extraction_methods:
      - method: regex
        inputs:
          regex: '^(?:[^_]*_){2}(?P<datetime>\d*)'

Recipe sections
===============

The description file consists of 5 top level keys:

A :ref:`Full JSON Schema<recipes/recipes:schema>` references below.

.. list-table::
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - ``paths``
    - list[str]
    - List of paths this workflow applies to.
  * - ``type``
    - str
    - Defines the extraction methods to create the assets matching the given path.
  * - ``id``
    - list[:ref:`Extraction Methods <extraction-methods>`]
    - Defines the ID of the STAC record runs after extraction methods.
  * - ``extraction_methods``
    - list[:ref:`Extraction Methods <extraction-methods>`]
    - Defines the extraction methods to generate the metadata for the STAC record.
  * - ``member_of``
    - list[str]
    - Defines the recipers for the Collections the generated Item or Collection is a member of.

Paths
-----

Describes the paths where this file applies. Can be multiple locations.
The path references all points below it in the hierarchy.

.. code-block:: yaml

    paths:
      - /badc/faam/data

Type
----

Defines the tyoe of STAC record to create.

.. code-block:: yaml

    type: item

ID
---

Defines a list of extraction methods used to generate the record's ID.
This is run after the extraction methods.

.. code-block:: yaml

    id:
      # Use directory name ID
      - method: default
        inputs:
          defaults:
            item_id: $instance_id

Extraction Methods
------------------

Defines a list of extraction methods used to generate the record's metadata.

.. code-block:: yaml
    
    extraction_methods:
      - method: lambda
        inputs:
          function: 'lambda uri: uri.replace("/badc/cmip6/data", "").strip("/").replace("/", ".")'
          input_args:
            - $uri
          output_key: instance_id

Member Of
---------

Defines a list of paths to recipes that this record is a member of.

.. code-block:: yaml

    member_of:
      - recipes/collection/cmip6.yaml

Schema
-------

.. program-output:: python -c "from stac_generator.core.baker import Recipe; import json; print(json.dumps(Recipe.schema(), indent=4))"
