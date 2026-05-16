from flask import Flask, render_template, request, jsonify
from models import init_db, Message

def create_app(database_url):
    app = Flask(__name__)

    engine, SessionLocal = init_db(database_url)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/messages", methods=["GET"])
    def get_messages():
        db = SessionLocal()
        try:
            messages = db.query(Message).order_by(Message.id.desc()).all()
            return jsonify(
                [{"id": m.id, "text": m.text} for m in messages]
            )
        finally:
            db.close()

    @app.route("/api/messages", methods=["POST"])
    def add_message():
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Empty text"}), 400

        db = SessionLocal()
        try:
            db.add(Message(text=text))
            db.commit()
            return jsonify({"status": "ok"}), 201
        finally:
            db.close()

    return app


if __name__ == "__main__":
    app = create_app("sqlite:///data/database.db")
    app.run(debug=True)
