import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
from datetime import datetime
from store.stupidchicken import Stupid_chicken
from store.stand03 import stand03
import locale
from PIL import Image, ImageTk
import os

locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8') 
class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🐾 Main Login 🐾")
        self.window.geometry("1280x720")
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

        ttk.Label(login_frame, text="Password:", font=("Helvetica", 10, "bold")).pack(pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(pady=5, ipady=10)
        self.password_entry.configure(width=100)

        login_button = tk.Button(
            login_frame,
            text="Login",
            width=10,
            height=2,
            font=("Helvetica", 10, "bold"),
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
            users_path = os.path.join(script_dir, "database_user_admin/users.json")
            with open(users_path, "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "Database User tidak ditemukan")
            return

        # Cek login admin
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

        # cek login user
        if username in users:
            if users[username]["password"] == password:
                messagebox.showinfo("Success", "Login Mahasiswa successful!")
                self.window.destroy()
                root = tk.Tk()
                app = pilih_kedai(root, username, users[username]["balance"], self.window)
                root.mainloop()
            else:
                messagebox.showerror("Error", "Invalid password!")
        else:
            messagebox.showerror("Error", "Username not found!")

class AdminWindow:
    """Class untuk membuat window Admin Dashboard"""
    def __init__(self, root, admin_id):
        self.root = root
        self.root.title(f"Admin Dashboard - {admin_id}")
        self.root.geometry("1280x720")
        self.root.configure(bg="#f0f0f0")

        self.admin_id = admin_id
        self.store_name = self.get_store_name(admin_id)
        self.transactions = self.load_transactions()
        self.products_file = self.get_products_file(admin_id)
        self.products = self.load_products()

        self.create_widgets()

    def get_store_name(self, admin_id):
        """ Fungsi untuk mendapatkan nama toko berdasarkan admin_id """
        store_mapping = {
            "admin1": "Stupid Chicken",
            "admin2": "data_produk/bakso_bakar.json",
            "admin3": "Mie Setan",
            "admin4": "Geprek Bensu"
        }
        return store_mapping.get(admin_id, "Unknown Store")

    def create_widgets(self):
        """ Fungsi untuk membuat widget di dalam window """
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, pady=10, padx=20)

        tk.Label(
            header_frame,
            text=f"{self.store_name} - Dashboard",
            font=("Helvetica", 24, "bold")
        ).pack(side=tk.LEFT)

        # Tabel Order
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

        # Tombol frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill=tk.X, pady=10, padx=20)

        # Tombol refresh
        ttk.Button(
            buttons_frame,
            text="Refresh Orders",
            command=self.refresh_orders
        ).pack(side=tk.LEFT, padx=5)

        # Tombol update order status
        ttk.Button(
            buttons_frame,
            text="Update Status",
            command=self.update_order_status
        ).pack(side=tk.LEFT, padx=5)

        # Tombol hapus pesanan
        ttk.Button(
            buttons_frame,
            text="Hapus Pesanan",
            command=self.delete_order
        ).pack(side=tk.LEFT, padx=5)

        # Tombol kelola stok
        ttk.Button(
            buttons_frame,
            text="Kelola Stok",
            command=self.open_manage_stock
        ).pack(side=tk.LEFT, padx=5)

        self.refresh_orders()

    def open_manage_stock(self):
        """ Fungsi untuk membuka window untuk mengatur stock produk """
        stock_window = tk.Toplevel(self.root)
        stock_window.title("Atur Stock Produk")
        columns = ("Nama Produk", "Stock")
        tree = ttk.Treeview(stock_window, columns=columns, show="headings")
        tree.heading("Nama Produk", text="Nama Produk")
        tree.heading("Stock", text="Stock")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for product_name, data in self.products.items():
            current_stock = data.get("stock", 0)
            tree.insert("", tk.END, values=(product_name, current_stock))

        def update_stock():
            """ Fungsi untuk mengupdate stock produk """
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih produk lebih dulu!")
                return
            prod_name, current_stock = tree.item(selected[0])["values"]
            new_stock = simpledialog.askinteger("Ubah Stock", f"Masukkan stock baru untuk {prod_name}:", initialvalue=current_stock, parent=stock_window)
            if new_stock is not None:
                self.products[prod_name]["stock"] = new_stock
                tree.set(selected[0], "Stock", new_stock)
                self.save_products()
                messagebox.showinfo("Sukses", f"Stock {prod_name} diubah menjadi {new_stock}!")

        ttk.Button(stock_window, text="Update Stock", command=update_stock).pack(pady=5)

    def delete_order(self):
        """ Fungsi untuk menghapus pesanan """
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih pesanan yang akan dihapus!")
            return
        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus pesanan ini?")
        if confirm:
            # Ambil datetime dari item yang dipilih
            item_values = self.orders_tree.item(selected_item[0])["values"]
            transaction_datetime = item_values[0]
                
            try:
                with open("data_transaksi/transactions.json", "r") as f:
                    transactions = json.load(f)
                    
                # Hapus transaksi dari list
                transactions = [t for t in transactions 
                            if t["datetime"] != transaction_datetime]
                
                with open("data_transaksi/transactions.json", "w") as f:
                    json.dump(transactions, f, indent=4)
                
            # Hapus item dari treeview
                self.orders_tree.delete(selected_item)
                
                messagebox.showinfo("Sukses", "Pesanan berhasil dihapus!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus pesanan: {str(e)}")
    
    def get_products_file(self, admin_id):
        """ Fungsi untuk mendapatkan nama file produk berdasarkan admin_id """
        store_mapping = {
            "admin1": "stupidchiken.json",
            "admin2": "bakso_bakar.json",
            "admin3": "mie_setan.json",
            "admin4": "geprek_bensu.json"
        }
        return store_mapping.get(admin_id, "unknown.json")
    
    def load_products(self):
        """ Fungsi untuk memuat produk dari file JSON """
        products_path = os.path.join("data_produk", self.products_file)
        try:
            with open(products_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {self.products_file} tidak ditemukan!")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Error decoding {self.products_file}!")
            return {}

    def load_transactions(self):
        """ Fungsi untuk memuat transaksi dari file JSON """
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "data_transaksi/transactions.json")
            print(f"Loading transactions from: {transactions_path}")  # Cetak path untuk debugging
            with open(transactions_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        
    def save_products(self):
        """ Fungsi untuk menyimpan produk ke file JSON """
        products_path = os.path.join("data_produk", self.products_file)
        try:
            with open(products_path, "w") as f:
                json.dump(self.products, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")

    def refresh_orders(self):
        """ Fungsi untuk merefresh pesanan """
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Load transactions
        self.transactions = self.load_transactions()

        # Load produk berdasarkan nama toko
        for transaction in self.transactions:
            if any(item in self.products for item in [i['name'] for i in transaction["items"]]):  # Ambil semua item dari transaksi
                items_str = ", ".join(f"{item['name']}({item['quantity']})" for item in transaction["items"])

                self.orders_tree.insert("", tk.END, values=(
                    transaction["datetime"],
                    transaction.get("username", "Unknown"),
                    items_str,
                    f"Rp {transaction['total']:,}",
                    transaction.get("status", "Pending")
                ))

    def update_order_status(self):
        """ Fungsi untuk mengupdate status pesanan """
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order to update")
            return

        status_window = tk.Toplevel(self.root)
        status_window.title("Update Status")
        status_window.geometry("400x250")

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

            # perbarui status di treeview
            values = list(self.orders_tree.item(item)["values"])
            values[-1] = new_status
            self.orders_tree.item(item, values=values)

            # perbarui status di file JSON
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "data_transaksi/transactions.json")
            transactions_path1 = os.path.join(script_dir, "data_transaksi/transactionshistory.json")
            for transaction in self.transactions:
                if transaction["datetime"] == transaction_date:
                    transaction["status"] = new_status

            with open(transactions_path, "w") as f:
                json.dump(self.transactions, f)
            with open(transactions_path1, "w") as f:
                json.dump(self.transactions, f)

            status_window.destroy()
            messagebox.showinfo("Success", "Order status updated successfully!")

        ttk.Button(
            status_window,
            text="Update",
            command=update
        ).pack(pady=10)

class pilih_kedai:
    """Class untuk membuat window Pilih Kedai"""
    def __init__(self, root, username, balance, parent):
        self.root = root
        self.root.title("Pilih Kedai")
        self.root.geometry("1280x720")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        self.parent = parent
        self.username = username
        self.balance = balance

        self.create_widgets()

    def create_widgets(self):
        """ Fungsi untuk membuat widget di dalam window """
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.pack_propagate(False)

        # frame atas
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X)

        # tombol kemabli ke login
        tk.Button(
            top_frame,
            text="Kembali ke menu login",
            font=("Helvetica", 10, "bold"),
            width=20,
            height=2,
            bg="#FF0000",
            command=self.kembali_ke_login
        ).pack(side=tk.RIGHT, pady=(0,5), padx=(0,10))

        # Frame untuk judul
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0,10))

        tk.Label(
            title_frame,
            text="Pilih Kedai UNESA",
            font=("Helvetica", 24, "bold"),
            bg="#f0f0f0"
        ).pack()

        tk.Label(
            title_frame,
            text=f"Saldo: Rp {self.balance:,}",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        ).pack()

        # Frame untuk kedai
        stores_frame = ttk.Frame(main_frame)
        stores_frame.pack(pady=(6,0)) 
        
        # daftar kedai
        stores = [
            ("Stupid Chicken", self.open_stupid_chicken, "images/stupidchiken/gambar_stupidchiken.jpg"),
            ("Stand 03", self.open_stand03, "images/stand03/gambar_stand03.jpg"),
            ("Nasi Goreng", self.open_nasi_goreng, "images/mie.jpg"),
            ("Geprek Bensu", self.open_teh_poci, "images/geprek.jpg")
        ]

        for idx, (store_name, command, img_path) in enumerate(stores):
            row = idx // 2
            col = idx % 2

            store_frame = ttk.Frame(stores_frame, padding=2)  
            store_frame.grid(row=row, column=col, padx=20, pady=10)  

            try:
                image = Image.open(img_path)
                image = image.resize((250, 150))
                photo = ImageTk.PhotoImage(image)
                logo = tk.Label(store_frame, image=photo)
                logo.image = photo
                logo.grid(row=0, column=0, pady=(0,1))
            except FileNotFoundError:
                print(f"Gambar tidak ditemukan: {img_path}")
                tk.Label(
                    store_frame,
                    text=store_name,
                    font=("Helvetica", 12)
                ).grid(row=0, column=0, pady=(0,1))

            # tombol pilih kedai
            tk.Button(
                store_frame,
                text=store_name,
                font=("Helvetica", 10, "bold"),
                width=30,
                bg="#ADD8E6",
                height=2,
                command=command
            ).grid(row=1, column=0)


    def kembali_ke_login(self):
        """ Fungsi untuk kembali ke menu login """
        self.root.destroy()
        global main_app_window
        app = LoginWindow()
        app.window.mainloop()

    def open_stupid_chicken(self):
        """ Fungsi untuk membuka window Stupid Chicken """
        self.root.withdraw()
        root = tk.Toplevel()
        app = Stupid_chicken(root, self.username, self.balance, self.root)
        root.mainloop()

    def open_stand03(self):
        """ Fungsi untuk membuka window Stand 03 """
        self.root.withdraw()
        root = tk.Toplevel()
        app = stand03(root, self.username, self.balance, self.root)
        root.mainloop()

    def open_nasi_goreng(self):
        self.root.withdraw()
        root = tk.Toplevel()
        app = nasi_goreng(root, self.username, self.balance, self.root)
        root.mainloop()

    def open_teh_poci(self):
        self.root.withdraw()
        root = tk.Toplevel()
        app = nasi_goreng(root, self.username, self.balance, self.root)
        root.mainloop()      

