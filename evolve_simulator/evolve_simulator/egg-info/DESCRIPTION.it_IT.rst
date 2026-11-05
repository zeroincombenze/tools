Evolve Simulator è un web server locale che si comporta come il servizio web di
fatturazione elettronica Evolve (certdoc.it); i moduli Odoo che inviano le fatture
elettroniche tramite Evolve (l10n_it_fatturapa_evolve, l10n_it_einvoice_send2sdi)
possono così essere sviluppati e collaudati senza un account reale e senza inviare
nulla al Sistema di Interscambio.

Funzionalità:

* Stessa API REST di Evolve: **Cerca**, **Salva** (caricamento) e **Recupera** (scaricamento)
* Stessa autenticazione: token Bearer cifrato AES verificato con la Client Key
* Tre archivi: inviati (3, in attesa), emesse (1, consegnate) e ricevute (2, fatture passive)
* Flusso SdI simulato con tempi ed esito configurabili:
  consegnata, scartata, non consegnata, accettata o rifiutata dalla PA
* Fatture duplicate, file XML non validi e autofatture (TD17, TD18, TD19) gestiti
  come nel servizio reale
* Simulazione guasti: HTTP 500, errore generico ed errore di autenticazione
* Pagina web per vedere gli archivi, cambiare lo stato dei documenti e ricevere fatture passive
