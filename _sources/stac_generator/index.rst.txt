**************
STAC Generator
**************

:fa:`github` `View on Github <https://github.com/cedadev/stac-generator>`_

This library aims to be a generic tool for extracting meta data. This meta dat can then be mapped into the STAC framework to generate
`STAC <https://github.com/radiantearth/stac-spec/>`_-like items and collections.

You should be able to generate content which contains all the relevant information to allow you to
construct a valid `STAC item <https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md>`_.

This library works on the premise that you can build a processing workflow for each of your datasets
by chaining together different extraction methods to extract and manipulate the relevant information.
The core facet extraction chain works on an atomic basis, where input plugins provide a single object
for inspection and output a single object.

Read the :ref:`Orientation <stac_generator/user_guide/orientation:Orientation>` guide as a introduction into the framework.

Installing
==========

.. code-block:: console

   pip install stac-generator

Usage
======

There is a console script defined by this package which can be used to run the
extractors ``stac_generator``.

.. code-block:: console

    usage: stac_generator [-c] path/to/conf

    Run the STAC Generator as configured

    required arguments:
      -c        Path to a yaml configuration file

    optional arguments:
      -h, --help  show this help message and exit


Configuration
==============

The configuration file feeds this top level script and configures the inputs/outputs
as well as the generator.

Base configuration options:
---------------------------

.. list-table::
   :header-rows: 1

   * - Option
     - Description
   * - ``generator``
     - The generator type ``item`` or ``collection``
   * - ``recipes_root``
     - ``REQUIRED`` Path to the root directory for the recipes. Used to describe workflows.
   * - ``inputs``
     - ``REQUIRED`` Must have at least one :ref:`input <stac_generator/inputs:Inputs>`.
   * - ``outputs``
     - ``REQUIRED`` Must have at least one :ref:`output <stac_generator/outputs:Outputs>`.
   * - ``extraction_methods``
     - ``OPTIONAL`` Defaults for any extraction methods that are being used :ref:`extraction methods <stac_generator/extraction_methods>`_.
   * - ``logging``
     - Kwargs passed to the `logging.basicConfig <https://docs.python.org/3/library/logging.html#logging.basicConfig>`_ setup method

The generator can be specified in the configuration file or can be loaded from
an entry point. The configuration value takes precedence over entry points.

.. warning::
    Only the first generator will be loaded from entry points.

Sample configuration
--------------------

   .. code-block:: yaml

      generator: item

      recipe_root: example/recipes

      inputs:
        - method: file_system
          path: /badc/faam/data/2005/b069-jan-05

      outputs:
        - method: standard_out

      logging:
         level: INFO


Plugins
=======

Plugins are used to add modular components and allow extension of the base
capabilities to fit your needs. The range of different Inputs, Outputs,
Extraction Methods, and Mappings have been developed to meet different use cases.


.. toctree::
   :maxdepth: 3

   inputs
   outputs
   extraction_methods
   mappings
   generators
