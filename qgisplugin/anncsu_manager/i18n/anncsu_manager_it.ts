<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="it_IT">
  <!-- ============================================================ -->
  <!-- utils/settings_manager.py                                    -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUSettingsManager</name>

    <message>
      <location filename="../utils/settings_manager.py" line="127"/>
      <source>Scope at {duckdb_path} is already syncked with remote repo {remote_git_repo}.</source>
      <translation>Scope in {duckdb_path} è già sincronizzato con il repository remoto {remote_git_repo}.</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="743"/>
      <source>Table &apos;{table_name}&apos; not found in duckdb at {duckdb_path}.</source>
      <translation>Tabella &apos;{table_name}&apos; non trovata nel duckdb in {duckdb_path}.</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="754"/>
      <source>Error: {e}</source>
      <translation>Errore: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="760"/>
      <source>Error reading {table_name} table from duckdb at {duckdb_path}: {e}</source>
      <translation>Errore durante la lettura della tabella {table_name} dal duckdb in {duckdb_path}: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="872"/>
      <source>Error merging geocoded dataframe with anncsu dataframe: {e}</source>
      <translation>Errore durante l&apos;unione del dataframe geocodificato con il dataframe anncsu: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="938"/>
      <source>Continue update?</source>
      <translation>Continuare l&apos;aggiornamento?</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="939"/>
      <source>The current session is not synchronized with the remote git repository.
If you update the session data, you may lose unsynchronized changes.</source>
      <translation>La sessione attuale non è sincronizzata con il repository git remoto.
Se aggiorni i dati della sessione, potresti perdere le modifiche non sincronizzate.</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="955"/>
      <source>Table &apos;geocoded_anncsu&apos; not found in duckdb at {duckdb_path}. Cannot update session.</source>
      <translation>Tabella &apos;geocoded_anncsu&apos; non trovata nel duckdb in {duckdb_path}. Impossibile aggiornare la sessione.</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="958"/>
      <source>Update not possible</source>
      <translation>Aggiornamento non possibile</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="959"/>
      <source>The &apos;geocoded_anncsu&apos; table was not found in the session database.
Make sure you have performed the update from Mergin.</source>
      <translation>La tabella &apos;geocoded_anncsu&apos; non è stata trovata nel database della sessione.
Assicurati di aver eseguito l&apos;aggiornamento da Mergin.</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1082"/>
      <source>Some addresses have updated coordinates compared to the local table.
Do you want to proceed with updating the session data?
Details show addresses with updated coordinates.
(Difference threshold: {threshold} degrees, approx. {meters:.2f} meters)</source>
      <translation>Alcuni accessi hanno coordinate aggiornate rispetto alla tabella locale.
