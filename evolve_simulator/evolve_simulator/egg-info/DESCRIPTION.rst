Evolve Simulator is a local web server that behaves like the Evolve (certdoc.it)
e-invoice web service, so the Odoo modules sending e-invoices through Evolve
(l10n_it_fatturapa_evolve, l10n_it_einvoice_send2sdi) can be developed and tested
without a real account and without sending anything to the Italian SdI.

Features:

* Same REST API as Evolve: **Cerca** (search), **Salva** (upload) and **Recupera** (download)
* Same authentication: AES encrypted Bearer token checked against the Client Key
* Three archives: sent (3, staging), out (1, delivered) and in (2, purchase invoices)
* Simulated SdI workflow with configurable delays and outcome:
  delivered, discarded, not delivered, accepted or refused by PA
* Duplicate invoices, invalid XML files and self invoices (TD17, TD18, TD19) handled
  like the real service
* Fault injection: HTTP 500, generic error and authentication error
* Web page to watch the archives, change document states and receive purchase invoices
