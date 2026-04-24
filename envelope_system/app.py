from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE = r"C:\Users\pache\OneDrive\Desktop\envelope_system\envelope_system\database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def is_admin():
    return session.get("role") == "admin"


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    total_envelopes = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes"
    ).fetchone()["total"]

    total_received = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE status = 'Received'"
    ).fetchone()["total"]

    total_dispatched = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE status = 'Dispatched'"
    ).fetchone()["total"]

    total_passport = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE service_type = 'Passport'"
    ).fetchone()["total"]

    total_notarial = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE service_type = 'Notarial'"
    ).fetchone()["total"]

    total_visa = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE service_type = 'Visa'"
    ).fetchone()["total"]

    total_admin = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE service_type = 'Administration'"
    ).fetchone()["total"]

    total_assistance = conn.execute(
        "SELECT COUNT(*) AS total FROM envelopes WHERE service_type = 'Assistance'"
    ).fetchone()["total"]

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session.get("role", "viewer"),
        total_envelopes=total_envelopes,
        total_received=total_received,
        total_dispatched=total_dispatched,
        total_passport=total_passport,
        total_notarial=total_notarial,
        total_visa=total_visa,
        total_admin=total_admin,
        total_assistance=total_assistance
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        user = conn.execute(
            """
            SELECT * FROM users
            WHERE username = ? AND password_hash = ? AND is_active = 1
            """,
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/new_entry", methods=["GET", "POST"])
def new_entry():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Access denied: consultation users cannot create records."

    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()
        outgoing_barcode = request.form.get("outgoing_barcode", "").strip()
        client_name = request.form.get("client_name", "").strip()
        address = request.form.get("address", "").strip()
        service_type = request.form.get("service_type", "").strip()

        requested_service_list = request.form.getlist("requested_service")
        requested_service = ", ".join(requested_service_list)

        documents_list = request.form.getlist("documents")
        payment_amount = request.form.get("payment_amount", "").strip()
        foreign_document = request.form.get("foreign_document", "").strip()
        other_document = request.form.get("other_document", "").strip()
        received_passport_barcode = request.form.get("received_passport_barcode", "").strip()

        if "Pagamento" in documents_list and payment_amount:
            documents_list.append(f"Pagamento: {payment_amount}")

        if "D. Estrangeiro" in documents_list and foreign_document:
            documents_list.append(f"D. Estrangeiro: {foreign_document}")

        if "Outros" in documents_list and other_document:
            documents_list.append(f"Outros: {other_document}")

        documents = ", ".join(documents_list)

        application_barcode = request.form.get("application_barcode", "").strip()
        passport_barcode = request.form.get("passport_barcode", "").strip()
        notes = request.form.get("notes", "").strip()

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO envelopes
            (barcode, outgoing_barcode, client_name, address, service_type, requested_service,
             documents, received_passport_barcode, application_barcode, passport_barcode, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                barcode,
                outgoing_barcode,
                client_name,
                address,
                service_type,
                requested_service,
                documents,
                received_passport_barcode,
                application_barcode,
                passport_barcode,
                notes,
                "Received"
            )
        )
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("new_entry.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))

    results = []

    if request.method == "POST":
        search_term = request.form.get("search_term", "").strip()
        entry_date = request.form.get("entry_date", "").strip()
        dispatch_date = request.form.get("dispatch_date", "").strip()

        query = """
            SELECT * FROM envelopes
            WHERE 1=1
        """
        params = []

        if search_term:
            query += """
                AND (
                    barcode LIKE ?
                    OR outgoing_barcode LIKE ?
                    OR client_name LIKE ?
                    OR service_type LIKE ?
                    OR requested_service LIKE ?
                    OR received_passport_barcode LIKE ?
                    OR application_barcode LIKE ?
                    OR passport_barcode LIKE ?
                    OR documents LIKE ?
                    OR notes LIKE ?
                )
            """
            params.extend([
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%",
                f"%{search_term}%"
            ])

        if entry_date:
            query += " AND date(entry_date) = ?"
            params.append(entry_date)

        if dispatch_date:
            query += " AND date(dispatch_date) = ?"
            params.append(dispatch_date)

        query += " ORDER BY id DESC"

        conn = get_db_connection()
        results = conn.execute(query, params).fetchall()
        conn.close()

    return render_template("search.html", results=results)


@app.route("/envelope/<int:envelope_id>")
def envelope_details(envelope_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    envelope = conn.execute(
        "SELECT * FROM envelopes WHERE id = ?",
        (envelope_id,)
    ).fetchone()
    conn.close()

    return render_template("envelope_details.html", envelope=envelope)


@app.route("/dispatch", methods=["GET", "POST"])
def dispatch():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Access denied: consultation users cannot dispatch records."

    results = []
    message = None

    if request.method == "POST":
        action = request.form.get("action", "").strip()

        conn = get_db_connection()

        if action == "search":
            search_term = request.form.get("search_term", "").strip()

            results = conn.execute(
                """
                SELECT * FROM envelopes
                WHERE outgoing_barcode LIKE ?
                   OR client_name LIKE ?
                ORDER BY id DESC
                """,
                (
                    f"%{search_term}%",
                    f"%{search_term}%"
                )
            ).fetchall()

        elif action == "dispatch":
            envelope_id = request.form.get("envelope_id", "").strip()

            envelope = conn.execute(
                "SELECT * FROM envelopes WHERE id = ?",
                (envelope_id,)
            ).fetchone()

            if envelope:
                conn.execute(
                    """
                    UPDATE envelopes
                    SET status = ?, dispatch_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    ("Dispatched", envelope_id)
                )
                conn.commit()
                message = "Envelope dispatched successfully."

                results = conn.execute(
                    "SELECT * FROM envelopes WHERE id = ?",
                    (envelope_id,)
                ).fetchall()
            else:
                message = "Envelope not found."

        conn.close()

    return render_template("dispatch.html", results=results, message=message)


@app.route("/delete_envelope/<int:envelope_id>", methods=["POST"])
def delete_envelope(envelope_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not is_admin():
        return "Access denied: consultation users cannot delete records."

    conn = get_db_connection()
    conn.execute("DELETE FROM envelopes WHERE id = ?", (envelope_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("search"))


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)