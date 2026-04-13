# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
