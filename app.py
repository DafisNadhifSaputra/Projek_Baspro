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

if __name__ == "__main__":
    app = LoginWindow()
    app.window.mainloop()