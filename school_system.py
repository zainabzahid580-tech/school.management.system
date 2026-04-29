import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re
from datetime import datetime

# ==========================================
# DATABASE SETUP (SQLITE)
# ==========================================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("school.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                father_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                class_name TEXT NOT NULL,
                address TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                subject TEXT NOT NULL,
                qualification TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_roll TEXT NOT NULL,
                student_name TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_roll TEXT NOT NULL,
                student_name TEXT NOT NULL,
                month TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        # Inject default admin
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'Admin123'))
            
        self.conn.commit()

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        # Convert to dictionary-like format for compatibility
        columns = [column[0] for column in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()
        if row:
            columns = [column[0] for column in self.cursor.description]
            return dict(zip(columns, row))
        return None

# ==========================================
# VALIDATION UTILS
# ==========================================
def validate_required(value):
    return bool(value and str(value).strip())

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def validate_phone(phone):
    return re.match(r'^03\d{9}$', phone) is not None

def validate_name(name):
    return re.match(r'^[a-zA-Z\s]+$', name) is not None and validate_required(name)

def validate_numeric(value):
    try:
        val = float(value)
        return val > 0
    except ValueError:
        return False

# ==========================================
# STYLING
# ==========================================
def apply_style():
    style = ttk.Style()
    style.theme_use("clam")
    
    # Colors
    BG_COLOR = "#f4f6f9"
    PRIMARY = "#007bff"
    TEXT = "#333333"

    style.configure(".", background=BG_COLOR, foreground=TEXT, font=("Helvetica", 12))
    style.configure("TFrame", background=BG_COLOR)
    style.configure("Card.TFrame", background="white", borderwidth=1, relief="groove")
    
    style.configure("Title.TLabel", font=("Helvetica", 24, "bold"), foreground=PRIMARY, background=BG_COLOR)
    style.configure("Heading.TLabel", font=("Helvetica", 16, "bold"), background="white")
    style.configure("TLabel", background=BG_COLOR)
    style.configure("Card.TLabel", background="white")
    
    style.configure("TButton", font=("Helvetica", 12, "bold"), padding=5)
    style.configure("Success.TButton", background="#28a745", foreground="white")
    style.configure("Danger.TButton", background="#dc3545", foreground="white")
    style.configure("Secondary.TButton", background="#6c757d", foreground="white")
    
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
    
def center_window(window, width, height):
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# ==========================================
# VIEWS
# ==========================================
class LoginView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.create_widgets()

    def create_widgets(self):
        card = ttk.Frame(self, style="Card.TFrame", padding=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="School Management System", style="Title.TLabel", background="white").grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(card, text="Username:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.username_var, width=30).grid(row=1, column=1, pady=5)

        ttk.Label(card, text="Password:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(card, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, pady=5)

        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Login", command=self.login, style="Success.TButton").pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Exit", command=self.controller.quit, style="Danger.TButton").pack(side="left", padx=10)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        user = self.db.fetch_one("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        
        if user:
            self.username_var.set("")
            self.password_var.set("")
            self.controller.show_view("DashboardView")
        else:
            messagebox.showerror("Error", "Invalid credentials.")

class DashboardView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.create_widgets()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.update_summaries()

    def update_summaries(self):
        students = self.db.fetch_one("SELECT COUNT(*) as c FROM students")['c']
        teachers = self.db.fetch_one("SELECT COUNT(*) as c FROM teachers")['c']
        fees = self.db.fetch_one("SELECT SUM(amount) as s FROM fees WHERE status='Paid'")['s'] or 0.0
        
        self.stu_var.set(str(students))
        self.tea_var.set(str(teachers))
        self.fee_var.set(f"${fees:.2f}")

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=20, padx=20)
        ttk.Label(header, text="Dashboard", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Logout", command=lambda: self.controller.show_view("LoginView"), style="Danger.TButton").pack(side="right")

        summary = ttk.Frame(self)
        summary.pack(fill="x", padx=20)
        
        self.stu_var = tk.StringVar()
        self.tea_var = tk.StringVar()
        self.fee_var = tk.StringVar()
        
        for i, (title, var) in enumerate([("Total Students", self.stu_var), ("Total Teachers", self.tea_var), ("Fees Collected", self.fee_var)]):
            card = ttk.Frame(summary, style="Card.TFrame", padding=20)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            summary.grid_columnconfigure(i, weight=1)
            ttk.Label(card, text=title, style="Heading.TLabel").pack()
            ttk.Label(card, textvariable=var, font=("Helvetica", 20, "bold"), foreground="#007bff", background="white").pack(pady=10)

        nav = ttk.Frame(self)
        nav.pack(fill="both", expand=True, padx=20, pady=20)
        
        buttons = [
            ("Student Management", "StudentView"), ("Teacher Management", "TeacherView"),
            ("Attendance Tracking", "AttendanceView"), ("Fee Management", "FeeView"),
            ("Reports", "ReportsView")
        ]
        for i, (text, view) in enumerate(buttons):
            ttk.Button(nav, text=text, command=lambda v=view: self.controller.show_view(v)).grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew", ipady=20)
            nav.grid_columnconfigure(i%3, weight=1)

class StudentView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.create_widgets()
        self.load_data()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_data()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=20)
        ttk.Label(header, text="Student Management", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Back", command=lambda: self.controller.show_view("DashboardView"), style="Secondary.TButton").pack(side="right")

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        form = ttk.Frame(content, style="Card.TFrame", padding=20)
        form.pack(side="left", fill="y", padx=(0, 20))

        self.vars = {f: tk.StringVar() for f in ["Roll Number", "Full Name", "Father Name", "Email", "Phone", "Class"]}
        self.address_text = tk.Text(form, height=4, width=30, font=("Helvetica", 12))

        for i, field in enumerate(self.vars.keys()):
            ttk.Label(form, text=field+":", style="Card.TLabel").grid(row=i, column=0, sticky="w", pady=5)
            ttk.Entry(form, textvariable=self.vars[field], width=30).grid(row=i, column=1, pady=5)
            
        ttk.Label(form, text="Address:", style="Card.TLabel").grid(row=6, column=0, sticky="w", pady=5)
        self.address_text.grid(row=6, column=1, pady=5)

        btns = ttk.Frame(form, style="Card.TFrame")
        btns.grid(row=7, column=0, columnspan=2, pady=20)
        ttk.Button(btns, text="Add", command=self.add, style="Success.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Update", command=self.update).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete", command=self.delete, style="Danger.TButton").grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Clear", command=self.clear, style="Secondary.TButton").grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btns, text="View All", command=self.load_data).grid(row=1, column=1, padx=5, pady=5)

        tree_frame = ttk.Frame(content)
        tree_frame.pack(side="right", fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("Roll", "Name", "Father", "Email", "Phone", "Class", "Address"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_select)

    def get_data(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        data["Address"] = self.address_text.get("1.0", tk.END).strip()
        
        if not all(validate_required(v) for v in data.values()):
            messagebox.showerror("Error", "All fields are required")
            return None
        if not validate_name(data["Full Name"]):
            messagebox.showerror("Error", "Invalid name format")
            return None
        if not validate_phone(data["Phone"]):
            messagebox.showerror("Error", "Phone must be 11 digits starting with 03")
            return None
        return data

    def add(self):
        data = self.get_data()
        if data:
            if self.db.execute_query("INSERT INTO students (roll_number, full_name, father_name, email, phone, class_name, address) VALUES (?,?,?,?,?,?,?)",
                                     (data["Roll Number"], data["Full Name"], data["Father Name"], data["Email"], data["Phone"], data["Class"], data["Address"])):
                messagebox.showinfo("Success", "Added successfully")
                self.load_data()
                self.clear()

    def update(self):
        data = self.get_data()
        if data:
            if self.db.execute_query("UPDATE students SET full_name=?, father_name=?, email=?, phone=?, class_name=?, address=? WHERE roll_number=?",
                                     (data["Full Name"], data["Father Name"], data["Email"], data["Phone"], data["Class"], data["Address"], data["Roll Number"])):
                messagebox.showinfo("Success", "Updated successfully")
                self.load_data()
                self.clear()

    def delete(self):
        roll = self.vars["Roll Number"].get().strip()
        if roll and messagebox.askyesno("Confirm", "Delete student?"):
            self.db.execute_query("DELETE FROM students WHERE roll_number=?", (roll,))
            self.load_data()
            self.clear()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.fetch_all("SELECT * FROM students"):
            self.tree.insert("", "end", values=(row['roll_number'], row['full_name'], row['father_name'], row['email'], row['phone'], row['class_name'], row['address']))

    def clear(self):
        for v in self.vars.values(): v.set("")
        self.address_text.delete("1.0", tk.END)

    def on_select(self, event):
        sel = self.tree.focus()
        if sel:
            vals = self.tree.item(sel, "values")
            for i, key in enumerate(self.vars.keys()):
                self.vars[key].set(vals[i])
            self.address_text.delete("1.0", tk.END)
            self.address_text.insert(tk.END, vals[6])

class TeacherView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.sel_id = None
        self.create_widgets()
        self.load_data()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_data()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=20)
        ttk.Label(header, text="Teacher Management", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Back", command=lambda: self.controller.show_view("DashboardView"), style="Secondary.TButton").pack(side="right")

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        form = ttk.Frame(content, style="Card.TFrame", padding=20)
        form.pack(side="left", fill="y", padx=(0, 20))

        self.vars = {f: tk.StringVar() for f in ["Full Name", "Email", "Phone", "Subject", "Qualification"]}
        for i, field in enumerate(self.vars.keys()):
            ttk.Label(form, text=field+":", style="Card.TLabel").grid(row=i, column=0, sticky="w", pady=5)
            ttk.Entry(form, textvariable=self.vars[field], width=30).grid(row=i, column=1, pady=5)

        btns = ttk.Frame(form, style="Card.TFrame")
        btns.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(btns, text="Add", command=self.add, style="Success.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Update", command=self.update).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete", command=self.delete, style="Danger.TButton").grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Clear", command=self.clear, style="Secondary.TButton").grid(row=1, column=0, padx=5, pady=5)

        tree_frame = ttk.Frame(content)
        tree_frame.pack(side="right", fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Email", "Phone", "Subject", "Qual"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("ID", width=50)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_select)

    def get_data(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        if not all(validate_required(v) for v in data.values()):
            messagebox.showerror("Error", "All fields are required")
            return None
        return data

    def add(self):
        data = self.get_data()
        if data and self.db.execute_query("INSERT INTO teachers (full_name, email, phone, subject, qualification) VALUES (?,?,?,?,?)",
                                          (data["Full Name"], data["Email"], data["Phone"], data["Subject"], data["Qualification"])):
            messagebox.showinfo("Success", "Added successfully")
            self.load_data()
            self.clear()

    def update(self):
        data = self.get_data()
        if data and self.sel_id and self.db.execute_query("UPDATE teachers SET full_name=?, email=?, phone=?, subject=?, qualification=? WHERE id=?",
                                                          (data["Full Name"], data["Email"], data["Phone"], data["Subject"], data["Qualification"], self.sel_id)):
            messagebox.showinfo("Success", "Updated successfully")
            self.load_data()
            self.clear()

    def delete(self):
        if self.sel_id and messagebox.askyesno("Confirm", "Delete teacher?"):
            self.db.execute_query("DELETE FROM teachers WHERE id=?", (self.sel_id,))
            self.load_data()
            self.clear()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.fetch_all("SELECT * FROM teachers"):
            self.tree.insert("", "end", values=(row['id'], row['full_name'], row['email'], row['phone'], row['subject'], row['qualification']))

    def clear(self):
        self.sel_id = None
        for v in self.vars.values(): v.set("")

    def on_select(self, event):
        sel = self.tree.focus()
        if sel:
            vals = self.tree.item(sel, "values")
            self.sel_id = vals[0]
            for i, key in enumerate(self.vars.keys()):
                self.vars[key].set(vals[i+1])

class AttendanceView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.create_widgets()
        self.vars["Date"].set(datetime.now().strftime("%Y-%m-%d"))

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=20)
        ttk.Label(header, text="Attendance", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Back", command=lambda: self.controller.show_view("DashboardView"), style="Secondary.TButton").pack(side="right")

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        form = ttk.Frame(content, style="Card.TFrame", padding=20)
        form.pack(side="left", fill="y", padx=(0, 20))

        self.vars = {"Roll": tk.StringVar(), "Name": tk.StringVar(), "Date": tk.StringVar(), "Status": tk.StringVar(value="Present")}
        
        ttk.Label(form, text="Roll Number:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Roll"]).grid(row=0, column=1, pady=5)
        self.vars["Roll"].trace_add("write", self.fetch_name)

        ttk.Label(form, text="Name:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Name"], state="readonly").grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Date:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Date"]).grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Status:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Combobox(form, textvariable=self.vars["Status"], values=["Present", "Absent", "Leave"], state="readonly").grid(row=3, column=1, pady=5)

        btns = ttk.Frame(form, style="Card.TFrame")
        btns.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btns, text="Mark", command=self.mark, style="Success.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="View Date", command=self.view_date).grid(row=0, column=1, padx=5)

        tree_frame = ttk.Frame(content)
        tree_frame.pack(side="right", fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Roll", "Name", "Date", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(side="left", fill="both", expand=True)

    def fetch_name(self, *args):
        roll = self.vars["Roll"].get().strip()
        student = self.db.fetch_one("SELECT full_name FROM students WHERE roll_number=?", (roll,))
        self.vars["Name"].set(student['full_name'] if student else "")

    def mark(self):
        roll, name, date, status = [self.vars[k].get() for k in ["Roll", "Name", "Date", "Status"]]
        if not name:
            messagebox.showerror("Error", "Invalid Roll Number")
            return
            
        existing = self.db.fetch_one("SELECT id FROM attendance WHERE student_roll=? AND date=?", (roll, date))
        if existing:
            self.db.execute_query("UPDATE attendance SET status=? WHERE id=?", (status, existing['id']))
        else:
            self.db.execute_query("INSERT INTO attendance (student_roll, student_name, date, status) VALUES (?,?,?,?)", (roll, name, date, status))
        messagebox.showinfo("Success", "Attendance Marked")
        self.view_date()

    def view_date(self):
        date = self.vars["Date"].get()
        self.tree.delete(*self.tree.get_children())
        for row in self.db.fetch_all("SELECT * FROM attendance WHERE date=?", (date,)):
            self.tree.insert("", "end", values=(row['id'], row['student_roll'], row['student_name'], row['date'], row['status']))

class FeeView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.sel_id = None
        self.create_widgets()
        self.load_data()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_data()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=20)
        ttk.Label(header, text="Fees", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Back", command=lambda: self.controller.show_view("DashboardView"), style="Secondary.TButton").pack(side="right")

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        form = ttk.Frame(content, style="Card.TFrame", padding=20)
        form.pack(side="left", fill="y", padx=(0, 20))

        self.vars = {"Roll": tk.StringVar(), "Name": tk.StringVar(), "Month": tk.StringVar(value=datetime.now().strftime("%B %Y")), "Amount": tk.StringVar(), "Status": tk.StringVar(value="Paid")}
        
        ttk.Label(form, text="Roll Number:", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Roll"]).grid(row=0, column=1, pady=5)
        self.vars["Roll"].trace_add("write", self.fetch_name)

        ttk.Label(form, text="Name:", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Name"], state="readonly").grid(row=1, column=1, pady=5)

        ttk.Label(form, text="Month:", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Month"]).grid(row=2, column=1, pady=5)

        ttk.Label(form, text="Amount:", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(form, textvariable=self.vars["Amount"]).grid(row=3, column=1, pady=5)

        ttk.Label(form, text="Status:", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=5)
        ttk.Combobox(form, textvariable=self.vars["Status"], values=["Paid", "Unpaid"], state="readonly").grid(row=4, column=1, pady=5)

        btns = ttk.Frame(form, style="Card.TFrame")
        btns.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(btns, text="Add", command=self.add, style="Success.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Update", command=self.update).grid(row=0, column=1, padx=5)
        ttk.Button(btns, text="Delete", command=self.delete, style="Danger.TButton").grid(row=0, column=2, padx=5)
        ttk.Button(btns, text="Clear", command=self.clear, style="Secondary.TButton").grid(row=1, column=0, padx=5, pady=5)

        tree_frame = ttk.Frame(content)
        tree_frame.pack(side="right", fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Roll", "Name", "Month", "Amount", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_select)

    def fetch_name(self, *args):
        roll = self.vars["Roll"].get().strip()
        student = self.db.fetch_one("SELECT full_name FROM students WHERE roll_number=?", (roll,))
        self.vars["Name"].set(student['full_name'] if student else "")

    def add(self):
        roll, name, month, amount, status = [self.vars[k].get() for k in ["Roll", "Name", "Month", "Amount", "Status"]]
        if not name or not validate_numeric(amount):
            messagebox.showerror("Error", "Invalid inputs")
            return
        if self.db.execute_query("INSERT INTO fees (student_roll, student_name, month, amount, status) VALUES (?,?,?,?,?)", (roll, name, month, amount, status)):
            messagebox.showinfo("Success", "Payment Added")
            self.load_data()
            self.clear()

    def update(self):
        if self.sel_id and self.db.execute_query("UPDATE fees SET amount=?, status=? WHERE id=?", (self.vars["Amount"].get(), self.vars["Status"].get(), self.sel_id)):
            messagebox.showinfo("Success", "Updated")
            self.load_data()
            self.clear()

    def delete(self):
        if self.sel_id and messagebox.askyesno("Confirm", "Delete payment?"):
            self.db.execute_query("DELETE FROM fees WHERE id=?", (self.sel_id,))
            self.load_data()
            self.clear()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.fetch_all("SELECT * FROM fees"):
            self.tree.insert("", "end", values=(row['id'], row['student_roll'], row['student_name'], row['month'], row['amount'], row['status']))

    def clear(self):
        self.sel_id = None
        for k in ["Roll", "Amount"]: self.vars[k].set("")
        self.vars["Status"].set("Paid")

    def on_select(self, event):
        sel = self.tree.focus()
        if sel:
            vals = self.tree.item(sel, "values")
            self.sel_id = vals[0]
            self.vars["Roll"].set(vals[1])
            self.vars["Month"].set(vals[3])
            self.vars["Amount"].set(vals[4])
            self.vars["Status"].set(vals[5])

class ReportsView(ttk.Frame):
    def __init__(self, parent, controller, db):
        super().__init__(parent)
        self.controller = controller
        self.db = db
        self.create_widgets()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_data()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=20)
        ttk.Label(header, text="Reports", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Back", command=lambda: self.controller.show_view("DashboardView"), style="Secondary.TButton").pack(side="right")

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Label(content, text="Defaulters List (Unpaid Fees)", style="Heading.TLabel").pack(anchor="w")
        tree_frame = ttk.Frame(content)
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Roll", "Name", "Month", "Amount"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(side="left", fill="both", expand=True)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.db.fetch_all("SELECT * FROM fees WHERE status='Unpaid'"):
            self.tree.insert("", "end", values=(row['student_roll'], row['student_name'], row['month'], row['amount']))

# ==========================================
# MAIN APP
# ==========================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Management System")
        self.geometry("1000x700")
        
        apply_style()
        self.db = Database()
        
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginView, DashboardView, StudentView, TeacherView, AttendanceView, FeeView, ReportsView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, db=self.db)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_view("LoginView")
        center_window(self, 1000, 700)

    def show_view(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
