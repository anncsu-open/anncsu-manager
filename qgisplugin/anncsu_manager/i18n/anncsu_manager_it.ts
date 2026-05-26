<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="it_IT">
  <!-- ============================================================ -->
  <!-- utils/settings_manager.py                                    -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUSettingsManager</name>

    <message>
      <source>Scope at {duckdb_path} is already syncked with remote repo {remote_git_repo}.</source>
      <translation>Scope in {duckdb_path} è già sincronizzato con il repository remoto {remote_git_repo}.</translation>
    </message>
    <message>
      <source>Table &apos;{table_name}&apos; not found in duckdb at {duckdb_path}.</source>
      <translation>Tabella &apos;{table_name}&apos; non trovata nel duckdb in {duckdb_path}.</translation>
    </message>
    <message>
      <source>Error: {e}</source>
      <translation>Errore: {e}</translation>
    </message>
    <message>
      <source>Error reading {table_name} table from duckdb at {duckdb_path}: {e}</source>
      <translation>Errore durante la lettura della tabella {table_name} dal duckdb in {duckdb_path}: {e}</translation>
    </message>
    <message>
      <source>Error merging geocoded dataframe with anncsu dataframe: {e}</source>
      <translation>Errore durante l&apos;unione del dataframe geocodificato con il dataframe anncsu: {e}</translation>
    </message>
    <message>
      <source>Continue update?</source>
      <translation>Continuare l&apos;aggiornamento?</translation>
    </message>
    <message>
      <source>The current session is not synchronized with the remote git repository.
If you update the session data, you may lose unsynchronized changes.</source>
      <translation>La sessione attuale non è sincronizzata con il repository git remoto.
Se aggiorni i dati della sessione, potresti perdere le modifiche non sincronizzate.</translation>
    </message>
    <message>
      <source>Table &apos;geocoded_anncsu&apos; not found in duckdb at {duckdb_path}. Cannot update session.</source>
      <translation>Tabella &apos;geocoded_anncsu&apos; non trovata nel duckdb in {duckdb_path}. Impossibile aggiornare la sessione.</translation>
    </message>
    <message>
      <source>Update not possible</source>
      <translation>Aggiornamento non possibile</translation>
    </message>
    <message>
      <source>The &apos;geocoded_anncsu&apos; table was not found in the session database.
Make sure you have performed the update from Mergin.</source>
      <translation>La tabella &apos;geocoded_anncsu&apos; non è stata trovata nel database della sessione.
