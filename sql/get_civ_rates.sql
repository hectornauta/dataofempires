SELECT
    id,
    name,
    nombre,
    winrate,
    pickrate,
    ladder_cat
FROM civ_rates
WHERE ladder_cat = %(ladder)s