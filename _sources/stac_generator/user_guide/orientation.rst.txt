Orientation
===========

The :ref:`STAC Generator <index:stac generator>` is a framework for generating
STAC catalogs and is built to be modular and extensible. This can be confusing
for new users but this guide aims to act as an orientation to help new users
understand what this package can do and how the pieces fit together.

There are various pluggable pieces:
    - Inputs
    - Outputs
    - Extraction Methods
    - Mappings

These pieces should allow you to construct a workflow which works for your use case and provide
python entry points to allow you to write your own plugins.
The STAC Generator package stores some :ref:`inputs <stac_generator/inputs:inputs>` which can be used to read from a range of different
sources messages of STAC objects to genertate.
The :ref:`item <stac_generator/generators:Item Generator>`, and :ref:`collection <stac_generator/generators:Collection Generator>`
generators take these messages and extract the required facets to buil the relevant STAC object using a variety of :ref:`extraction methods <stac_generator/extraction_methods:Extraction Methods>`.
These generated objects can then be passed to a range of :ref:`outputs <stac_generator/outputs:outputs>`.

The generators have two levels of configuration. Global configuration, passed at the command line on
invocation, which defines the inputs, ouputs, logging etc.

An example can be found :ref:`here <stac_generator/index:Sample configuration>`.

The second level of configuration comes in the form of recipes. These YAML files
describe the workflow for extracting facets and other metadata to build the items and collections of the STAC Catalog.
Background for recipes can be found `here <recipes/recipes:Recipes>`_
and a guide for how to build, and test these files is :ref:`here <recipes/building_a_workflow:building an Recipe>`.

The different available extraction methods which can construct these workflows are found :ref:`here <stac_generator/extraction_methods:Extraction Methods>`.

The `CEDA repository containing these recipes <https://github.com/cedadev/stac-recipes>`_ can
be used as an example. An example which includes extracting metadata from the NetCDF header is
`sentinel5 <https://github.com/cedadev/stac-recipes/blob/master/descriptions/neodc/sentinel/sentinel5.yml>`_