Vuoi procedere con l&apos;aggiornamento dei dati della sessione?
I dettagli mostrano gli accessi con coordinate aggiornate.
(Soglia di differenza: {threshold} gradi, circa {meters:.2f} metri)</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1085"/>
      <source>Update address coordinates?</source>
      <translation>Aggiornare le coordinate degli accessi?</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1139"/>
      <source>Error updating session with new anncsu data: {e}</source>
      <translation>Errore durante l&apos;aggiornamento della sessione con i nuovi dati anncsu: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1182"/>
      <source>Error in populate_table_from_source_task: {e}</source>
      <translation>Errore in populate_table_from_source_task: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1189"/>
      <source>Table {table_name} successfully populated from {source_db}</source>
      <translation>Tabella {table_name} popolata con successo da {source_db}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1191"/>
      <source>Error populating table {table_name} from {source_db}</source>
      <translation>Errore durante il popolamento della tabella {table_name} da {source_db}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1228"/>
      <source>Connect remote DB: {source_db}</source>
      <translation>Connessione al DB remoto: {source_db}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1294"/>
      <source>Connect local DB: {source_db}</source>
      <translation>Connessione al DB locale: {source_db}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1317"/>
      <source>Error populating {table_name} table from source database: {e}</source>
      <translation>Errore durante il popolamento della tabella {table_name} dal database sorgente: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1320"/>
      <source>Populated {table_name} table from source database: {source_db}</source>
      <translation>Tabella {table_name} popolata dal database sorgente: {source_db}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1339"/>
      <source>Creating new session for municipality {anncsu_id} from source db {source_db}...</source>
      <translation>Creazione nuova sessione per il comune {anncsu_id} dal database sorgente {source_db}...</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1352"/>
      <source>Invalid remote HTTP(S) git repo URL: {remote_git_repo} check if SSH. error: {e}</source>
      <translation>URL repository git remoto HTTP(S) non valido: {remote_git_repo}. Verificare se si tratta di SSH. Errore: {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1359"/>
      <source>Invalid remote git repo URL: {remote_git_repo}</source>
      <translation>URL repository git remoto non valido: {remote_git_repo}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1388"/>
      <source>Successfully cloned/pulled {remote_git_repo} into {local_path}</source>
      <translation>Repository {remote_git_repo} clonato/aggiornato con successo in {local_path}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="418"/>
      <source>Failed to load default geocoder configs. Reset to default values. {e}</source>
      <translation>Impossibile caricare la configurazione predefinita dei geocoder. Ripristino ai valori predefiniti. {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="596"/>
      <source>Could not find geocoders.json at {path}. Reverting to default path.</source>
      <translation>File geocoders.json non trovato in {path}. Ripristino al percorso predefinito.</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1259"/>
      <source>Failed to download source database: {error_msg}</source>
      <translation>Download del database sorgente non riuscito: {error_msg}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1409"/>
      <source>Error creating new session: {exception}</source>
      <translation>Errore durante la creazione della nuova sessione: {exception}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- utils/misc_utils.py — DownloadFileTask                       -->
  <!-- ============================================================ -->
  <context>
    <name>DownloadFileTask</name>

    <message>
      <location filename="../utils/misc_utils.py" line="192"/>
      <source>Successfully downloaded url: {url} to {destination_path}</source>
      <translation>URL {url} scaricato con successo in {destination_path}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="197"/>
      <source>Failed to download url: {url}. Error: {error_msg}</source>
      <translation>Download dell&apos;URL {url} non riuscito. Errore: {error_msg}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="274"/>
      <source>Downloading from {url} to {destination_path}...</source>
      <translation>Download in corso da {url} verso {destination_path}...</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="287"/>
      <source>Download completed: {destination_path}</source>
      <translation>Download completato: {destination_path}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- utils/misc_utils.py — clone_or_pull_git_repo_task            -->
  <!-- ============================================================ -->
  <context>
    <name>clone_or_pull_git_repo_task</name>

    <message>
      <location filename="../utils/misc_utils.py" line="353"/>
      <source>Cloning repo {remote_git_repo}</source>
      <translation>Clonazione repository {remote_git_repo}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="382"/>
      <source>Error in clone_or_pull_git_repo_task: {e}</source>
      <translation>Errore in clone_or_pull_git_repo_task: {e}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="389"/>
      <source>Repo {remote_git_repo} cloned successfully in {local_path}</source>
      <translation>Repository {remote_git_repo} clonato con successo in {local_path}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="391"/>
      <source>Error cloning repo {remote_git_repo} in {local_path}</source>
      <translation>Errore durante la clonazione del repository {remote_git_repo} in {local_path}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="442"/>
      <source>Pulling latest changes from git repository at {url}...</source>
      <translation>Aggiornamento del repository git da {url}...</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="457"/>
      <source>Repository already exists at {local_path}, pulled latest changes.</source>
      <translation>Il repository esiste già in {local_path}; aggiornamento completato.</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="477"/>
      <source>Cloning latest changes from git repository at {url}...</source>
      <translation>Clonazione del repository git da {url}...</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="481"/>
      <source>Error cloning git repository {remote_git_repo}: {e}</source>
      <translation>Errore durante la clonazione del repository git {remote_git_repo}: {e}</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="495"/>
      <source>Successfully cloned repo {remote_git_repo} to {local_path}.</source>
      <translation>Repository {remote_git_repo} clonato con successo in {local_path}.</translation>
    </message>
    <message>
      <location filename="../utils/misc_utils.py" line="500"/>
      <source>Error cloning/pulling git repository {remote_git_repo}: {e}</source>
      <translation>Errore durante la clonazione/aggiornamento del repository git {remote_git_repo}: {e}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_settings.py                             -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardSettings</name>

    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="157"/>
      <source>No session selected to synchronize.</source>
      <translation>Nessuna sessione selezionata da sincronizzare.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="177"/>
      <source>Session &apos;{session}&apos; synchronized with the remote repository.</source>
      <translation>Sessione &apos;{session}&apos; sincronizzata con il repository remoto.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="182"/>
      <source>Error synchronizing session &apos;{session}&apos;: {error}</source>
      <translation>Errore durante la sincronizzazione della sessione &apos;{session}&apos;: {error}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="195"/>
      <source>No session selected to update.</source>
      <translation>Nessuna sessione selezionata da aggiornare.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="223"/>
      <source>Error creating new session: {exception}</source>
      <translation>Errore durante la creazione della nuova sessione: {exception}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="227"/>
      <source>Successfully updated ANNCSU table for session {session}</source>
      <translation>Tabella ANNCSU aggiornata con successo per la sessione {session}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="233"/>
      <source>ANNCSU update cancelled.</source>
      <translation>Aggiornamento ANNCSU annullato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="239"/>
      <source>ANNCSU successfully updated for the selected session.</source>
      <translation>ANNCSU aggiornato con successo per la sessione selezionata.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="248"/>
      <source>No session selected to delete.</source>
      <translation>Nessuna sessione selezionata da eliminare.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="254"/>
      <source>Delete ANNCSU session</source>
      <translation>Eliminazione sessione ANNCSU</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="255"/>
      <source>Are you sure you want to delete session &apos;{session}&apos;?</source>
      <translation>Sei sicuro di voler eliminare la sessione &apos;{session}&apos;?</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="276"/>
      <source>Session &apos;{session}&apos; deleted.</source>
      <translation>Sessione &apos;{session}&apos; eliminata.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="316"/>
      <source>No municipality code associated with the selected session.
Select one and save to create a working session.</source>
      <translation>Nessun codice comune associato alla sessione selezionata.
Selezionarne uno e salvare per creare una sessione di lavoro.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="378"/>
      <source>Select municipality code</source>
      <translation>Seleziona codice comune</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="393"/>
      <source>Select session</source>
      <translation>Seleziona sessione</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="432"/>
      <source>Could not register geocoder &apos;{geocoder_name}&apos;: {e}</source>
      <translation>Impossibile registrare il geocoder &apos;{geocoder_name}&apos;: {e}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="456"/>
      <source>Select a municipality code to proceed.</source>
      <translation>Selezionare un codice comune per procedere.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="472"/>
      <source>New session creation task already in progress.</source>
      <translation>Task di creazione nuova sessione già in esecuzione.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="478"/>
      <source>Forcing creation of a new ANNCSU session. Do you want to proceed?</source>
      <translation>Forzando la creazione di una nuova sessione ANNCSU. Vuoi procedere?</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="481"/>
      <source>The municipality code or ANNCSU source database have been modified compared to the current session.
A new ANNCSU session will be generated. Do you want to proceed?</source>
      <translation>Il codice comune o il database sorgente ANNCSU sono stati modificati rispetto alla sessione attuale.
Verrà generata una nuova sessione ANNCSU. Vuoi procedere?</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="484"/>
      <source>Source ANNCSU DB or municipality code modified</source>
      <translation>DB sorgente ANNCSU o codice comune modificati</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="499"/>
      <source>No changes saved</source>
      <translation>Nessuna modifica salvata</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="534"/>
      <source>Error creating new session</source>
      <translation>Errore durante la creazione della nuova sessione</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="567"/>
      <source>ANNCSU QGIS Plugin settings saved.</source>
      <translation>Impostazioni del plugin ANNCSU QGIS salvate.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_settings.py" line="574"/>
      <source>ANNCSU QGIS Plugin settings reset.</source>
      <translation>Impostazioni del plugin ANNCSU QGIS ripristinate.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_update_from_mergin.py                   -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardUpdateFromMergin</name>

    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="74"/>
      <source>-- Select Mergin Project --</source>
      <translation>-- Seleziona Progetto Mergin --</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="87"/>
      <source>No local Mergin project found. Configure Mergin before proceeding.</source>
      <translation>Nessun progetto Mergin locale trovato. Configurare Mergin prima di procedere.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="112"/>
      <source>Select a valid Mergin project before proceeding.</source>
      <translation>Selezionare un progetto Mergin valido prima di procedere.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="128"/>
      <source>Continue saving?</source>
      <translation>Continuare il salvataggio?</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="129"/>
      <source>The selected Mergin project &apos;{project_name}&apos; does not match the open QGIS project &apos;{cur_project}&apos;. Proceed anyway?</source>
      <translation>Il progetto Mergin selezionato &apos;{project_name}&apos; non corrisponde al progetto QGIS aperto &apos;{cur_project}&apos;. Procedere comunque?</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_generate_mergin_step.py                 -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardGenerateMerginStep</name>

    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="79"/>
      <source>-- Select Mergin Project --</source>
      <translation>-- Seleziona Progetto Mergin --</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="92"/>
      <source>No local Mergin project found. Configure Mergin before proceeding.</source>
      <translation>Nessun progetto Mergin locale trovato. Configurare Mergin prima di procedere.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="122"/>
      <source>Select a valid Mergin project before proceeding.</source>
      <translation>Selezionare un progetto Mergin valido prima di procedere.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="137"/>
      <source>Continue saving?</source>
      <translation>Continuare il salvataggio?</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="138"/>
      <source>The selected Mergin project &apos;{project_name}&apos; does not match the open QGIS project &apos;{cur_project}&apos;. Proceed anyway?</source>
      <translation>Il progetto Mergin selezionato &apos;{project_name}&apos; non corrisponde al progetto QGIS aperto &apos;{cur_project}&apos;. Procedere comunque?</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="149"/>
      <source>Unable to load the ANNCSU table. Make sure the table is available before proceeding.</source>
      <translation>Impossibile caricare la tabella ANNCSU. Assicurarsi che la tabella sia disponibile prima di procedere.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="175"/>
      <source>Loading: {layer_name}</source>
      <translation>Caricamento: {layer_name}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="257"/>
      <source>Added results for geocoder &apos;{geocoder_name}&apos; into Mergin project &apos;{project_name}&apos;.</source>
      <translation>Risultati per il geocoder &apos;{geocoder_name}&apos; aggiunti al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="331"/>
      <source>Saving geocoded ANNCSU table into Mergin project &apos;{project_name}&apos;.</source>
      <translation>Salvataggio della tabella ANNCSU geocodificata nel progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_materialise_layers.py                   -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardMaterialiseLayers</name>

    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="96"/>
      <source>Loading: {layer_name}</source>
      <translation>Caricamento: {layer_name}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="170"/>
      <source>Added results for geocoder &apos;{geocoder_name}&apos; into git repo.</source>
      <translation>Risultati per il geocoder &apos;{geocoder_name}&apos; aggiunti al repository git.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_evaluate_geocode_step.py                -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardEvaluateGeocodeStep</name>

    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="222"/>
      <source>Loading layer: {layer_name}</source>
      <translation>Caricamento layer: {layer_name}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- utils/message_manager.py                                    -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUMessageManager</name>

    <message>
      <location filename="../utils/message_manager.py" line="35"/>
      <source>Success</source>
      <translation>Successo</translation>
    </message>
    <message>
      <location filename="../utils/message_manager.py" line="37"/>
      <source>Info</source>
      <translation>Info</translation>
    </message>
    <message>
      <location filename="../utils/message_manager.py" line="39"/>
      <source>Warning</source>
      <translation>Avviso</translation>
    </message>
    <message>
      <location filename="../utils/message_manager.py" line="43"/>
      <source>Error</source>
      <translation>Errore</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- utils/processing_feedback.py                                 -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUProcessingFeedback</name>

    <message>
      <location filename="../utils/processing_feedback.py" line="37"/>
      <source>Command: {info}</source>
      <translation>Comando: {info}</translation>
    </message>
    <message>
      <location filename="../utils/processing_feedback.py" line="40"/>
      <source>Debug: {info}</source>
      <translation>Debug: {info}</translation>
    </message>
    <message>
      <location filename="../utils/processing_feedback.py" line="43"/>
      <source>Console: {info}</source>
      <translation>Console: {info}</translation>
    </message>
    <message>
      <location filename="../utils/processing_feedback.py" line="53"/>
      <source>Processing failed.</source>
      <translation>Elaborazione non riuscita.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_main.py                                 -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardDialog</name>

    <message>
      <location filename="../anncsu_wizard/wizard_main.py" line="42"/>
      <source>ANNCSU Wizard</source>
      <translation>ANNCSU Wizard</translation>
    </message>
  </context>

  <context>
    <name>ANNCSUWizard</name>

    <message>
      <location filename="../anncsu_wizard/wizard_main.py" line="67"/>
      <source>ANNCSU Manager</source>
      <translation>ANNCSU Manager</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_main.py" line="70"/>
      <source>Settings</source>
      <translation>Impostazioni</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_main.py" line="73"/>
      <source>About</source>
      <translation>Info</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_geocoder_step.py                        -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardRunGeocoders</name>

    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="66"/>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="68"/>
      <source>No scope is currently selected. Please select a scope in the settings before running geocoders.</source>
      <translation>Nessuno scope selezionato. Selezionare uno scope nelle impostazioni prima di eseguire i geocoder.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="73"/>
      <source>No DuckDB database path found in the current scope settings.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope corrente.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="78"/>
      <source>Could not connect to DuckDB database at {duck_db_source}.</source>
      <translation>Impossibile connettersi al database DuckDB in {duck_db_source}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="93"/>
      <source>Skipping inactive geocoder {geocoder_name}...</source>
      <translation>Geocoder inattivo ignorato: {geocoder_name}...</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="102"/>
      <source>Could not instantiate geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>Impossibile istanziare il geocoder &apos;{geocoder_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="126"/>
      <source>Geocoding {count} addresses using {geocoder_name}...</source>
      <translation>Geocodifica di {count} indirizzi con {geocoder_name}...</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="129"/>
      <source>Geocoding {count} bulk addresses to speedup process.</source>
      <translation>Geocodifica massiva di {count} indirizzi per accelerare il processo.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="133"/>
      <source>Geocoded {count} addresses in {elapsed} seconds using {geocoder_name}.</source>
      <translation>Geocodificati {count} indirizzi in {elapsed} secondi con {geocoder_name}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="158"/>
      <source>Saving geocoding results into table {result_table_name}...</source>
      <translation>Salvataggio risultati geocodifica nella tabella {result_table_name}...</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="200"/>
      <source>Geocoder &apos;{geocoder_name}&apos;: Geocodings saved into table {result_table_name}.</source>
      <translation>Geocoder &apos;{geocoder_name}&apos;: geocodifiche salvate nella tabella {result_table_name}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="203"/>
      <source>All geocoding processes completed.</source>
      <translation>Tutti i processi di geocodifica completati.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="208"/>
      <source>warning:  Scope repo locally updated need to be synched to remote repo.</source>
      <translation>warning:  Repository scope aggiornato localmente, sincronizzazione con il repository remoto necessaria.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_geocoder_step.py" line="218"/>
      <source>An error occurred: {error}</source>
      <translation>Si è verificato un errore: {error}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_reduce_clusters_step.py                 -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardReduceClustersStep</name>

    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="105"/>
      <source>Table &apos;remaining_clusters&apos; or &apos;remaining_duplicates&apos; does not exist. Run Deduplicate step first.</source>
      <translation>La tabella &apos;remaining_clusters&apos; o &apos;remaining_duplicates&apos; non esiste. Eseguire prima il passo di deduplicazione.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="106"/>
      <source>N/A - run Deduplicate step</source>
      <translation>N/D - eseguire il passo di deduplicazione</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="109"/>
      <source>No DuckDB database path found in the current scope settings. Cannot update reduced clusters statistics.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope. Impossibile aggiornare le statistiche.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="110"/>
      <source>N/A</source>
      <translation>N/D</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="124"/>
      <source>No DuckDB database path found in the current scope settings. Cannot run reduce clusters process.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope. Impossibile eseguire il processo di riduzione cluster.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="258"/>
      <source>Error while running reduce clusters process: {error}</source>
      <translation>Errore durante il processo di riduzione cluster: {error}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="262"/>
      <source>success: Reduce clusters process completed successfully.</source>
      <translation>success: Processo di riduzione cluster completato con successo.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="105"/>
      <source>info: Reduce clusters process effectiveness: {effectiveness:.2f}% of clusters reduced.</source>
      <translation>info: Efficacia del processo di riduzione cluster: {effectiveness:.2f}% di cluster ridotti.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="108"/>
      <source>info: Reduce clusters process effectiveness: {effectiveness:.2f}% of overlapped addresses reduced.</source>
      <translation>info: Efficacia del processo di riduzione cluster: {effectiveness:.2f}% di indirizzi sovrapposti ridotti.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="138"/>
      <source>info: geocoders ordered by number of overlapped addresses from min to max</source>
      <translation>info: geocoder ordinati per numero di indirizzi sovrapposti dal minore al maggiore</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_reduce_clusters_step.py" line="139"/>
      <source>info: geocoders order: {geocoders_order}</source>
      <translation>info: ordine geocoder: {geocoders_order}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_evaluate_geocode_step.py (new strings)  -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCUGeocodeResultTab</name>

    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="135"/>
      <source>{success_rate:.2f}% (Threshold: {threshold})</source>
      <translation>{success_rate:.2f}% (Soglia: {threshold})</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="178"/>
      <source>Error loading results: {error}</source>
      <translation>Errore durante il caricamento dei risultati: {error}</translation>
    </message>
  </context>

  <context>
    <name>ANNCSUWizardEvaluateGeocode</name>

    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="296"/>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="299"/>
      <source>No scope is currently selected. Please select a scope in the settings before running geocoders.</source>
      <translation>Nessuno scope selezionato. Selezionare uno scope nelle impostazioni prima di eseguire i geocoder.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="304"/>
      <source>No DuckDB database path found in the current scope settings.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope corrente.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="309"/>
      <source>Could not connect to DuckDB database at {duck_db_source}.</source>
      <translation>Impossibile connettersi al database DuckDB in {duck_db_source}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_evaluate_geocode_step.py" line="325"/>
      <source>Results table &apos;{result_table_name}&apos; does not exist. Skipping evaluation for geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>La tabella dei risultati &apos;{result_table_name}&apos; non esiste. Valutazione del geocoder &apos;{geocoder_name}&apos; ignorata.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_materialise_layers.py (new strings)     -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardMaterialiseLayers</name>

    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="65"/>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="67"/>
      <source>No scope is currently selected. Please select a scope in the settings before running geocoders.</source>
      <translation>Nessuno scope selezionato. Selezionare uno scope nelle impostazioni prima di eseguire i geocoder.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="73"/>
      <source>Scope local repo path &apos;{out_path}&apos; does not exist. Please check your scope settings.</source>
      <translation>Il percorso del repository locale dello scope &apos;{out_path}&apos; non esiste. Verificare le impostazioni dello scope.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="92"/>
      <source>info: Preparing to add geocoding results for &apos;{geocoder_name}&apos; to local scope folder.</source>
      <translation>info: Preparazione aggiunta risultati geocodifica per &apos;{geocoder_name}&apos; nella cartella locale dello scope.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="93"/>
      <source>info: Adding results into folder: {out_path}.</source>
      <translation>info: Aggiunta risultati nella cartella: {out_path}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="106"/>
      <source>info: Geofence polygon layer &apos;{layer_geofence_polygon}&apos; added to local git repo.</source>
      <translation>info: Layer poligono geofence &apos;{layer_geofence_polygon}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="123"/>
      <source>info: Fails layer &apos;{layer_name_fails}&apos; added to local git repo.</source>
      <translation>info: Layer dei fallimenti &apos;{layer_name_fails}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="140"/>
      <source>info: Out of geofence layer &apos;{layer_name_out_of_geofence}&apos; added to local git repo.</source>
      <translation>info: Layer fuori geofence &apos;{layer_name_out_of_geofence}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="157"/>
      <source>info: Success layer &apos;{layer_name_success}&apos; added to local git repo.</source>
      <translation>info: Layer dei successi &apos;{layer_name_success}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_materialise_layers.py" line="165"/>
      <source>info: Commit and push layers into git repo.</source>
      <translation>info: Commit e push dei layer nel repository git.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_generate_mergin_step.py (new strings)   -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardGenerateMerginStep</name>

    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="83"/>
      <source>info: Found Mergin project: {project_name} workspace: {workspace} at path: {path} on server: {project_server}.</source>
      <translation>info: Trovato progetto Mergin: {project_name} workspace: {workspace} al percorso: {path} sul server: {project_server}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="106"/>
      <source>info: Current QGIS project &apos;{cur_project}&apos; matches Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Il progetto QGIS corrente &apos;{cur_project}&apos; corrisponde al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="171"/>
      <source>info: Preparing to add geocoding results for &apos;{geocoder_name}&apos; to Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Preparazione aggiunta risultati geocodifica per &apos;{geocoder_name}&apos; al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="172"/>
      <source>info: Adding results into folder: {out_path}.</source>
      <translation>info: Aggiunta risultati nella cartella: {out_path}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="185"/>
      <source>info: Geofence polygon layer &apos;{layer_geofence_polygon}&apos; added to Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Layer poligono geofence &apos;{layer_geofence_polygon}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="197"/>
      <source>error: Unable to merge geocoded results with anncsu table for geocoder &apos;{geocoder_name}&apos;. Skipping saving success layer.</source>
      <translation>error: Impossibile unire i risultati geocodificati con la tabella anncsu per il geocoder &apos;{geocoder_name}&apos;. Salvataggio layer successi ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="209"/>
      <source>info: Success layer &apos;{layer_name_success}&apos; added to Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Layer dei successi &apos;{layer_name_success}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="221"/>
      <source>error: Unable to merge fails results with anncsu table for geocoder &apos;{geocoder_name}&apos;. Skipping saving fails layer.</source>
      <translation>error: Impossibile unire i risultati dei fallimenti con la tabella anncsu per il geocoder &apos;{geocoder_name}&apos;. Salvataggio layer fallimenti ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="232"/>
      <source>info: Fails layer &apos;{layer_name_fails}&apos; added to Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Layer dei fallimenti &apos;{layer_name_fails}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="244"/>
      <source>error: Unable to merge out of geofence results with anncsu table for geocoder &apos;{geocoder_name}&apos;. Skipping saving out of geofence layer.</source>
      <translation>error: Impossibile unire i risultati fuori geofence con la tabella anncsu per il geocoder &apos;{geocoder_name}&apos;. Salvataggio layer fuori geofence ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_generate_mergin_step.py" line="255"/>
      <source>info: Out of geofence layer &apos;{layer_name_out_of_geofence}&apos; added to Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Layer fuori geofence &apos;{layer_name_out_of_geofence}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_update_from_mergin.py (new strings)     -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardUpdateFromMergin</name>

    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="78"/>
      <source>info: Found Mergin project: {project_name} workspace: {workspace} at path: {path} on server: {project_server}.</source>
      <translation>info: Trovato progetto Mergin: {project_name} workspace: {workspace} al percorso: {path} sul server: {project_server}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="101"/>
      <source>info: Current QGIS project &apos;{cur_project}&apos; matches Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Il progetto QGIS corrente &apos;{cur_project}&apos; corrisponde al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="143"/>
      <source>Current scope id &apos;{current_scope_id}&apos; not found among defined scopes.</source>
      <translation>L&apos;id scope corrente &apos;{current_scope_id}&apos; non trovato tra gli scope definiti.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="146"/>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="151"/>
      <source>No DuckDB database path found in the current scope settings.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope corrente.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="155"/>
      <source>Updating DuckDB database at {duck_db_source} from Mergin project &apos;{project_name}&apos;.</source>
      <translation>Aggiornamento database DuckDB in {duck_db_source} dal progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="157"/>
      <source>Could not connect to DuckDB database at {duck_db_source}.</source>
      <translation>Impossibile connettersi al database DuckDB in {duck_db_source}.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="171"/>
      <source>info: Skipping inactive geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>info: Geocoder inattivo ignorato: &apos;{geocoder_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="182"/>
      <source>info: Processing layer &apos;{layer_name}&apos; for geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>info: Elaborazione layer &apos;{layer_name}&apos; per il geocoder &apos;{geocoder_name}&apos;.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="188"/>
      <source>warning: Layer &apos;{layer_name}&apos; not found in the project. Skipping.</source>
      <translation>warning: Layer &apos;{layer_name}&apos; non trovato nel progetto. Ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="193"/>
      <source>warning: Layer file &apos;{layer_path}&apos; not found in Mergin project folder. Skipping.</source>
      <translation>warning: File layer &apos;{layer_path}&apos; non trovato nella cartella del progetto Mergin. Ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="197"/>
      <source>warning: Could not load layer from file &apos;{layer_path}&apos;. Skipping.</source>
      <translation>warning: Impossibile caricare il layer dal file &apos;{layer_path}&apos;. Ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="200"/>
      <source>info: Loaded layer &apos;{layer_name}&apos; from Mergin project folder.</source>
      <translation>info: Layer &apos;{layer_name}&apos; caricato dalla cartella del progetto Mergin.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="220"/>
      <source>info: Dumped layer &apos;{layer_name}&apos; into DuckDB table &apos;{table_name}&apos; with {count} records.</source>
      <translation>info: Layer &apos;{layer_name}&apos; salvato nella tabella DuckDB &apos;{table_name}&apos; con {count} record.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="244"/>
      <source>info: Dumped layer &apos;geocoded_anncsu&apos; into DuckDB table &apos;geocoded_anncsu&apos; with {count} records.</source>
      <translation>info: Layer &apos;geocoded_anncsu&apos; salvato nella tabella DuckDB &apos;geocoded_anncsu&apos; con {count} record.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="246"/>
      <source>info: &apos;geocoded_anncsu.gpkg&apos; file not found in Mergin project folder. Skipping.</source>
      <translation>info: File &apos;geocoded_anncsu.gpkg&apos; non trovato nella cartella del progetto Mergin. Ignorato.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="250"/>
      <source>Error while updating from Mergin: {error}</source>
      <translation>Errore durante l&apos;aggiornamento da Mergin: {error}</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="257"/>
      <source>info: Reopened DuckDB database to consolidate changes.</source>
      <translation>info: Database DuckDB riaperto per consolidare le modifiche.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="261"/>
      <source>info: Update from Mergin completed successfully.</source>
      <translation>info: Aggiornamento da Mergin completato con successo.</translation>
    </message>
    <message>
      <location filename="../anncsu_wizard/wizard_update_from_mergin.py" line="266"/>
      <source>warning:  Scope repo locally updated need to be synched to remote repo.</source>
      <translation>warning:  Repository scope aggiornato localmente, sincronizzazione con il repository remoto necessaria.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- utils/settings_manager.py (new strings)                      -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUSettingsManager</name>

    <message>
      <location filename="../utils/settings_manager.py" line="469"/>
      <source>Failed to load default scopes. Reset to default values. {e}</source>
      <translation>Impossibile caricare gli scope predefiniti. Ripristino ai valori predefiniti. {e}</translation>
    </message>
    <message>
      <location filename="../utils/settings_manager.py" line="1259"/>
      <source>Failed to download source database: {error_msg}</source>
      <translation>Impossibile scaricare il database sorgente: {error_msg}</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- resources/ui/wizard_settings.ui                             -->
  <!-- ============================================================ -->
  <!-- ============================================================ -->
  <!-- resources/ui/wizard_settings.ui + wizard_about.ui           -->
  <!-- + geocode_results_tab.ui (all class="Form")                 -->
  <!-- ============================================================ -->
  <context>
    <name>Form</name>

    <!-- wizard_settings.ui -->
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>ANNCSU Wizard settings</source>
      <translation>Impostazioni ANNCSU Wizard</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>ANNCSU</source>
      <translation>ANNCSU</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>DB:</source>
      <translation>DB:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Municipality:</source>
      <translation>Comune:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Session name:</source>
      <translation>Nome sessione:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Remove Session</source>
      <translation>Rimuovi Sessione</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Session URL:</source>
      <translation>URL Sessione:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Sync</source>
      <translation>Sincronizza</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Update from ANNCSU</source>
      <translation>Aggiorna da ANNCSU</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Create New Session</source>
      <translation>Crea Nuova Sessione</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Geocoders</source>
      <translation>Geocoder</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Mergin project</source>
      <translation>Progetto Mergin</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Workspace:</source>
      <translation>Area di lavoro:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>ANNCSU layer will be saved in the Mergin project path</source>
      <translation>Il layer ANNCSU verrà salvato nel percorso del progetto Mergin</translation>
    </message>

    <!-- geocode_results_tab.ui -->
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Statistics</source>
      <translation>Statistiche</translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Records: </source>
      <translation>Record: </translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Successes: </source>
      <translation>Successi: </translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Fails: </source>
      <translation>Fallimenti: </translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Out of  geofence:</source>
      <translation>Fuori geofence:</translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Score: </source>
      <translation>Punteggio: </translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Clusters:</source>
      <translation>Cluster:</translation>
    </message>
    <message>
      <location filename="../resources/ui/geocode_results_tab.ui"/>
      <source>Overlapped:</source>
      <translation>Sovrapposti:</translation>
    </message>

    <!-- wizard_about.ui -->
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>Getting started</source>
      <translation type="obsolete">Per iniziare</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>To run any tools of ANNCSU QGIS Plugin, you need to install ANNCSU Toolkit. ANNCSU Toolkit needs to be installed separately from ANNCSU QGIS Plugin due to package incompabilities between ANNCSU Toolkit and QGIS.</source>
      <translation type="obsolete">Per utilizzare gli strumenti del plugin ANNCSU QGIS, è necessario installare ANNCSU Toolkit. ANNCSU Toolkit va installato separatamente dal plugin ANNCSU QGIS a causa di incompatibilità di pacchetti tra ANNCSU Toolkit e QGIS.</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>You can install ANNCSU Toolkit in any Python environment, but using a clean Conda environment or venv is recommended. For detailed installation instructions, see ANNCSU Toolkit GitHub (link below). After installation, set the location of your Python environment on Settings page.</source>
      <translation type="obsolete">È possibile installare ANNCSU Toolkit in qualsiasi ambiente Python, ma si consiglia di utilizzare un ambiente Conda o venv pulito. Per istruzioni dettagliate sull&apos;installazione, consultare il repository GitHub di ANNCSU Toolkit (link in basso). Dopo l&apos;installazione, impostare il percorso dell&apos;ambiente Python nella pagina Impostazioni.</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>ANNCSU-Manager is a QGIS plugin to update Italian official portal data database called ANNCSU.</source>
      <translation>ANNCSU-Manager è un plugin QGIS per aggiornare il database del portale ufficiale italiano denominato ANNCSU.</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>Sources and help</source>
      <translation>Risorse e assistenza</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>ANNCSU QGIS Plugin GitHub repository</source>
      <translation>Repository GitHub ANNCSU QGIS Plugin</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>ANNCSU Toolkit GitHub repository</source>
      <translation>Repository GitHub ANNCSU Toolkit</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>User manual / guide</source>
      <translation>Manuale utente / guida</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>License</source>
      <translation>Licenza</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_about.ui"/>
      <source>This QGIS plugin is licensed under GPL version 2.</source>
      <translation>Questo plugin QGIS è rilasciato con licenza GPL versione 2.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- resources/ui/wizard_run_geocoders_page.ui +                  -->
  <!-- wizard_materialise_layers.ui + wizard_evaluate_geocode_page.ui-->
  <!-- wizard_reduce_clusters_page.ui + wizard_generate_mergin_page -->
  <!-- wizard_update_from_mergin.ui  (all class="WizardPage")       -->
  <!-- ============================================================ -->
  <context>
    <name>WizardPage</name>

    <!-- wizard_run_geocoders_page.ui -->
    <message>
      <location filename="../resources/ui/wizard_run_geocoders_page.ui"/>
      <source>Geocode</source>
      <translation>Geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_run_geocoders_page.ui"/>
      <source>Run configured geocoders</source>
      <translation>Esegui i geocoder configurati</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_run_geocoders_page.ui"/>
      <source>Run geocoders</source>
      <translation>Esegui geocoder</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_run_geocoders_page.ui"/>
      <source>Show details</source>
      <translation>Mostra dettagli</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_run_geocoders_page.ui"/>
      <source>progress log</source>
      <translation>log di avanzamento</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_run_geocoders_page.ui"/>
      <source>Clear</source>
      <translation>Cancella</translation>
    </message>

    <!-- wizard_materialise_layers.ui -->
    <message>
      <location filename="../resources/ui/wizard_materialise_layers.ui"/>
      <source>Materialize layers</source>
      <translation>Materializza layer</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_materialise_layers.ui"/>
      <source>Include Fails</source>
      <translation>Includi fallimenti</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_materialise_layers.ui"/>
      <source>Include Success</source>
      <translation>Includi successi</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_materialise_layers.ui"/>
      <source>Include Out of Geofence</source>
      <translation>Includi fuori geofence</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_materialise_layers.ui"/>
      <source>Include Geofence</source>
      <translation>Includi geofence</translation>
    </message>

    <!-- wizard_evaluate_geocode_page.ui -->
    <message>
      <location filename="../resources/ui/wizard_evaluate_geocode_page.ui"/>
      <source>Evaluate Geocode</source>
      <translation>Valuta geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_evaluate_geocode_page.ui"/>
      <source>Evalute geocoding results</source>
      <translation>Valuta i risultati della geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_evaluate_geocode_page.ui"/>
      <source>Load all (memory) layers</source>
      <translation>Carica tutti i layer (in memoria)</translation>
    </message>

    <!-- wizard_reduce_clusters_page.ui -->
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Reduce Clusters</source>
      <translation>Riduci cluster</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Reduce ovelapped addresses mixig geocoding results</source>
      <translation>Riduci indirizzi sovrapposti combinando risultati geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Reduce overlapped clusters</source>
      <translation>Riduci cluster sovrapposti</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Records: </source>
      <translation>Record: </translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Previous clusters:</source>
      <translation>Cluster precedenti:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Previous overlapped:</source>
      <translation>Sovrapposti precedenti:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Clusters:</source>
      <translation>Cluster:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Overlapped:</source>
      <translation>Sovrapposti:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Statistics (on all geocoders)</source>
      <translation>Statistiche (su tutti i geocoder)</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_reduce_clusters_page.ui"/>
      <source>Update geocoded ANNCSU table</source>
      <translation>Aggiorna tabella ANNCSU geocodificata</translation>
    </message>

    <!-- wizard_generate_mergin_page.ui -->
    <message>
      <location filename="../resources/ui/wizard_generate_mergin_page.ui"/>
      <source>Add layers to Mergin</source>
      <translation>Aggiungi layer a Mergin</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_generate_mergin_page.ui"/>
      <source>Export geocoded layers to a Mergin project</source>
      <translation>Esporta layer geocodificati in un progetto Mergin</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_generate_mergin_page.ui"/>
      <source>Add layers to mergin</source>
      <translation>Aggiungi layer a Mergin</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_generate_mergin_page.ui"/>
      <source>Mergin project:</source>
      <translation>Progetto Mergin:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_generate_mergin_page.ui"/>
      <source>geocoded</source>
      <translation>geocodificato</translation>
    </message>

    <!-- wizard_update_from_mergin.ui -->
    <message>
      <location filename="../resources/ui/wizard_update_from_mergin.ui"/>
      <source>Update from Mergin</source>
      <translation>Aggiorna da Mergin</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_update_from_mergin.ui"/>
      <source>Merge modified Mergin layers into geocoded results</source>
      <translation>Unisci layer Mergin modificati nei risultati geocodificati</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- resources/ui/wizard_manager.ui (class="Wizard")              -->
  <!-- ============================================================ -->
  <context>
    <name>Wizard</name>

    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Geocode</source>
      <translation>Geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Run configured geocoders</source>
      <translation>Esegui i geocoder configurati</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Run geocoders</source>
      <translation>Esegui geocoder</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Evaluate Geocode</source>
      <translation>Valuta geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Evalute geocoding results</source>
      <translation>Valuta i risultati della geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Load layers</source>
      <translation>Carica layer</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Statistics</source>
      <translation>Statistiche</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Preview</source>
      <translation>Anteprima</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Select results</source>
      <translation>Seleziona risultati</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Decide gocoding results accepting rule</source>
      <translation>Definisci le regole di accettazione dei risultati geocodifica</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Update session</source>
      <translation>Aggiorna sessione</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_manager.ui"/>
      <source>Update current session with geocoded results</source>
      <translation>Aggiorna la sessione corrente con i risultati geocodificati</translation>
    </message>
  </context>

</TS>
