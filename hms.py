import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from contextlib import contextmanager

# ------ CONFIGURATION ------
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 
USERNAME = "Hridoy"
PASSWORD = "1234"
DATABASE_NAME = "hms_v4.db" # Updated DB name

# ------ DATABASE LOGIC ------
@contextmanager
def connect_db():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

def setup_database():
    """Creates all necessary tables: patients, inventory, staff, and prescriptions."""
    with connect_db() as conn:
        cursor = conn.cursor()
        
        # 1. Patients Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                disease TEXT
            )
        """)
        # 2. Medicine Inventory Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                med_id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                quantity INTEGER,
                price REAL
            )
        """)
        # 3. Staff Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                staff_id TEXT PRIMARY KEY,
                name TEXT,
                role TEXT, 
                department TEXT
            )
        """)
        # 4. NEW: Prescriptions/Billing Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                bill_id INTEGER PRIMARY KEY,
                patient_id TEXT,
                med_id TEXT,
                quantity_dispensed INTEGER,
                total_cost REAL,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (med_id) REFERENCES inventory(med_id)
            )
        """)
        conn.commit()

setup_database()

# ====================================================================
# Login Application
# ====================================================================
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconphoto(False, ctk.CTkImage(file="logo.png"))
        self.title("HMS - Secure Login")
        self.geometry("400x350")
        self.resizable(False, False)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(frame, text="Hospital Management System", font=("Arial", 20, "bold")).pack(pady=(30, 20))
        
        self.user_ent = ctk.CTkEntry(frame, placeholder_text="Username", width=250)
        self.user_ent.pack(pady=10)
        
        self.pass_ent = ctk.CTkEntry(frame, placeholder_text="Password", show='*', width=250)
        self.pass_ent.pack(pady=10)

        ctk.CTkButton(frame, text="Login", command=self.login, width=250).pack(pady=20)

    def login(self):
        if self.user_ent.get() == USERNAME and self.pass_ent.get() == PASSWORD:
            self.withdraw()
            HMSApp(self)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

