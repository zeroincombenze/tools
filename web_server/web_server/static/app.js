const { createApp } = Vue;

createApp({
    template: `
        <div>
            <h1 class="title">Store messages</h1>

            <div class="field has-addons">
                <div class="control is-expanded">
                    <input
                        class="input"
                        type="text"
                        v-model="newMessage"
                        placeholder="Enter text"
                        @keyup.enter="saveMessage"
                    >
                </div>
                <div class="control">
                    <button class="button is-primary" @click="saveMessage">
                        Save
                    </button>
                </div>
            </div>

            <p class="has-text-danger" v-if="error">
                {{ error }}
            </p>

            <hr>

            <h2 class="subtitle">Stored messages</h2>

            <ul>
                <li v-for="msg in messages" :key="msg.id">
                    {{ msg.text }}
                </li>
            </ul>
        </div>
    `,
    data() {
        return {
            newMessage: "",
            messages: [],
            error: ""
        };
    },
    methods: {
        async loadMessages() {
            const response = await fetch("/api/messages");
            this.messages = await response.json();
        },
        async saveMessage() {
            this.error = "";

            if (!this.newMessage.trim()) {
                this.error = "Message cannot be empty";
                return;
            }

            const response = await fetch("/api/messages", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text: this.newMessage })
            });

            if (!response.ok) {
                const data = await response.json();
                this.error = data.error || "Error saving message";
                return;
            }

            this.newMessage = "";
            this.loadMessages();
        }
    },
    mounted() {
        this.loadMessages();
    }
}).mount("#app");
