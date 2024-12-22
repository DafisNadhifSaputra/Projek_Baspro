import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime
from PIL import Image, ImageTk
import os
print("halo aron")

print("halo mahesa!!")
class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🐾 Main Login 🐾")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#f0f0f0")
        
        self.create_widgets()
        
    def create_widgets(self):

        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        

        title_label = tk.Label(
            main_frame,
            text="🐾 Kantin UNESA 🐾",
            font=("Helvetica", 30, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=10)
        
       
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(fill=tk.BOTH, expand=True, pady=50)
        
        
        ttk.Label(login_frame, text="Email:", font=("Helvetica", 10, "bold")).pack(pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.configure(width=100)
        self.username_entry.pack(pady=15)
        self.username_entry.pack(ipady=10)
        
        
        ttk.Label(login_frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(pady=5, ipady=10)
        self.password_entry.configure(width=100)
        
        
        login_button = ttk.Button(
            login_frame,
            text="Login",
            command=self.login
        )
        login_button.pack(pady=20)
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            users_path = os.path.join(script_dir, "users.json")
            with open(users_path, "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Database User tidak ditemukan")
            return

        # Check if admin login
        admin_accounts = ['admin1', 'admin2', 'admin3', 'admin4']
        if username in admin_accounts:
            if username in users and users[username]["password"] == password:
                messagebox.showinfo("Success", "Login Admin Successful!")
                self.window.destroy()
                root = tk.Tk()
                app = AdminWindow(root, username)
                root.mainloop()
            else:
                messagebox.showerror("Error", "Invalid admin credentials!")
            return

        # Regular user login
        if username in users:
            if users[username]["password"] == password:
                messagebox.showinfo("Success", "Login Mahasiswa successful!")
                self.window.destroy()
                root = tk.Tk()
                app = pilih_kedai(root, username, users[username]["balance"])
                root.mainloop()
            else:
                messagebox.showerror("Error", "Invalid password!")
        else:
            messagebox.showerror("Error", "Username not found!")

class AdminWindow:
    def __init__(self, root, admin_id):
        self.root = root
        self.root.title(f"Admin Dashboard - {admin_id}")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f0f0")

        self.admin_id = admin_id
        self.store_name = self.get_store_name(admin_id)
        self.transactions = self.load_transactions()

        # Data produk untuk setiap toko (Anda dapat memindahkannya ke file JSON terpisah jika perlu)
        self.products = {
            "Stupid Chicken": {
                "Nasi Ayam Lada Hitam": {"price": 12000},
                "Nasi Ayam Sambal Matah": {"price": 12000},
                "Royal Canin": {"price": 150000},
                "Whiskas": {"price": 85000},
                "Kandang Premium": {"price": 750000},
                "Mainan Kucing": {"price": 45000}
            },
            "Bakso Bakar": {
                # ... (produk untuk Bakso Bakar, sesuaikan)
                "Bakso Bakar Original": {"price": 15000},
                "Bakso Bakar Pedas": {"price": 17000},
                "Es Teh Manis": {"price": 5000}
            },
            "Mie Setan": {
                # ... (produk untuk Mie Setan, sesuaikan)
                "Mie Setan Level 1": {"price": 12000},
                "Mie Setan Level 3": {"price": 15000},
                "Mie Setan Level 5": {"price": 18000},
                "Es Jeruk": {"price": 6000}
            },
            "Geprek Bensu": {
                # ... (produk untuk Geprek Bensu, sesuaikan)
                "Ayam Geprek Original": {"price": 15000},
                "Ayam Geprek Keju": {"price": 20000},
                "Nasi Putih": {"price": 5000},
                "Es Teh Tawar": {"price": 4000}
            }
        }

        self.create_widgets()

    def get_store_name(self, admin_id):
        store_mapping = {
            "admin1": "Stupid Chicken",
            "admin2": "Bakso Bakar",
            "admin3": "Mie Setan",
            "admin4": "Geprek Bensu"
        }
        return store_mapping.get(admin_id, "Unknown Store")

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, pady=10, padx=20)

        tk.Label(
            header_frame,
            text=f"{self.store_name} - Dashboard",
            font=("Helvetica", 24, "bold")
        ).pack(side=tk.LEFT)

        # Orders Table
        orders_frame = ttk.Frame(self.root)
        orders_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("datetime", "username", "items", "total", "Status")
        self.orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings")

        for col in columns:
            self.orders_tree.heading(col, text=col)

        scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons Frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill=tk.X, pady=10, padx=20)

        ttk.Button(
            buttons_frame,
            text="Refresh Orders",
            command=self.refresh_orders
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Update Status",
            command=self.update_order_status
        ).pack(side=tk.LEFT, padx=5)

        self.refresh_orders()

    def load_transactions(self):
        try:
            # Dapatkan path absolut ke direktori tempat script ini berada
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Gabungkan dengan nama file transactions.json
            transactions_path = os.path.join(script_dir, "transactions.json")
            print(f"Loading transactions from: {transactions_path}")  # Cetak path untuk debugging
            with open(transactions_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def refresh_orders(self):
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Reload transactions
        self.transactions = self.load_transactions()

        # Filter and display orders for this store
        for transaction in self.transactions:
            # Periksa apakah transaksi berasal dari toko yang sesuai
            if any(item in self.products[self.store_name] for item in transaction["items"].keys()):
                # Ambil semua item dari transaksi
                items_str = ", ".join(f"{k}({v})" for k, v in transaction["items"].items())

                self.orders_tree.insert("", tk.END, values=(
                    transaction["datetime"],
                    transaction.get("username", "Unknown"),
                    items_str,
                    f"Rp {transaction['total']:,}",
                    transaction.get("status", "Pending")
                ))

    def update_order_status(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order to update")
            return

        status_window = tk.Toplevel(self.root)
        status_window.title("Update Status")
        status_window.geometry("300x150")

        status_var = tk.StringVar(value="Processing")
        statuses = ["Processing", "Ready", "Completed", "Cancelled"]

        for status in statuses:
            ttk.Radiobutton(
                status_window,
                text=status,
                value=status,
                variable=status_var
            ).pack(pady=5)

        def update():
            new_status = status_var.get()
            item = selected[0]
            transaction_date = self.orders_tree.item(item)["values"][0]

            # Update in treeview
            values = list(self.orders_tree.item(item)["values"])
            values[-1] = new_status
            self.orders_tree.item(item, values=values)

            # Update in transactions.json
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "transactions.json")
            for transaction in self.transactions:
                if transaction["datetime"] == transaction_date:
                    transaction["status"] = new_status

            with open(transactions_path, "w") as f:
                json.dump(self.transactions, f)

            status_window.destroy()
            messagebox.showinfo("Success", "Order status updated successfully!")

        ttk.Button(
            status_window,
            text="Update",
            command=update
        ).pack(pady=10)

class pilih_kedai:
    def __init__(self, root, username, balance):
        self.root = root
        self.root.title("Pilih Kedai")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f0f0")

        self.username = username
        self.balance = balance
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            main_frame,
            text="Pilih Kedai UNESA",
            font=("Helvetica", 30, "bold"),
            bg="#f0f0f0"
        )
        title_label.pack(pady=20)

        # Balance display
        balance_label = tk.Label(
            main_frame,
            text=f"Saldo: Rp {self.balance:,}",
            font=("Helvetica", 14),
            bg="#f0f0f0"
        )
        balance_label.pack(pady=10)

        # Store buttons frame
        stores_frame = ttk.Frame(main_frame)
        stores_frame.pack(pady=50)

        # Create grid for store buttons
        stores = [
            ("Stupid Chicken", self.open_stupid_chicken),
            ("Bakso Bakar", self.open_bakso_bakar),
            ("Mie Setan", self.open_mie_setan),
            ("Geprek Bensu", self.open_geprek_bensu)
        ]

        for idx, (store_name, command) in enumerate(stores):
            row = idx // 2
            col = idx % 2
            
            store_frame = ttk.Frame(stores_frame)
            store_frame.grid(row=row, column=col, padx=20, pady=20)

            # Try to load store logo
            try:
                image = Image.open(f"images/{store_name.lower().replace(' ', '_')}.png")
                image = image.resize((200, 200))
                photo = ImageTk.PhotoImage(image)
                logo = tk.Label(store_frame, image=photo)
                logo.image = photo
                logo.pack(pady=10)
            except:
                # If image not found, show text only
                pass

            tk.Button(
                store_frame,
                text=store_name,
                font=("Helvetica", 12, "bold"),
                width=20,
                height=2,
                command=command
            ).pack()

    def open_stupid_chicken(self):
        self.root.destroy()
        root = tk.Tk()
        app = Stupid_chicken(root, self.username, self.balance)
        root.mainloop()

    def open_bakso_bakar(self):
        self.root.destroy()
        root = tk.Tk()
        app = Bakso_bakar(root, self.username, self.balance)
        root.mainloop()

    def open_mie_setan(self):
        self.root.destroy()
        root = tk.Tk()
        app = Mie_setan(root, self.username, self.balance)
        root.mainloop()

    def open_geprek_bensu(self):
        self.root.destroy()
        root = tk.Tk()
        app = Geprek_bensu(root, self.username, self.balance)
        root.mainloop()
        

class Stupid_chicken:
    def __init__(self, root, username, initial_balance):
        self.root = root
        self.root.title("🐾 Stupid Chicken 🐾")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#f0f0f0")
        
        self.username = username
        self.current_balance = initial_balance
        
        # Menyiapkan cache untuk gambar
        self.image_cache = {}
        
        # Data produk dengan path gambar
        self.products = {
            "Nasi Ayam Lada Hitam": {
                "price": 12000,
                "stock": True,
                "category": "Makanan",
                "image": "images/stupidchiken_ladahitam.jpg"
            },
            "Nasi Ayam Sambal Matah": {
                "price": 12000,
                "stock": "Ada",
                "category": "Makanan",
                "image": "images/stupidchiken_sambalmatah.jpeg"
            },
            "Royal Canin": {
                "price": 150000,
                "stock": 20,
                "category": "Makanan",
                "image": "images/royal_canin.jpg"
            },
            "Whiskas": {
                "price": 85000,
                "stock": 30,
                "category": "Makanan",
                "image": "images/whiskas.jpg"
            },
            "Kandang Premium": {
                "price": 750000,
                "stock": 10,
                "category": "Aksesoris",
                "image": "images/cage.jpg"
            },
            "Mainan Kucing": {
                "price": 45000,
                "stock": 25,
                "category": "Aksesoris",
                "image": "images/toy.jpg"
            },
        }
        
        self.cart = {}
        self.create_widgets()
        self.load_transaction_history()
        
    def create_widgets(self):
        # Frame utama dengan proporsi 70-30
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header Frame
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(header_frame, 
                text="Stupid Chicken", 
                font=("Helvetica", 24, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.balance_label = tk.Label(header_frame,
                                    text=f"Saldo: Rp {self.current_balance:,}",
                                    font=("Helvetica", 12))
        self.balance_label.pack(side=tk.RIGHT, padx=10)
        
        # Container untuk produk dan keranjang
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame produk (kiri, 70%)
        product_frame = ttk.Frame(content_frame)
        product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Filter Frame
        filter_frame = ttk.Frame(product_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        categories = ["Semua", "Minuman", "Makanan"]
        self.category_var = tk.StringVar(value="Semua")
        for category in categories:
            ttk.Radiobutton(filter_frame, text=category, value=category,
                          variable=self.category_var,
                          command=self.filter_products).pack(side=tk.LEFT, padx=5)
        
        # Scrollable Product Frame
        product_scroll = ttk.Frame(product_frame)
        product_scroll.pack(fill=tk.BOTH, expand=True)
        
        self.product_canvas = tk.Canvas(product_scroll)
        scrollbar = ttk.Scrollbar(product_scroll, orient="vertical", 
                                command=self.product_canvas.yview)
        
        self.product_grid = ttk.Frame(self.product_canvas)
        
        self.product_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_frame = self.product_canvas.create_window(
            (0, 0),
            window=self.product_grid,
            anchor="w",
            width=self.product_canvas.winfo_reqwidth()
        )
        
        # Frame keranjang (kanan, 30%)
        cart_frame = ttk.Frame(content_frame)
        cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        
        tk.Label(cart_frame, text="🛒 Keranjang Belanja",
                font=("Helvetica", 14, "bold")).pack(pady=10)
        
        self.cart_text = tk.Text(cart_frame, height=15, width=35)
        self.cart_text.pack(padx=10, pady=5)
        
        self.total_label = tk.Label(cart_frame, text="Total: Rp 0",
                                  font=("Helvetica", 12, "bold"))
        self.total_label.pack(pady=5)
        
        ttk.Button(cart_frame, text="Checkout",
                  command=self.checkout).pack(pady=5)
        
        ttk.Button(cart_frame, text="Riwayat Transaksi",
                  command=self.show_history).pack(pady=5)
        
        # Bind events
        self.product_grid.bind("<Configure>", self.on_frame_configure)
        self.product_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Tampilkan produk
        self.display_products()

    def load_and_resize_image(self, image_path, size=(150, 150)):
        """Load gambar dan resize sesuai ukuran yang diinginkan"""
        try:
            if image_path not in self.image_cache:
                image = Image.open(image_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_cache[image_path] = photo
            return self.image_cache[image_path]
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return self.get_placeholder_image(size)

    def get_placeholder_image(self, size=(150, 150)):
        """Membuat placeholder image jika gambar tidak ditemukan"""
        if 'placeholder' not in self.image_cache:
            img = Image.new('RGB', size, color='lightgray')
            photo = ImageTk.PhotoImage(img)
            self.image_cache['placeholder'] = photo
        return self.image_cache['placeholder']

    def display_products(self):
        # Hapus produk yang ada
        for widget in self.product_grid.winfo_children():
            widget.destroy()
        
        # Filter produk berdasarkan kategori
        filtered_products = {}
        selected_category = self.category_var.get()
        
        for name, details in self.products.items():
            if selected_category == "Semua" or details["category"] == selected_category:
                filtered_products[name] = details
        
        # Tampilkan produk dalam grid
        row = 0
        col = 0
        for name, details in filtered_products.items():
            product_frame = ttk.Frame(self.product_grid)
            product_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Load dan tampilkan gambar
            image_path = details["image"]
            photo = self.load_and_resize_image(image_path)
            image_label = tk.Label(product_frame, image=photo)
            image_label.image = photo
            image_label.pack(pady=5)
            
            tk.Label(product_frame, text=name,
                    font=("Helvetica", 10, "bold")).pack()
            
            tk.Label(product_frame, 
                    text=f"Rp {details['price']:,}").pack()
            stock = "Ada" if details['stock'] == True else "Habis"
            tk.Label(product_frame,
                    text=f"Stok: {stock}").pack()
            
            # Add quantity control frame
            quantity_frame = ttk.Frame(product_frame)
            quantity_frame.pack(pady=5)
            
            minus_btn = ttk.Button(quantity_frame, text="-", width=3,
                                 command=lambda p=name: self.decrease_quantity(p))
            minus_btn.pack(side=tk.LEFT, padx=2)
            
            quantity_label = tk.Label(quantity_frame, 
                                    text=str(self.cart.get(name, 0)),
                                    width=5)
            quantity_label.pack(side=tk.LEFT, padx=2)
            
            plus_btn = ttk.Button(quantity_frame, text="+", width=3,
                                command=lambda p=name: self.add_to_cart(p))
            plus_btn.pack(side=tk.LEFT, padx=2)
            
            # Store reference to quantity label
            if not hasattr(self, 'quantity_labels'):
                self.quantity_labels = {}
            self.quantity_labels[name] = quantity_label
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # Konfigurasi grid
        for i in range(3):
            self.product_grid.grid_columnconfigure(i, weight=1)

    def decrease_quantity(self, product_name):
        if product_name in self.cart:
            if self.cart[product_name] > 1:
                self.cart[product_name] -= 1
            else:
                del self.cart[product_name]
            
            # Update quantity label
            if product_name in self.quantity_labels:
                self.quantity_labels[product_name].config(
                    text=str(self.cart.get(product_name, 0)))
            
            self.update_cart_display()
    
    # Di kelas Stupid_chicken:

    def check_stock_available(self, product_name, requested_quantity=1):
        stock = self.products[product_name]["stock"]
        
        # Jika stock adalah string "Ada"
        if isinstance(stock, str) and stock.lower() == True:
            return True
        
        # Jika stock adalah angka
        elif isinstance(stock, (int, float)):
            current_in_cart = self.cart.get(product_name, 0)
            return stock >= (current_in_cart + requested_quantity)
        
        return False

    def add_to_cart(self, product_name):
        if self.check_stock_available(product_name):
            if product_name in self.cart:
                # Cek stok lagi untuk penambahan
                if self.check_stock_available(product_name, 1):
                    self.cart[product_name] += 1
                else:
                    messagebox.showwarning("Stok Tidak Cukup", 
                                        f"Maaf, stok {product_name} tidak mencukupi!")
                    return
            else:
                self.cart[product_name] = 1
            
            # Update quantity label
            if product_name in self.quantity_labels:
                self.quantity_labels[product_name].config(
                    text=str(self.cart[product_name]))
            
            self.update_cart_display()
        else:
            messagebox.showwarning("Stok Habis", 
                                f"Maaf, {product_name} sedang kosong!")

    def update_cart_display(self):
        self.cart_text.delete(1.0, tk.END)
        total = 0
        
        for product, quantity in self.cart.items():
            price = self.products[product]["price"]
            subtotal = price * quantity
            total += subtotal
            
            self.cart_text.insert(tk.END,
                                f"{product} x{quantity}\n"
                                f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n")
        
        self.total_label.config(text=f"Total: Rp {total:,}")

    def checkout(self):
        if len(self.cart) == 0:
            messagebox.showwarning("Keranjang Kosong", 
                                 "Silakan tambahkan produk ke keranjang terlebih dahulu!")
            return
        
        total = 0
        for product, quantity in self.cart.items():
            price = self.products[product]["price"]
            total = total + (price * quantity)
        
        if total > self.current_balance:
            messagebox.showerror("Saldo Tidak Cukup",
                               "Maaf, saldo Anda tidak mencukupi untuk melakukan pembelian ini!")
            return
        
        self.current_balance = self.current_balance - total
        self.balance_label.config(text=f"Saldo: Rp {self.current_balance:,}")
        
        transaction = {
            "username": self.username,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": dict(self.cart),
            "total": total
        }
        self.save_transaction(transaction)
        
        self.cart.clear()
        self.update_cart_display()
        
        messagebox.showinfo("Sukses", "Terima kasih atas pembelian Anda!")

    def add_to_cart(self, product_name):
        if self.products[product_name]["stock"] == True:
            if product_name in self.cart:
                self.cart[product_name] = self.cart[product_name] + 1
            else:
                self.cart[product_name] = 1
                
            self.update_cart_display()
            self.display_products()
        else:
            messagebox.showwarning("Stok Habis", f"Maaf, {product_name} sedang kosong!")

    def save_transaction(self, transaction):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "transactions.json")
            with open(transactions_path, "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            transactions = []

        transactions.append(transaction)

        with open(transactions_path, "w") as f:
            json.dump(transactions, f)

    def load_transaction_history(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "transactions.json")
            with open(transactions_path, "r") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Riwayat Transaksi")
        history_window.geometry("500x400")
        
        columns = ("Tanggal", "Total")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        
        tree.heading("Tanggal", text="Tanggal")
        tree.heading("Total", text="Total")
        
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        for transaction in self.transactions:
            tree.insert("", tk.END, values=(
                transaction["datetime"],
                f"Rp {transaction['total']:,}"
            ))
            
        def show_details(event):
            selected_item = tree.selection()
            if len(selected_item) > 0:
                item = selected_item[0]
                transaction = self.transactions[tree.index(item)]
                
                details = "Detail Pembelian:\n\n"
                for product, quantity in transaction["items"].items():
                    price = self.products[product]["price"]
                    subtotal = price * quantity
                    details = details + f"{product} x{quantity}\n"
                    details = details + f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n"
                
                messagebox.showinfo("Detail Transaksi", details)
        
        tree.bind("<Double-1>", show_details)
            
    def on_frame_configure(self, event=None):
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.product_canvas.itemconfig(self.canvas_frame, width=event.width)

    def filter_products(self):
        self.display_products()


app = LoginWindow()
app.window.mainloop()