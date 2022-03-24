SELECT
    M.match_id,
    MP.slot,
    MP.civ,
    MP.won,
    MP.rating,
    MP.country,
    MP.team,
    M.map_type
FROM
    matches AS M
    INNER JOIN matches_players AS MP
    ON M.match_id = MP.match_id
WHERE m.leaderboard_id = 4
AND M.num_players = 4
AND NOT EXISTS(
    SELECT M2.MATCH_ID
    FROM MATCHES AS M2
        INNER JOIN MATCHES_PLAYERS AS MP2
        ON M2.MATCH_ID=MP2.MATCH_ID
    WHERE M2.MATCH_ID=M.match_id
    AND (
        MP2.rating IS NULL
        OR MP2.rating <1000
        )
    )