# Hospital Management System

A desktop-based Hospital Management System (HMS) developed using Python and CustomTkinter.
This application manages hospital operations such as patient records, staff details, medicine inventory, and billing.

## Features

* Secure Login System
* Patient Management (Add, Update, Delete, Search)
* Staff Management
* Medicine Inventory Management
* Billing & Prescription System
* SQLite Database Integration
* Real-time stock updates and validation

## Technologies Used

* Python 3
* CustomTkinter (GUI)
* SQLite (Database)
* Pillow (Image handling)

## Project Structure

* `hms.py` : Main Python file containing GUI and functionality
* `logo.png` : Application logo
* `login_screen.png` : Screenshot of login screen
* `dashboard.png` : Screenshot of main dashboard
* `README.md` : Project documentation

## How to Run the Project

1. Clone the repository:

```bash
git clone https://github.com/Hridoy-KO/Hospital-Management-System.git
cd Hospital-Management-System
```

2. (Optional) Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# On Windows use: venv\Scripts\activate
```

3. Install required Python packages:

```bash
pip install customtkinter pillow
```

4. Run the application:

```bash
python hms.py
```

## Notes

* Default login credentials:

  * **Username:** Hridoy
  * **Password:** 1234
* Database file `hms_v4.db` will be created automatically on first run.