class Bakso_bakar:
    def __init__(self, root, username, initial_balance, parent):
        self.root = root
        self.root.title("🐾 Bakso Bakar 🐾")
        self.root.geometry("1280x720")
        self.root.configure(bg="#f0f0f0")

        self.parent_root = parent
        self.username = username
        self.current_balance = initial_balance

        # Menyiapkan cache untuk gambar
        self.image_cache = {}

        # Data produk dengan path gambar
        self.products = self.load_products()


        self.cart = {}
        self.history_transaksi = []
        self.create_widgets()
        self.load_transaction_history()

    def load_products(self):
        """Load products from data_produk/bakso_bakar.json"""
        try:
            with open("data_produk/bakso_bakar.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "data_produk/bakso_bakar.json file not found!")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding data_produk/bakso_bakar.json!")
            return {}
    def create_widgets(self):
        # Frame utama dengan proporsi 70-30
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header Frame
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        tk.Label(header_frame,
                 text="Stand 03",
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

        ttk.Button(cart_frame, text="Kembali",
                   command=self.kembali_ke_pilih_kedai).pack(pady=5)
        
        ttk.Button(cart_frame, text="Lihat Pesanan",
                   command=self.pesanan).pack(pady=5)

        # Bind events
        self.product_grid.bind("<Configure>", self.on_frame_configure)
        self.product_canvas.bind("<Configure>", self.on_canvas_configure)

        # Tampilkan produk
        self.display_products()


    def kembali_ke_pilih_kedai(self):
        self.root.destroy()
        self.parent_root.deiconify()
    
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
        for widget in self.product_grid.winfo_children():
            widget.destroy()

        filtered_products = {
            name: details
            for name, details in self.products.items()
            if self.category_var.get() == "Semua" or details["category"] == self.category_var.get()
        }

        row = 0
        col = 0
        for name, details in filtered_products.items():
            product_frame = ttk.Frame(self.product_grid)
            product_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            image_path = details["image"]
            photo = self.load_and_resize_image(image_path)
            image_label = tk.Label(product_frame, image=photo)
            image_label.image = photo
            image_label.pack(pady=5)

            tk.Label(product_frame, text=name, font=("Helvetica", 10, "bold")).pack()
            tk.Label(product_frame, text=f"Rp {details['price']:,}").pack()

            stock_label = tk.Label(product_frame, text=f"Stok: {details['stock']}")
            stock_label.pack()

            quantity_frame = ttk.Frame(product_frame)
            quantity_frame.pack(pady=5)

            minus_btn = ttk.Button(quantity_frame, text="-", width=3, command=lambda p=name: self.decrease_quantity(p))
            minus_btn.pack(side=tk.LEFT, padx=2)

            quantity_label = tk.Label(quantity_frame, text=str(self.cart.get(name, 0)), width=5)
            quantity_label.pack(side=tk.LEFT, padx=2)

            plus_btn = ttk.Button(quantity_frame, text="+", width=3, command=lambda p=name: self.add_to_cart(p))
            plus_btn.pack(side=tk.LEFT, padx=2)

            if not hasattr(self, 'quantity_labels'):
                self.quantity_labels = {}
            self.quantity_labels[name] = quantity_label

            col += 1
            if col > 2:
                col = 0
                row += 1

        for i in range(3):
            self.product_grid.grid_columnconfigure(i, weight=1)

    def decrease_quantity(self, product_name):
        if product_name in self.cart:
            if self.cart[product_name] > 1:
                self.cart[product_name] -= 1
            else:
                del self.cart[product_name]
            self.quantity_labels[product_name].config(text=str(self.cart.get(product_name, 0)))
            self.update_cart_display()

    def check_stock_available(self, product_name, requested_quantity=1):
        stock = self.products[product_name]["stock"]
        
        # Jika stock adalah angka
        if isinstance(stock, (int, float)):
            current_in_cart = self.cart.get(product_name, 0)
            return stock >= (current_in_cart + requested_quantity)
        
        return False

    def add_to_cart(self, product_name):
        if self.check_stock_available(product_name):
            if product_name in self.cart:
                if self.check_stock_available(product_name, 1):
                    self.cart[product_name] += 1
                else:
                    messagebox.showwarning("Stok Tidak Cukup", f"Maaf, stok {product_name} tidak mencukupi!")
                    return
            else:
                self.cart[product_name] = 1

            self.quantity_labels[product_name].config(text=str(self.cart[product_name]))
            self.update_cart_display()
        else:
            messagebox.showwarning("Stok Habis", f"Maaf, {product_name} sedang kosong!")


    def update_cart_display(self):
        self.cart_text.delete(1.0, tk.END)
        total = 0
        total_cook_time = 0

        for product, quantity in self.cart.items():
            price = self.products[product]["price"]
            subtotal = price * quantity
            total += subtotal

            cook_time = self.products[product]["cook_time"]
            total_cook_time += cook_time * quantity

            self.cart_text.insert(tk.END,
                                 f"{product} x{quantity}\n"
                                 f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n")

        self.total_label.config(text=f"Total: Rp {total:,}")
        self.cart_text.insert(tk.END, f"\nEstimasi Waktu: {total_cook_time} menit")

    def cetak_struk(self):
        if not self.cart:
            messagebox.showwarning("Peringatan", "Keranjang belanja kosong!")
            return

        waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        struk = f"Struk Belanja\n{waktu}\n\n"

        # Header
        struk += f"{'Barang'.ljust(25)}{'Harga'.ljust(10)}{'Jumlah'.ljust(10)}{'Subtotal'.center(15)}\n"
        struk += "-" * 70 + "\n"

        total_harga = 0
        total_cook_time = 0
        for item, jumlah in self.cart.items():
            harga_satuan = self.products[item]["price"]
            subtotal = jumlah * harga_satuan
            total_harga += subtotal
            total_cook_time += self.products[item]["cook_time"] * jumlah

            struk += f"{item.ljust(25)}{'Rp'+locale.format_string('%d', harga_satuan, grouping=True).ljust(10)}{str(jumlah).ljust(10)}{'Rp'+locale.format_string('%d', subtotal, grouping=True):<15}\n"

        struk += "-" * 70 + "\n"
        struk += f"{' '*35}{'Total:'}{' '*6}{'Rp'+locale.format_string('%d', total_harga, grouping=True):<15}\n"
        struk += f"Estimasi Waktu: {total_cook_time} menit\n"
        struk += "Terima kasih telah berbelanja!"

        # Tampilkan struk di jendela baru
        struk_window = tk.Toplevel(self.root)
        struk_window.title("Struk Belanja")
        text_area = tk.Text(struk_window, wrap='word')
        text_area.insert(tk.END, struk)
        text_area.config(state=tk.DISABLED)
        text_area.pack(padx=10, pady=10)

        self.cart.clear()
        self.update_cart_display()

    def pesanan(self):
        """Display order history and status for current user"""
        # Create new window
        pesanan_window = tk.Toplevel(self.root)
        pesanan_window.title("Pesanan Saya")
        pesanan_window.geometry("800x600")

        # Create header
        tk.Label(
            pesanan_window,
            text="Riwayat Pesanan",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        # Create table
        columns = ("Tanggal", "Items", "Total", "Status")
        tree = ttk.Treeview(pesanan_window, columns=columns, show="headings", height=15)
        
        # Configure columns
        tree.heading("Tanggal", text="Tanggal")
        tree.heading("Items", text="Items")
        tree.heading("Total", text="Total")
        tree.heading("Status", text="Status")
        
        tree.column("Tanggal", width=150)
        tree.column("Items", width=350)
        tree.column("Total", width=150)
        tree.column("Status", width=100)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(pesanan_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        try:
            with open("data_transaksi/transactions.json", "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            transactions = []

        # Filter transactions by username
        user_transactions = [
            transaction for transaction in transactions
            if transaction.get("username") == self.username
        ]

        # Add transactions to table
        for transaction in user_transactions:
            items_str = ", ".join(f"{item['name']}({item['quantity']})" for item in transaction["items"])
            tree.insert("", tk.END, values=(
                transaction["datetime"],
                items_str,  # Tampilkan items sebagai string
                f"Rp {transaction['total']:,}",
                transaction.get("status")
            ))
            
        def show_details(event):
            selected_item = tree.selection()
            if selected_item:
                item_id = selected_item[0]
                values = tree.item(item_id)['values']
                transaction_time = values[0]

                # Cari transaksi yang sesuai dengan waktu yang dipilih
                for transaction in user_transactions:
                    if transaction["datetime"] == transaction_time:
                        details = "Detail Pembelian:\n\n"
                        for product in transaction["items"]:
                            # Menggunakan get untuk menghindari KeyError jika 'name' tidak ada
                            product_name = product.get("name", "Unknown Product")
                            quantity = product.get("quantity", 0)

                            # Memastikan produk ada di dictionary products
                            if product_name in self.products:
                                price = self.products[product_name]["price"]
                                subtotal = price * quantity
                                details += f"{product_name} x{quantity}\n"
                                details += f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n"
                            else:
                                details += f"{product_name} x{quantity} (Harga tidak tersedia)\n\n"

                        # Tampilkan feedback jika ada
                        if "feedback" in transaction:
                            details += f"\nFeedback: {transaction['feedback']}"

                        messagebox.showinfo("Detail Transaksi", details)
                        break

        tree.bind("<Double-1>", show_details)


    def save_transaction(self, transaction):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "data_transaksi/transactions.json")
            history_path = os.path.join(script_dir, "data_transaksi/transactionshistory.json")

            # Load transactions
            with open(transactions_path, "r") as f:
                transactions = json.load(f)

            # Load transaction history
            try:
                with open(history_path, "r") as f:
                    transaction_history = json.load(f)
            except FileNotFoundError:
                transaction_history = []

            # Add transaction to both files
            transactions.append(transaction)
            transaction_history.append(transaction)

            # Save transactions
            with open(transactions_path, "w") as f:
                json.dump(transactions, f, indent=4)

            # Save transaction history
            with open(history_path, "w") as f:
                json.dump(transaction_history, f, indent=4)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan transaksi: {e}")

    def load_transaction_history(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            transactions_path = os.path.join(script_dir, "data_transaksi/transactions.json")
            with open(transactions_path, "r") as f:
                self.transactions = json.load(f)  # Muat data ke self.transactions
        except FileNotFoundError:
            self.transactions = []

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Keranjang Kosong", "Silakan tambahkan produk ke keranjang terlebih dahulu!")
            return

        total = sum(self.products[product]["price"] * quantity for product, quantity in self.cart.items())

        if total > self.current_balance:
            messagebox.showerror("Saldo Tidak Cukup", "Maaf, saldo Anda tidak mencukupi untuk melakukan pembelian ini!")
            return

        self.current_balance -= total
        self.update_balance_in_file(self.username, self.current_balance)  # Update saldo di users.json
        self.balance_label.config(text=f"Saldo: Rp {self.current_balance:,}")

        # Kurangi stok dan catat transaksi
        for product, quantity in self.cart.items():
            self.products[product]["stock"] -= quantity

        transaction = {
            "username": self.username,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": [{"name": item, "quantity": quantity} for item, quantity in self.cart.items()],
            "total": total,
            "status": "Processing",
            "estimasi_waktu": self.calculate_total_cook_time()
        }
        self.save_transaction(transaction)
        messagebox.showinfo("Sukses", "Terima kasih atas pembelian Anda!")
        self.cetak_struk()

        # Update tampilan setelah checkout
        self.cart.clear()
        self.update_cart_display()
        self.display_products()
    
    def update_balance_in_file(self, username, new_balance):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            users_path = os.path.join(script_dir, "users.json")
            with open(users_path, "r") as f:
                users = json.load(f)

            # Update balance for the specific user
            if username in users:
                users[username]['balance'] = new_balance

            # Write the updated data back to users.json
            with open(users_path, "w") as f:
                json.dump(users, f, indent=4)

        except FileNotFoundError:
            messagebox.showerror("Error", "File users.json tidak ditemukan.")

    def calculate_total_cook_time(self):
        total_cook_time = 0
        for item, jumlah in self.cart.items():
            total_cook_time += self.products[item]["cook_time"] * jumlah
        return total_cook_time

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Riwayat Transaksi")
        history_window.geometry("800x400")

        columns = ("Tanggal", "Total", "Estimasi Waktu", "Status")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")

        tree.heading("Tanggal", text="Tanggal")
        tree.heading("Total", text="Total")
        tree.heading("Estimasi Waktu", text="Estimasi Waktu")
        tree.heading("Status", text="Status")

        tree.column("Tanggal", width=200, anchor=tk.W)
        tree.column("Total", width=150, anchor=tk.CENTER)
        tree.column("Estimasi Waktu", width=150, anchor=tk.CENTER)
        tree.column("Status", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Load and display transactions from data_transaksi/transactionshistory.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        transactions_path = os.path.join(script_dir, "data_transaksi/transactionshistory.json")  # Ganti ke data_transaksi/transactionshistory.json
        try:
            with open(transactions_path, "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            transactions = []

        # Filter transactions by username
        user_transactions = [
            transaction for transaction in transactions
            if transaction.get("username") == self.username
        ]

        for transaction in user_transactions:
            # Handle missing 'datetime' key
            datetime_str = transaction.get("datetime", transaction.get("waktu", "N/A"))
            tree.insert("", tk.END, values=(
                datetime_str,
                f"Rp {transaction['total']:,}",
                f"{transaction['estimasi_waktu']} menit" if "estimasi_waktu" in transaction else "N/A",
                transaction.get("status", "N/A")
            ))

        def show_details(event):
            selected_item = tree.selection()
            if selected_item:
                item_id = selected_item[0]
                values = tree.item(item_id)['values']
                transaction_time = values[0]

                # Cari transaksi yang sesuai dengan waktu yang dipilih
                for transaction in user_transactions:
                    if transaction["datetime"] == transaction_time:
                        details = "Detail Pembelian:\n\n"
                        for product in transaction["items"]:
                            # Menggunakan get untuk menghindari KeyError jika 'name' tidak ada
                            product_name = product.get("name", "Unknown Product")
                            quantity = product.get("quantity", 0)

                            # Memastikan produk ada di dictionary products
                            if product_name in self.products:
                                price = self.products[product_name]["price"]
                                subtotal = price * quantity
                                details += f"{product_name} x{quantity}\n"
                                details += f"Rp {price:,} x {quantity} = Rp {subtotal:,}\n\n"
                            else:
                                details += f"{product_name} x{quantity} (Harga tidak tersedia)\n\n"

                        # Tampilkan feedback jika ada
                        if "feedback" in transaction:
                            details += f"\nFeedback: {transaction['feedback']}"

                        messagebox.showinfo("Detail Transaksi", details)
                        break

        tree.bind("<Double-1>", show_details)


    def on_frame_configure(self, event=None):
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.product_canvas.itemconfig(self.canvas_frame, width=event.width)

    def filter_products(self):
        self.display_products()



if __name__ == "__main__":
    app = LoginWindow()
    app.window.mainloop()