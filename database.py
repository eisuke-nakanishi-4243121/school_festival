import sqlite3
import os

DATABASE_FILE = 'festival_stores.db'

def init_database():
    """データベースを初期化し、テーブルを作成"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # stores テーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            description TEXT
        )
    ''')
    
    # products テーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_FILE}' has been initialized")

def get_connection():
    """データベース接続を取得"""
    return sqlite3.connect(DATABASE_FILE)

def add_store(name, latitude, longitude, description=""):
    """店舗を追加"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO stores (name, latitude, longitude, description)
        VALUES (?, ?, ?, ?)
    ''', (name, latitude, longitude, description))
    
    store_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return store_id

def add_product(store_id, product_name, price):
    """商品を追加"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (store_id, product_name, price)
        VALUES (?, ?, ?)
    ''', (store_id, product_name, price))
    
    conn.commit()
    conn.close()

def get_all_stores():
    """すべての店舗とその商品を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.id, s.name, s.latitude, s.longitude, s.description
        FROM stores s
    ''')
    
    stores = []
    for row in cursor.fetchall():
        store = {
            'id': row[0],
            'name': row[1],
            'latitude': row[2],
            'longitude': row[3],
            'description': row[4],
            'products': []
        }
        
        # 各店舗の商品を取得
        cursor.execute('''
            SELECT product_name, price
            FROM products
            WHERE store_id = ?
        ''', (store['id'],))
        
        for product_row in cursor.fetchall():
            store['products'].append({
                'name': product_row[0],
                'price': product_row[1]
            })
        
        stores.append(store)
    
    conn.close()
    return stores

def delete_store(store_id):
    """店舗を削除（関連する商品も自動削除）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM stores WHERE id = ?', (store_id,))
    
    conn.commit()
    conn.close()

def delete_all_stores():
    """すべての店舗を削除（関連する商品も自動削除）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 外部キー制約により、商品も自動削除される
    cursor.execute('DELETE FROM stores')
    
    conn.commit()
    conn.close()
    print("All stores have been deleted from the database")

def update_store_coordinates(store_id, new_latitude, new_longitude):
    """店舗の座標を更新"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE stores
        SET latitude = ?, longitude = ?
        WHERE id = ?
    ''', (new_latitude, new_longitude, store_id))

    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        print(f"Store ID {store_id} coordinates updated to ({new_latitude}, {new_longitude})")
        return True
    else:
        conn.close()
        print(f"Store ID {store_id} not found")
        return False

def update_store(store_id, name, latitude, longitude, description=""):
    """店舗情報を更新"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE stores
        SET name = ?, latitude = ?, longitude = ?, description = ?
        WHERE id = ?
    ''', (name, latitude, longitude, description, store_id))

    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def delete_products_by_store(store_id):
    """特定店舗の商品をすべて削除"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM products WHERE store_id = ?', (store_id,))

    conn.commit()
    conn.close()

def get_store_by_id(store_id):
    """IDで店舗を取得"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, name, latitude, longitude, description
        FROM stores
        WHERE id = ?
    ''', (store_id,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    store = {
        'id': row[0],
        'name': row[1],
        'latitude': row[2],
        'longitude': row[3],
        'description': row[4],
        'products': []
    }

    # 商品を取得
    cursor.execute('''
        SELECT product_name, price
        FROM products
        WHERE store_id = ?
    ''', (store_id,))

    for product_row in cursor.fetchall():
        store['products'].append({
            'name': product_row[0],
            'price': product_row[1]
        })

    conn.close()
    return store

if __name__ == "__main__":
    init_database()