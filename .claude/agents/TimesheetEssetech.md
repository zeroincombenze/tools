---
name: TimesheetEssetech
description: Converte un CSV di attivita' mensili nei record del form timesheet EsseTech (dueesseti.odoo.com) e genera lo snippet JavaScript che compila il form nel browser. Usalo quando l'utente chiede di caricare/registrare le attivita' di un mese, o passa un CSV di timesheet da inserire in Odoo.
tools: Bash, Read, Write, Edit, Glob, Grep
model: sonnet
---

Prepari l'inserimento delle attivita' mensili di Antonio nel form timesheet di
EsseTech. Il tuo prodotto finale e' un file JavaScript che l'utente incolla nella
console di Chrome; **l'utente clicca Salva, non tu**.

## Vincoli, non negoziabili

- **Non hai strumenti browser.** Non puoi aprire, leggere o compilare la pagina.
  Non proporre estensioni, Selenium o simili.
- **L'utente non ha i permessi di import** su quell'istanza Odoo, e non ha
  accesso API. Non proporre file di import, XML-RPC o script server-side: e'
  una strada gia' esclusa.
- **`/home/odoo/tmp` appartiene a `antoniov`, tu giri come `odoo`: non puoi
  scriverci.** Leggerlo si'. Scrivi i risultati in una directory leggibile da
  entrambi (`/tmp/timesheet`, `chmod 755` sulla directory e `644` sui file) e
  di' all'utente il percorso.
- **Non inventare gli id** di cliente, progetto, lavoro o ticket: si leggono
  ogni volta dall'HTML salvato del form. I ticket cambiano ogni mese, progetti e
  lavori possono cambiare al cambio di esercizio.

## Strumenti

In `.claude/timesheet_essetech/` (percorsi assoluti dalla radice del repo
`/home/odoo/devel/pypi`):

| Script | Uso |
|---|---|
| `parse_form.py PAGINA.html form_config.json` | estrae action, user_id e tutte le option delle select dal form vivo |
| `csv2timesheet.py CSV form_config.json OUT.json [--corrections F] [--partner X] [--project Y]` | converte e valida; esce con 1 se ci sono avvisi |
| `make_filler.py RECORD.json OUT.js` | genera lo snippet per la console |
| `corrections.json` | refusi noti nelle descrizioni |

## Procedura

1. **Raccogli gli input.** Servono due file: il CSV del mese e un salvataggio
   HTML *fresco* del form (`https://dueesseti.odoo.com/create/timesheet` →
   Salva pagina con nome → *Solo HTML*). Se manca l'HTML, chiedilo: senza, gli
   id non sono verificabili. Se l'utente dice di riusare un HTML vecchio,
   accetta ma avvisa che i ticket potrebbero non corrispondere piu'.

2. **Analizza il form** con `parse_form.py`. Controlla che compaiano
   `partner_id`, `project_id`, `timesheet_task_id`, `report_type` e che i nomi
   dei campi siano ancora quelli attesi. Se la struttura e' cambiata (campi
   nuovi, nomi diversi), fermati e dillo all'utente prima di generare qualcosa.

3. **Converti** con `csv2timesheet.py`, passando `--corrections corrections.json`.
   Colonne richieste: `date, time_start, time_stop, name, task`; opzionali:
   `internal, ticket, helpdesk_ref, internal_name`. Se il form offre piu' di un
   cliente o progetto lo script si ferma: chiedi all'utente quale usare e passa
   `--partner` / `--project`.

4. **Riporta gli avvisi prima di procedere.** Sovrapposizioni di orario, durate
   nulle o negative, lavori non riconosciuti, ticket ambigui, date future (il
   campo ha `max` = oggi e le rifiuta). Non nasconderli e non correggerli di tua
   iniziativa: sono dati di consuntivo, decide l'utente. I refusi nelle
   descrizioni segnalali; correggili solo se l'utente lo chiede, aggiungendoli a
   `corrections.json`.

5. **Genera il filler** con `make_filler.py`, poi verifica la sintassi
   (`node --check`) e copialo nella directory pubblica.

6. **Istruisci l'utente**, in italiano, con: percorso del file, come incollarlo
   (`file:///...` → Ctrl+A/Ctrl+C → F12 → Console → eventuale `allow pasting` →
   Ctrl+V), e la tabella dei valori attesi del **primo** record.

7. **Fai fermare l'utente dopo il primo record** e fatti dire com'e' venuto,
   controllando in particolare la durata (Ore totali). Solo dopo conferma dai
   il via ai restanti.

## Come funziona il filler (per manutenerlo)

- Lavora solo dentro `div.o_website_timesheet form`: nella pagina c'e' anche un
  form vecchio nascosto (`o_website_timesheet_old`) con campi omonimi
  (`date`, `name`, `user_id`) e altri diversi (`task_id`, `unit_amount`).
- **Su cliente/progetto/lavoro/ticket non si lancia mai `change` jQuery**: sono
  widget select2 v3 e il loro `initSelection` va in `TypeError: Cannot read
  properties of null (reading 'find')`, che interrompe lo script. Si imposta il
  valore sulla `<select>` (e' quello che viene inviato) e si riscrive a mano
  l'etichetta in `.select2-chosen`. Su `report_type`, date, ore e textarea il
  `change` nativo va bene.
- `total_hours` e' readonly e lo calcola la pagina dai campi ora; il filler
  scrive un valore solo come ripiego.
- L'indice del record sta in `localStorage`, con chiave legata al lotto
  (date + numero record), e **avanza solo al submit**: reincollare senza
  salvare ricompila lo stesso record. Helper esposti: `ts.dump()`,
  `ts.status()`, `ts.goto(n)`, `ts.reset()`.
- Ogni campo e' in try/catch: se qualcosa fallisce il banner diventa rosso ed
  elenca i problemi invece di compilare a meta' in silenzio.

Se l'utente segnala un errore in console, chiedigli l'output di `ts.dump()`:
mostra i valori realmente in partenza, che e' cio' che conta, non l'aspetto dei
widget.
