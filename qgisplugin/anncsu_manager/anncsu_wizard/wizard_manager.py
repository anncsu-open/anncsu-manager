from qgis.PyQt.QtWidgets import (
    QWizard,
    QProgressBar,
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui

# wizard pages
from anncsu_manager.anncsu_wizard.wizard_geocoder_step import ANNCSUWizardRunGeocoders
from anncsu_manager.anncsu_wizard.wizard_evaluate_geocode_step import ANNCSUWizardEvaluateGeocode
from anncsu_manager.anncsu_wizard.wizard_generate_project_step import ANNCUWizardGenerateProjectStep
# from anncsu_manager.anncsu_wizard.wizard_materialise_layers import ANNCUWizardMaterialiseLayersStep
from anncsu_manager.anncsu_wizard.wizard_update_from_project import ANNCUWizardUpdateFromProjectStep
from anncsu_manager.anncsu_wizard.wizard_reduce_clusters_step import ANNCSUWizardReduceClustersStep

FORM_CLASS: QWizard = load_ui("wizard_manager.ui")


class ANNCSUWizardManager(QWizard, FORM_CLASS):

    def __init__(self, parent=None, progress_bar: QProgressBar=None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        # DECLARE TYPES

        # set progress bar and feedback manager for long operations
        self.progressBar: QProgressBar = progress_bar if progress_bar is not None else QProgressBar()
        self.progressBar.setVisible(False)

        # add run geocoder wizard page
        self.run_geocoders_page = ANNCSUWizardRunGeocoders(parent=self, progress_bar=self.progressBar)
        self.run_geocoders_page_id = self.addPage(self.run_geocoders_page)

        # add evaluate geocode wizard page
        self.evaluate_geocode_page = ANNCSUWizardEvaluateGeocode(parent=self, progress_bar=self.progressBar)
        self.evaluate_geocode_page_id = self.addPage(self.evaluate_geocode_page)

        # add materialize layers wizard page
        # self.materialize_layers_page = ANNCUWizardMaterialiseLayersStep(parent=self, progress_bar=self.progressBar)
        # self.materialize_layers_page_id = self.addPage(self.materialize_layers_page)

        # add Mergin wizard page
        self.generate_mergin_page = ANNCUWizardGenerateProjectStep(parent=self, progress_bar=self.progressBar)
        self.generate_mergin_page_id = self.addPage(self.generate_mergin_page)

        # add update from Mergin wizard page
        self.update_from_project_page = ANNCUWizardUpdateFromProjectStep(parent=self, progress_bar=self.progressBar)
        self.update_from_project_page_id = self.addPage(self.update_from_project_page)

        # add reduce clusters wizard page
        self.reduce_clusters_page = ANNCSUWizardReduceClustersStep(parent=self, progress_bar=self.progressBar)
        self.reduce_clusters_page_id = self.addPage(self.reduce_clusters_page)

        # activate first page to allow enable it's events
        self.setStartId(self.run_geocoders_page_id)
