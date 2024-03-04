******************
Building an Recipe
******************

Building an STAC catalog workflow consists of 4 mains steps:
    1. Write a :ref:`recipe <recipes/recipes>` file for each STAC level to describe the workflow
    2. Test the workflow on a subset of data
    3. Index that subset of data to check it works as expected
    4. Index full dataset

Parts 1 and 2 will likely go round in a loop, whilst you are developing the
workflow file, with several iterations until you are happy.

1. Write a recipe
=================

A basic recipe consists of up to 5 sections:
    1. ``paths``
    2. ``type``
    3. ``id``
    4. ``extraction_methods``
    5. ``member_of``

An example recipe can be found :ref:`here <recipes/recipes:Example Recipe>`

The extraction methods section describes how the facets are extracted from the data.

To check your recipe works as expected, you will need to run it.

2. Running the recipe on a subset of data
=========================================

To run your workflow, you will need to create a config file.
This will define an input path and output to standard out.

Example configuration
---------------------

.. include:: ../stac_generator/user_guide/example_config.rst

You should choose a filepath with a relatively small number of files to
make iteration quick and allow you to make tweaks.

You can then run your workflow using:

``stac_generator -c <path_to_config_file>``

.. program-output:: stac_generator -h

.. note::

    It is likely that this will be an iterative process to make sure that the correct
    facets are extracted and the output is as desired.

3. Indexing the data
====================

This step is as simple as changing your output plugin to point to the final destination.

Here is an example for the stac-fastapi output making use of additional kwargs:

.. code-block::

    - name: stac_fastapi
      api_url: <API_URL>
      verify: False

Once this works as expected...

4. Indexing the full dataset
============================

This is done by increasing the scope of the input plugin.
In the example we used the path ``/badc/faam/data/2005/b069-jan-05``. If our
description file covered ``/badc/faam/data`` we could now expand our input to cover
``/badc/faam/data``.

.. note::

    The higher up the tree you put the input, the longer it will take. You might
    wish to consider splitting the run into smaller segments and running in parallel.