Assicurati di aver eseguito l&apos;aggiornamento da Mergin.</translation>
    </message>
    <message>
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
      <source>Update address coordinates?</source>
      <translation>Aggiornare le coordinate degli accessi?</translation>
    </message>
    <message>
      <source>Error updating session with new anncsu data: {e}</source>
      <translation>Errore durante l&apos;aggiornamento della sessione con i nuovi dati anncsu: {e}</translation>
    </message>
    <message>
      <source>Error in populate_table_from_source_task: {e}</source>
      <translation>Errore in populate_table_from_source_task: {e}</translation>
    </message>
    <message>
      <source>Table {table_name} successfully populated from {source_db}</source>
      <translation>Tabella {table_name} popolata con successo da {source_db}</translation>
    </message>
    <message>
      <source>Error populating table {table_name} from {source_db}</source>
      <translation>Errore durante il popolamento della tabella {table_name} da {source_db}</translation>
    </message>
    <message>
      <source>Connect remote DB: {source_db}</source>
      <translation>Connessione al DB remoto: {source_db}</translation>
    </message>
    <message>
      <source>Connect local DB: {source_db}</source>
      <translation>Connessione al DB locale: {source_db}</translation>
    </message>
    <message>
      <source>Error populating {table_name} table from source database: {e}</source>
      <translation>Errore durante il popolamento della tabella {table_name} dal database sorgente: {e}</translation>
    </message>
    <message>
      <source>Populated {table_name} table from source database: {source_db}</source>
      <translation>Tabella {table_name} popolata dal database sorgente: {source_db}</translation>
    </message>
    <message>
      <source>Creating new session for municipality {anncsu_id} from source db {source_db}...</source>
      <translation>Creazione nuova sessione per il comune {anncsu_id} dal database sorgente {source_db}...</translation>
    </message>
    <message>
      <source>Invalid remote HTTP(S) git repo URL: {remote_git_repo} check if SSH. error: {e}</source>
      <translation>URL repository git remoto HTTP(S) non valido: {remote_git_repo}. Verificare se si tratta di SSH. Errore: {e}</translation>
    </message>
    <message>
      <source>Invalid remote git repo URL: {remote_git_repo}</source>
      <translation>URL repository git remoto non valido: {remote_git_repo}</translation>
    </message>
    <message>
      <source>Successfully cloned/pulled {remote_git_repo} into {local_path}</source>
      <translation>Repository {remote_git_repo} clonato/aggiornato con successo in {local_path}</translation>
    </message>
    <message>
      <source>Failed to load default geocoder configs. Reset to default values. {e}</source>
      <translation>Impossibile caricare la configurazione predefinita dei geocoder. Ripristino ai valori predefiniti. {e}</translation>
    </message>
    <message>
      <source>Could not find geocoders.json at {path}. Reverting to default path.</source>
      <translation>File geocoders.json non trovato in {path}. Ripristino al percorso predefinito.</translation>
    </message>
    <message>
      <source>Failed to download source database: {error_msg}</source>
      <translation>Download del database sorgente non riuscito: {error_msg}</translation>
    </message>
    <message>
      <source>Error creating new session: {exception}</source>
      <translation>Errore durante la creazione della nuova sessione: {exception}</translation>
    </message>
    <message>
      <source>Failed to clone or pull remote git repo: {remote_git_repo}</source>
      <translation>Impossibile clonare o aggiornare il repository git remoto: {remote_git_repo}</translation>
    </message>
    <message>
      <source>No duckdb sessions available. Please create a new session for {nome} or select another session.</source>
      <translation>Nessuna sessione duckdb disponibile. Crea una nuova sessione per {nome} o seleziona un&apos;altra sessione.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- utils/misc_utils.py — DownloadFileTask                       -->
  <!-- ============================================================ -->
  <context>
    <name>DownloadFileTask</name>

    <message>
      <source>Successfully downloaded url: {url} to {destination_path}</source>
      <translation>URL {url} scaricato con successo in {destination_path}</translation>
    </message>
    <message>
      <source>Failed to download url: {url}. Error: {error_msg}</source>
      <translation>Download dell&apos;URL {url} non riuscito. Errore: {error_msg}</translation>
    </message>
    <message>
      <source>Downloading from {url} to {destination_path}...</source>
      <translation>Download in corso da {url} verso {destination_path}...</translation>
    </message>
    <message>
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
      <source>Cloning repo {remote_git_repo}</source>
      <translation>Clonazione repository {remote_git_repo}</translation>
    </message>
    <message>
      <source>Error in clone_or_pull_git_repo_task: {e}</source>
      <translation>Errore in clone_or_pull_git_repo_task: {e}</translation>
    </message>
    <message>
      <source>Repo {remote_git_repo} cloned successfully in {local_path}</source>
      <translation>Repository {remote_git_repo} clonato con successo in {local_path}</translation>
    </message>
    <message>
      <source>Error cloning repo {remote_git_repo} in {local_path}</source>
      <translation>Errore durante la clonazione del repository {remote_git_repo} in {local_path}</translation>
    </message>
    <message>
      <source>Pulling latest changes from git repository at {url}...</source>
      <translation>Aggiornamento del repository git da {url}...</translation>
    </message>
    <message>
      <source>Repository already exists at {local_path}, pulled latest changes.</source>
      <translation>Il repository esiste già in {local_path}; aggiornamento completato.</translation>
    </message>
    <message>
      <source>Cloning latest changes from git repository at {url}...</source>
      <translation>Clonazione del repository git da {url}...</translation>
    </message>
    <message>
      <source>Error cloning git repository {remote_git_repo}: {e}</source>
      <translation>Errore durante la clonazione del repository git {remote_git_repo}: {e}</translation>
    </message>
    <message>
      <source>Successfully cloned repo {remote_git_repo} to {local_path}.</source>
      <translation>Repository {remote_git_repo} clonato con successo in {local_path}.</translation>
    </message>
    <message>
      <source>Error cloning/pulling git repository {remote_git_repo}: {e}</source>
      <translation>Errore durante la clonazione/aggiornamento del repository git {remote_git_repo}: {e}</translation>
    </message>
    <message>
      <source>Remote repository {remote_git_repo} is empty (no commits). Push at least one commit before syncing.</source>
      <translation>Il repository remoto {remote_git_repo} è vuoto (nessun commit). Esegui almeno un commit prima di sincronizzare.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_settings.py                             -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardSettings</name>

    <message>
      <source>No session or municipality selected to synchronize.</source>
      <translation>Nessuna sessione o comune selezionato da sincronizzare.</translation>
    </message>
    <message>
      <source>Session &apos;{session}&apos; synchronized with the remote repository.</source>
      <translation>Sessione &apos;{session}&apos; sincronizzata con il repository remoto.</translation>
    </message>
    <message>
      <source>Error synchronizing session &apos;{session}&apos;: {error}</source>
      <translation>Errore durante la sincronizzazione della sessione &apos;{session}&apos;: {error}</translation>
    </message>
    <message>
      <source>No session selected to update.</source>
      <translation>Nessuna sessione selezionata da aggiornare.</translation>
    </message>
    <message>
      <source>Error creating new session: {exception}</source>
      <translation>Errore durante la creazione della nuova sessione: {exception}</translation>
    </message>
    <message>
      <source>Successfully updated ANNCSU table for session {session}</source>
      <translation>Tabella ANNCSU aggiornata con successo per la sessione {session}</translation>
    </message>
    <message>
      <source>ANNCSU update cancelled.</source>
      <translation>Aggiornamento ANNCSU annullato.</translation>
    </message>
    <message>
      <source>ANNCSU successfully updated for the selected session.</source>
      <translation>ANNCSU aggiornato con successo per la sessione selezionata.</translation>
    </message>
    <message>
      <source>No session selected to delete.</source>
      <translation>Nessuna sessione selezionata da eliminare.</translation>
    </message>
    <message>
      <source>Delete ANNCSU session</source>
      <translation>Eliminazione sessione ANNCSU</translation>
    </message>
    <message>
      <source>Are you sure you want to delete session &apos;{session}&apos;?</source>
      <translation>Sei sicuro di voler eliminare la sessione &apos;{session}&apos;?</translation>
    </message>
    <message>
      <source>Session &apos;{session}&apos; deleted.</source>
      <translation>Sessione &apos;{session}&apos; eliminata.</translation>
    </message>
    <message>
      <source>No municipality code associated with the selected session.
Select one and save to create a working session.</source>
      <translation>Nessun codice comune associato alla sessione selezionata.
