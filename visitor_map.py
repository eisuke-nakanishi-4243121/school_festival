import folium
from store_manager import StoreManager
import os

def create_visitor_map(output_file="festival_visitor_map.html"):
    """来場者向けの学園祭マップを作成"""
    
    # 盛岡市大通を中心に設定
    center_lat, center_lng = 39.703483, 141.144167
    
    # 地図を作成
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=19,
        tiles='OpenStreetMap'
    )
    
    # 店舗管理クラスから店舗データを取得
    store_manager = StoreManager()
    stores = store_manager.get_stores_for_display()
    
    # 各店舗をマーカーで表示
    for store in stores:
        # ポップアップ用のHTML作成
        popup_html = f"""
        <div style="width: 250px; font-family: Arial, sans-serif;">
            <h3 style="color: #2E8B57; margin-bottom: 10px;">{store['name']}</h3>
            {f'<p style="color: #666; margin-bottom: 8px;"><em>{store["description"]}</em></p>' if store['description'] else ''}
            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 5px;">
                <h4 style="color: #495057; margin-top: 0; margin-bottom: 8px;">商品・価格</h4>
        """
        
        # 商品リストを追加
        if store['products']:
            for product in store['products']:
                popup_html += f'<div style="margin-bottom: 3px;">• {product["name"]}: <span style="font-weight: bold; color: #dc3545;">{product["price"]}円</span></div>'
        else:
            popup_html += '<div style="color: #999;">商品情報なし</div>'
        
        popup_html += """
            </div>
        </div>
        """
        
        # マーカーを追加
        folium.Marker(
            [store['latitude'], store['longitude']],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=store['name'],
            icon=folium.Icon(
                color='green',
                icon='cutlery',
                prefix='fa'
            )
        ).add_to(m)
    
    # 中心地にタイトル用のマーカーを追加
    folium.Marker(
        [center_lat, center_lng],
        popup=folium.Popup(
            "<h3 style='color: #FF6B35; text-align: center;'>学園祭会場</h3><p style='text-align: center;'>各店舗のマーカーをクリックしてください！</p>",
            max_width=200
        ),
        tooltip="学園祭会場",
        icon=folium.Icon(
            color='red',
            icon='star',
            prefix='fa'
        )
    ).add_to(m)
    
    # HTMLファイルに保存
    m.save(output_file)
    
    print(f"来場者用マップが '{output_file}' として保存されました")
    print(f"店舗数: {len(stores)} 店舗")
    
    return output_file

def open_visitor_map():
    """来場者用マップを作成してブラウザで開く"""
    import webbrowser
    map_file = create_visitor_map()
    webbrowser.open(f'file:///{os.path.abspath(map_file)}')

if __name__ == "__main__":
    # テスト実行
    from database import init_database
    init_database()
    
    # サンプルデータがない場合は作成
    store_manager = StoreManager()
    existing_stores = store_manager.get_stores_for_display()
    
    if not existing_stores:
        print("サンプル店舗を作成中...")
        
        # サンプル店舗データ
        sample_stores = [
            {
                "name": "たこ焼き屋台",
                "lat": 39.7035,
                "lng": 141.1438,
                "products": [
                    {"name": "たこ焼き", "price": 400},
                    {"name": "イカ焼き", "price": 300}
                ],
                "description": "大阪風の本格たこ焼き"
            },
            {
                "name": "クレープスタンド",
                "lat": 39.7031,
                "lng": 141.1434,
                "products": [
                    {"name": "チョコバナナクレープ", "price": 350},
                    {"name": "いちごクレープ", "price": 320},
                    {"name": "カフェオレ", "price": 250}
                ],
                "description": "手作りクレープとドリンク"
            },
            {
                "name": "焼きそば本舗",
                "lat": 39.7033,
                "lng": 141.1440,
                "products": [
                    {"name": "焼きそば", "price": 300},
                    {"name": "焼きうどん", "price": 350},
                    {"name": "ジュース", "price": 150}
                ],
                "description": "特製ソースの焼きそば"
            }
        ]
        
        for store_data in sample_stores:
            store_manager.create_store_with_products(
                store_data["name"],
                store_data["lat"],
                store_data["lng"],
                store_data["products"],
                store_data["description"]
            )
        
        print("サンプル店舗を作成しました")
    
    # マップを作成
    create_visitor_map()
    
    # ブラウザで開く
    open_visitor_map()