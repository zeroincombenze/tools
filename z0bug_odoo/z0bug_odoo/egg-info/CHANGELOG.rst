2.0.17 (2024-02-27)
~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: minor improvements
* [FIX] TestEnv: crash if no account.journal in data
* [IMP] Data with date range 2024

2.0.16 (2024-02-17)
~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: nested +multi fields with Odoo cmd

2.0.15 (2024-01-27)
~~~~~~~~~~~~~~~~~~~

* [IMP] Documentation typo corrections
* [IMP] Date range file .xlsx for TestEnv
* [IMP] TestEnv: local data dir new rules
* [FIX] TestEnv: 3 level xref, sometime fails with "_" in module name
* [FIX] TestEnv: caller environment more than 1 level
* [FIX] TestEnv: sometime is_action() fails
* [FIX] TestEnv: wizard active model
* [FIX] TestEnv: wizard module name is current module under test
* [IMP] TestEnv: binding model in view for Odoo 11.0+
* [IMP] TestEnv: write with xref can update xref id
* [IMP] TestEnv: warning if no setUp() declaration
* [IMP] TestEnv: resource_download, now default filed name is "data"


2.0.14 (2023-12-22)
~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: commit odoo data became internal feature
* [IMP] TestEnv: test on model asset.asset
* [IMP] TestEnv: detail external reference coding free
* [IMP] TestEnv: empty currency_id is set with company currency
* [FIX] TestEnv: minor fixes in mixed environment excel + zerobug
* [FIX] TestEnv: sometimes external.KEY did not work
* [FIX] TestEnv: 3 level xref fails when module ha "_" in its name
* [IMP] _check4deps.py: documentation clearing

2.0.13 (2023-12-01)
~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: now you can declare you own source data directory
* [IMP] TestEnv: file account.account.xlsx with l10n_generic_oca + some useful records
* [IMP] TestEnv: file account.tax.xlsx with some italian taxes for l10n_generic_oca
* [IMP] TestEnv: simple expression for data value

2.0.12 (2023-09-12)
~~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: validate_records with 2 identical template records

2.0.10 (2023-07-02)
~~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: new feature, external reference with specific field value
* [REF] TestEnv: tomany casting refactoring

2.0.9 (2023-06-24)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: sometimes, validate_records does not match many2one fields
* [FIX[ TestEnv: sometime crash in wizard on Odoo 11.0+ due inexistent ir.default
* [FIX] TestEnv: default value in wizard creation, overlap default function
* [FIX] TestEnv: record not found for xref of other group
* [IMP] TestEnv: resource_bind is not more available: it is replaced by resource_browse

2.0.8 (2023-04-26)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: multiple action on the same records

2.0.7 (2023-04-08)
~~~~~~~~~~~~~~~~~~

* [NEW] TestEnv: assertion counter
* [IMP] TestEnv: is_xref recognizes dot name, i.e "zobug.external.10"
* [IMP] TestEnv: the field <description> is not mode key (only acount.tax)
* [IMP] TestEnv: 3th level xref may be a many2one field type

2.0.6 (2023-02-20)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: _get_xref_id recognize any group
* [FIX] TestEnv: datetime field more precise (always with time)
* [FIX] TestEnv: resource_make / resource_write fall in crash if repeated on headr/detail models
* [NEW] TestEnv: 2many fields accepts more xref values
* [IMP] TestEnv: debug message with more icons and more readable
* [IMP] TestEnv: cast_types with formatting for python objects
* [IMP] TestEnv: validate_record now uses intelligent algorithm to match pattern templates and records

2.0.5 (2023-01-25)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: in some rare cases, wizard crashes
* [NEW] TestEnv: get_records_from_act_windows()
* [IMP] TestEnv: resource_make now capture demo record if available
* [IMP] TestEnv: resource is not required for declared xref
* [IMP] TestEnv: self.module has all information about current testing module
* [IMP] TestEnv: conveyance functions for all fields (currenly jsust for account.payment.line)
* [IMP] TestEnv: fields many2one accept object as value
* [IMP] TestEnv: function validate_records() improvements
* [FIX] TestEnv: company_setup, now you can declare bank account
* [IMP] TesEnv: minor improvements

2.0.4 (2023-01-13)
~~~~~~~~~~~~~~~~~~

* [FIX] TestEnv: resource_create does not duplicate record
* [FIX] TestEnv: resource_write after save calls write() exactly like Odoo behavior
* [NEW] TestEnv: new function field_download()
* [NEW] TestEnv: new function validate_records()
* [IMP] TestEnv: convert_to_write convert binary fields too
* [IMP] TestEnv: minor improvements

2.0.3 (2022-12-29)
~~~~~~~~~~~~~~~~~~

* [IMP] TestEnv: more debug messages
* [IMP] TestEnv: more improvements
* [FIX] TestEnv: sometime crashes if default use context
* [FIX] TestEnv: bug fixes

2.0.2 (2022-12-09)
~~~~~~~~~~~~~~~~~~

* [FIX] Automatic conversion of integer into string for 'char' fields
* [IMP] TestEnv

2.0.1.1 (2022-11-03)
~~~~~~~~~~~~~~~~~~~~

* [REF] clone_oca_dependencies.py

2.0.1 (2022-10-20)
~~~~~~~~~~~~~~~~~~

* [IMP] Stable version

2.0.0.1 (2022-10-15)
~~~~~~~~~~~~~~~~~~~~

* [FIX] Crash in travis

2.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~

* [REF] Stable version
