from qgis.PyQt.QtWidgets import (
    QWizardPage,
    QProgressBar,
    QTextEdit,
    QLabel,
    QPushButton,
    QCheckBox,
)

from anncsu_manager.qgis_plugin_tools.tools.resources import load_ui
from anncsu_manager.utils.message_manager import ANNCSUMessageManager
from anncsu_manager.utils.settings_manager import ANNCSUSettingsManager
from anncsu_manager.utils.processing_feedback import ANNCSUProcessingFeedback

import duckdb

FORM_CLASS: QWizardPage = load_ui("wizard_reduce_clusters_page.ui")
class ANNCSUWizardReduceClustersStep(QWizardPage, FORM_CLASS):

    def __init__(self, parent=None, progress_bar: QProgressBar = QProgressBar()) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.statistics = {}

        # gui elements
        self.reduce_clusters_pb: QPushButton
        self.reduce_clusters_pb.clicked.connect(self.run_reduce_clusters_process)
        self.update_geocoded_anncsu_ckb: QCheckBox
        self.update_geocoded_anncsu_ckb.setChecked(True)
        self.progress_text: QTextEdit
        self.statistics_num_of_records: QLabel
        self.statistics_sum_of_previous_clusters: QLabel
        self.statistics_sum_of_previous_overlapped: QLabel
        self.statistics_num_of_clusters: QLabel
        self.statistics_num_of_overlapped: QLabel

        # setup GUI feedback during geocoding
        self.feedback: ANNCSUProcessingFeedback = ANNCSUProcessingFeedback(
            text_edit=None,
            progress_bar=progress_bar,
        )
        self.feedback.text_edit = self.progress_text
        self.feedback.progress_signal.connect(self.update_feedback_progress)
        self.feedback.text_signal.connect(self.update_feedback_text)


    def initializePage(self):
        """Called when the page is about to be shown."""
        self.update_statistics()


    def update_statistics(self):
        """Update statistics labels of available results before and after reduce clusters."""

        parent_wizard = self.wizard()
        geocode_page = parent_wizard.page(parent_wizard.evaluate_geocode_page_id)

        # get previous statistics from geocode_page tabs populating dict with geocoder name as key
        # and statistics as value to be used later in the reduce clusters process
        sum_of_previous_clusters = 0
        sum_of_previous_overlapped = 0
        sum_num_of_records = 0
        for i in range(geocode_page.geocoders_tabs.count()):
            tab: ANNCUGeocodeResultTab = geocode_page.geocoders_tabs.widget(i)
            geocoder_name = geocode_page.geocoders_tabs.tabText(i)
            num_of_records = tab.statistics_num_of_records.text()
            num_of_previous_clusters = tab.statistics_num_of_clusters.text()
            num_of_previous_overlapped = tab.statistics_num_of_overlapped_addresses.text()

            self.statistics[geocoder_name] = {
                "num_of_previous_clusters": num_of_previous_clusters,
                "num_of_previous_overlapped": num_of_previous_overlapped,
                "num_of_records": num_of_records,
            }

            sum_of_previous_clusters += int(num_of_previous_clusters)
            sum_of_previous_overlapped += int(num_of_previous_overlapped)
            sum_num_of_records += int(num_of_records)
            # # add before layer_geofence_polygon to remain under the other layers
            # self.feedback.pushInfo(f"info: Preparing to add geocoding results for '{geocoder_name}' to Mergin project '{project_name}'.")
            # self.feedback.pushInfo(f"info: Adding results into folder: {out_path}.")

        # update total statistics labels with sum of all geocoders
        self.statistics_num_of_records.setText(f"{str(sum_num_of_records)} ({int(sum_num_of_records/geocode_page.geocoders_tabs.count())} addresses)")
        self.statistics_sum_of_previous_clusters.setText(str(sum_of_previous_clusters))
        self.statistics_sum_of_previous_overlapped.setText(str(sum_of_previous_overlapped))

        # if deoverlapped_geocoded_anncsu table exists, get statistics of reduced clusters and update labels
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes.get(current_scope_id, {})
        duck_db_source = current_scope.to_dict().get("duckdb_path", "")
        if duck_db_source:
            with duckdb.connect(duck_db_source) as conn:
                try:
                    result = conn.execute("SELECT COUNT(*) AS remaining_clusters FROM remaining_clusters;").fetchone()
                    num_of_clusters = result[0]
                    result = conn.execute("SELECT COUNT(*) AS remaining_overlapped FROM remaining_duplicates;").fetchone()
                    num_of_overlapped = result[0]

                    # calc effectiveness of reduce clusters process as percentage of reduced clusters over previous clusters
                    if sum_of_previous_clusters > 0:
                        effectiveness = ((sum_of_previous_clusters - num_of_clusters) / sum_of_previous_clusters) * 100
                        self.feedback.pushInfo(self.tr("info: Reduce clusters process effectiveness: {effectiveness:.2f}% of clusters reduced.").format(effectiveness=effectiveness))
                    if sum_of_previous_overlapped > 0:
                        effectiveness_overlapped = ((sum_of_previous_overlapped - num_of_overlapped) / sum_of_previous_overlapped) * 100
                        self.feedback.pushInfo(self.tr("info: Reduce clusters process effectiveness: {effectiveness:.2f}% of overlapped addresses reduced.").format(effectiveness=effectiveness_overlapped))

                    self.statistics_num_of_clusters.setText(f"{num_of_clusters} - better {effectiveness:.2f}%")
                    self.statistics_num_of_overlapped.setText(f"{num_of_overlapped} - better {effectiveness_overlapped:.2f}%")
                except Exception as e:
                    self.feedback.pushWarning(self.tr("Table 'remaining_clusters' or 'remaining_duplicates' does not exist. Run Deduplicate step first."))
                    self.statistics_num_of_clusters.setText(self.tr("N/A - run Deduplicate step"))
                    self.statistics_num_of_overlapped.setText(self.tr("N/A - run Deduplicate step"))
        else:
            self.feedback.pushWarning(self.tr("No DuckDB database path found in the current scope settings. Cannot update reduced clusters statistics."))
            self.statistics_num_of_clusters.setText(self.tr("N/A"))
            self.statistics_num_of_overlapped.setText(self.tr("N/A"))


    def run_reduce_clusters_process(self):
        """Run sql to resolve most of duplicated addresses mixing geocoders results starting from the geocoder
        with the lowest overlapped addresses."""

        # check if db is available
        current_scope_id = ANNCSUSettingsManager.get_current_scope_id()
        scopes = ANNCSUSettingsManager.get_scopes()
        current_scope = scopes.get(current_scope_id, {})
        duck_db_source = current_scope.to_dict().get("duckdb_path", "")
        if not duck_db_source:
            self.feedback.pushError(self.tr("No DuckDB database path found in the current scope settings. Cannot run reduce clusters process."))
            return

        # order geocoders basing on the number of overlapped addresses to have the geocoder
        # with the lowest overlapped addresses on top
        sorted_geocoders = sorted(self.statistics.items(), key=lambda x: int(x[1]["num_of_previous_overlapped"]), reverse=False)
        self.feedback.pushInfo(self.tr("info: geocoders ordered by number of overlapped addresses from min to max"))
        self.feedback.pushInfo(self.tr("info: geocoders order: {geocoders_order}").format(geocoders_order=', '.join([g[0] for g in sorted_geocoders])))

        with duckdb.connect(duck_db_source) as conn:
            # begin transaction
            conn.execute("BEGIN;")

            try:
                # fist copy geocoded_anncsu as base to solve overlapped
                setup_unoverlapped_query = f"""
                    CREATE OR REPLACE TABLE deoverlapped_geocoded_anncsu AS
                    SELECT * FROM geocoded_anncsu;
                """
                conn.execute(setup_unoverlapped_query)

                # loop on every ordered geocoder fixing the duplicated addresses if any can be fixed with
                # that in the list of geocoded in the next geocoder in the list with more overlapped addresses,
                # then move to the next geocoder in the list and so on until the end of the list is reached
                lowest_geocoder_index = 0
                while lowest_geocoder_index < len(sorted_geocoders)-1:
                    current_geocoder_name = sorted_geocoders[lowest_geocoder_index][0]
                    next_geocoder_name = sorted_geocoders[lowest_geocoder_index+1][0]

                    # find cluster of coordinates with more than 1 record in the current geocoder success table
                    geocoder_clusters_query = f"""
                        CREATE OR REPLACE TABLE {current_geocoder_name}_clusters AS (
                            SELECT
                                COORD_X_COMUNE,
                                COORD_Y_COMUNE,
                                COUNT(*) AS record_count
                            FROM {current_geocoder_name}_success
                            GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
                            HAVING record_count > 1
                            ORDER BY record_count DESC
                        );"""
                    conn.execute(geocoder_clusters_query)

                    # find all addresses belogns to the clusters
                    geocoder_overlapped_query = f"""
                        CREATE OR REPLACE TABLE {current_geocoder_name}_overlapped AS (
                            SELECT
                                A.PROGRESSIVO_ACCESSO,
                                A.COORD_X_COMUNE,
                                A.COORD_Y_COMUNE
                            FROM
                                main.{current_geocoder_name}_success A,
                                {current_geocoder_name}_clusters B
                            WHERE
                                A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
                                A.COORD_Y_COMUNE = B.COORD_Y_COMUNE
                        );"""
                    conn.execute(geocoder_overlapped_query)

                    # solve overlapped addresses in current geocoder with that in the next geocoder success table
                    solved_by_next_geocoder_query = f"""
                        CREATE OR REPLACE TABLE solved_by_{next_geocoder_name} AS (
                            WITH
                                same_ids_from_{next_geocoder_name} AS (
                                    SELECT *
                                    FROM
                                        {next_geocoder_name}_success A,
                                        {current_geocoder_name}_overlapped B
                                    WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
                                )
                            SELECT
                                PROGRESSIVO_ACCESSO,
                                COORD_X_COMUNE,
                                COORD_Y_COMUNE,
                                COUNT(*) AS record_count
                            FROM same_ids_from_{next_geocoder_name}
                            GROUP BY
                                PROGRESSIVO_ACCESSO,
                                COORD_X_COMUNE,
                                COORD_Y_COMUNE
                            HAVING record_count = 1
                        );"""
                    conn.execute(solved_by_next_geocoder_query)

                    # update deoverlapped_geocoded_anncsu table with the solved addresses by the next geocoder
                    update_deoverlapped_query = f"""
                        UPDATE deoverlapped_geocoded_anncsu
                        SET
                            COORD_X_COMUNE = S.COORD_X_COMUNE,
                            COORD_Y_COMUNE = S.COORD_Y_COMUNE
                        FROM
                            solved_by_{next_geocoder_name} S
                        WHERE
                            deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;
                    """
                    conn.execute(update_deoverlapped_query)

                    # continue to the next pair of geocoders
                    lowest_geocoder_index += 1

                # after the loop is finished, create remaining_clusters table with the reduced clusters and
                # remaining_duplicates table with the still duplicated addresses
                remaining_clusters_query = f"""
                    CREATE OR REPLACE TABLE remaining_clusters AS (
                        SELECT
                            COORD_X_COMUNE,
                            COORD_Y_COMUNE,
                            COUNT(*) AS record_count
                        FROM deoverlapped_geocoded_anncsu
                        GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
                        HAVING record_count > 1
                        ORDER BY record_count DESC
                    );
                """
                conn.execute(remaining_clusters_query)

                remaining_duplicates_query = f"""
                    CREATE OR REPLACE TABLE remaining_duplicates AS (
                        SELECT
                            A.PROGRESSIVO_ACCESSO,
                            A.COORD_X_COMUNE,
                            A.COORD_Y_COMUNE
                        FROM
                            deoverlapped_geocoded_anncsu A,
                            remaining_clusters B
                        WHERE
                            A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
                            A.COORD_Y_COMUNE = B.COORD_Y_COMUNE
                    );
                """
                conn.execute(remaining_duplicates_query)

                # if user specified to update geocoded_anncsu with the reduced clusters,
                # update geocoded_anncsu table with deoverlapped_geocoded_anncsu
                if self.update_geocoded_anncsu_ckb.isChecked():
                    # save a backup of geocoded_anncsu before updating it with the reduced
                    # clusters in case user want to restore it later
                    backup_geocoded_anncsu_query = f"""
                        CREATE OR REPLACE TABLE geocoded_anncsu_not_deoverlapped AS
                        SELECT * FROM geocoded_anncsu;
                    """
                    conn.execute(backup_geocoded_anncsu_query)

                    # update geocoded_anncsu with deoverlapped_geocoded_anncsu
                    update_geocoded_anncsu_query = f"""
                        UPDATE geocoded_anncsu
                        SET
                            COORD_X_COMUNE = D.COORD_X_COMUNE,
                            COORD_Y_COMUNE = D.COORD_Y_COMUNE
                        FROM
                            deoverlapped_geocoded_anncsu D
                        WHERE
                            geocoded_anncsu.PROGRESSIVO_ACCESSO = D.PROGRESSIVO_ACCESSO;
                    """
                    conn.execute(update_geocoded_anncsu_query)

            except Exception as e:
                conn.execute("ROLLBACK;")
                self.feedback.reportError(self.tr("Error while running reduce clusters process: {error}").format(error=str(e)))
                return
            else:
                conn.execute("COMMIT;")
                self.feedback.pushInfo(self.tr("success: Reduce clusters process completed successfully."))
                self.update_statistics()


    def update_feedback_progress(self, progress: int):
        self.feedback.progress_bar.setValue(progress)

    def update_feedback_text(self, text: str):
        if "success: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="success", duration=5)
        elif "info:" in text.lower():
            pass
        elif "warning:" in text.lower():
            ANNCSUMessageManager().show_message(text, level="warning", duration=5)
        elif "invalid: " in text.lower():
            ANNCSUMessageManager().show_message(text, level="invalid", duration=10)
        elif "error:" in text.lower():
            ANNCSUMessageManager().show_message(text, level="error", duration=0)

        if self.feedback.text_edit is not None:
            if isinstance(self.feedback.text_edit, QTextEdit):
                self.feedback.text_edit.append(text)
            elif isinstance(self.feedback.text_edit, QLabel):
                self.feedback.text_edit.setText(text)

