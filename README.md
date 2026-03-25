# ANNCSU_MANAGER
A QGIS plugin to facilitate updates to the ANCSU database, the official Italian database of geocoded addresses.

## Scope of anncsu_manager

The plugin dynamically integrates various commercial/free, local, and remote geocoders to resolve address coordinates not yet available in the ANNCSU database.
The target user of the plugin is a municipality that wants or needs to geocode all its ANNCSU addresses.

## Architecture

### Scope session
The core of the plugin is a DuckDB single-file spatial database where all tables are saved.
Each DuckDB file is a session named based on the municipality ANNCSU code and creation date.
Each Scope session DB is a self-consistent session where all geocoding actions are saved.
The Scope session is managed in the Settings section of the plugin.

### Municipality git repo
Each municipality would have a Git repository where the Scope session is saved/synced using common Git commands. Sync can be triggered with the plugin sync button or manually with a standard Git commit/push workflow.

### Mergin integration
For addresses that geocoders are not able to geocode, the plugin integrates features to prepare a [Mergin Maps](https://merginmaps.com/) project where all unresolved addresses are exported for manual field-survey correction.
Edited layers in a Mergin project are then imported back into the Scope session DB through ANNCSU_MANAGER.

### ANNCSU-SDK integration via GitHub actions

The Scope session is committed/synced in the municipality Git repository. After each commit, a set of GitHub Actions is triggered to update the ANNCSU DB using [ANNCSU-SDK](https://github.com/anncsu-open/anncsu-sdk).
Each commit extracts a diff from the previous commit on a specific configured table using the [geodiff](https://github.com/MerginMaps/geodiff) tool.
New, deleted, or updated records drive updates to the ANNCSU database using [ANNCSU-SDK](https://github.com/anncsu-open/anncsu-sdk) and GitHub Actions infrastructure.

## Installation/Setup

### Setup pixi environment and install anncsu_manager QGIS plugin
This section explains how to install the QGIS plugin that lives in the local folder `qgisplugin` and how to configure the Pixi virtual environment defined in `qgisenv`.

1. Install Pixi as described at https://pixi.sh/latest/

2. Set up the Pixi virtual environment
    - `cd qgisenv`
    - Run `pixi install`

3. Run QGIS installed in the Pixi environment
    - `cd qgisenv`
    - Enter the Pixi environment with `pixi shell`
    - A new shell prompt appears, marked as `(qgis-parquet) $`
    - Run QGIS from that shell with `qgis`

4. Install the plugin (`qgisplugin`)
    - Option A - install for development (recommended)
        - Copy the folder into your active QGIS profile plugin folder (depending on your QGIS profile setup):
            - Linux:
                `cp -r /path/to/anncsu-manager/qgisplugin/anncsu_manager ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
            - macOS:
                `cp -r /path/to/anncsu-manager/qgisplugin/anncsu_manager ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/`
            - Windows (PowerShell):
                `Copy-Item -Recurse C:\path\to\anncsu-manager\qgisplugin\anncsu_manager $env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\`
    - Restart QGIS and enable the plugin in Plugins -> Manage and Install Plugins -> Installed.

    - Option B TODO - install from a ZIP (if you prefer)
        - Create a ZIP:
            - `cd /mnt/data/PROGRAMMING/AUTONOMO/GeoBeyond/Civici/anncsu-manager/qgisplugin`
            - `zip -r anncsu_manager.zip anncsu_manager`
        - In QGIS: Plugins -> Manage and Install Plugins -> Install from ZIP -> select anncsu_manager.zip -> Install -> enable.

Notes:
- Keep the plugin folder name unchanged when copying it into the plugins directory.

## Local geocoding using WhereAbouts geocoder DB from Overture Maps

The plugin includes the WhereAbouts library, which allows offline and local geocoding from Overture Maps extracted data.
To make it work, it is necessary to create a WhereAbouts DB.
The included WhereAbouts code is here: https://github.com/geobeyond/anncsu-manager/tree/main/qgisplugin/anncsu_manager/whereabouts

### WhereAbout disclaimer

The WhereAbouts project and original source code are here: https://github.com/ajl2718/whereabouts/
### Extract Overture Maps data for WhereAbouts

The following snippets download all Italian addresses and save them in a Parquet file (almost 300 MB compressed).
Note that the saved Parquet file must be organized in a specific way to allow the geocoder to work.

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

Prepare `setup.yaml` to build the DB, tuning the content below based on your specific needs.
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

Run DB creation with the command:

```
python -m whereabouts setup_geocoder /path/to/file/setup.yaml
```

The DB will be created in: `/path/to/qgisplugin/anncsu_manager/whereabouts/models`

