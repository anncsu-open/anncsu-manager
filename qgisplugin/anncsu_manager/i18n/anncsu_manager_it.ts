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
  <!-- resources/ui/wizard_settings.ui                             -->
  <!-- ============================================================ -->
  <context>
    <name>Form</name>

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
      <source>Session URL:</source>
      <translation>URL Sessione:</translation>
    </message>
    <message>
      <location filename="../resources/ui/wizard_settings.ui"/>
      <source>Remove Session</source>
      <translation>Rimuovi Sessione</translation>
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
  </context>

</TS>
