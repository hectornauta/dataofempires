SELECT
    M.match_id,
    MP.slot,
    MP.civ,
    MP.won,
    MP.rating,
    MP.country,
    M.map_type
FROM
    matches AS M
    INNER JOIN matches_players AS MP
    ON M.match_id = MP.match_id