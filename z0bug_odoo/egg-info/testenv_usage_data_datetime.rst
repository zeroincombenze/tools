Date and Datetime value are managed in special way.
They are processed by ``compute_date()`` function (read below).
You can issue a single value or a 2 values list, 1st is the date,
2nd is the reference date.

::

    self.resource_create(
        "res.partner",
        xref="z0bug.partner1",
        values={
             {
                ...
                "activity_date_deadline": "####-1>-##",    # Next month
                "signup_expiration": "###>-##-##",         # Next year
                "date": -1,                                # Yesterday
                "last_time_entries_checked":
                    [+2, another_date],                    # 2 days after another day
                "message_last_post": "2023-06-26",         # Specific date, ISO format
            }
        }
    )