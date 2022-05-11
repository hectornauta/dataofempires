UPDATE
    matches_players
SET
    civ = 43
FROM
    matches
WHERE matches.match_id = matches_players.match_id
AND
    civ = 20
AND
    started<1651086000