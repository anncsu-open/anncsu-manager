update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_mapbox S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;

update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_google S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;

update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_whereabouts S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;


update deoverlapped_geocoded_anncsu
SET
    COORD_X_COMUNE = S.COORD_X_COMUNE,
    COORD_Y_COMUNE = S.COORD_Y_COMUNE
FROM
    solved_by_azuremaps S
WHERE
    deoverlapped_geocoded_anncsu.PROGRESSIVO_ACCESSO = S.PROGRESSIVO_ACCESSO;