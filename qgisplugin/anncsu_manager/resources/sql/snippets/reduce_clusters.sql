CREATE OR REPLACE TABLE solved_by_mapbox AS (
WITH
    herev7_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM main.HereV7_success
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	herev7_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			main.HereV7_success A,
			herev7_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_y_COMUNE
	),
	same_ids_from_mapbox AS (
		SELECT *
		FROM
			MapBox_success A,
			herev7_clustered_addresses B
		WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
	),
	_solved_by_mapbox AS (
		SELECT
            PROGRESSIVO_ACCESSO,
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_mapbox
		GROUP BY PROGRESSIVO_ACCESSO, COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count = 1
    )
    SELECT * FROM _solved_by_mapbox
);


CREATE OR REPLACE TABLE solved_by_google AS (
WITH
    deoverlapped_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM deoverlapped_geocoded_anncsu
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	deoverlapped_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			deoverlapped_geocoded_anncsu A,
			deoverlapped_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_Y_COMUNE
	),
	same_ids_from_google AS (
		SELECT *
		FROM
			GoogleV3_success A,
			deoverlapped_clustered_addresses B
		WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
	),
	_solved_by_google AS (
		SELECT
            PROGRESSIVO_ACCESSO,
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_google
		GROUP BY PROGRESSIVO_ACCESSO, COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count = 1
    )
    SELECT * FROM _solved_by_google
);

CREATE OR REPLACE TABLE solved_by_whereabouts AS (
WITH
    deoverlapped_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM deoverlapped_geocoded_anncsu
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	deoverlapped_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			deoverlapped_geocoded_anncsu A,
			deoverlapped_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_Y_COMUNE
	),
	same_ids_from_whereabouts AS (
		SELECT *
		FROM
			Whereabouts_success A,
			deoverlapped_clustered_addresses B
		WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
	),
	_solved_by_whereabouts AS (
		SELECT
            PROGRESSIVO_ACCESSO,
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_whereabouts
		GROUP BY PROGRESSIVO_ACCESSO, COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count = 1
    )
    SELECT * FROM _solved_by_whereabouts
);

CREATE OR REPLACE TABLE solved_by_azuremaps AS (
WITH
    deoverlapped_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM deoverlapped_geocoded_anncsu
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	deoverlapped_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			deoverlapped_geocoded_anncsu A,
			deoverlapped_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_Y_COMUNE
	),
	same_ids_from_azuremaps AS (
		SELECT *
		FROM
			AzureMaps_success A,
			deoverlapped_clustered_addresses B
		WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
	),
	_solved_by_azuremaps AS (
		SELECT
            PROGRESSIVO_ACCESSO,
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_azuremaps
		GROUP BY PROGRESSIVO_ACCESSO, COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count = 1
    )
    SELECT * FROM _solved_by_azuremaps
);

