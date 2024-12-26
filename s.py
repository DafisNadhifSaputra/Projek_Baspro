a = 0 // 3
b = 1 // 3
c = 2 // 3
d = 3 // 3
print(a, b, c, d)

f = 0 % 3
g = 1 % 3
h = 2 % 3
i = 3 % 3
print(f, g, h, i)

stores = [
            ("Stupid Chicken", "a", "images/stupidchiken/gambar_stupidchiken.jpg"),
            ("Stand 03", "b", "images/stand03/gambar_stand03.jpg"),
            ("Nasi Goreng", "c", "images/nasi_goreng/gambar_nasi_goreng.jpg"),
            ("Teh Poci", "d", "images/teh_poci/gambar_teh_poci.jpg")
        ]

for idx, (store, a, b) in enumerate(stores):
    row = idx // 2
    col = idx % 2
    print(row, col, store, a, b)