from database import add_store, add_product, get_all_stores, delete_store

class StoreManager:
    """店舗管理クラス"""
    
    def __init__(self):
        pass
    
    def create_store_with_products(self, store_name, latitude, longitude, products_data, description=""):
        """
        店舗と商品を一括で作成
        products_data: [{"name": "商品名", "price": 価格}, ...]
        """
        try:
            # 店舗を追加
            store_id = add_store(store_name, latitude, longitude, description)
            
            # 商品を追加
            for product in products_data:
                add_product(store_id, product["name"], product["price"])
            
            return store_id, "店舗が正常に登録されました"
        
        except Exception as e:
            return None, f"店舗登録中にエラーが発生しました: {str(e)}"
    
    def get_stores_for_display(self):
        """表示用の店舗データを取得"""
        stores = get_all_stores()
        display_stores = []
        
        for store in stores:
            # 商品リストを文字列形式に変換
            products_text = []
            for product in store['products']:
                products_text.append(f"{product['name']}: {product['price']}円")
            
            display_store = {
                'id': store['id'],
                'name': store['name'],
                'latitude': store['latitude'],
                'longitude': store['longitude'],
                'description': store['description'],
                'products_text': "\n".join(products_text),
                'products': store['products']
            }
            display_stores.append(display_store)
        
        return display_stores
    
    def remove_store(self, store_id):
        """店舗を削除"""
        try:
            delete_store(store_id)
            return True, "店舗が削除されました"
        except Exception as e:
            return False, f"店舗削除中にエラーが発生しました: {str(e)}"
    
    def parse_products_from_text(self, products_text):
        """
        テキストから商品データを解析
        入力例: "クレープ:300\nドリンク:200\nたこ焼き:250"
        """
        products = []
        lines = products_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                try:
                    name, price_str = line.split(':', 1)
                    price = int(price_str.strip().replace('円', ''))
                    products.append({
                        "name": name.strip(),
                        "price": price
                    })
                except ValueError:
                    continue  # 不正な形式の行は無視
        
        return products

if __name__ == "__main__":
    # テスト用
    manager = StoreManager()
    
    # テスト商品データ
    test_products = [
        {"name": "クレープ", "price": 300},
        {"name": "ドリンク", "price": 200}
    ]
    
    # テスト店舗作成
    store_id, message = manager.create_store_with_products(
        "テスト店舗", 39.7033, 141.1436, test_products, "テスト用の店舗です"
    )
    
    print(f"作成結果: {message}")
    
    # 店舗一覧表示
    stores = manager.get_stores_for_display()
    for store in stores:
        print(f"店舗: {store['name']}")
        print(f"商品:\n{store['products_text']}")
        print("---")