Selezionarne uno e salvare per creare una sessione di lavoro.</translation>
    </message>
    <message>
      <source>Select municipality code</source>
      <translation>Seleziona codice comune</translation>
    </message>
    <message>
      <source>Select session</source>
      <translation>Seleziona sessione</translation>
    </message>
    <message>
      <source>Could not register geocoder &apos;{geocoder_name}&apos;: {e}</source>
      <translation>Impossibile registrare il geocoder &apos;{geocoder_name}&apos;: {e}</translation>
    </message>
    <message>
      <source>Select a municipality code to proceed.</source>
      <translation>Selezionare un codice comune per procedere.</translation>
    </message>
    <message>
      <source>New session creation task already in progress.</source>
      <translation>Task di creazione nuova sessione già in esecuzione.</translation>
    </message>
    <message>
      <source>Forcing creation of a new ANNCSU session. Do you want to proceed?</source>
      <translation>Forzando la creazione di una nuova sessione ANNCSU. Vuoi procedere?</translation>
    </message>
    <message>
      <source>The municipality code or ANNCSU source database have been modified compared to the current session.
A new ANNCSU session will be generated. Do you want to proceed?</source>
      <translation>Il codice comune o il database sorgente ANNCSU sono stati modificati rispetto alla sessione attuale.
Verrà generata una nuova sessione ANNCSU. Vuoi procedere?</translation>
    </message>
    <message>
      <source>Source ANNCSU DB or municipality code modified</source>
      <translation>DB sorgente ANNCSU o codice comune modificati</translation>
    </message>
    <message>
      <source>No changes saved</source>
      <translation>Nessuna modifica salvata</translation>
    </message>
    <message>
      <source>Error creating new session</source>
      <translation>Errore durante la creazione della nuova sessione</translation>
    </message>
    <message>
      <source>ANNCSU QGIS Plugin settings saved.</source>
      <translation>Impostazioni del plugin ANNCSU QGIS salvate.</translation>
    </message>
    <message>
      <source>ANNCSU QGIS Plugin settings reset.</source>
      <translation>Impostazioni del plugin ANNCSU QGIS ripristinate.</translation>
    </message>
    <message>
      <source>Private tables detected</source>
      <translation>Tabelle private rilevate</translation>
    </message>
    <message>
      <source>The current session has private tables that will be lost if you synchronize with the remote repository.
Do you want to proceed?</source>
      <translation>La sessione corrente contiene tabelle private che andranno perse se si sincronizza con il repository remoto.
