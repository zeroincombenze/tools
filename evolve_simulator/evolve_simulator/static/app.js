// Copyright 2026 Zeroincombenze srls <https://www.zeroincombenze.it>
// License LGPL-3.0-or-later (https://www.gnu.org/licenses/lgpl).
const { createApp } = Vue;

async function api(method, url, body) {
    const options = { method, headers: { "Content-Type": "application/json" } };
    if (body !== undefined) {
        options.body = JSON.stringify(body);
    }
    const response = await fetch("/sim/api" + url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "HTTP " + response.status);
    }
    return data;
}

createApp({
    template: `
    <div>
        <h1 class="title">Evolve Simulator</h1>
        <p class="subtitle is-6">
            Odoo SdI channel &rarr; Sender URL:
            <code>{{ senderUrl }}</code>
        </p>
        <p class="notification is-danger is-light" v-if="error">{{ error }}</p>

        <div class="tabs">
            <ul>
                <li v-for="tab in tabs" :key="tab.id" :class="{ 'is-active': current === tab.id }">
                    <a @click="current = tab.id">{{ tab.label }}</a>
                </li>
            </ul>
        </div>

        <div v-if="isArchive">
            <div class="buttons">
                <button class="button is-small" @click="load">Refresh</button>
                <button class="button is-small is-danger is-light" @click="reset">
                    Delete all documents
                </button>
            </div>
            <div class="table-container">
            <table class="table is-fullwidth is-striped is-narrow is-hoverable">
                <thead><tr>
                    <th>Id</th><th>Number</th><th>Date</th><th>TD</th><th>File</th>
                    <th>Loaded</th><th>State</th><th>Outcome</th><th>Note</th><th></th>
                </tr></thead>
                <tbody>
                <tr v-for="doc in archiveDocs" :key="doc.id">
                    <td>{{ doc.id }}</td>
                    <td>{{ doc.number }}</td>
                    <td>{{ (doc.date || "").substring(0, 10) }}</td>
                    <td>{{ doc.td }}</td>
                    <td>{{ doc.file_name }}</td>
                    <td>{{ doc.loaded_at }}</td>
                    <td :class="stateClass(doc)">
                        {{ doc.invoice_state || doc.sdi_state }}
                        <span v-if="doc.next_step_at" class="has-text-grey">
                            (next {{ doc.next_step_at.substring(11) }})
                        </span>
                    </td>
                    <td>
                        <div class="select is-small" v-if="doc.step < 2">
                            <select v-model="doc.outcome" @change="patch(doc, { outcome: doc.outcome })">
                                <option :value="null">(default)</option>
                                <option v-for="o in settings.outcomes" :key="o" :value="o">{{ o }}</option>
                            </select>
                        </div>
                        <div class="select is-small" v-else-if="doc.archive !== settings.ARCHIVE_SENT">
                            <select v-model="doc.invoice_state" @change="patch(doc, { invoice_state: doc.invoice_state })">
                                <option v-for="o in stateChoices(doc)" :key="o" :value="o">{{ o }}</option>
                            </select>
                        </div>
                    </td>
                    <td>{{ doc.note }}</td>
                    <td class="is-nowrap">
                        <button class="button is-small is-info is-light" v-if="doc.step < 2"
                                @click="advance(doc)">Next step</button>
                        <button class="button is-small is-danger is-light"
                                @click="remove(doc)">Delete</button>
                    </td>
                </tr>
                <tr v-if="!archiveDocs.length"><td colspan="10" class="has-text-grey">No documents</td></tr>
                </tbody>
            </table>
            </div>

            <div v-if="current === settings.ARCHIVE_IN" class="box">
                <h2 class="subtitle">Receive a purchase invoice</h2>
                <div class="field">
                    <input class="input is-small" type="file" accept=".xml" @change="readInbox">
                </div>
                <button class="button is-primary is-small" :disabled="!inbox.xml" @click="sendInbox">
                    Put in archive
                </button>
            </div>
        </div>

        <div v-if="current === 'settings'" class="columns">
            <div class="column is-half">
                <div class="box">
                    <h2 class="subtitle">Behaviour</h2>
                    <label class="checkbox">
                        <input type="checkbox" v-model="settings.AUTH_CHECK"> Check authentication
                    </label>
                    <div class="field mt-3">
                        <label class="label is-small">Token tolerance (seconds)</label>
                        <input class="input is-small" type="number" v-model.number="settings.AUTH_TOLERANCE">
                    </div>
                    <div class="field">
                        <label class="label is-small">Seconds before delivery to SdI</label>
                        <input class="input is-small" type="number" v-model.number="settings.SDI_DELAY">
                    </div>
                    <div class="field">
                        <label class="label is-small">Seconds before outcome</label>
                        <input class="input is-small" type="number" v-model.number="settings.OUTCOME_DELAY">
                    </div>
                    <div class="field">
                        <label class="label is-small">Default outcome</label>
                        <div class="select is-small">
                            <select v-model="settings.DEFAULT_OUTCOME">
                                <option v-for="o in settings.outcomes" :key="o" :value="o">{{ o }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="field">
                        <label class="label is-small">Fault injection</label>
                        <div class="select is-small">
                            <select v-model="settings.FAULT">
                                <option value="">none</option>
                                <option value="http500">HTTP 500</option>
                                <option value="esito1">EsitoChiamata = 1 (generic error)</option>
                                <option value="auth">EsitoChiamata = 2 (auth error)</option>
                            </select>
                        </div>
                    </div>
                    <button class="button is-primary is-small" @click="saveSettings">Save</button>
                </div>
            </div>
            <div class="column is-half">
                <div class="box">
                    <h2 class="subtitle">Clients</h2>
                    <table class="table is-fullwidth is-narrow">
                        <thead><tr><th>Client ID</th><th>Client Key</th><th>Company ID</th></tr></thead>
                        <tbody>
                        <tr v-for="c in clients" :key="c.id">
                            <td>{{ c.client_id }}</td><td><code>{{ c.client_key }}</code></td><td>{{ c.company_id }}</td>
                        </tr>
                        </tbody>
                    </table>
                    <div class="field is-grouped">
                        <input class="input is-small" placeholder="Client ID" v-model="newClient.client_id">
                        <input class="input is-small" placeholder="Client Key (16/24/32)" v-model="newClient.client_key">
                        <input class="input is-small" type="number" placeholder="Company" v-model.number="newClient.company_id">
                        <button class="button is-small is-primary" @click="addClient">Save</button>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="current === 'calls'">
            <button class="button is-small mb-2" @click="load">Refresh</button>
            <table class="table is-fullwidth is-striped is-narrow">
                <thead><tr><th>Time</th><th>Action</th><th>Client</th><th>Archive</th><th>Esito</th><th>Message</th></tr></thead>
                <tbody>
                <tr v-for="c in calls" :key="c.id">
                    <td>{{ c.called_at }}</td><td>{{ c.action }}</td><td>{{ c.client_id }}</td>
                    <td>{{ c.archive }}</td>
                    <td :class="c.esito === 0 ? 'state-ok' : 'state-ko'">{{ c.esito }}</td>
                    <td>{{ c.message }}</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
    `,
    data() {
        return {
            current: 3,
            settings: { outcomes: [], API_PREFIX: "/rest/api/v1" },
            documents: [],
            clients: [],
            calls: [],
            newClient: { client_id: "", client_key: "", company_id: 1 },
            inbox: { file_name: "", xml: "" },
            error: "",
            timer: null,
        };
    },
    computed: {
        tabs() {
            return [
                { id: this.settings.ARCHIVE_SENT, label: "Sent archive (" + this.settings.ARCHIVE_SENT + ")" },
                { id: this.settings.ARCHIVE_OUT, label: "Out archive (" + this.settings.ARCHIVE_OUT + ")" },
                { id: this.settings.ARCHIVE_IN, label: "In archive (" + this.settings.ARCHIVE_IN + ")" },
                { id: "calls", label: "Call log" },
                { id: "settings", label: "Settings" },
            ];
        },
        isArchive() {
            return typeof this.current === "number";
        },
        archiveDocs() {
            return this.documents.filter((d) => d.archive === this.current);
        },
        senderUrl() {
            return window.location.origin + this.settings.API_PREFIX + "/";
        },
    },
    methods: {
        async run(fn) {
            this.error = "";
            try {
                await fn();
            } catch (e) {
                this.error = e.message;
            }
        },
        load() {
            return this.run(async () => {
                this.settings = await api("GET", "/settings");
                this.documents = await api("GET", "/documents");
                this.clients = await api("GET", "/clients");
                this.calls = await api("GET", "/calls");
            });
        },
        stateClass(doc) {
            const s = doc.invoice_state || doc.sdi_state || "";
            if (/consegna|accettato|ricevuta/i.test(s) && !/mancata/i.test(s)) return "state-ok";
            if (/scarto|errore|non |rifiutato|mancata/i.test(s)) return "state-ko";
            return "state-wip";
        },
        stateChoices(doc) {
            const res = ["Inviato", "Ricevuta"].concat(this.settings.outcomes);
            if (doc.invoice_state && !res.includes(doc.invoice_state)) res.unshift(doc.invoice_state);
            return res;
        },
        patch(doc, values) {
            return this.run(async () => {
                await api("PATCH", "/documents/" + doc.id, values);
                await this.load();
            });
        },
        advance(doc) {
            return this.run(async () => {
                await api("POST", "/documents/" + doc.id + "/advance");
                await this.load();
            });
        },
        remove(doc) {
            return this.run(async () => {
                await api("DELETE", "/documents/" + doc.id);
                await this.load();
            });
        },
        reset() {
            return this.run(async () => {
                await api("POST", "/reset");
                await this.load();
            });
        },
        saveSettings() {
            return this.run(async () => {
                const s = this.settings;
                this.settings = await api("PUT", "/settings", {
                    AUTH_CHECK: s.AUTH_CHECK,
                    AUTH_TOLERANCE: s.AUTH_TOLERANCE,
                    SDI_DELAY: s.SDI_DELAY,
                    OUTCOME_DELAY: s.OUTCOME_DELAY,
                    DEFAULT_OUTCOME: s.DEFAULT_OUTCOME,
                    FAULT: s.FAULT,
                });
            });
        },
        addClient() {
            return this.run(async () => {
                await api("POST", "/clients", this.newClient);
                this.newClient = { client_id: "", client_key: "", company_id: 1 };
                await this.load();
            });
        },
        async readInbox(event) {
            const file = event.target.files[0];
            this.inbox = { file_name: file ? file.name : "", xml: file ? await file.text() : "" };
        },
        sendInbox() {
            return this.run(async () => {
                await api("POST", "/inbox", this.inbox);
                this.inbox = { file_name: "", xml: "" };
                await this.load();
            });
        },
    },
    mounted() {
        this.load();
        this.timer = setInterval(() => {
            if (this.isArchive || this.current === "calls") this.load();
        }, 5000);
    },
    unmounted() {
        clearInterval(this.timer);
    },
}).mount("#app");
