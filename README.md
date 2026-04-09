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

### User workflow to update ANNCSU db

Actually the workflow need a Mergin project locally. In the future these dependecy could be overrided.
The steps of a common workflow are:
1) Install the plugin
2) (optional) Install Whereabouts matcher db
3) Run the plugin
4) Configure active geocoders in plugin settings
5) Create a new scope session in plugin settings. Thiso will create a new DuckDB session into `anncsu_manager/resources/data` folder.
6) Run geocoders
7) Save generated layers in a Merging project folder
8) (optional) modify Success/Fails/Out Of Fence layers to match real coordinates
9) Update scope session with Success/Fails/Out Of Fence layers from mergin project folder.
10) Sync current scope session with remote git repo
11) Remote git repo actions will be in charge to extract modifications from porios commits and update ANNCSU official DB.
12) (optional) A scope session can be aligned with the actual ANNCSU database with "Update from ANNCSU" button in plugin settings.

## Installation/Setup

### Setup pixi environment and install anncsu_manager QGIS plugin
This section explains how to install the QGIS plugin that lives in the local folder `qgisplugin` and how to configure the Pixi virtual environment defined in `qgisenv` folder.

1. Install Pixi as described at https://pixi.sh/latest/

2. Set up the Pixi virtual environment
    - `cd qgisenv`
    - Run `pixi install`

Notes:
all dependencies are described into `./qgisenv/pixi.toml`

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

    - Option B - install from QGIS plugin repo as usual

Notes:
- Keep the plugin folder name unchanged when copying it into the plugins directory.

## Local geocoding using WhereAbouts geocoder DB from Overture Maps

The plugin includes the WhereAbouts library, which allows offline and local geocoding from Overture Maps extracted data.
To make it work, it is necessary to create a WhereAbouts DB.
The included WhereAbouts code is here: https://github.com/anncsu-open/anncsu-manager/tree/main/qgisplugin/anncsu_manager/whereabouts

### Precompiled whereabouts DB

A precompiled version of DB is available (here)[https://github.com/anncsu-open/anncsu-data/blob/main/italia_whereabouts.db.zip], download it and unzip the file in the `anncsu_manager/whereabouts/models`
plugin folder configuring it's name as `italia_whereabouts` in `matcher_db` key into WhereAbout geocoder
configuration.

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

