
==================
z0bug_odoo 0.2.3.9
==================



|Maturity| |Build Status| |Coverage Status| |license gpl|




Overview
========

zerobug
=======

Zeroincombenze® continuous testing for odoo
-------------------------------------------

This package aim to easily create odoo tests.

*z0bug_odoo* is built on follow concepts:

* Odoo version independent
* Read-made database
* Quality Check Id

qci
---

+-------------+-----------------------------------------------------------------------------------+
| qci         | description                                                                       |
+-------------+-----------------------------------------------------------------------------------+
| pay.SCT     | Credit Transfer payment / Pagamento bonifico                                      |
+-------------+-----------------------------------------------------------------------------------+
| pay.RB      | RiBA payment / Pagamento RiBA (IT)                                                |
+-------------+-----------------------------------------------------------------------------------+
| pay.SDD     | Sepa Direct Debit / Pagamento Sepa DD                                             |
+-------------+-----------------------------------------------------------------------------------+
| part.pt1    | Partner with one date payment / Cliente con pagamento in unica soluzione          |
+-------------+-----------------------------------------------------------------------------------+
| part.pt2    | Partner with multiple date payment / Cliente con pagamento di più scadenze        |
+-------------+-----------------------------------------------------------------------------------+
| part.it     | Local partner (Italy) / Cliente italiano                                          |
+-------------+-----------------------------------------------------------------------------------+
| part.eu     | EU partner / Cliente intraUE                                                      |
+-------------+-----------------------------------------------------------------------------------+
| part.xeu    | Extra-EU partner / Cliente extraUE                                                |
+-------------+-----------------------------------------------------------------------------------+
| acc.rc      | Reverse Charge                                                                    |
+-------------+-----------------------------------------------------------------------------------+
| acc.sp      | Split Payment                                                                     |
+-------------+-----------------------------------------------------------------------------------+
| part.PA     | Partne is PA                                                                      |
+-------------+-----------------------------------------------------------------------------------+
| acc.uVAT    | Full Undeductible VAT / IVA totalmente indetraibile                               |
+-------------+-----------------------------------------------------------------------------------+
| acc.puVAT   | Undeductible VAT / IVA parzialmente indetraibile                                  |
+-------------+-----------------------------------------------------------------------------------+
| inv.asset   | Invoice with asset/Fattura di beni strumentali                                    |
+-------------+-----------------------------------------------------------------------------------+
| inv.asalem  | Corrispettivi misti                                                               |
+-------------+-----------------------------------------------------------------------------------+
| inv.asalex  | Corrispettivi ripartiti (ventilazione)                                            |
+-------------+-----------------------------------------------------------------------------------+
| acc.uRB     | Insoluto RiBA                                                                     |
+-------------+-----------------------------------------------------------------------------------+
| invo.sp     | Sale invoice with split payment / Fattura di vendita con split-payment            |
+-------------+-----------------------------------------------------------------------------------+
| invo.rc     | Sale invoice with reverse charge / Fattura di vendita con reverse charge          |
+-------------+-----------------------------------------------------------------------------------+
| invo.eu     | Sale invoice to EU partner / Fattura di vendita intraUE                           |
+-------------+-----------------------------------------------------------------------------------+
| invo.xeu    | Sale invoice to xEU partner / Fattura di vendita extraUE                          |
+-------------+-----------------------------------------------------------------------------------+
| invo.li     | Sale invoice with lettera di intento / Fattura di vendita lettera di intento      |
+-------------+-----------------------------------------------------------------------------------+
| invo.wht    | Sale invoice with withholding / Fattura di vendita ritenuta d'acconto             |
+-------------+-----------------------------------------------------------------------------------+
| invo.enas   | Sale invoice with enasarco / Fattura di vendita con ensarco                       |
+-------------+-----------------------------------------------------------------------------------+
| invi.sp     | Purchase invoice with split payment / Fattura di acquisto con split-payment       |
+-------------+-----------------------------------------------------------------------------------+
| invi.rc     | Purchase invoice with reverse charge / Fattura di acquisto con reverse charge     |
+-------------+-----------------------------------------------------------------------------------+
| invi.eu     | Purchase invoice from EU partner / Fattura di acquisto intraUE                    |
+-------------+-----------------------------------------------------------------------------------+
| invi.xeu    | Purchase invoice fromxEU partner / Fattura di acquisto extraUE                    |
+-------------+-----------------------------------------------------------------------------------+
| invi.li     | Purchase invoice with lettera di intento / Fattura di acquisto lettera di intento |
+-------------+-----------------------------------------------------------------------------------+
| invi.wht    | Purchase invoice with withholding / Fattura da fornitore con ritenuta d'acconto   |
+-------------+-----------------------------------------------------------------------------------+
| invi.enas   | Purchase invoice with enasarco / Fattura da fornitore con ensarco                 |
+-------------+-----------------------------------------------------------------------------------+
| einvo.ind   | E-invoice to individual / Fattura elettronica a privato                           |
+-------------+-----------------------------------------------------------------------------------+
| einvo.stamp | E-invoice with virtual stamp / Fattura elettronica con bollo virtuale             |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat3   | Sale invoice with vat 22% / Fattura di vendita con IVA 22%                        |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat2   | Sale invoice with vat 10% / Fattura di vendita con IVA 10%                        |
+-------------+-----------------------------------------------------------------------------------+
| invo.vat1   | Sale invoice with vat 4% / Fattura di vendita con IVA 4%                          |
+-------------+-----------------------------------------------------------------------------------+
| invo.N1     | Sale invoice with out of vat / Fattura di vendita con FC art. 15                  |
+-------------+-----------------------------------------------------------------------------------+