# ====================================================================
# Main Application Dashboard
# ====================================================================
class HMSApp(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("HMS Dashboard - Management System")
        self.geometry("1400x800") # Increased size for 4 tabs
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create Tabview with 4 tabs
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.tab_patients = self.tabs.add("Patient Management")
        self.tab_inventory = self.tabs.add("Medicine Inventory")
        self.tab_staff = self.tabs.add("Staff Management")
        self.tab_billing = self.tabs.add("Billing & Prescriptions") # NEW TAB

        # Setup all UI sections
        self.setup_patient_ui()
        self.setup_inventory_ui()
        self.setup_staff_ui()
        self.setup_billing_ui() # NEW SETUP

        # Apply common ttk style for dark theme
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), foreground="white", background="#2b2b2b")
        style.configure("Treeview", background="#343638", foreground="white", fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#3B8ED4')])
        
        # Load initial data for all sections
        self.load_patients()
        self.load_inventory()
        self.load_staff()
        self.load_prescriptions()


    # --- EXISTING PATIENT, INVENTORY, STAFF CODE GOES HERE ---
    # (Keeping these condensed for brevity, they remain unchanged from the last step)
    # ----------------------------------------------------------------
    # PATIENT SECTION
    # ----------------------------------------------------------------
    def setup_patient_ui(self):
        self.tab_patients.grid_columnconfigure(1, weight=1)
        self.tab_patients.grid_rowconfigure(0, weight=1)
        left_f = ctk.CTkFrame(self.tab_patients, width=300); left_f.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        ctk.CTkLabel(left_f, text="Patient Details", font=("Arial", 16, "bold")).pack(pady=10)
        self.p_entries = {}
        for field in ["ID", "Name", "Age", "Disease"]:
            ctk.CTkLabel(left_f, text=field).pack(anchor="w", padx=20); ent = ctk.CTkEntry(left_f, width=220)
            ent.pack(pady=(0, 10), padx=20); self.p_entries[field] = ent
        ctk.CTkButton(left_f, text="Add Patient", fg_color="green", command=self.add_patient).pack(pady=5)
        ctk.CTkButton(left_f, text="Update", command=self.update_patient).pack(pady=5)
        ctk.CTkButton(left_f, text="Delete", fg_color="red", command=self.delete_patient).pack(pady=5)
        ctk.CTkButton(left_f, text="Clear", command=self.clear_p_fields).pack(pady=5)
        right_f = ctk.CTkFrame(self.tab_patients); right_f.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.p_search = ctk.CTkEntry(right_f, placeholder_text="Search Patients..."); self.p_search.pack(fill="x", padx=10, pady=10)
        self.p_search.bind("<KeyRelease>", lambda e: self.load_patients(self.p_search.get()))
        cols = ("ID", "Name", "Age", "Disease"); self.p_tree = ttk.Treeview(right_f, columns=cols, show="headings", style="Treeview")
        for c in cols: self.p_tree.heading(c, text=c); self.p_tree.column(c, anchor=ctk.CENTER, width=100)
        self.p_tree.pack(expand=True, fill="both", padx=10, pady=10); self.p_tree.bind("<<TreeviewSelect>>", self.select_patient)
    def add_patient(self):
        data = [self.p_entries[f].get() for f in ["ID", "Name", "Age", "Disease"]]
        if not all(data): return messagebox.showwarning("Empty", "Fill all fields")
        try:
            with connect_db() as conn: conn.execute("INSERT INTO patients VALUES (?,?,?,?)", data); conn.commit()
            self.load_patients(); self.clear_p_fields()
        except Exception as e: messagebox.showerror("Error", str(e))
    def load_patients(self, term=""):
        for i in self.p_tree.get_children(): self.p_tree.delete(i)
        with connect_db() as conn:
            cursor = conn.cursor()
            if term: cursor.execute("SELECT * FROM patients WHERE name LIKE ? OR id LIKE ?", (f"%{term}%", f"%{term}%"))
            else: cursor.execute("SELECT * FROM patients")
            for row in cursor.fetchall(): self.p_tree.insert("", "end", values=row)
    def select_patient(self, event):
        sel = self.p_tree.selection()
        if sel:
            val = self.p_tree.item(sel)['values']; self.clear_p_fields()
            self.p_entries["ID"].insert(0, val[0]); self.p_entries["ID"].configure(state="disabled")
            self.p_entries["Name"].insert(0, val[1]); self.p_entries["Age"].insert(0, val[2]); self.p_entries["Disease"].insert(0, val[3])
    def update_patient(self):
        pid = self.p_entries["ID"].get(); self.p_entries["ID"].configure(state="normal") 
        data = (self.p_entries["Name"].get(), self.p_entries["Age"].get(), self.p_entries["Disease"].get(), pid)
        with connect_db() as conn: conn.execute("UPDATE patients SET name=?, age=?, disease=? WHERE id=?", data); conn.commit()
        self.load_patients(); self.clear_p_fields()
    def delete_patient(self):
        pid = self.p_entries["ID"].get();
        if not pid: return
        with connect_db() as conn: conn.execute("DELETE FROM patients WHERE id=?", (pid,)); conn.commit()
        self.load_patients(); self.clear_p_fields()
    def clear_p_fields(self):
        for e in self.p_entries.values(): e.configure(state="normal"); e.delete(0, 'end')

    # ----------------------------------------------------------------
    # INVENTORY SECTION
    # ----------------------------------------------------------------
    def setup_inventory_ui(self):
        self.tab_inventory.grid_columnconfigure(1, weight=1); self.tab_inventory.grid_rowconfigure(0, weight=1)
        inv_left = ctk.CTkFrame(self.tab_inventory, width=300); inv_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        ctk.CTkLabel(inv_left, text="Medicine Details", font=("Arial", 16, "bold")).pack(pady=10)
        self.i_entries = {}
        for field in ["Med ID", "Med Name", "Category", "Quantity", "Price"]:
            ctk.CTkLabel(inv_left, text=field).pack(anchor="w", padx=20); ent = ctk.CTkEntry(inv_left, width=220)
            ent.pack(pady=(0, 10), padx=20); self.i_entries[field] = ent
        ctk.CTkButton(inv_left, text="Add Medicine", fg_color="green", command=self.add_medicine).pack(pady=5)
        ctk.CTkButton(inv_left, text="Update Stock", command=self.update_medicine).pack(pady=5)
        ctk.CTkButton(inv_left, text="Delete Med", fg_color="red", command=self.delete_medicine).pack(pady=5)
        ctk.CTkButton(inv_left, text="Clear", command=self.clear_i_fields).pack(pady=5)
        inv_right = ctk.CTkFrame(self.tab_inventory); inv_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.i_search = ctk.CTkEntry(inv_right, placeholder_text="Search Medicine Inventory..."); self.i_search.pack(fill="x", padx=10, pady=10)
        self.i_search.bind("<KeyRelease>", lambda e: self.load_inventory(self.i_search.get()))
        i_cols = ("ID", "Name", "Category", "Qty", "Price"); self.i_tree = ttk.Treeview(inv_right, columns=i_cols, show="headings", style="Treeview")
        for c in i_cols: self.i_tree.heading(c, text=c); self.i_tree.column(c, anchor=ctk.CENTER, width=100)
        self.i_tree.pack(expand=True, fill="both", padx=10, pady=10); self.i_tree.bind("<<TreeviewSelect>>", self.select_medicine)
        self.i_tree.tag_configure('low_stock', background='#8B0000', foreground='white')
    def load_inventory(self, term=""):
        for i in self.i_tree.get_children(): self.i_tree.delete(i)
        with connect_db() as conn:
            cursor = conn.cursor()
            if term: cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{term}%",))
            else: cursor.execute("SELECT * FROM inventory")
            for row in cursor.fetchall():
                tag = 'low_stock' if row[3] <= 5 else ''
                self.i_tree.insert("", "end", values=row, tags=(tag,))
    def add_medicine(self):
        data = [self.i_entries[f].get() for f in ["Med ID", "Med Name", "Category", "Quantity", "Price"]]
        if not all(data): return messagebox.showwarning("Empty", "Fill all fields")
        try:
            with connect_db() as conn: conn.execute("INSERT INTO inventory VALUES (?,?,?,?,?)", data); conn.commit()
            self.load_inventory(); self.clear_i_fields()
        except Exception as e: messagebox.showerror("Error", str(e))
    def select_medicine(self, event):
        sel = self.i_tree.selection()
        if sel:
            val = self.i_tree.item(sel)['values']; self.clear_i_fields()
            self.i_entries["Med ID"].insert(0, val[0]); self.i_entries["Med ID"].configure(state="disabled")
            self.i_entries["Med Name"].insert(0, val[1]); self.i_entries["Category"].insert(0, val[2]); self.i_entries["Quantity"].insert(0, val[3]); self.i_entries["Price"].insert(0, val[4])
    def update_medicine(self):
        mid = self.i_entries["Med ID"].get(); self.i_entries["Med ID"].configure(state="normal")
        data = (self.i_entries["Med Name"].get(), self.i_entries["Category"].get(), self.i_entries["Quantity"].get(), self.i_entries["Price"].get(), mid)
        with connect_db() as conn: conn.execute("UPDATE inventory SET name=?, category=?, quantity=?, price=? WHERE med_id=?", data); conn.commit()
        self.load_inventory(); self.clear_i_fields()
    def delete_medicine(self):
        mid = self.i_entries["Med ID"].get();
        if not mid: return
        with connect_db() as conn: conn.execute("DELETE FROM inventory WHERE med_id=?", (mid,)); conn.commit()
        self.load_inventory(); self.clear_i_fields()
    def clear_i_fields(self):
        for e in self.i_entries.values(): e.configure(state="normal"); e.delete(0, 'end')

    # ----------------------------------------------------------------
    # STAFF SECTION
    # ----------------------------------------------------------------
    def setup_staff_ui(self):
        self.tab_staff.grid_columnconfigure(1, weight=1); self.tab_staff.grid_rowconfigure(0, weight=1)
        staff_left = ctk.CTkFrame(self.tab_staff, width=300); staff_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        ctk.CTkLabel(staff_left, text="Staff Details", font=("Arial", 16, "bold")).pack(pady=10)
        self.s_entries = {}
        for field in ["Staff ID", "Name", "Role", "Department"]:
            ctk.CTkLabel(staff_left, text=field).pack(anchor="w", padx=20)
            if field == "Role":
                self.s_entries[field] = ctk.CTkOptionMenu(staff_left, values=["Doctor", "Nurse", "Admin", "Support"], width=220); self.s_entries[field].set("Doctor"); self.s_entries[field].pack(pady=(0, 10), padx=20)
            else:
                ent = ctk.CTkEntry(staff_left, width=220); ent.pack(pady=(0, 10), padx=20); self.s_entries[field] = ent
        ctk.CTkButton(staff_left, text="Add Staff", fg_color="green", command=self.add_staff).pack(pady=5)
        ctk.CTkButton(staff_left, text="Update Staff", command=self.update_staff).pack(pady=5)
        ctk.CTkButton(staff_left, text="Delete Staff", fg_color="red", command=self.delete_staff).pack(pady=5)
        ctk.CTkButton(staff_left, text="Clear", command=self.clear_s_fields).pack(pady=5)
        staff_right = ctk.CTkFrame(self.tab_staff); staff_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.s_search = ctk.CTkEntry(staff_right, placeholder_text="Search Staff by ID, Name, or Role..."); self.s_search.pack(fill="x", padx=10, pady=10)
        self.s_search.bind("<KeyRelease>", lambda e: self.load_staff(self.s_search.get()))
        s_cols = ("ID", "Name", "Role", "Department"); self.s_tree = ttk.Treeview(staff_right, columns=s_cols, show="headings", style="Treeview")
        for c in s_cols: self.s_tree.heading(c, text=c); self.s_tree.column(c, anchor=ctk.CENTER, width=100)
        self.s_tree.pack(expand=True, fill="both", padx=10, pady=10); self.s_tree.bind("<<TreeviewSelect>>", self.select_staff)
    def load_staff(self, term=""):
        for i in self.s_tree.get_children(): self.s_tree.delete(i)
        with connect_db() as conn:
            cursor = conn.cursor()
            if term:
                sql = "SELECT * FROM staff WHERE staff_id LIKE ? OR name LIKE ? OR role LIKE ? OR department LIKE ?"
                params = (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"); cursor.execute(sql, params)
            else: cursor.execute("SELECT * FROM staff")
            for row in cursor.fetchall(): self.s_tree.insert("", "end", values=row)
    def add_staff(self):
        staff_id = self.s_entries["Staff ID"].get(); name = self.s_entries["Name"].get(); role = self.s_entries["Role"].get(); department = self.s_entries["Department"].get()
        data = [staff_id, name, role, department];
        if not all(data): return messagebox.showwarning("Empty", "Fill all fields")
        try:
            with connect_db() as conn: conn.execute("INSERT INTO staff VALUES (?,?,?,?)", data); conn.commit()
            self.load_staff(); self.clear_s_fields()
        except Exception as e: messagebox.showerror("Error", f"Could not add staff: {e}")
    def select_staff(self, event):
        sel = self.s_tree.selection();
        if sel:
            val = self.s_tree.item(sel)['values']; self.clear_s_fields()
            self.s_entries["Staff ID"].insert(0, val[0]); self.s_entries["Staff ID"].configure(state="disabled")
            self.s_entries["Name"].insert(0, val[1]); self.s_entries["Department"].insert(0, val[3]); self.s_entries["Role"].set(val[2])
    def update_staff(self):
        staff_id = self.s_entries["Staff ID"].get(); self.s_entries["Staff ID"].configure(state="normal") 
        data = (self.s_entries["Name"].get(), self.s_entries["Role"].get(), self.s_entries["Department"].get(), staff_id)
        with connect_db() as conn: conn.execute("UPDATE staff SET name=?, role=?, department=? WHERE staff_id=?", data); conn.commit()
        self.load_staff(); self.clear_s_fields()
    def delete_staff(self):
        staff_id = self.s_entries["Staff ID"].get();
        if not staff_id: return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete staff ID: {staff_id}?"):
            with connect_db() as conn: conn.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,)); conn.commit()
            self.load_staff(); self.clear_s_fields()
    def clear_s_fields(self):
        for key, widget in self.s_entries.items():
            if key == "Role": widget.set("Doctor")
            else: widget.configure(state="normal"); widget.delete(0, 'end')

    # ----------------------------------------------------------------
    # NEW: BILLING & PRESCRIPTION SECTION
    # ----------------------------------------------------------------
    def setup_billing_ui(self):
        self.tab_billing.grid_columnconfigure(1, weight=1)
        self.tab_billing.grid_rowconfigure(0, weight=1)

        # Left Frame (Prescription Input)
        bill_left = ctk.CTkFrame(self.tab_billing, width=350)
        bill_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsw")
        ctk.CTkLabel(bill_left, text="Prescription / Billing", font=("Arial", 18, "bold")).pack(pady=15)

        self.b_entries = {}
        fields = ["Patient ID", "Med ID", "Quantity", "Total Cost"]
        
        for field in fields:
            ctk.CTkLabel(bill_left, text=field).pack(anchor="w", padx=20)
            ent = ctk.CTkEntry(bill_left, width=250)
            ent.pack(pady=(0, 10), padx=20)
            self.b_entries[field] = ent
        
        # Total Cost field should be disabled (calculated)
        self.b_entries["Total Cost"].configure(state="disabled")
        
        # Button to calculate cost and reduce stock
        ctk.CTkButton(bill_left, text="Dispense & Bill", fg_color="#3B8ED4", hover_color="#276FA6", command=self.dispense_and_bill).pack(pady=15)
        ctk.CTkButton(bill_left, text="Clear Fields", command=self.clear_b_fields).pack(pady=5)
        
        # Button to look up Patient/Med Info
        ctk.CTkButton(bill_left, text="Look up Patient Info", command=self.lookup_patient).pack(pady=(20, 5))
        ctk.CTkButton(bill_left, text="Look up Medicine Price", command=self.lookup_medicine).pack(pady=5)

        # Right Frame (Prescriptions List)
        bill_right = ctk.CTkFrame(self.tab_billing)
        bill_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(bill_right, text="Transaction History", font=("Arial", 16, "bold")).pack(pady=10, anchor="w")

        b_cols = ("Bill ID", "Patient ID", "Med ID", "Qty Dispensed", "Total Cost")
        self.b_tree = ttk.Treeview(bill_right, columns=b_cols, show="headings", style="Treeview")
        for c in b_cols: 
            self.b_tree.heading(c, text=c)
            self.b_tree.column(c, anchor=ctk.CENTER, width=100)
        
        self.b_tree.pack(expand=True, fill="both", padx=10, pady=10)

    def dispense_and_bill(self):
        # 1. Gather Data and Validate
        pid = self.b_entries["Patient ID"].get()
        mid = self.b_entries["Med ID"].get()
        qty_str = self.b_entries["Quantity"].get()
        
        if not all([pid, mid, qty_str]):
            return messagebox.showwarning("Input Error", "Patient ID, Medicine ID, and Quantity must be filled.")
        
        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except ValueError:
            return messagebox.showwarning("Input Error", "Quantity must be a positive integer.")

        with connect_db() as conn:
            cursor = conn.cursor()
            try:
                # 2. Check Medicine Stock and Price
                cursor.execute("SELECT quantity, price FROM inventory WHERE med_id=?", (mid,))
                med_data = cursor.fetchone()
                
                if not med_data:
                    return messagebox.showerror("Error", f"Medicine ID {mid} not found in inventory.")
                
                current_stock, unit_price = med_data
                
                if current_stock < qty:
                    return messagebox.showwarning("Stock Error", f"Insufficient stock. Available: {current_stock}.")
                
                # 3. Calculate Cost
                total_cost = unit_price * qty
                
                # 4. Perform Transaction (Two-step integrity: record and update)
                
                # Step 4a: Record the Prescription/Bill
                cursor.execute(
                    "INSERT INTO prescriptions (patient_id, med_id, quantity_dispensed, total_cost) VALUES (?, ?, ?, ?)",
                    (pid, mid, qty, total_cost)
                )
                
                # Step 4b: Update Inventory (Reduce Stock)
                new_stock = current_stock - qty
                cursor.execute(
                    "UPDATE inventory SET quantity=? WHERE med_id=?",
                    (new_stock, mid)
                )
                
                conn.commit()
                
                # 5. Display Result
                self.b_entries["Total Cost"].configure(state="normal")
                self.b_entries["Total Cost"].delete(0, 'end')
                self.b_entries["Total Cost"].insert(0, f"₹{total_cost:.2f}")
                self.b_entries["Total Cost"].configure(state="disabled")
                
                messagebox.showinfo("Success", f"Dispensed {qty}x {mid} to Patient {pid}. Total Cost: ₹{total_cost:.2f}. Stock updated.")
                
                # 6. Reload Tables
                self.load_prescriptions()
                self.load_inventory() # To update the stock view
                self.clear_b_fields(keep_cost=True)
                
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Transaction Failed", f"An error occurred: {e}")

    def load_prescriptions(self):
        for i in self.b_tree.get_children(): self.b_tree.delete(i)
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prescriptions ORDER BY bill_id DESC")
            for row in cursor.fetchall():
                self.b_tree.insert("", "end", values=row)

    def lookup_patient(self):
        pid = self.b_entries["Patient ID"].get()
        if not pid: return messagebox.showwarning("Lookup", "Please enter a Patient ID first.")
        
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, disease FROM patients WHERE id=?", (pid,))
            patient_data = cursor.fetchone()
            
            if patient_data:
                messagebox.showinfo("Patient Found", f"Name: {patient_data[0]}\nDisease: {patient_data[1]}")
            else:
                messagebox.showwarning("Not Found", f"Patient ID {pid} not found.")

    def lookup_medicine(self):
        mid = self.b_entries["Med ID"].get()
        if not mid: return messagebox.showwarning("Lookup", "Please enter a Medicine ID first.")
        
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, quantity, price FROM inventory WHERE med_id=?", (mid,))
            med_data = cursor.fetchone()
            
            if med_data:
                name, qty, price = med_data
                messagebox.showinfo("Medicine Info", f"Name: {name}\nStock: {qty}\nUnit Price: ₹{price:.2f}")
            else:
                messagebox.showwarning("Not Found", f"Medicine ID {mid} not found.")

    def clear_b_fields(self, keep_cost=False):
        for key, widget in self.b_entries.items():
            if key == "Total Cost":
                widget.configure(state="normal")
                if not keep_cost: widget.delete(0, 'end')
                widget.configure(state="disabled")
            else:
                widget.delete(0, 'end')
    
    def on_closing(self):
        """Handles closing the main dashboard."""
        if messagebox.askyesno("Exit System", "Are you sure you want to shut down the Hospital Management System?"):
            self.master.destroy()

# ====================================================================
# START
# ====================================================================
if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
