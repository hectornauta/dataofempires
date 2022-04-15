DELETE FROM   
    players AS P1
WHERE
    P1.finished<
    (
        SELECT
            MAX(P2.finished)
        FROM
            players AS P2
        WHERE
            P2.profile_id=P1.profile_id
        GROUP BY
            P2.profile_id
    )