.. code-block:: yaml

  paths:
    - /neodc/sentinel_ard/data/sentinel_2

  type: item

  # This will be run over the meta files, example: neodc/sentinel_ard/data/sentinel_2/2018/07/05/S2A_20180705_lat57lon375_T30VVJ_ORB123_utm30n_osgb_vmsk_sharp_rad_srefdem_stdsref_meta.xml
  id:
    # Use full path minus the extension for ID
    - method: default
      inputs:
        defaults:
          item_id: $instance_id

  extraction_methods:
   # Extract information from the meta file
    - method: xml
      inputs:
        extraction_keys:
          - name: east
            key: .//gmd:eastBoundLongitude/gco:Decimal
          - name: west
            key: .//gmd:westBoundLongitude/gco:Decimal
          - name: north
            key: .//gmd:northBoundLatitude/gco:Decimal
          - name: south
            key: .//gmd:southBoundLatitude/gco:Decimal
          - name: start_datetime
            key: .//gml:beginPosition
          - name: end_datetime
            key: .//gml:beginPosition
          - name: supInfo
            key: .//gmd:supplementalInformation/gco:CharacterString
          - name: EPSG
            key: .//gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString
        namespaces:
          gmd: http://www.isotc211.org/2005/gmd
          gml: http://www.opengis.net/gml
          gco: http://www.isotc211.org/2005/gco

    # Extract the variables from the supInfo field
    - method: regex
      inputs:
        regex: 'ESA file name: (?P<esa_file_name>.*)'
        input_term: supInfo

    - method: regex
      inputs:
        regex: 'Mean_Sun_Angle_Zenith: (?P<Mean_Sun_Angle_Zenith>.*)'
        input_term: supInfo

    - method: regex
      inputs:
        regex: 'Mean_Sun_Angle_Azimuth: (?P<Mean_Sun_Angle_Azimuth>.*)'
        input_term: supInfo

    # Extract the manifest path info
    - method: regex
      inputs:
        regex: 'neodc\/sentinel_ard\/data\/sentinel_2\/(?P<year>\d{4})\/(?P<month>\d{2})\/(?P<day>\d{2})\/S2(?P<satellite>[abAB]{1}).*'
        input_term: uri

    - method: lambda
      inputs:
        function: 'lambda satellite: satellite.lower()'
        input_args:
          - $satellite
        output_key: satellite

    # Generate path to the manifest file
    - method: string_template
      inputs:
        template: '/neodc/sentinel2{satellite}/data/L1C_MSI/{year}/{month}/{day}/{esa_file_name}.manifest'
        output_key: manifest_file

    # Extract information from the manifest file
    - method: xml
      inputs:
        input_term: manifest_file
        extraction_keys:
          - name: Instrument Family Name
            key: .//safe:platform/safe:instrument/safe:familyName
          - name: Instrument Family Name Abbreviation
            key: .//safe:platform/safe:instrument/safe:familyName
            attribute: abbreviation
          - name: Platform Number
            key: .//safe:platform/safe:number
          - name: NSSDC Identifier
            key: .//safe:platform/safe:nssdcIdentifier
          - name: Start Relative Orbit Number
            key: .//safe:orbitReference/safe:relativeOrbitNumber
          - name: Start Orbit Number
            key: .//safe:orbitReference/safe:orbitNumber
          - name: Ground Tracking Direction
            key: .//safe:orbitReference/safe:orbitNumber
            attribute: groundTrackDirection
          - name: Instrument Mode
            key: .//safe:platform/safe:instrument/safe:mode
          - name: Coordinates
            key: .//safe:frameSet/safe:footPrint/gml:coordinates
        namespaces:
          safe: http://www.esa.int/safe/sentinel/1.1
          gml: http://www.opengis.net/gml

    - method: regex
      inputs:
        regex: '(?P<path_root>.+?)_vmsk_sharp_rad_srefdem_stdsref_meta\.'

    - method: lambda
      inputs:
        function: 'lambda coords_string: [[float(i), float(k)]for i,k in zip(coords_string.strip().split()[1::2], coords_string.strip().split()[0::2])]'
        input_args:
          - $Coordinates
        output_key: coords

    - method: geometry_polygon
      inputs:
        coordinates_term: coords

    - method: geometry_to_bbox
      inputs:
        type: polygon

    - method: string_template
      inputs:
        template: '{esa_file_name}.SAFE/MTD_MSIL1C.xml'
        output_key: inner_file

    - method: string_template
      inputs:
        template: '/neodc/sentinel2{satellite}/data/L1C_MSI/{year}/{month}/{day}/{esa_file_name}.zip'
        output_key: zip_file

    - method: open_zip
      inputs:
        zip_file: $zip_file
        inner_file: $inner_file
        output_key: esa_product

    - method: xml
      inputs:
        input_term: esa_product
        extraction_keys:
          - name: Cloud Coverage Assessment
            key: .//psd-14:Quality_Indicators_Info/Cloud_Coverage_Assessment
          - name: Product Type
            key: .//psd-14:General_Info/Product_Info/PRODUCT_TYPE
          - name: Datatake Type
            key: .//psd-14:General_Info/Product_Info/Datatake/DATATAKE_TYPE
        namespaces:
          psd-14: https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-1C.xsd


    - method: string_template
      inputs:
        template: '{path_root}.*.tif'
        output_key: data_regex

    - method: string_template
      inputs:
        template: '{path_root}.*_thumbnail.jpg'
        output_key: thumbnail_regex

    - method: string_template
      inputs:
        template: '{path_root}.*_meta.xml'
        output_key: metadata_regex

    - method: elasticsearch_assets
      inputs:
        search_field: path
        regex_term: data_regex
        fields:
          - name: size
          - name: location
        extraction_methods:
          - method: default
            inputs:
              defaults:
                roles: ["data"]

    - method: elasticsearch_assets
      inputs:
        search_field: path
        regex_term: thumbnail_regex
        fields:
          - name: size
          - name: location
        extraction_methods:
          - method: default
            inputs:
              defaults:
                roles: ["thumbnail"]

    - method: elasticsearch_assets
      inputs:
        search_field: path
        regex_term: metadata_regex
        fields:
          - name: size
          - name: location
        extraction_methods:
          - method: default
            inputs:
              defaults:
                roles: ["metadata"]

    - method: rename_assets
      inputs:
        rename:
          - name: cog
            regex: '.*_stdsref.tif'
          - name: cloud
            regex: '.*_clouds.tif'
          - name: cloud_probability
            regex: '.*_clouds_prob.tif'
          - name: topographic_shadow
            regex: '.*_toposhad.tif'
          - name: metadata
            regex: '.*_meta.xml'
          - name: thumbnail
            regex: '.*_thumbnail.jpg'
          - name: saturated_pixels
            regex: '.*_sat.tif'
          - name: valid_pixels
            regex: '.*_valid.tif'
        output_key: data_regex

    - method: lambda
      inputs:
        function: 'lambda assets: {asset_key: asset_value | {"href": "https://dap.ceda.ac.uk" + asset_value["href"]} for asset_key, asset_value in sorted(assets.items())}'
        input_args:
          - $assets
        output_key: assets

    - method: lambda
      inputs:
        function: 'lambda path_root: path_root.replace("/badc/sentinel1b/data", "").replace("/badc/sentinel1a/data", "").strip("/").replace("/", ".")'
        input_args:
          - $path_root
        output_key: instance_id

    - method: iso_date
      inputs:
        date_keys:
          - start_datetime
          - end_datetime
        formats:
          - '%Y-%m-%dT%H%M%SZ'

    - method: datetime_bound_to_centroid

    # Clean up unneeded terms
    - method: remove
      inputs:
        keys:
          - supInfo
          - year
          - month
          - day
          - manifest_file
          - west
          - south
          - east
          - north
          - path_root
          - data_regex
          - thumbnail_regex
          - metadata_regex
          - Coordinates
          - coords
          - satellite
          - zip_file
          - inner_file
          - esa_product
          - uri

  member_of:
    - recipes/collection/sentinel2_ARD.yaml

The “extraction_methods” are the workflow. In the example shows the xml extaction method being used to extract some facets
from a meta data file, then this information is then manipulated by several different extaction methods including retrieving
a list of assets from CEDA's elasticsearch index.

The extraction methods can also be used for collection generation but typically this will be aggregation of their items.
