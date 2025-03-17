from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT)''')
    conn.commit()
    conn.close()

# Function to resequence IDs after deletion
def resequence_ids():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("SELECT id, name, phone, email FROM contacts ORDER BY id")
    contacts = c.fetchall()
    c.execute("DROP TABLE contacts")
    c.execute('''CREATE TABLE contacts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT)''')
    for idx, (_, name, phone, email) in enumerate(contacts, start=1):
        c.execute("INSERT INTO contacts (id, name, phone, email) VALUES (?, ?, ?, ?)", 
                  (idx, name, phone, email))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            c.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))  # Redirect after adding
        
        elif action == 'delete':
            contact_id = request.form['id']
            c.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            resequence_ids()  # Reorder IDs after deletion
            conn.close()
            return redirect(url_for('index'))  # Redirect after deleting
        
        elif action == 'update':
            contact_id = request.form['id']
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            c.execute("UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?", 
                      (name, phone, email, contact_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))  # Redirect after updating

    # For GET requests or after redirects
    c.execute("SELECT * FROM contacts")
    contacts = c.fetchall()
    edit_id = request.args.get('edit_id')
    conn.close()
    
    return render_template('index.html', contacts=contacts, edit_id=edit_id)

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?", 
              ('%' + search_term + '%', '%' + search_term + '%'))
    contacts = c.fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts, search_term=search_term)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)