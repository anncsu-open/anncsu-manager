# Setup pixi environment and install anncsu_manager QGIS plugin

This document explains how to install the QGIS plugin that lives in the local folder `qgisplugin` and how to configure the Python package/module `pixi virtual env` as configured in `qgisenv`.

1) Install pixi as in https://pixi.sh/latest/

2) Setup pixi virtual environment
    - cd qgisenv
    - execute `$> pixi install`

3) Run qgis installed in pixi environment
    - cd qgisenv
    - enter in pixi env with `$> pixi shell`
    - A new ernv will be available marked as `(qgis-parquet) $>`
    - Run qgis in pixi env `(qgis-parquet) $> qgis`


4) Install the plugin (qgisplugin)
    - Option A — install for development (recommended)
        - Copy the folder into your active QGIS profile plugin folder:
            - Linux:
                cp -r /mnt/data/PROGRAMMING/AUTONOMO/GeoBeyond/Civici/anncsu_manager/qgisplugin/anncsu-manager ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
            - macOS:
                cp -r /mnt/data/.../qgisplugin/anncsu_manager ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/
            - Windows (PowerShell):
                Copy-Item -Recurse C:\path\to\qgisplugin\anncsu_manager $env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\
        - Restart QGIS and enable the plugin in Plugins → Manage and Install Plugins → Installed.

    - Option B — install from a ZIP (if you prefer)
        - Create a zip:
            cd /mnt/data/PROGRAMMING/AUTONOMO/GeoBeyond/Civici/anncsu-manager/qgisplugin
            zip -r anncsu_manager.zip anncsu_manager
        - In QGIS: Plugins → Manage and Install Plugins → Install from ZIP → select anncsu_manager.zip → Install → enable.


Notes
- Keep the plugin folder name unchanged when copying into the plugins directory.

## Create WhereAbouts geocoder DB from overturemaps

The plugin include WhereAbout library that allow offline and local geocoding from Ovrturemaps extracted data.
To make it at work, it is necessary to create a WhereAbout DB.
WhereAbout included code is here: https://github.com/geobeyond/anncsu-manager/tree/main/qgisplugin/anncsu_manager/whereabouts

### WhereAbout disclaimer

WhereAbouts project and original sourcecode is here: https://github.com/ajl2718/whereabouts/

### Extract Overturemaps data for WhereAbouts:

The following snippets download all Italian addressess and save them in a parquet file (almost 300MB compressed).
Note that the saved parquet need to be organized in a specific way to allow geocoder to works

```
INSTALL spatial;
LOAD spatial;
INSTALL httpfs;LOAD httpfs;

SET s3_region='us-west-2';
CREATE SEQUENCE id_sequence START 1;

CREATE OR REPLACE TABLE italia_whereabouts AS
SELECT
    nextval('id_sequence') AS id,
    ST_X(geometry) AS longitude,
    ST_Y(geometry) AS latitude,
    country,
    postal_city,
    address_levels[1].value AS region,
    address_levels[2].value AS province,
    address_levels[3].value AS municipality,
    postcode,
    street,
    number,
    unit,
    CONCAT_WS(' ', street, unit, number, municipality, province, postcode, 'Italy') AS full_address,
    sources[1].dataset AS primary_source,
    sources[1].confidence AS source_confidence,
    version
FROM read_parquet(
    's3://overturemaps-us-west-2/release/2025-10-22.0/theme=addresses/type=address/*',
    filename = true,
    hive_partitioning = 1
)
WHERE country = 'IT';

COPY italia_whereabouts TO 'italia_whereabouts.parquet' (FORMAT PARQUET, COMPRESSION zstd);
```

### Create WhereAbout Matcher DB

Prepare setup.yaml to build DB with the following content tuining depending on specific needs.

```
data:
    db_name: italia_whereabouts
    folder: geodb
    filepath: "/path/to/file/italia_whereabouts.parquet"
    sep: ","
geocoder:
    matchers: [standard]
    states: [IT]
schema:
    addr_id: id
    address_label: full_address
    address_site_name: full_address
    locality_name: municipality
    postcode: postcode
    state: country
    latitude: latitude
    longitude: longitude
```

and run the DB creation with the command:

```
python -m whereabouts setup_geocoder /path/to/file/setup.yaml
```

DB will be created in the folder: https://github.com/geobeyond/anncsu-manager/tree/main/qgisplugin/anncsu_manager/whereabouts/models

### TODO

- Make whereabouts to use remote located duckdb