from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

def my_table():
    conn = sqlite3.connect('debtorg.db')
    ams = conn.cursor()
    ams.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='borrower'")
    result = ams.fetchone()
    conn.close()
    return result is not None


def init_db():
    if not my_table():
        conn = sqlite3.connect('debtorg.db')
        ams = conn.cursor()
        ams.execute('''
        CREATE TABLE IF NOT EXISTS borrower (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    loan_type TEXT NOT NULL,
                    day_of_payment TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    amount INT NOT NULL,
                    status TEXT DEFAULT 'Unpaid'           
        )''')
        conn.commit()
        conn.close()


# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_borrower', methods=['POST'])
def add_borrower():
    name = request.form['name']
    loan_type = request.form['loan_type']
    day_of_payment = request.form['day_of_payment']
    due_date = request.form['due_date']
    amount = request.form['amount']

    conn = sqlite3.connect('debtorg.db')
    ams = conn.cursor()
    ams.execute("INSERT INTO borrower (name, loan_type, day_of_payment, due_date, amount) VALUES (?, ?, ?, ?, ?)",
                (name, loan_type, day_of_payment, due_date, amount))

    conn.commit()
    conn.close()

    return redirect(url_for('view_borrowers'))



# Display borrowers
@app.route('/borrowers')
def view_borrowers():
    conn = sqlite3.connect('debtorg.db')
    ams = conn.cursor()

    # Fetch all borrowers
    ams.execute("SELECT * FROM borrower ORDER BY id DESC")
    borrowers = ams.fetchall()

    # Fetch statistics
    ams.execute("SELECT COUNT(DISTINCT id) FROM borrower")
    borrower_count = ams.fetchone()[0]

    ams.execute("SELECT SUM(amount) FROM borrower")
    total_amount = ams.fetchone()[0] or 0  # Handle None case

    conn.close()

    return render_template('borrowers.html', borrowers=borrowers, borrower_count=borrower_count, total_amount=total_amount)



# For editing
@app.route('/edit/<int:id>', methods=['GET'])
def edit_borrower(id):
    conn = sqlite3.connect('debtorg.db')
    ams = conn.cursor()
    ams.execute("SELECT * FROM borrower WHERE id = ?", (id,))
    borrower = ams.fetchone()
    conn.close()

    if borrower:
        return render_template('edit_borrower.html', borrower=borrower)
    else:
        return redirect(url_for('view_borrowers'))


# For updating
@app.route('/update_borrower/<int:id>', methods=['POST'])
def update_borrower(id):
    name = request.form['name']
    loan_type = request.form['loan_type']
    day_of_payment = request.form['day_of_payment']
    due_date = request.form['due_date']
    amount = request.form['amount']

    conn = sqlite3.connect('debtorg.db')
    ams = conn.cursor()
    ams.execute('''
                UPDATE borrower
                SET name = ?, loan_type = ?, day_of_payment = ?, due_date = ?, amount = ?
                WHERE id = ?
                ''', (name, loan_type, day_of_payment, due_date, amount, id))
    conn.commit()
    conn.close()

    return redirect(url_for('view_borrowers'))

#for deleting records
@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    conn = sqlite3.connect('debtorg.db')
    ams = conn.cursor()
    ams.execute("DELETE FROM borrower WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_borrowers'))



@app.route('/mark-paid/<int:borrower_id>', methods=['POST'])
def mark_paid(borrower_id):
    try:
        conn = sqlite3.connect('debtorg.db')
        ams = conn.cursor()
        ams.execute("UPDATE borrower SET status = 'Paid' WHERE id = ?", (borrower_id,))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return redirect(url_for('view_borrowers'))



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
