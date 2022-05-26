SELECT
    M.match_id,
    MP.profile_id,
    MP.slot,
    MP.civ,
    MP.won,
    MP.rating,
    MP.country,
    M.map_type,
    M.finished
FROM
    matches AS M
    INNER JOIN matches_players AS MP
    ON M.match_id = MP.match_id
WHERE m.leaderboard_id = %(ladder)s