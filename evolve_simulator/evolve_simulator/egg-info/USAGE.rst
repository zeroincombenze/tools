Start the simulator::

    evolve-simulator -p 5000

Default credentials are Client ID ``test.odoo@zeroincombenze.it``,
Client Key ``0123456789abcdef0123456789abcdef`` and Company ID ``93``; to use others::

    evolve-simulator -p 5000 -c odoo -k 0123456789abcdef0123456789abcdef -C 1

Options:

* ``-H``, ``--host``: bind address (default 127.0.0.1)
* ``-p``, ``--port``: TCP port (default 5000)
* ``-d``, ``--database-url``: SQLAlchemy URL (default sqlite file ``evolve_simulator.db`` in current directory)
* ``-c``, ``--client-id`` / ``-k``, ``--client-key`` / ``-C``, ``--company-id``: client credentials
* ``--sdi-delay`` / ``--outcome-delay``: seconds before SdI delivery and before outcome (default 10 / 60)
* ``--outcome``: default SdI outcome (default "Ricevuta di consegna")
* ``--pid-file``: file where the simulator writes its pid (removed at exit);
  stop the simulator with ``kill $(cat <pid-file>)``
* ``--filestore``: directory of xml files to receive as inbound invoices (see below)
* ``-n``, ``--no-auth``: do not check the authentication token

Every option can also be set by an environment variable ``EVOLVE_SIM_<NAME>``,
e.g. ``EVOLVE_SIM_SDI_DELAY=0``.

Then set the Odoo SdI channel "Evolve (Web service)":

* Sender URL: ``http://127.0.0.1:5000/rest/api/v1/``
* Client ID, Client Key and Company ID of client: same values passed to the simulator
* Archive # to send / sent / to receive: 3 / 1 / 2
* Exchange Hub IP: any value

Open ``http://127.0.0.1:5000/`` to watch the archives. From the page you can:

* choose the outcome of a document before SdI replies, or force the next step
* change the state of a delivered document
* put a purchase invoice in the in archive
* change delays, default outcome and fault injection in the Settings tab
* read the log of every call received

To simulate inbound invoices without the web page, start the simulator with
``--filestore <dir>`` and copy FatturaPA xml files into ``<dir>``: at the next
request each ``*.xml`` file is put in the in archive, as received from SdI,
and moved into ``<dir>/done``.
