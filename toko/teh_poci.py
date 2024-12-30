import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import locale
from PIL import Image, ImageTk

class teh_poci:
    def __init__(self, root, username, initial_balance, parent):
        self.root = root
        self.root.title("🐾 Teh Poci 🐾")
        lebar_layar = self.root.winfo_screenwidth()
        tinggi_layar = self.root.winfo_screenheight()
        self.root.geometry(f"{lebar_layar}x{tinggi_layar}")
        self.root.configure(bg="#f0f0f0")
        # self.root.attributes("-fullscreen", True)

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
        """Load products from data_produk/tehpoci.json"""
        try:
            with open("data_produk/tehpoci.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "data_produk/tehpoci.json file not found!")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding data_produk/tehpoci.json!")
            return {}

    def create_widgets(self):
        # Frame utama dengan proporsi 70-30
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header Frame
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        tk.Label(header_frame,
                 text="Teh Poci",
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
        """Menampilkan produk ke dalam grid"""
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

            stock_label = tk.Label(product_frame, text=f"Stok: {'Ada' if details['stock'] >= 1 else 'Habis'}")
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
        """Kurangi jumlah produk dalam keranjang"""
        if product_name in self.cart:
            if self.cart[product_name] > 1:
                self.cart[product_name] -= 1
            else:
                del self.cart[product_name]
            self.quantity_labels[product_name].config(text=str(self.cart.get(product_name, 0)))
            self.update_cart_display()

    def check_stock_available(self, product_name, requested_quantity=1):
        """Periksa apakah stok produk mencukupi"""
        stock = self.products[product_name]["stock"]
        
        # Jika stock adalah angka
        if isinstance(stock, (int, float)):
            current_in_cart = self.cart.get(product_name, 0)
            return stock >= (current_in_cart + requested_quantity)
        
        return False

    def add_to_cart(self, product_name):
        """menambahkan produk ke keranjang"""
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
        """Menampilkan isi keranjang belanja"""
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
        """Cetak struk belanja ke jendela baru"""
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
        """Menampilkan pesanan"""
        pesanan_window = tk.Toplevel(self.root)
        pesanan_window.title("Pesanan Saya")
        pesanan_window.geometry("800x600")

        tk.Label(
            pesanan_window,
            text="Pesanan",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        columns = ("Tanggal", "Items", "Total", "Status")
        tree = ttk.Treeview(pesanan_window, columns=columns, show="headings", height=15)
        
        tree.heading("Tanggal", text="Tanggal")
        tree.heading("Items", text="Items")
        tree.heading("Total", text="Total")
        tree.heading("Status", text="Status")
        
        tree.column("Tanggal", width=150)
        tree.column("Items", width=350)
        tree.column("Total", width=150)
        tree.column("Status", width=100)

        scrollbar = ttk.Scrollbar(pesanan_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        try:
            with open("data_transaksi/transactions.json", "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            transactions = []

        user_transactions = [
            transaction for transaction in transactions
            if transaction.get("username") == self.username
        ]

        for transaction in user_transactions:
            items_str = ", ".join(f"{item['name']}({item['quantity']})" for item in transaction["items"])
            tree.insert("", tk.END, values=(
                transaction["datetime"],
                items_str,  # items sebagai string
                f"Rp {transaction['total']:,}",
                transaction.get("status")
            ))
            
        def show_details(event):
            selected_item = tree.selection()
            if selected_item:
                item_id = selected_item[0]
                values = tree.item(item_id)['values']
                transaction_time = values[0]

                # mencari transaksi yang sesuai dengan waktu yang dipilih
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

                        # menampilkan feedback jika ada
                        if "feedback" in transaction:
                            details += f"\nFeedback: {transaction['feedback']}"

                        messagebox.showinfo("Detail Transaksi", details)
                        break

        tree.bind("<Double-1>", show_details)


    def save_transaction(self, transaction):
        """Menyimpan transaksi ke dalam file JSON"""
        try:
            transactions_path = "data_transaksi/transactions.json"
            history_path = "data_transaksi/transactionshistory.json"

            # Load transaksi
            with open(transactions_path, "r") as f:
                transactions = json.load(f)

            # load transaksi history
            try:
                with open(history_path, "r") as f:
                    transaction_history = json.load(f)
            except FileNotFoundError:
                transaction_history = []

            # Menambahkan transaksi baru
            transactions.append(transaction)
            transaction_history.append(transaction)

            # Menyimpan transaksi
            with open(transactions_path, "w") as f:
                json.dump(transactions, f, indent=4)

            # Menyimpan transaksi history
            with open(history_path, "w") as f:
                json.dump(transaction_history, f, indent=4)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan transaksi: {e}")

    def load_transaction_history(self):
        """Load transaksi dari file JSON"""
        try:
            transactions_path = "data_transaksi/transactions.json"
            with open(transactions_path, "r") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []

    def checkout(self):
        """Checkout produk yang ada di keranjang"""
        if not self.cart:
            messagebox.showwarning("Keranjang Kosong", "Silakan tambahkan produk ke keranjang terlebih dahulu!")
            return

        total = sum(self.products[product]["price"] * quantity for product, quantity in self.cart.items())

        if total > self.current_balance:
            messagebox.showerror("Saldo Tidak Cukup", "Maaf, saldo Anda tidak mencukupi untuk melakukan pembelian ini!")
            return

        self.current_balance -= total
        self.update_balance_in_file(self.username, self.current_balance)
        self.balance_label.config(text=f"Saldo: Rp {self.current_balance:,}")

        # Kurangi stok dan catat transaksi
        for product, quantity in self.cart.items():
            self.products[product]["stock"] -= quantity

        with open("data_produk/tehpoci.json", "w") as f:
            json.dump(self.products, f, indent=4)

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
        """Update saldo user di file users.json"""
        try:
            users_path = "database_user_admin/users.json"
            with open(users_path, "r") as f:
                users = json.load(f)

            # Update balance
            if username in users:
                users[username]['balance'] = new_balance

            # menulis kembali ke file
            with open(users_path, "w") as f:
                json.dump(users, f, indent=4)

        except FileNotFoundError:
            messagebox.showerror("Error", "File users.json tidak ditemukan.")

    def calculate_total_cook_time(self):
        """Menghitung total waktu memasak produk dalam keranjang"""
        total_cook_time = 0
        for item, jumlah in self.cart.items():
            total_cook_time += self.products[item]["cook_time"] * jumlah
        return total_cook_time

    def show_history(self):
        """Menampilkan riwayat transaksi"""
        pesanan_window = tk.Toplevel(self.root)
        pesanan_window.title("Pesanan Saya")
        pesanan_window.geometry("800x600")

        tk.Label(
            pesanan_window,
            text="Riwayat Transaksi",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        columns = ("Tanggal", "Items", "Total", "Status")
        tree = ttk.Treeview(pesanan_window, columns=columns, show="headings", height=15)
        
        tree.heading("Tanggal", text="Tanggal")
        tree.heading("Items", text="Items")
        tree.heading("Total", text="Total")
        tree.heading("Status", text="Status")
        
        tree.column("Tanggal", width=150)
        tree.column("Items", width=350)
        tree.column("Total", width=150)
        tree.column("Status", width=100)

        scrollbar = ttk.Scrollbar(pesanan_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        try:
            with open("data_transaksi/transactionshistory.json", "r") as f:
                transactions = json.load(f)
        except FileNotFoundError:
            transactions = []

        user_transactions = [
            transaction for transaction in transactions
            if transaction.get("username") == self.username
        ]

        for transaction in user_transactions:
            items_str = ", ".join(f"{item['name']}({item['quantity']})" for item in transaction["items"])
            tree.insert("", tk.END, values=(
                transaction["datetime"],
                items_str,  # items sebagai string
                f"Rp {transaction['total']:,}",
                transaction.get("status")
            ))
            
        def show_details(event):
            selected_item = tree.selection()
            if selected_item:
                item_id = selected_item[0]
                values = tree.item(item_id)['values']
                transaction_time = values[0]

                # mencari transaksi yang sesuai dengan waktu yang dipilih
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

                        # menampilkan feedback jika ada
                        if "feedback" in transaction:
                            details += f"\nFeedback: {transaction['feedback']}"

                        messagebox.showinfo("Detail Transaksi", details)
                        break

        tree.bind("<Double-1>", show_details)


    def on_frame_configure(self, event=None):
        """Update scrollregion saat ukuran frame berubah"""
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Update lebar canvas saat ukuran frame"""
        self.product_canvas.itemconfig(self.canvas_frame, width=event.width)

    def filter_products(self):
        """Filter produk berdasarkan kategori"""
        self.display_products()  