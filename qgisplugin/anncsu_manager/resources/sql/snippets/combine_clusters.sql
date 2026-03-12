WITH herev7_clusters AS (
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
	mapbox_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_mapbox
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	mapbox_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			same_ids_from_mapbox A,
			mapbox_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_y_COMUNE
	),
	same_ids_from_google AS (
		SELECT *
		FROM
			GoogleV3_success A,
			mapbox_clustered_addresses B
		WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
	),
	google_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_google
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	google_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			same_ids_from_google A,
			google_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_y_COMUNE
	),
	same_ids_from_whereabouts AS (
		SELECT *
		FROM
			WhereAbouts_success A,
			google_clustered_addresses B
		WHERE A.PROGRESSIVO_ACCESSO = B.PROGRESSIVO_ACCESSO
	),
	whereabouts_clusters AS (
		SELECT
		    COORD_X_COMUNE,
		    COORD_Y_COMUNE,
		    COUNT(*) AS record_count
		FROM same_ids_from_whereabouts
		GROUP BY COORD_X_COMUNE, COORD_Y_COMUNE
		HAVING record_count > 1
		ORDER BY record_count DESC
	),
	whereabouts_clustered_addresses AS (
		SELECT
			A.PROGRESSIVO_ACCESSO,
			A.COORD_X_COMUNE,
			A.COORD_Y_COMUNE
		FROM
			same_ids_from_whereabouts A,
			whereabouts_clusters B
		WHERE
			A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
			A.COORD_Y_COMUNE = B.COORD_y_COMUNE
	)
select * from whereabouts_clustered_addresses;