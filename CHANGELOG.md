# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.18] - 2026-06-12

### Added

- Session path is now a configurable and persisted setting with a folder-browser widget; it auto-updates when a session is selected and validates the path before saving

## [0.0.17] - 2026-06-12

### Fixed

- Windows exception when checking a file option that does not exist: added existence guard before accessing the file path

### Changed

- Improved Italian translations and GUI label names across the wizard settings

## [0.0.16] - 2026-06-10

### Fixed

- Geometry column detection now checks the column type before applying `ST_GeomFromWKB`: if the column is already a native geometry (as returned by DuckDB spatial >1.5), the table is loaded as-is without conversion, avoiding spurious warnings and exceptions

### Changed

- Adapted code to DuckDB >1.5 which returns native geometry from `st_read` instead of a BLOB

## [0.0.15] - 2026-06-03

### Changed

- Geocoding action now runs as a `QgsTask` to avoid blocking the GUI during long operations
- Layer loading to GeoPackage now runs as a `QgsTask` to keep the interface responsive

## [0.0.14] - 2026-05-28

### Fixed

- File locking issue on Windows when writing: replaced plain file writes with a specific OGR wrapper to properly handle file access
- Windows path with drive letter (e.g. `C:\`) was incorrectly parsed as a URL schema, causing exceptions

## [0.0.13] - 2026-05-27

### Added

- Helper to auto-fill ODONIMO default value from the nearest feature of the same layer
- Matcher DB can now be placed in a custom folder outside the model directory, preventing it from being overwritten on plugin update

### Changed

- Simplified `geocoded_anncsu` editing form to show only a configurable set of fields, reducing noise from ANNCSU-only attributes
- Restored original ANNCSU source database as the default value for the ANNCSU source setting

### Fixed

- Form fields were not saved during save-settings and reset operations
- Empty string was not treated as `None` when reading comboBox data, causing unexpected behaviour

## [0.0.12] - 2026-05-26

### Added

- Sync now can clone remote repo ans setup available sessions
- Remove proprietary geocoder result before sync
- Prevent sync if proprietary geocoder results are present in geocoded_anncsu

### Changed

- Fixed git credential management and moved under misc_utils
- Fixed cast of coord to float when reading back from geocoded_anncsu

## [0.0.11] - 2026-05-18

### Added

- Windows scripts to unpack installer and run qgis in pixi env
- Manage new portal insertion setting up default values for new records
- Added git in pixi env to facilitate windows installation

### Changed

- Fix OGR limitation under windows

## [0.0.10] - 2026-05-06

### Added

- Allow to save and import into/from project not only from Mergin project
- geocoded_anncsu default value setup to facilitate manual editing
- Moved geocoder layers styles to dedicated folders

### Changed

- Style fixes
- Set default values for PLUIN_* attributes when importing

## [0.0.9] - 2026-04-24

### Changed

- Probably fixed detect-secrets in plugin repo

## [0.0.8] - 2026-04-24

### Changed

- Fixed bandit for a reverted commit

## [0.0.7] - 2026-04-24

### Changed

- Fixed bandit stuffs also for included lib

## [0.0.6] - 2026-04-24

### Changed

- Fixed some secret warning to and bumped version due to issue in qguis plugin repo
  that is not able to reload same version with fixed issues

## [0.0.5] - 2026-04-22

### Added

- Optionally merge deoverlapped results into geocoded_anncsu

### Changed

- Fixed wrong table name during roundtrip updating from ANNCSU
- Fixed all SQL for possible SQL injections to make Bandit happy

## [0.0.4] - 2026-04-15

### Changed

- Better plugin close management
- Notify lack of Mergin plugin in case use of some feature and do not rise error

## [0.0.3] - 2026-04-13

### Changed

- Readme and plugin icon fixes

## [0.0.2] - 2026-04-07

### Changed

- minor fixes

## [0.0.1] - 2026-04-07

### Added

- Initial plugin structure for ANNCSU geocoding workflow (wizard-based UI)
- WhereAbouts local geocoder with Italian address database
- OvertureMaps geocoder
- geopy-based geocoders: MapBox, HereV7, AzureMap, Nominatim, OpenCage
- Progress bar feedback during long-running downloads and ANNCSU updates
- Statistics of geocoding clusters and overlapped addresses by coordinates
- Materialized table for statistics visualization in the GUI
- `progressivo_accesso` column in address table
- Step to reduce cluster mixing in geocode results
- History preservation: previous ANNCSU data saved before session update
- Traceability: involved tables saved to trace modifications
- Translation support (Italian UI strings compiled)
- About dialog with updated logos and links
- pixi environment for reproducible QGIS + plugin execution with all dependencies
- Singleton `MessageManager` for centralized logging

### Changed

- Refactored geometry column usage (`geom` instead of `geometry`) for compatibility with `st_read` from GeoPackage
- Better management of time-consuming tasks with simplified task control
- Reduced number of SQL queries for performance
- Aligned column types to those imported from ANNCSU `.zip`
- Reduced decimal places to conform to ANNCSU API limitations
- Updated DB documentation to better describe plugin scope, architecture, and installation
- Renamed internal modules to align with plugin name
- Removed unused settings parameter

### Fixed

- Error in table naming and WKB format issue when loading GeoPackage
- Memory leak: clean deletion of allocated geocoder to avoid leaving DB connections open
- Detach of Matched DB for WhereAbouts geocoder made more robust
- Working roundtrip to update current session from ANNCSU data with threshold-based change notification
- `session_url` field made editable in the wizard

[0.0.1]: https://github.com/anncsu-open/anncsu-manager/releases/tag/v0.0.1
