# Visitor Management System (VMS)

A secure and customizable **Flask-based visitor management system** with role-based access, photo capture, viewer dashboard, and notification features. Ideal for offices, institutions, or residential buildings.

---

## 🚀 Features

* 📷 Capture visitor photos via webcam
* 🛡️ Role-based login system (Admin, Guard, Viewer)
* 📥 Real-time entry logging with name, phone, company, reason
* 📤 CSV download of visitor records
* ⏱️ Mark entry/exit with live viewer panel
* 🔔 Send SMS/WhatsApp/email alerts for "person of interest"
* 🔍 Viewer dashboard with search & sort options (React)
* 🔒 Secure session management using Flask sessions

---

## 📁 Project Structure

```
visitor-system/
├── app.py                  # Flask application backend
├── database.db             # SQLite database (ignored in .gitignore)
├── templates/              # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   └── viewer.html
├── static/
│   ├── script.js           # JS logic for photo capture, UI updates
│   └── styles.css          # Optional custom CSS
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules (for .env, DB, etc.)
├── requirements.txt        # Python packages needed
├── README.md               # Project documentation
```

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/visitor-system.git
cd visitor-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` and rename it to `.env`, then update your secrets:

```env
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
location=YourLocation
```

### 5. Initialize the Database

You can use the included `database.db`, or delete and recreate:

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 6. Run the App

```bash
python app.py
```

Access the site at: `http://127.0.0.1:5000`

---


## 🧠 Future Improvements

* ✅ Facial recognition (optional add-on)
* ✅ Admin panel to view logs by date/location
* ✅ Multi-user support with location filtering
* ✅ Export PDF report

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📞 Contact

Built by [Shaurya Chokshi](https://github.com/shaurya200911)

For questions, reach me at: `shaurya111109@gmail.com`