Vuoi procedere?</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_update_from_project.py                   -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCUWizardUpdateFromProjectStep</name>

    <message>
      <source>-- Select Mergin Project --</source>
      <translation>-- Seleziona Progetto Mergin --</translation>
    </message>
    <message>
      <source>No local Mergin project found. Configure Mergin before proceeding.</source>
      <translation>Nessun progetto Mergin locale trovato. Configurare Mergin prima di procedere.</translation>
    </message>
    <message>
      <source>Select a valid Mergin project before proceeding.</source>
      <translation>Selezionare un progetto Mergin valido prima di procedere.</translation>
    </message>
    <message>
      <source>Continue saving?</source>
      <translation>Continuare il salvataggio?</translation>
    </message>
    <message>
      <source>The selected Mergin project &apos;{project_name}&apos; does not match the open QGIS project &apos;{cur_project}&apos;. Proceed anyway?</source>
      <translation>Il progetto Mergin selezionato &apos;{project_name}&apos; non corrisponde al progetto QGIS aperto &apos;{cur_project}&apos;. Procedere comunque?</translation>
    </message>
    <message>
      <source>Current project does not have a valid home path. Please save the project before proceeding.</source>
      <translation>Il progetto corrente non ha un percorso valido. Salvare il progetto prima di procedere.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_generate_project_step.py                 -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCUWizardGenerateProjectStep</name>

    <message>
      <source>-- Select Mergin Project --</source>
      <translation>-- Seleziona Progetto Mergin --</translation>
    </message>
    <message>
      <source>No local Mergin project found. Configure Mergin before proceeding.</source>
      <translation>Nessun progetto Mergin locale trovato. Configurare Mergin prima di procedere.</translation>
    </message>
    <message>
      <source>Select a valid Mergin project before proceeding.</source>
      <translation>Selezionare un progetto Mergin valido prima di procedere.</translation>
    </message>
    <message>
      <source>Continue saving?</source>
      <translation>Continuare il salvataggio?</translation>
    </message>
    <message>
      <source>The selected Mergin project &apos;{project_name}&apos; does not match the open QGIS project &apos;{cur_project}&apos;. Proceed anyway?</source>
      <translation>Il progetto Mergin selezionato &apos;{project_name}&apos; non corrisponde al progetto QGIS aperto &apos;{cur_project}&apos;. Procedere comunque?</translation>
    </message>
    <message>
      <source>Unable to load the ANNCSU table. Make sure the table is available before proceeding.</source>
      <translation>Impossibile caricare la tabella ANNCSU. Assicurarsi che la tabella sia disponibile prima di procedere.</translation>
    </message>
    <message>
      <source>Loading: {layer_name}</source>
      <translation>Caricamento: {layer_name}</translation>
    </message>
    <message>
      <source>Added results for geocoder &apos;{geocoder_name}&apos; into project &apos;{project_name}&apos;.</source>
      <translation>Risultati per il geocoder &apos;{geocoder_name}&apos; aggiunti al progetto &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>Saving geocoded ANNCSU table into project &apos;{project_name}&apos;.</source>
      <translation>Salvataggio della tabella ANNCSU geocodificata nel progetto &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>Current project does not have a valid home path. Please save the project before proceeding.</source>
      <translation>Il progetto corrente non ha un percorso valido. Salvare il progetto prima di procedere.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_materialise_layers.py                   -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardMaterialiseLayers</name>

    <message>
      <source>Loading: {layer_name}</source>
      <translation>Caricamento: {layer_name}</translation>
    </message>
    <message>
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
      <source>Success</source>
      <translation>Successo</translation>
    </message>
    <message>
      <source>Info</source>
      <translation>Info</translation>
    </message>
    <message>
      <source>Warning</source>
      <translation>Avviso</translation>
    </message>
    <message>
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
      <source>Command: {info}</source>
      <translation>Comando: {info}</translation>
    </message>
    <message>
      <source>Debug: {info}</source>
      <translation>Debug: {info}</translation>
    </message>
    <message>
      <source>Console: {info}</source>
      <translation>Console: {info}</translation>
    </message>
    <message>
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
      <source>ANNCSU Wizard</source>
      <translation>ANNCSU Wizard</translation>
    </message>
  </context>

  <context>
    <name>ANNCSUWizard</name>

    <message>
      <source>ANNCSU Manager</source>
      <translation>ANNCSU Manager</translation>
    </message>
    <message>
      <source>Settings</source>
      <translation>Impostazioni</translation>
    </message>
    <message>
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
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <source>No scope is currently selected. Please select a scope in the settings before running geocoders.</source>
      <translation>Nessuno scope selezionato. Selezionare uno scope nelle impostazioni prima di eseguire i geocoder.</translation>
    </message>
    <message>
      <source>No DuckDB database path found in the current scope settings.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope corrente.</translation>
    </message>
    <message>
      <source>Could not connect to DuckDB database at {duck_db_source}.</source>
      <translation>Impossibile connettersi al database DuckDB in {duck_db_source}.</translation>
    </message>
    <message>
      <source>Skipping inactive geocoder {geocoder_name}...</source>
      <translation>Geocoder inattivo ignorato: {geocoder_name}...</translation>
    </message>
    <message>
      <source>Could not instantiate geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>Impossibile istanziare il geocoder &apos;{geocoder_name}&apos;.</translation>
    </message>
    <message>
      <source>Geocoding {count} addresses using {geocoder_name}...</source>
      <translation>Geocodifica di {count} indirizzi con {geocoder_name}...</translation>
    </message>
    <message>
      <source>Geocoding {count} bulk addresses to speedup process.</source>
      <translation>Geocodifica massiva di {count} indirizzi per accelerare il processo.</translation>
    </message>
    <message>
      <source>Geocoded {count} addresses in {elapsed} seconds using {geocoder_name}.</source>
      <translation>Geocodificati {count} indirizzi in {elapsed} secondi con {geocoder_name}.</translation>
    </message>
    <message>
      <source>Saving geocoding results into table {result_table_name}...</source>
      <translation>Salvataggio risultati geocodifica nella tabella {result_table_name}...</translation>
    </message>
    <message>
      <source>Geocoder &apos;{geocoder_name}&apos;: Geocodings saved into table {result_table_name}.</source>
      <translation>Geocoder &apos;{geocoder_name}&apos;: geocodifiche salvate nella tabella {result_table_name}.</translation>
    </message>
    <message>
      <source>All geocoding processes completed.</source>
      <translation>Tutti i processi di geocodifica completati.</translation>
    </message>
    <message>
      <source>warning:  Scope repo locally updated need to be synched to remote repo.</source>
      <translation>warning:  Repository scope aggiornato localmente, sincronizzazione con il repository remoto necessaria.</translation>
    </message>
    <message>
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
      <source>Table &apos;remaining_clusters&apos; or &apos;remaining_duplicates&apos; does not exist. Run Deduplicate step first.</source>
      <translation>La tabella &apos;remaining_clusters&apos; o &apos;remaining_duplicates&apos; non esiste. Eseguire prima il passo di deduplicazione.</translation>
    </message>
    <message>
      <source>N/A - run Deduplicate step</source>
      <translation>N/D - eseguire il passo di deduplicazione</translation>
    </message>
    <message>
      <source>No DuckDB database path found in the current scope settings. Cannot update reduced clusters statistics.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope. Impossibile aggiornare le statistiche.</translation>
    </message>
    <message>
      <source>N/A</source>
      <translation>N/D</translation>
    </message>
    <message>
      <source>No DuckDB database path found in the current scope settings. Cannot run reduce clusters process.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope. Impossibile eseguire il processo di riduzione cluster.</translation>
    </message>
    <message>
      <source>Error while running reduce clusters process: {error}</source>
      <translation>Errore durante il processo di riduzione cluster: {error}</translation>
    </message>
    <message>
      <source>success: Reduce clusters process completed successfully.</source>
      <translation>success: Processo di riduzione cluster completato con successo.</translation>
    </message>
    <message>
      <source>info: Reduce clusters process effectiveness: {effectiveness:.2f}% of clusters reduced.</source>
      <translation>info: Efficacia del processo di riduzione cluster: {effectiveness:.2f}% di cluster ridotti.</translation>
    </message>
    <message>
      <source>info: Reduce clusters process effectiveness: {effectiveness:.2f}% of overlapped addresses reduced.</source>
      <translation>info: Efficacia del processo di riduzione cluster: {effectiveness:.2f}% di indirizzi sovrapposti ridotti.</translation>
    </message>
    <message>
      <source>info: geocoders ordered by number of overlapped addresses from min to max</source>
      <translation>info: geocoder ordinati per numero di indirizzi sovrapposti dal minore al maggiore</translation>
    </message>
    <message>
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
      <source>{success_rate:.2f}% (Threshold: {threshold})</source>
      <translation>{success_rate:.2f}% (Soglia: {threshold})</translation>
    </message>
    <message>
      <source>Error loading results: {error}</source>
      <translation>Errore durante il caricamento dei risultati: {error}</translation>
    </message>
  </context>

  <context>
    <name>ANNCSUWizardEvaluateGeocode</name>

    <message>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <source>No scope is currently selected. Please select a scope in the settings before running geocoders.</source>
      <translation>Nessuno scope selezionato. Selezionare uno scope nelle impostazioni prima di eseguire i geocoder.</translation>
    </message>
    <message>
      <source>No DuckDB database path found in the current scope settings.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope corrente.</translation>
    </message>
    <message>
      <source>Could not connect to DuckDB database at {duck_db_source}.</source>
      <translation>Impossibile connettersi al database DuckDB in {duck_db_source}.</translation>
    </message>
    <message>
      <source>Results table &apos;{result_table_name}&apos; does not exist. Skipping evaluation for geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>La tabella dei risultati &apos;{result_table_name}&apos; non esiste. Valutazione del geocoder &apos;{geocoder_name}&apos; ignorata.</translation>
    </message>
    <message>
      <source>DuckDB database file not found at {duck_db_source}.</source>
      <translation>File database DuckDB non trovato in {duck_db_source}.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_materialise_layers.py (new strings)     -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCSUWizardMaterialiseLayers</name>

    <message>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <source>No scope is currently selected. Please select a scope in the settings before running geocoders.</source>
      <translation>Nessuno scope selezionato. Selezionare uno scope nelle impostazioni prima di eseguire i geocoder.</translation>
    </message>
    <message>
      <source>Scope local repo path &apos;{out_path}&apos; does not exist. Please check your scope settings.</source>
      <translation>Il percorso del repository locale dello scope &apos;{out_path}&apos; non esiste. Verificare le impostazioni dello scope.</translation>
    </message>
    <message>
      <source>info: Preparing to add geocoding results for &apos;{geocoder_name}&apos; to local scope folder.</source>
      <translation>info: Preparazione aggiunta risultati geocodifica per &apos;{geocoder_name}&apos; nella cartella locale dello scope.</translation>
    </message>
    <message>
      <source>info: Adding results into folder: {out_path}.</source>
      <translation>info: Aggiunta risultati nella cartella: {out_path}.</translation>
    </message>
    <message>
      <source>info: Geofence polygon layer &apos;{layer_geofence_polygon}&apos; added to local git repo.</source>
      <translation>info: Layer poligono geofence &apos;{layer_geofence_polygon}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <source>info: Fails layer &apos;{layer_name_fails}&apos; added to local git repo.</source>
      <translation>info: Layer dei fallimenti &apos;{layer_name_fails}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <source>info: Out of geofence layer &apos;{layer_name_out_of_geofence}&apos; added to local git repo.</source>
      <translation>info: Layer fuori geofence &apos;{layer_name_out_of_geofence}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <source>info: Success layer &apos;{layer_name_success}&apos; added to local git repo.</source>
      <translation>info: Layer dei successi &apos;{layer_name_success}&apos; aggiunto al repository git locale.</translation>
    </message>
    <message>
      <source>info: Commit and push layers into git repo.</source>
      <translation>info: Commit e push dei layer nel repository git.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_generate_project_step.py (new strings)   -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCUWizardGenerateProjectStep</name>

    <message>
      <source>info: Found Mergin project: {project_name} workspace: {workspace} at path: {path} on server: {project_server}.</source>
      <translation>info: Trovato progetto Mergin: {project_name} workspace: {workspace} al percorso: {path} sul server: {project_server}.</translation>
    </message>
    <message>
      <source>info: Current QGIS project &apos;{cur_project}&apos; matches Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Il progetto QGIS corrente &apos;{cur_project}&apos; corrisponde al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>info: Preparing to add geocoding results for &apos;{geocoder_name}&apos; to project &apos;{project_name}&apos;.</source>
      <translation>info: Preparazione aggiunta risultati geocodifica per &apos;{geocoder_name}&apos; al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>info: Adding results into folder: {out_path}.</source>
      <translation>info: Aggiunta risultati nella cartella: {out_path}.</translation>
    </message>
    <message>
      <source>info: Geofence polygon layer &apos;{layer_geofence_polygon}&apos; added to project &apos;{project_name}&apos;.</source>
      <translation>info: Layer poligono geofence &apos;{layer_geofence_polygon}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>error: Unable to merge geocoded results with anncsu table for geocoder &apos;{geocoder_name}&apos;. Skipping saving success layer.</source>
      <translation>error: Impossibile unire i risultati geocodificati con la tabella anncsu per il geocoder &apos;{geocoder_name}&apos;. Salvataggio layer successi ignorato.</translation>
    </message>
    <message>
      <source>info: Success layer &apos;{layer_name_success}&apos; added to project &apos;{project_name}&apos;.</source>
      <translation>info: Layer dei successi &apos;{layer_name_success}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>error: Unable to merge fails results with anncsu table for geocoder &apos;{geocoder_name}&apos;. Skipping saving fails layer.</source>
      <translation>error: Impossibile unire i risultati dei fallimenti con la tabella anncsu per il geocoder &apos;{geocoder_name}&apos;. Salvataggio layer fallimenti ignorato.</translation>
    </message>
    <message>
      <source>info: Fails layer &apos;{layer_name_fails}&apos; added to project &apos;{project_name}&apos;.</source>
      <translation>info: Layer dei fallimenti &apos;{layer_name_fails}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>error: Unable to merge out of geofence results with anncsu table for geocoder &apos;{geocoder_name}&apos;. Skipping saving out of geofence layer.</source>
      <translation>error: Impossibile unire i risultati fuori geofence con la tabella anncsu per il geocoder &apos;{geocoder_name}&apos;. Salvataggio layer fuori geofence ignorato.</translation>
    </message>
    <message>
      <source>info: Out of geofence layer &apos;{layer_name_out_of_geofence}&apos; added to project &apos;{project_name}&apos;.</source>
      <translation>info: Layer fuori geofence &apos;{layer_name_out_of_geofence}&apos; aggiunto al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- anncsu_wizard/wizard_update_from_project.py (new strings)     -->
  <!-- ============================================================ -->
  <context>
    <name>ANNCUWizardUpdateFromProjectStep</name>

    <message>
      <source>info: Found Mergin project: {project_name} workspace: {workspace} at path: {path} on server: {project_server}.</source>
      <translation>info: Trovato progetto Mergin: {project_name} workspace: {workspace} al percorso: {path} sul server: {project_server}.</translation>
    </message>
    <message>
      <source>info: Current QGIS project &apos;{cur_project}&apos; matches Mergin project &apos;{project_name}&apos;.</source>
      <translation>info: Il progetto QGIS corrente &apos;{cur_project}&apos; corrisponde al progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>Current scope id &apos;{current_scope_id}&apos; not found among defined scopes.</source>
      <translation>L&apos;id scope corrente &apos;{current_scope_id}&apos; non trovato tra gli scope definiti.</translation>
    </message>
    <message>
      <source>Using scope: {current_scope_id}</source>
      <translation>Utilizzo scope: {current_scope_id}</translation>
    </message>
    <message>
      <source>No DuckDB database path found in the current scope settings.</source>
      <translation>Nessun percorso database DuckDB trovato nelle impostazioni dello scope corrente.</translation>
    </message>
    <message>
      <source>Updating DuckDB database at {duck_db_source} from Mergin project &apos;{project_name}&apos;.</source>
      <translation>Aggiornamento database DuckDB in {duck_db_source} dal progetto Mergin &apos;{project_name}&apos;.</translation>
    </message>
    <message>
      <source>Could not connect to DuckDB database at {duck_db_source}.</source>
      <translation>Impossibile connettersi al database DuckDB in {duck_db_source}.</translation>
    </message>
    <message>
      <source>info: Skipping inactive geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>info: Geocoder inattivo ignorato: &apos;{geocoder_name}&apos;.</translation>
    </message>
    <message>
      <source>info: Processing layer &apos;{layer_name}&apos; for geocoder &apos;{geocoder_name}&apos;.</source>
      <translation>info: Elaborazione layer &apos;{layer_name}&apos; per il geocoder &apos;{geocoder_name}&apos;.</translation>
    </message>
    <message>
      <source>warning: Layer &apos;{layer_name}&apos; not found in the project. Skipping.</source>
      <translation>warning: Layer &apos;{layer_name}&apos; non trovato nel progetto. Ignorato.</translation>
    </message>
    <message>
      <source>warning: Layer file &apos;{layer_path}&apos; not found in project folder. Skipping.</source>
      <translation>warning: File layer &apos;{layer_path}&apos; non trovato nella cartella del progetto. Ignorato.</translation>
    </message>
    <message>
      <source>warning: Could not load layer from file &apos;{layer_path}&apos;. Skipping.</source>
      <translation>warning: Impossibile caricare il layer dal file &apos;{layer_path}&apos;. Ignorato.</translation>
    </message>
    <message>
      <source>info: Loaded layer &apos;{layer_name}&apos; from project folder.</source>
      <translation>info: Layer &apos;{layer_name}&apos; caricato dalla cartella del progetto.</translation>
    </message>
    <message>
      <source>Invalid geocoder name: &apos;{table_name}&apos;. Skipping.</source>
      <translation>Nome geocoder non valido: &apos;{table_name}&apos;. Ignorato.</translation>
    </message>
    <message>
      <source>info: Dumped layer &apos;{layer_name}&apos; into DuckDB table &apos;{table_name}&apos; with {count} records.</source>
      <translation>info: Layer &apos;{layer_name}&apos; salvato nella tabella DuckDB &apos;{table_name}&apos; con {count} record.</translation>
    </message>
    <message>
      <source>info: Dumped layer &apos;geocoded_anncsu&apos; into DuckDB table &apos;geocoded_anncsu&apos; with {count} records.</source>
      <translation>info: Layer &apos;geocoded_anncsu&apos; salvato nella tabella DuckDB &apos;geocoded_anncsu&apos; con {count} record.</translation>
    </message>
    <message>
      <source>info: &apos;geocoded_anncsu.gpkg&apos; file not found in Mergin project folder. Skipping.</source>
      <translation>info: File &apos;geocoded_anncsu.gpkg&apos; non trovato nella cartella del progetto Mergin. Ignorato.</translation>
    </message>
    <message>
      <source>Error while updating from project: {error}</source>
      <translation>Errore durante l&apos;aggiornamento dal progetto: {error}</translation>
    </message>
    <message>
      <source>info: Reopened DuckDB database to consolidate changes.</source>
      <translation>info: Database DuckDB riaperto per consolidare le modifiche.</translation>
    </message>
    <message>
      <source>info: Update from project completed successfully.</source>
      <translation>info: Aggiornamento dal progetto completato con successo.</translation>
    </message>
    <message>
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
      <source>Failed to load default scopes. Reset to default values. {e}</source>
      <translation>Impossibile caricare gli scope predefiniti. Ripristino ai valori predefiniti. {e}</translation>
    </message>
    <message>
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
      <source>ANNCSU Wizard settings</source>
      <translation>Impostazioni ANNCSU Wizard</translation>
    </message>
    <message>
      <source>ANNCSU</source>
      <translation>ANNCSU</translation>
    </message>
    <message>
      <source>DB:</source>
      <translation>DB:</translation>
    </message>
    <message>
      <source>Municipality:</source>
      <translation>Comune:</translation>
    </message>
    <message>
      <source>Session name:</source>
      <translation>Nome sessione:</translation>
    </message>
    <message>
      <source>Remove Session</source>
      <translation>Rimuovi Sessione</translation>
    </message>
    <message>
      <source>Session URL:</source>
      <translation>URL Sessione:</translation>
    </message>
    <message>
      <source>Sync</source>
      <translation>Sincronizza</translation>
    </message>
    <message>
      <source>Update from ANNCSU</source>
      <translation>Aggiorna da ANNCSU</translation>
    </message>
    <message>
      <source>Create New Session</source>
      <translation>Crea Nuova Sessione</translation>
    </message>
    <message>
      <source>Geocoders</source>
      <translation>Geocoder</translation>
    </message>
    <message>
      <source>Mergin project</source>
      <translation>Progetto Mergin</translation>
    </message>
    <message>
      <source>Workspace:</source>
      <translation>Area di lavoro:</translation>
    </message>
    <message>
      <source>ANNCSU layer will be saved in the Mergin project path</source>
      <translation>Il layer ANNCSU verrà salvato nel percorso del progetto Mergin</translation>
    </message>

    <!-- geocode_results_tab.ui -->
    <message>
      <source>Statistics</source>
      <translation>Statistiche</translation>
    </message>
    <message>
      <source>Records: </source>
      <translation>Record: </translation>
    </message>
    <message>
      <source>Successes: </source>
      <translation>Successi: </translation>
    </message>
    <message>
      <source>Fails: </source>
      <translation>Fallimenti: </translation>
    </message>
    <message>
      <source>Out of  geofence:</source>
      <translation>Fuori geofence:</translation>
    </message>
    <message>
      <source>Score: </source>
      <translation>Punteggio: </translation>
    </message>
    <message>
      <source>Clusters:</source>
      <translation>Cluster:</translation>
    </message>
    <message>
      <source>Overlapped:</source>
      <translation>Sovrapposti:</translation>
    </message>

    <!-- wizard_about.ui -->
    <message>
      <source>Getting started</source>
      <translation type="obsolete">Per iniziare</translation>
    </message>
    <message>
      <source>To run any tools of ANNCSU QGIS Plugin, you need to install ANNCSU Toolkit. ANNCSU Toolkit needs to be installed separately from ANNCSU QGIS Plugin due to package incompabilities between ANNCSU Toolkit and QGIS.</source>
      <translation type="obsolete">Per utilizzare gli strumenti del plugin ANNCSU QGIS, è necessario installare ANNCSU Toolkit. ANNCSU Toolkit va installato separatamente dal plugin ANNCSU QGIS a causa di incompatibilità di pacchetti tra ANNCSU Toolkit e QGIS.</translation>
    </message>
    <message>
      <source>You can install ANNCSU Toolkit in any Python environment, but using a clean Conda environment or venv is recommended. For detailed installation instructions, see ANNCSU Toolkit GitHub (link below). After installation, set the location of your Python environment on Settings page.</source>
      <translation type="obsolete">È possibile installare ANNCSU Toolkit in qualsiasi ambiente Python, ma si consiglia di utilizzare un ambiente Conda o venv pulito. Per istruzioni dettagliate sull&apos;installazione, consultare il repository GitHub di ANNCSU Toolkit (link in basso). Dopo l&apos;installazione, impostare il percorso dell&apos;ambiente Python nella pagina Impostazioni.</translation>
    </message>
    <message>
      <source>ANNCSU-Manager is a QGIS plugin to update Italian official portal data database called ANNCSU.</source>
      <translation>ANNCSU-Manager è un plugin QGIS per aggiornare il database del portale ufficiale italiano denominato ANNCSU.</translation>
    </message>
    <message>
      <source>Sources and help</source>
      <translation>Risorse e assistenza</translation>
    </message>
    <message>
      <source>ANNCSU QGIS Plugin GitHub repository</source>
      <translation>Repository GitHub ANNCSU QGIS Plugin</translation>
    </message>
    <message>
      <source>ANNCSU Toolkit GitHub repository</source>
      <translation>Repository GitHub ANNCSU Toolkit</translation>
    </message>
    <message>
      <source>User manual / guide</source>
      <translation>Manuale utente / guida</translation>
    </message>
    <message>
      <source>License</source>
      <translation>Licenza</translation>
    </message>
    <message>
      <source>This QGIS plugin is licensed under GPL version 2.</source>
      <translation>Questo plugin QGIS è rilasciato con licenza GPL versione 2.</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- resources/ui/wizard_run_geocoders_page.ui +                  -->
  <!-- wizard_materialise_layers.ui + wizard_evaluate_geocode_page.ui-->
  <!-- wizard_reduce_clusters_page.ui + wizard_generate_project_page -->
  <!-- wizard_update_from_project.ui  (all class="WizardPage")       -->
  <!-- ============================================================ -->
  <context>
    <name>WizardPage</name>

    <!-- wizard_run_geocoders_page.ui -->
    <message>
      <source>Geocode</source>
      <translation>Geocodifica</translation>
    </message>
    <message>
      <source>Run configured geocoders</source>
      <translation>Esegui i geocoder configurati</translation>
    </message>
    <message>
      <source>Run geocoders</source>
      <translation>Esegui geocoder</translation>
    </message>
    <message>
      <source>Show details</source>
      <translation>Mostra dettagli</translation>
    </message>
    <message>
      <source>progress log</source>
      <translation>log di avanzamento</translation>
    </message>
    <message>
      <source>Clear</source>
      <translation>Cancella</translation>
    </message>

    <!-- wizard_materialise_layers.ui -->
    <message>
      <source>Materialize layers</source>
      <translation>Materializza layer</translation>
    </message>
    <message>
      <source>Include Fails</source>
      <translation>Includi fallimenti</translation>
    </message>
    <message>
      <source>Include Success</source>
      <translation>Includi successi</translation>
    </message>
    <message>
      <source>Include Out of Geofence</source>
      <translation>Includi fuori geofence</translation>
    </message>
    <message>
      <source>Include Geofence</source>
      <translation>Includi geofence</translation>
    </message>

    <!-- wizard_evaluate_geocode_page.ui -->
    <message>
      <source>Evaluate Geocode</source>
      <translation>Valuta geocodifica</translation>
    </message>
    <message>
      <source>Evalute geocoding results</source>
      <translation>Valuta i risultati della geocodifica</translation>
    </message>
    <message>
      <source>Load all (memory) layers</source>
      <translation>Carica tutti i layer (in memoria)</translation>
    </message>

    <!-- wizard_reduce_clusters_page.ui -->
    <message>
      <source>Reduce Clusters</source>
      <translation>Riduci cluster</translation>
    </message>
    <message>
      <source>Reduce ovelapped addresses mixig geocoding results</source>
      <translation>Riduci indirizzi sovrapposti combinando risultati geocodifica</translation>
    </message>
    <message>
      <source>Reduce overlapped clusters</source>
      <translation>Riduci cluster sovrapposti</translation>
    </message>
    <message>
      <source>Records: </source>
      <translation>Record: </translation>
    </message>
    <message>
      <source>Previous clusters:</source>
      <translation>Cluster precedenti:</translation>
    </message>
    <message>
      <source>Previous overlapped:</source>
      <translation>Sovrapposti precedenti:</translation>
    </message>
    <message>
      <source>Clusters:</source>
      <translation>Cluster:</translation>
    </message>
    <message>
      <source>Overlapped:</source>
      <translation>Sovrapposti:</translation>
    </message>
    <message>
      <source>Statistics (on all geocoders)</source>
      <translation>Statistiche (su tutti i geocoder)</translation>
    </message>
    <message>
      <source>Update geocoded ANNCSU table</source>
      <translation>Aggiorna tabella ANNCSU geocodificata</translation>
    </message>

    <!-- wizard_generate_project_page.ui -->
    <message>
      <source>Add layers to a project</source>
      <translation>Aggiungi layer a un progetto</translation>
    </message>
    <message>
      <source>Export geocoded layers to a Mergin project</source>
      <translation>Esporta layer geocodificati in un progetto Mergin</translation>
    </message>
    <message>
      <source>Add layers to a project</source>
      <translation>Aggiungi layer a un progetto</translation>
    </message>
    <message>
      <source>Mergin project:</source>
      <translation>Progetto Mergin:</translation>
    </message>
    <message>
      <source>geocoded</source>
      <translation>geocodificato</translation>
    </message>

    <!-- wizard_update_from_project.ui -->
    <message>
      <source>Update from project</source>
      <translation>Aggiorna da progetto</translation>
    </message>
    <message>
      <source>Merge modified project layers into geocoded results</source>
      <translation>Unisci layer del progetto modificati nei risultati geocodificati</translation>
    </message>
  </context>

  <!-- ============================================================ -->
  <!-- resources/ui/wizard_manager.ui (class="Wizard")              -->
  <!-- ============================================================ -->
  <context>
    <name>Wizard</name>

    <message>
      <source>Geocode</source>
      <translation>Geocodifica</translation>
    </message>
    <message>
      <source>Run configured geocoders</source>
      <translation>Esegui i geocoder configurati</translation>
    </message>
    <message>
      <source>Run geocoders</source>
      <translation>Esegui geocoder</translation>
    </message>
    <message>
      <source>Evaluate Geocode</source>
      <translation>Valuta geocodifica</translation>
    </message>
    <message>
      <source>Evalute geocoding results</source>
      <translation>Valuta i risultati della geocodifica</translation>
    </message>
    <message>
      <source>Load layers</source>
      <translation>Carica layer</translation>
    </message>
    <message>
      <source>Statistics</source>
      <translation>Statistiche</translation>
    </message>
    <message>
      <source>Preview</source>
      <translation>Anteprima</translation>
    </message>
    <message>
      <source>Select results</source>
      <translation>Seleziona risultati</translation>
    </message>
    <message>
      <source>Decide gocoding results accepting rule</source>
      <translation>Definisci le regole di accettazione dei risultati geocodifica</translation>
    </message>
    <message>
      <source>Update session</source>
      <translation>Aggiorna sessione</translation>
    </message>
    <message>
      <source>Update current session with geocoded results</source>
      <translation>Aggiorna la sessione corrente con i risultati geocodificati</translation>
    </message>
  </context>

</TS>
