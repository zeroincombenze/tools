Avviare il simulatore::

    evolve-simulator -p 5000

Le credenziali predefinite sono Client ID ``test.odoo@zeroincombenze.it``,
Client Key ``0123456789abcdef0123456789abcdef`` e Company ID ``93``; per usarne altre::

    evolve-simulator -p 5000 -c odoo -k 0123456789abcdef0123456789abcdef -C 1

Opzioni:

* ``-H``, ``--host``: indirizzo di ascolto (predefinito 127.0.0.1)
* ``-p``, ``--port``: porta TCP (predefinita 5000)
* ``-d``, ``--database-url``: URL SQLAlchemy (predefinito il file sqlite ``evolve_simulator.db`` nella cartella corrente)
* ``-c``, ``--client-id`` / ``-k``, ``--client-key`` / ``-C``, ``--company-id``: credenziali del cliente
* ``--sdi-delay`` / ``--outcome-delay``: secondi prima della consegna allo SdI e prima dell'esito (predefiniti 10 / 60)
* ``--outcome``: esito SdI predefinito (predefinito "Ricevuta di consegna")
* ``--pid-file``: file in cui il simulatore scrive il proprio pid (rimosso all'uscita);
  fermare il simulatore con ``kill $(cat <pid-file>)``
* ``--filestore``: cartella dei file xml da ricevere come fatture passive (vedi sotto)
* ``-n``, ``--no-auth``: non verificare il token di autenticazione

Ogni opzione si può impostare anche con la variabile d'ambiente ``EVOLVE_SIM_<NOME>``,
ad esempio ``EVOLVE_SIM_SDI_DELAY=0``.

Configurare poi il canale SdI "Evolve (Web service)" di Odoo:

* Sender URL: ``http://127.0.0.1:5000/rest/api/v1/``
* Client ID, Client Key e Company ID of client: gli stessi valori passati al simulatore
* Archive # to send / sent / to receive: 3 / 1 / 2
* Exchange Hub IP: qualsiasi valore

Aprire ``http://127.0.0.1:5000/`` per vedere gli archivi. Dalla pagina si può:

* scegliere l'esito di un documento prima della risposta dello SdI, o forzare il passo successivo
* cambiare lo stato di un documento consegnato
* inserire una fattura passiva nell'archivio ricevute
* cambiare tempi, esito predefinito e simulazione guasti nella scheda Settings
* leggere il registro di tutte le chiamate ricevute

Per simulare fatture passive senza la pagina web, avviare il simulatore con
``--filestore <cartella>`` e copiare i file xml FatturaPA in ``<cartella>``: alla
richiesta successiva ogni file ``*.xml`` viene inserito nell'archivio ricevute,
come ricevuto dallo SdI, e spostato in ``<cartella>/done``.
