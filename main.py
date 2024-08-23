import flet as ft
import sqlite3

# SQLiteデータベースに接続（check_same_thread=False を指定）
conn = sqlite3.connect('inventory.db', check_same_thread=False)
cursor = conn.cursor()

# 商品テーブルを作成（存在しない場合）
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
''')
conn.commit()

def main(page: ft.Page):
    page.title = "在庫管理システム"

    # UI要素
    product_list = ft.ListView(expand=True)
    editing_product_id = None
    editing_product_name = None

    # データベースから商品リストを取得
    def load_products():
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return products

    # 商品リストを表示する関数
    def update_product_list():
        product_list.controls.clear()
        products = load_products()
        for product in products:
            if editing_product_id == product[0]:
                product_list.controls.append(
                    ft.Row(
                        [
                            ft.TextField(
                                value=editing_product_name,
                                expand=True,
                                on_change=lambda e: handle_name_change(e),
                            ),
                            ft.IconButton(
                                icon=ft.icons.SAVE,
                                on_click=lambda e: save_name_change(),
                            ),
                            ft.IconButton(
                                icon=ft.icons.CANCEL,
                                on_click=lambda e: cancel_name_change(),
                                icon_color=ft.colors.RED,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )
            else:
                product_list.controls.append(
                    ft.Row(
                        [
                            ft.Text(product[1], expand=True),  # 商品名
                            ft.Text(f"在庫数: {product[2]}"),  # 在庫数
                            ft.IconButton(
                                icon=ft.icons.REMOVE,
                                on_click=lambda e, p=product: decrease_stock(p),
                            ),
                            ft.IconButton(
                                icon=ft.icons.ADD,
                                on_click=lambda e, p=product: increase_stock(p),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                on_click=lambda e, p=product: delete_product(p),
                                icon_color=ft.colors.RED,
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                on_click=lambda e, p=product: start_editing(p),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )
        page.update()

    # 在庫を減らす関数
    def decrease_stock(product):
        if product[2] > 0:
            cursor.execute("UPDATE products SET quantity = quantity - 1 WHERE id = ?", (product[0],))
            conn.commit()
            update_product_list()

    # 在庫を増やす関数
    def increase_stock(product):
        cursor.execute("UPDATE products SET quantity = quantity + 1 WHERE id = ?", (product[0],))
        conn.commit()
        update_product_list()

    # 商品を削除する関数
    def delete_product(product):
        cursor.execute("DELETE FROM products WHERE id = ?", (product[0],))
        conn.commit()
        update_product_list()

    # 商品を追加する関数
    def add_product(name, quantity):
        cursor.execute("INSERT INTO products (name, quantity) VALUES (?, ?)", (name, quantity))
        conn.commit()
        update_product_list()

    # 商品名を修正する関数
    def update_product_name(product_id, new_name):
        cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, product_id))
        conn.commit()
        update_product_list()

    # 商品名の編集を開始する関数
    def start_editing(product):
        nonlocal editing_product_id, editing_product_name
        editing_product_id = product[0]
        editing_product_name = product[1]
        update_product_list()

    # 商品名修正の保存を行う関数
    def save_name_change():
        nonlocal editing_product_id, editing_product_name
        if editing_product_id is not None:
            update_product_name(editing_product_id, editing_product_name)
            editing_product_id = None
            editing_product_name = None
            update_product_list()

    # 商品名修正をキャンセルする関数
    def cancel_name_change():
        nonlocal editing_product_id, editing_product_name
        editing_product_id = None
        editing_product_name = None
        update_product_list()

    # テキストフィールドの変更を処理する関数
    def handle_name_change(e):
        nonlocal editing_product_name
        editing_product_name = e.control.value

    # 商品名と在庫数のフィールド
    new_product_name = ft.TextField(label="商品名")
    new_product_quantity = ft.TextField(label="在庫数", value="0", keyboard_type="number")

    def handle_add_product(e):
        name = new_product_name.value
        quantity = int(new_product_quantity.value)

        if name and quantity >= 0:
            add_product(name, quantity)
            new_product_name.value = ""
            new_product_quantity.value = "0"
            page.update()

    # 商品を追加するためのアイコンボタン
    add_product_button = ft.IconButton(icon=ft.icons.ADD, on_click=handle_add_product)

    # レイアウトに追加
    page.add(
        ft.Column(
            [
                new_product_name,
                new_product_quantity,
                add_product_button,
                product_list
            ],
            expand=True,
        )
    )

    update_product_list()

# 環境変数からポート番号を取得し、Fletアプリケーションを起動
import os
port = int(os.getenv("PORT", 8000))
ft.app(target=main, view=ft.WEB_BROWSER, port=port)