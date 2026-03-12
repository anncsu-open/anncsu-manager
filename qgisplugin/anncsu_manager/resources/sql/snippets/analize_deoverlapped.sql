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
	)
select * from deoverlapped_clustered_addresses;



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
	)
select * from deoverlapped_clusters;
