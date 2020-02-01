users_sql = """
        SELECT
            user_id
        FROM
            public.user_rates
        WHERE
            rate IS NOT NULL
        GROUP BY
            user_id
        HAVING
            count(image_id) >= 5
        """


image_sql = """
        SELECT 
            image_id
        FROM
            public.user_rates
        WHERE
            rate IS NOT NULL
            AND
            user_id IN (
                SELECT
                    user_id
                FROM
                    public.user_rates
                WHERE
                    rate IS NOT NULL
                GROUP BY
                    user_id
                HAVING
                    count(image_id) >= 5
            )
        GROUP BY
            image_id
        HAVING
            count(user_id) >= 2
    """

rate_matrix = """
        SELECT
            image_id, user_id, rate
        FROM
            public.user_rates
        WHERE
            rate IS NOT NULL
    """

insert_query = """
        INSERT INTO public.recommendations
            VALUES (DEFAULT, %s, %s, %s, CURRENT_DATE);"""