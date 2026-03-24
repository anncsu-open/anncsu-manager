-- Step 1
-- duplicate geocoded_anncsu into deoverlapped_geocoded_anncsu
CREATE OR REPLACE TABLE deoverlapped_geocoded_anncsu AS
SELECT * FROM geocoded_anncsu;

-- Step 2
-- Start with that table (HereV7_success) that contains the minimum number of duplications.
-- This query identifies records from the HereV7_success table that have duplicate coordinates
-- (COORD_X_COMUNE, COORD_Y_COMUNE) and then checks if those records can be uniquely matched with
-- records in the MapBox_success table based on the PROGRESSIVO_ACCESSO field.
-- The final result is stored in the solved_by_mapbox table, which contains only those records
-- that have a unique match in the MapBox_success table.
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

-- Step 3
-- Update the coordinates in the deoverlapped_geocoded_anncsu table with the unique matches found in the solved_by_mapbox table.
update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_mapbox S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;

-- Step 4
-- Create a table with the unique matches found in the GoogleV3_success table.
-- starting from the deoverlapped_geocoded_anncsu table, which has been updated
-- with the unique matches from the MapBox_success table.
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


-- Step 5
-- Update the coordinates in the deoverlapped_geocoded_anncsu table with the unique matches found in the solved_by_google table.
update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_google S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;

-- step 6
-- to deduplicate using whereaabouts need to mix success and fails from whereabouts
-- because thay are are discriminated by score that could not be useful for deduplication
CREATE OR REPLACE TABLE WhereAbouts_mixed AS (
SELECT * FROM WhereAbouts_success
UNION ALL
SELECT * FROM WhereAbouts_fails
);

-- Step 7
-- Create a table with the unique matches found in the WhereAbouts_mixed table.
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
			WhereAbouts_mixed A,
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

-- Step 8
-- Update the coordinates in the deoverlapped_geocoded_anncsu table with the unique
-- matches found in the solved_by_whereabouts table.
update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_whereabouts S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;

-- Step 9
-- Create a table with the unique matches found in the AzureMaps_success table.
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

-- Step 10
-- Update the coordinates in the deoverlapped_geocoded_anncsu table with the
-- unique matches found in the solved_by_azuremaps table.
update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_azuremaps S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;

-- Step 11 (checking)
-- After all the updates, check if there are still duplicate coordinates in the deoverlapped_geocoded_anncsu table.
-- This query identifies any remaining duplicate coordinates in the deoverlapped_geocoded_anncsu table
-- after all the updates have been applied.
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

-- Step 12 (checking)
-- Create a table with the records that still have duplicate coordinates after all the updates.
CREATE OR REPLACE TABLE remaining_duplicates AS (
    SELECT
        A.*,
        B.ODONIMO,
        B.CIVICO,
        B.ESPONENTE
    FROM
        remaining_clusters A,
        deoverlapped_geocoded_anncsu B
    WHERE
        A.COORD_X_COMUNE = B.COORD_X_COMUNE AND
        A.COORD_Y_COMUNE = B.COORD_Y_COMUNE
);