partner qci
-----------

+----------------------+-------------------------------------+-------------------+----------------------------+
| id                   | name                                | side              | icq                        |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_1  | Prima Distribuzione S.p.A.          | customer/supplier | icq_0002 icq_0006 icq_pa11 |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_10 | Notaio Libero Jackson               | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_11 | Nebula Caffè S.p.A.                 | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_12 | Freie Universität Berlin            | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_13 | Axelor GmbH                         | customer          | icq_pa12                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_14 | SS Carrefur                         | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_15 | Ente Porto                          | customer          | icq_0002 icq_pa14 icq_pa16 |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_16 | Viking Office Depot Italia s.r.l.   | customer/supplier |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_17 | Vexor BV                            | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_2  | Agro Latte Due  s.n.c.              | customer          | icq_0002 icq_0007          |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_3  | Import Export Trifoglio s.r.l.      | customer          | icq_0001 icq_0006          |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_4  | Delta 4 s.r.l.                      | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_5  | Five Stars Hotel                    | supplier          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_6  | Esa Electronic S.p.A                | customer          | icq_0003                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_7  | Università della Svizzera Italiana  | customer          | icq_pa13                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_8  | Global Solution s.r.l.              | customer          | icq_pa15                   |
+----------------------+-------------------------------------+-------------------+----------------------------+
| z0bug.res_partner_9  | Mario Rossi                         | customer          |                            |
+----------------------+-------------------------------------+-------------------+----------------------------+





|

Features
--------

Data to use in tests are store in csv files in data directory.
File names are tha name of the models (table) with characters '.' (dot) replaced by '_' (underscore)

Header of file must be the names of table fields.

Rows can contains value to store or Odoo external reference or macro.

For type char, text, html, int, float, monetary: value are constants inserted as is.

For type many2one: value may be an integer (record id) or Odoo external reference (format "module.name").

For type data, datetime: value may be a constant or relative date





|

Usage
=====

Code example:
::

    # -*- coding: utf-8 -*-
    #
    # Copyright 2017-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
    #
    # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
    #
    from z0bug_odoo import test_common

    class ExampleTest(test_common.SingleTransactionCase):

        def setUp(self):
            super(ExampleTest, self).setUp()
            self.set_test_company()
            # Assure 2 res.partner records
            self.build_model_data('res.partner', ['base.res_partner_2',
                                                  'z0bug.res_partner_2'])

        def test_example(self):
            partner = self.browse_ref(self.ref612('base.res_partner_2'))
            partner = self.browse_ref(self.ref612('z0bug.res_partner_2'))




Following function are avaiable.

`set_test_company(self)`

Create or update company to test and assign it to current user as default company. This function should be put in setUp().


`create_id(model, values)`

Create a record of the model and return id (like Odoo 7.0- API).


`create_rec(model, values)`

Create a record of the model and return record itself (like Odoo 8.0+ API).


`write_rec(model, id, values)`

Write the record of model with passed id and return record itself.


`browse_rec(model, id)`

Return the record of model with passed id.


`env612(model)`

Return env/pool of model (like pool of Odoo 7.0- API or env of Odoo 8.0+ API)


`ref_value(model, xid)`

Return values of specific xid. If xid is Odoo standard xid, i.e. "base.res_partner_1",
return current record values that may be different from original demo data.
If xid begins with "z0bug." return default values even if they are update form previous tests.
See valid xid from this document.


`build_model_data(model, xrefs)`

Assure records of model with reference list xrefs.
For every item of xrefs, a record is created o updated.
Function ref_value is used to retrieve values of each record (see above).


::

    # -*- coding: utf-8 -*-
    #
    # Copyright 2017-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
    #
    # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
    #
    from zerobug import Z0testOdoo

    class ExampleTest():

        def test_example(self):
            res = Z0bugOdoo().get_test_values(
                'res.partner','z0bug.res_partner_1')


`get_test_values(self, model, xid)`

Return values of specific xid. If xid is Odoo standard xid, i.e. "base.res_partner_1",
return empty dictionary.
If xid begins with "z0bug." return default values to use in test.
This function is used by `ref_value` to get default values.
Warning: returned values may contain some field of uninstalled module.


`get_data_file(self, model, csv_fn)`

Load data of model from csv_fn. Internal use only.


|
|

Getting started
===============


|

Installation
------------

For stable version:

`pip install z0bug_odoo`

For current version:

`cd $HOME`
`git@github.com:zeroincombenze/tools.git`
`cd $HOME/tools`
`./install_tools.sh`


|
|

Credits
=======

Copyright
---------

SHS-AV s.r.l. <https://www.shs-av.com/>


Contributors
------------

* Antonio M. Vigliotti <info@shs-av.com>


|

This module is part of tools project.

Last Update / Ultimo aggiornamento: 2020-07-22

.. |Maturity| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/tools.svg?branch=0.2.3.9
    :target: https://travis-ci.org/zeroincombenze/tools
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/tools/badge.svg?branch=0.2.3.9
    :target: https://coveralls.io/github/zeroincombenze/tools?branch=0.2.3.9
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.9/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/tools/branch/0.2.3.9
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-2.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/0.2.3.9/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-2.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/0.2.3.9/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-2.svg
    :target: https://erp2.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/tools/branch/0.2.3.9/graph/badge.svg
    :target: https://codecov.io/gh/OCA/tools/branch/0.2.3.9
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
   :target: https://www.zeroincombenze.it/
   :alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png
.. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png
.. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png
.. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png
.. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png
.. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png
.. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png
.. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png
.. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png
.. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png
.. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
.. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
.. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
.. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif
   :target: https://t.me/axitec_helpdesk


