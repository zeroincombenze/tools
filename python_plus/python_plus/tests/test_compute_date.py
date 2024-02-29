# -*- coding: utf-8 -*-
# Copyright (C) 2015-2024 SHS-AV s.r.l. (<http://www.zeroincombenze.org>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
    Python-plus Regression Test Suite
"""
from __future__ import print_function, unicode_literals

import sys
from datetime import date, datetime

from python_plus import compute_date
from zerobug import z0test

MODULE_ID = 'python_plus'
TEST_FAILED = 1
TEST_SUCCESS = 0

__version__ = "2.0.11"


def version():
    return __version__


class RegressionTest:

    def test_01(self):
        for (res, text_date) in (
            (None, None),
            (False, False),
            ('2021-06-22', '2021-06-22'),
            (str(date.today()), '####-##-##'),
        ):
            self.assertEqual(res,
                             compute_date(text_date),
                             msg_info="compute_date(%s)" % text_date)
        refdate = datetime.strptime('2022-01-02', '%Y-%m-%d')
        for (res, text_date) in (
            (None, None),
            (False, False),
            ('2021-06-22', '2021-06-22'),
            ('2022-01-02', '####-##-##'),
            ('2022-01-02', '0000-00-00'),
            ('2022-01-03', '+1'),
            ('2022-01-04', 2),
            ('2022-01-01', '-1'),
            ('2022-01-01', -1),
            ('2021-12-03', '-30'),
            ('2021-01-02', '<###-##-##'),
            ('2023-01-02', '###>-##-##'),
            ('2023-01-02', '#>-##-##'),
            ('2019-02-28', '<3-02-99'),
            ('2019-02-28', '<003-02-99'),
            ('2019-12-31', '<3-12-99'),
            ('2019-03-03', '<3-#>-31'),
            ('2024-01-02', '2>-##-##'),
            ('2024-01-02', '002>-##-##'),
            ('2021-12-18', '####-##-<15'),
            ('2021-12-02', '####-<#-##'),
            ('2020-12-02', '####-<#-<365'),
            ('2021-12-31 00:00:00', '####-<1-99 00:00:00'),
            ('2021-12-31T23:59:59', '####-<1-99T23:59:59'),
        ):
            self.assertEqual(res,
                             compute_date(text_date, refdate=refdate),
                             msg_info="compute_date(%s)" % text_date)


# Run main if executed as a script
if __name__ == "__main__":
    exit(
        z0test.main_local(
            z0test.parseoptest(sys.argv[1:], version=version()), RegressionTest
        )
    )


