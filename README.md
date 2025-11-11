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
