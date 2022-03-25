SELECT
	profile_id,
	ROUND(AVG(rating)) AS elo
FROM
	matches_players AS MP
	INNER JOIN matches AS M
	ON M.match_id=MP.match_id
WHERE
	M.leaderboard_id = 3
	AND MP.rating IS NOT NULL
GROUP BY
	profile_id
HAVING
	AVG(rating) >0
ORDER BY
	ROUND(AVG(rating)) DESC