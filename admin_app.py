import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import folium
import webbrowser
import os
import tempfile
import threading
from database import init_database
from store_manager import StoreManager
# locations モジュールは不要になったため削除
from map_selector import select_coordinates_from_map

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("学園祭店舗管理システム - 運営者画面")
        self.root.geometry("800x700")
        
        # データベース初期化
        init_database()
        self.store_manager = StoreManager()
        
        # 選択された座標
        self.selected_lat = None
        self.selected_lng = None
        
        self.create_widgets()
        self.load_stores()
    
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 座標入力セクション
        coord_frame = ttk.LabelFrame(main_frame, text="店舗位置入力", padding="10")
        coord_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 座標表示
        self.coord_label = ttk.Label(coord_frame, text="座標を入力してください", font=("", 9))
        self.coord_label.grid(row=0, column=0, columnspan=5, sticky=tk.W, pady=(0, 10))
        
        # 座標入力フレーム
        input_coord_frame = ttk.Frame(coord_frame)
        input_coord_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E))
        
        # 緯度入力
        ttk.Label(input_coord_frame, text="緯度:", font=("", 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.manual_lat_var = tk.StringVar()
        lat_entry = ttk.Entry(input_coord_frame, textvariable=self.manual_lat_var, width=18)
        lat_entry.grid(row=0, column=1, padx=(0, 15))
        
        # 経度入力
        ttk.Label(input_coord_frame, text="経度:", font=("", 9)).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.manual_lng_var = tk.StringVar()
        lng_entry = ttk.Entry(input_coord_frame, textvariable=self.manual_lng_var, width=18)
        lng_entry.grid(row=0, column=3, padx=(0, 15))
        
        # 座標確定ボタン
        ttk.Button(input_coord_frame, text="座標確定", command=self.confirm_manual_coordinates).grid(row=0, column=4)
        
        # ボタンフレーム
        button_coord_frame = ttk.Frame(coord_frame)
        button_coord_frame.grid(row=2, column=0, columnspan=5, pady=(10, 0))
        
        # 地図から選択ボタン
        ttk.Button(button_coord_frame, text="🗺️ 地図から選択", command=self.open_map_selector).pack(side=tk.LEFT, padx=(0, 10))
        
        # プレビュー地図ボタン
        ttk.Button(button_coord_frame, text="👁️ 地図プレビュー", command=self.show_preview_map).pack(side=tk.LEFT)
        
        # 店舗情報入力セクション
        self.input_frame = ttk.LabelFrame(main_frame, text="店舗情報入力", padding="10")
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # 編集モード表示用
        self.edit_mode_label = ttk.Label(self.input_frame, text="", font=('Arial', 10, 'bold'), foreground='red')
        self.edit_mode_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # 編集中店舗ID
        self.editing_store_id = None
        
        # 店舗名
        ttk.Label(self.input_frame, text="店舗名:", font=("", 10)).grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
        self.store_name_var = tk.StringVar()
        store_entry = ttk.Entry(self.input_frame, textvariable=self.store_name_var, width=35, font=("", 10))
        store_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 8))

        # 店舗説明
        ttk.Label(self.input_frame, text="店舗説明:", font=("", 10)).grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        self.description_var = tk.StringVar()
        desc_entry = ttk.Entry(self.input_frame, textvariable=self.description_var, width=35, font=("", 10))
        desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 8))

        # 商品情報の動的リスト
        ttk.Label(self.input_frame, text="商品情報:", font=("", 10)).grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(8, 0))

        # 商品リスト用フレーム
        self.products_frame = ttk.Frame(self.input_frame)
        self.products_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(8, 0))
        
        # 商品リストの管理
        self.product_entries = []
        
        # 商品追加ボタンを先に作成
        self.add_product_btn = ttk.Button(self.products_frame, text="+ 商品を追加", command=self.add_product_row)
        
        # 初期商品を追加
        self.add_product_row("クレープ", "300")
        self.add_product_row("ドリンク", "200")
        self.add_product_row("たこ焼き", "250")\
        
        # ボタンフレーム
        button_frame = ttk.Frame(self.input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        # 登録ボタン（強調）
        self.register_btn = ttk.Button(button_frame, text="🏪 店舗を登録", command=self.register_store)
        self.register_btn.grid(row=0, column=0, padx=(0, 15))

        # 更新ボタン（編集時に表示）
        self.update_btn = ttk.Button(button_frame, text="💾 更新", command=self.update_store)
        self.update_btn.grid(row=0, column=0, padx=(0, 15))
        self.update_btn.grid_remove()  # 初期は非表示

        # クリアボタン
        self.clear_btn = ttk.Button(button_frame, text="🗑️ クリア", command=self.clear_form)
        self.clear_btn.grid(row=0, column=1, padx=(0, 15))

        # キャンセルボタン（編集時に表示）
        self.cancel_btn = ttk.Button(button_frame, text="❌ キャンセル", command=self.cancel_edit)
        self.cancel_btn.grid(row=0, column=2)
        self.cancel_btn.grid_remove()  # 初期は非表示
        
        # 店舗一覧セクション
        list_frame = ttk.LabelFrame(main_frame, text="📋 登録済み店舗一覧", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview for store list
        columns = ("ID", "店舗名", "座標", "商品数")
        self.store_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.store_tree.heading(col, text=col)
            self.store_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.store_tree.yview)
        self.store_tree.configure(yscrollcommand=scrollbar.set)
        
        self.store_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 店舗操作ボタン
        store_button_frame = ttk.Frame(list_frame)
        store_button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(store_button_frame, text="📝 詳細編集", command=self.edit_store_details).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(store_button_frame, text="📍 位置編集", command=self.edit_store_coordinates).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(store_button_frame, text="🗑️ 削除", command=self.delete_selected_store).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(store_button_frame, text="🌐 来場者用マップを開く", command=self.open_visitor_map).grid(row=0, column=3)
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.input_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def confirm_manual_coordinates(self):
        """手動入力座標を確定"""
        try:
            lat = float(self.manual_lat_var.get())
            lng = float(self.manual_lng_var.get())
            
            self.selected_lat = lat
            self.selected_lng = lng
            self.coord_label.config(text=f"座標確定: 緯度 {lat:.6f}, 経度 {lng:.6f}")
            
        except ValueError:
            messagebox.showerror("エラー", "有効な数値を入力してください")
    
    def open_map_selector(self):
        """地図選択ウィンドウを開く"""
        def on_coordinates_selected(lat, lng):
            # UIを更新（メインスレッドで実行）
            self.root.after(0, lambda: self._update_coordinates_from_map(lat, lng))
        
        # 別スレッドで地図選択ウィンドウを開く
        def run_map_selector():
            try:
                coordinates = select_coordinates_from_map(on_coordinates_selected)
                if coordinates:
                    lat, lng = coordinates
                    # メインスレッドでUIを更新
                    self.root.after(0, lambda: self._update_coordinates_from_map(lat, lng))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("エラー", f"地図選択中にエラーが発生しました: {e}"))
        
        # 地図選択を別スレッドで実行
        thread = threading.Thread(target=run_map_selector, daemon=True)
        thread.start()
    
    def _update_coordinates_from_map(self, lat, lng):
        """地図から選択された座標でUIを更新"""
        self.manual_lat_var.set(f"{lat:.6f}")
        self.manual_lng_var.set(f"{lng:.6f}")
        self.selected_lat = lat
        self.selected_lng = lng
        self.coord_label.config(text=f"座標確定: 緯度 {lat:.6f}, 経度 {lng:.6f}")
    
    def show_preview_map(self):
        """プレビュー用の地図を表示"""
        self.open_preview_map()
    
    def open_preview_map(self):
        """プレビュー用の地図を開く"""
        # 盛岡市大通を中心とした地図を作成
        center_lat, center_lng = 39.7033, 141.1436
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=17,
            tiles='OpenStreetMap'
        )
        
        # 既存の店舗をドラッグ可能マーカーで表示
        stores = self.store_manager.get_stores_for_display()
        for store in stores:
            # ドラッグ可能マーカーを作成
            marker = folium.Marker(
                [store['latitude'], store['longitude']],
                popup=f"""
                <div>
                    <strong>{store['name']}</strong><br>
                    ID: {store['id']}<br>
                    座標: ({store['latitude']:.6f}, {store['longitude']:.6f})<br>
                    <button onclick="editStore({store['id']})">編集</button>
                    <button onclick="deleteStore({store['id']})">削除</button>
                </div>
                """,
                tooltip=f"ドラッグして移動: {store['name']}",
                icon=folium.Icon(color='red', icon='info-sign'),
                draggable=True
            )
            marker.add_to(m)
        
        # プリセット場所をマーカーで表示
        from locations import PRESET_LOCATIONS
        for location_name, location_data in PRESET_LOCATIONS.items():
            if location_data['latitude'] is not None and location_data['longitude'] is not None:
                folium.Marker(
                    [location_data['latitude'], location_data['longitude']],
                    popup=f"候補地: {location_name}<br>{location_data['description']}",
                    tooltip=location_name,
                    icon=folium.Icon(color='green', icon='flag')
                ).add_to(m)
        
        # 座標表示用JavaScript
        coord_display_js = '''
        var coordinateDisplay = L.control({position: 'bottomleft'});
        coordinateDisplay.onAdd = function(map) {
            var div = L.DomUtil.create('div', 'coordinate-display');
            div.style.backgroundColor = 'white';
            div.style.padding = '5px 10px';
            div.style.border = '2px solid rgba(0,0,0,0.2)';
            div.style.borderRadius = '5px';
            div.style.fontSize = '12px';
            div.innerHTML = '座標: マウスを地図上に移動してください';
            return div;
        };
        coordinateDisplay.addTo(map);
        
        // マウス移動時の座標表示
        map.on('mousemove', function(e) {
            var lat = e.latlng.lat.toFixed(6);
            var lng = e.latlng.lng.toFixed(6);
            document.querySelector('.coordinate-display').innerHTML = 
                '座標: ' + lat + ', ' + lng;
        });
        
        // クリック時の座標コピー
        map.on('click', function(e) {
            var lat = e.latlng.lat.toFixed(6);
            var lng = e.latlng.lng.toFixed(6);
            
            // クリップボードにコピー
            navigator.clipboard.writeText(lat + ',' + lng).then(function() {
                document.querySelector('.coordinate-display').innerHTML = 
                    'コピーしました: ' + lat + ', ' + lng;
                setTimeout(function() {
                    document.querySelector('.coordinate-display').innerHTML = 
                        '座標: ' + lat + ', ' + lng;
                }, 2000);
            });
        });
        
        // 右クリックメニュー
        var contextMenu = null;
        var rightClickLatLng = null;
        
        map.on('contextmenu', function(e) {
            rightClickLatLng = e.latlng;
            
            // 既存のメニューを削除
            if (contextMenu) {
                map.removeControl(contextMenu);
            }
            
            // 右クリックメニューを作成
            contextMenu = L.control({position: 'topleft'});
            contextMenu.onAdd = function(map) {
                var div = L.DomUtil.create('div', 'context-menu');
                div.style.position = 'absolute';
                div.style.left = e.containerPoint.x + 'px';
                div.style.top = e.containerPoint.y + 'px';
                div.style.backgroundColor = 'white';
                div.style.border = '2px solid #ccc';
                div.style.borderRadius = '5px';
                div.style.padding = '5px';
                div.style.zIndex = '1000';
                div.innerHTML = '<button onclick="addStoreHere()">ここに店舗を追加</button>';
                return div;
            };
            contextMenu.addTo(map);
            
            // 3秒後にメニューを自動削除
            setTimeout(function() {
                if (contextMenu) {
                    map.removeControl(contextMenu);
                    contextMenu = null;
                }
            }, 3000);
        });
        
        // ドラッグ終了時のイベント処理
        map.eachLayer(function(layer) {
            if (layer instanceof L.Marker && layer.options.draggable) {
                layer.on('dragend', function(e) {
                    var newLatLng = e.target.getLatLng();
                    var lat = newLatLng.lat.toFixed(6);
                    var lng = newLatLng.lng.toFixed(6);
                    
                    // マーカー移動完了の通知
                    document.querySelector('.coordinate-display').innerHTML = 
                        'マーカー移動: ' + lat + ', ' + lng + ' (保存してください)';
                });
            }
        });
        
        // JavaScript関数の定義
        function addStoreHere() {
            if (rightClickLatLng) {
                var lat = rightClickLatLng.lat.toFixed(6);
                var lng = rightClickLatLng.lng.toFixed(6);
                alert('新しい店舗を追加\\n座標: ' + lat + ', ' + lng + '\\n\\n管理画面で手動入力を使用して登録してください。');
                navigator.clipboard.writeText(lat + ',' + lng);
            }
        }
        
        function editStore(storeId) {
            alert('店舗ID ' + storeId + ' の編集\\n\\n管理画面の店舗一覧から編集してください。');
        }
        
        function deleteStore(storeId) {
            if (confirm('店舗ID ' + storeId + ' を削除しますか？')) {
                alert('管理画面の店舗一覧から削除してください。');
            }
        }
        '''
        
        # HTMLテンプレート
        html_template = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>学園祭会場プレビューマップ</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }}
                #map {{
                    height: 85vh;
                    width: 100%;
                }}
                #info {{
                    height: 15vh;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-top: 2px solid #dee2e6;
                    text-align: center;
                }}
                .instruction {{
                    font-size: 14px;
                    color: #495057;
                    margin: 0;
                }}
                .legend {{
                    margin-top: 5px;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            {m._repr_html_()}
            <div id="info">
                <p class="instruction">緑のフラグ: プリセット場所 | 赤いマーカー: 既存店舗</p>
                <p class="legend">地図をクリックすると座標がコピーされます（左下に表示）</p>
            </div>
            <script>
                {coord_display_js}
            </script>
        </body>
        </html>
        '''
        
        # 一時ファイルに保存して開く
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_template)
            temp_file = f.name
        
        webbrowser.open(f'file:///{temp_file}')
    
    
    def register_store(self):
        """店舗を登録"""
        if self.selected_lat is None or self.selected_lng is None:
            messagebox.showerror("エラー", "まず地図上で位置を選択してください")
            return
        
        store_name = self.store_name_var.get().strip()
        if not store_name:
            messagebox.showerror("エラー", "店舗名を入力してください")
            return
        
        products = self.get_products_data()
        
        if not products:
            messagebox.showerror("エラー", "商品情報を正しい形式で入力してください\\n形式: 商品名:価格")
            return
        
        description = self.description_var.get().strip()
        
        # 店舗を登録
        store_id, message = self.store_manager.create_store_with_products(
            store_name, self.selected_lat, self.selected_lng, products, description
        )
        
        if store_id:
            messagebox.showinfo("成功", message)
            self.clear_form()
            self.load_stores()
        else:
            messagebox.showerror("エラー", message)
    
    def add_product_row(self, name="", price=""):
        """商品行を追加"""
        row_num = len(self.product_entries)
        
        # 商品名入力
        name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(self.products_frame, textvariable=name_var, width=20)
        name_entry.grid(row=row_num, column=0, padx=(0, 5), pady=2)
        
        # 価格入力
        price_var = tk.StringVar(value=price)
        price_entry = ttk.Entry(self.products_frame, textvariable=price_var, width=8)
        price_entry.grid(row=row_num, column=1, padx=(0, 5), pady=2)
        
        # 円ラベル
        ttk.Label(self.products_frame, text="円").grid(row=row_num, column=2, padx=(0, 10), pady=2)
        
        # 削除ボタン
        delete_btn = ttk.Button(self.products_frame, text="削除", width=6,
                               command=lambda: self.remove_product_row(row_num))
        delete_btn.grid(row=row_num, column=3, pady=2)
        
        # エントリを保存
        self.product_entries.append({
            'name_var': name_var,
            'price_var': price_var,
            'name_entry': name_entry,
            'price_entry': price_entry,
            'delete_btn': delete_btn
        })
        
        self.update_add_button_position()
    
    def remove_product_row(self, row_num):
        """商品行を削除"""
        if len(self.product_entries) <= 1:
            messagebox.showwarning("警告", "最低1つの商品が必要です")
            return
        
        # ウィジェットを削除
        entry = self.product_entries[row_num]
        entry['name_entry'].destroy()
        entry['price_entry'].destroy()
        entry['delete_btn'].destroy()
        
        # リストから削除
        del self.product_entries[row_num]
        
        # 再配置
        self.reorganize_products()
        self.update_add_button_position()
    
    def reorganize_products(self):
        """商品リストを再配置"""
        for i, entry in enumerate(self.product_entries):
            entry['name_entry'].grid(row=i, column=0, padx=(0, 5), pady=2)
            entry['price_entry'].grid(row=i, column=1, padx=(0, 5), pady=2)
            entry['delete_btn'].grid(row=i, column=3, pady=2)
            # 削除ボタンのコマンドを更新
            entry['delete_btn'].config(command=lambda idx=i: self.remove_product_row(idx))
    
    def update_add_button_position(self):
        """追加ボタンの位置を更新"""
        row_num = len(self.product_entries)
        self.add_product_btn.grid(row=row_num, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
    
    def get_products_data(self):
        """商品データを取得"""
        products = []
        for entry in self.product_entries:
            name = entry['name_var'].get().strip()
            price_str = entry['price_var'].get().strip()
            
            if name and price_str:
                try:
                    price = int(price_str)
                    products.append({"name": name, "price": price})
                except ValueError:
                    continue
        return products
    
    def clear_form(self):
        """フォームをクリア"""
        self.store_name_var.set("")
        self.description_var.set("")
        
        # 商品リストをリセット
        for entry in self.product_entries:
            entry['name_entry'].destroy()
            entry['price_entry'].destroy()
            entry['delete_btn'].destroy()
        self.product_entries.clear()
        
        # 初期商品を再追加
        self.add_product_row("クレープ", "300")
        self.add_product_row("ドリンク", "200")
        self.add_product_row("たこ焼き", "250")
        
        # 座標関連をクリア
        self.selected_lat = None
        self.selected_lng = None
        self.manual_lat_var.set("")
        self.manual_lng_var.set("")
        self.coord_label.config(text="座標を入力してください")
    
    def load_stores(self):
        """店舗一覧を読み込み"""
        for item in self.store_tree.get_children():
            self.store_tree.delete(item)
        
        stores = self.store_manager.get_stores_for_display()
        for store in stores:
            coord_text = f"({store['latitude']:.6f}, {store['longitude']:.6f})"
            product_count = len(store['products'])
            
            self.store_tree.insert('', 'end', values=(
                store['id'],
                store['name'],
                coord_text,
                f"{product_count}個"
            ))
    
    def delete_selected_store(self):
        """選択された店舗を削除"""
        selection = self.store_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除する店舗を選択してください")
            return
        
        item = self.store_tree.item(selection[0])
        store_id = item['values'][0]
        store_name = item['values'][1]
        
        if messagebox.askyesno("確認", f"店舗 '{store_name}' を削除しますか？"):
            success, message = self.store_manager.remove_store(store_id)
            if success:
                messagebox.showinfo("成功", message)
                self.load_stores()
            else:
                messagebox.showerror("エラー", message)
    
    def edit_store_coordinates(self):
        """選択された店舗の座標を編集"""
        selected_items = self.store_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "編集する店舗を選択してください")
            return
        
        item = selected_items[0]
        store_data = self.store_tree.item(item)['values']
        store_id = store_data[0]
        store_name = store_data[1]
        current_coords = store_data[2]  # "lat, lng" format
        
        # 現在の座標を解析
        try:
            lat_str, lng_str = current_coords.split(', ')
            current_lat = float(lat_str)
            current_lng = float(lng_str)
        except:
            current_lat = 39.7033
            current_lng = 141.1436
        
        # 座標編集ダイアログを表示
        self.show_coordinate_edit_dialog(store_id, store_name, current_lat, current_lng)
    
    def show_coordinate_edit_dialog(self, store_id, store_name, current_lat, current_lng):
        """座標編集ダイアログを表示"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"座標編集 - {store_name}")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 中央に配置
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # メインフレーム
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 店舗名表示
        ttk.Label(main_frame, text=f"店舗: {store_name}", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 緯度入力
        ttk.Label(main_frame, text="緯度:").grid(row=1, column=0, sticky=tk.W, pady=5)
        lat_var = tk.StringVar(value=str(current_lat))
        lat_entry = ttk.Entry(main_frame, textvariable=lat_var, width=20)
        lat_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 経度入力
        ttk.Label(main_frame, text="経度:").grid(row=2, column=0, sticky=tk.W, pady=5)
        lng_var = tk.StringVar(value=str(current_lng))
        lng_entry = ttk.Entry(main_frame, textvariable=lng_var, width=20)
        lng_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 現在位置表示
        current_info = ttk.Label(main_frame, text=f"現在位置: ({current_lat:.6f}, {current_lng:.6f})", 
                                font=('Arial', 9))
        current_info.grid(row=3, column=0, columnspan=2, pady=5)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save_coordinates():
            try:
                new_lat = float(lat_var.get())
                new_lng = float(lng_var.get())
                
                # 座標の妥当性チェック
                if not (-90 <= new_lat <= 90):
                    messagebox.showerror("エラー", "緯度は-90から90の間で入力してください")
                    return
                if not (-180 <= new_lng <= 180):
                    messagebox.showerror("エラー", "経度は-180から180の間で入力してください")
                    return
                
                # データベースを更新
                from database import update_store_coordinates
                if update_store_coordinates(store_id, new_lat, new_lng):
                    messagebox.showinfo("成功", f"店舗の座標を更新しました\\n新しい座標: ({new_lat:.6f}, {new_lng:.6f})")
                    dialog.destroy()
                    self.load_stores()  # 店舗一覧を更新
                    # 地図プレビューがある場合は自動更新
                    self.refresh_preview_if_open()
                else:
                    messagebox.showerror("エラー", "座標の更新に失敗しました")
            except ValueError:
                messagebox.showerror("エラー", "有効な数値を入力してください")
        
        ttk.Button(button_frame, text="保存", command=save_coordinates).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="キャンセル", command=dialog.destroy).grid(row=0, column=1)
        
        # グリッド設定
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # フォーカスを緯度入力に設定
        lat_entry.focus()
        lat_entry.select_range(0, tk.END)
    
    def refresh_preview_if_open(self):
        """地図プレビューが開いている場合は更新"""
        # プレビューマップを再生成して表示
        try:
            # 既存のプレビューファイルを削除
            preview_files = ['festival_preview_map.html']
            for file in preview_files:
                if os.path.exists(file):
                    os.remove(file)
            
            # 新しいプレビューマップを自動で開く
            self.show_preview_map()
        except:
            pass  # エラーが発生しても処理を継続
    
    def edit_store_details(self):
        """選択された店舗の詳細を編集"""
        selected_items = self.store_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "編集する店舗を選択してください")
            return

        item = selected_items[0]
        store_data = self.store_tree.item(item)['values']
        store_id = store_data[0]

        # データベースから店舗の詳細情報を取得
        from database import get_store_by_id
        store = get_store_by_id(store_id)

        if not store:
            messagebox.showerror("エラー", "店舗データが見つかりません")
            return

        self.load_store_for_editing(store)

    def load_store_for_editing(self, store):
        """メイン画面で店舗を編集モードに切り替え"""
        # 編集モードに設定
        self.editing_store_id = store['id']

        # UI表示を編集モードに変更
        self.edit_mode_label.config(text=f"編集中: {store['name']} (ID: {store['id']})")
        self.input_frame.config(text="店舗情報編集")

        # ボタン表示を変更
        self.register_btn.grid_remove()
        self.clear_btn.grid_remove()
        self.update_btn.grid()
        self.cancel_btn.grid()

        # フォームに既存データを読み込み
        self.store_name_var.set(store['name'])
        self.description_var.set(store['description'] or "")
        self.manual_lat_var.set(f"{store['latitude']:.6f}")
        self.manual_lng_var.set(f"{store['longitude']:.6f}")
        self.selected_lat = store['latitude']
        self.selected_lng = store['longitude']
        self.coord_label.config(text=f"座標確定: 緯度 {store['latitude']:.6f}, 経度 {store['longitude']:.6f}")

        # 既存商品をクリア
        for entry in self.product_entries:
            entry['name_entry'].destroy()
            entry['price_entry'].destroy()
            entry['delete_btn'].destroy()
        self.product_entries.clear()

        # 既存商品を読み込み
        if store['products']:
            for product in store['products']:
                self.add_product_row(product['name'], str(product['price']))
        else:
            self.add_product_row()

    def cancel_edit(self):
        """編集をキャンセルして通常モードに戻る"""
        self.editing_store_id = None

        # UI表示を通常モードに戻す
        self.edit_mode_label.config(text="")
        self.input_frame.config(text="店舗情報入力")

        # ボタン表示を戻す
        self.update_btn.grid_remove()
        self.cancel_btn.grid_remove()
        self.register_btn.grid()
        self.clear_btn.grid()

        # フォームをクリア
        self.clear_form()

    def update_store(self):
        """編集中の店舗を更新"""
        if not self.editing_store_id:
            messagebox.showerror("エラー", "編集中の店舗がありません")
            return

        if self.selected_lat is None or self.selected_lng is None:
            messagebox.showerror("エラー", "座標を設定してください")
            return

        store_name = self.store_name_var.get().strip()
        if not store_name:
            messagebox.showerror("エラー", "店舗名を入力してください")
            return

        products = self.get_products_data()
        if not products:
            messagebox.showerror("エラー", "最低1つの商品が必要です")
            return

        description = self.description_var.get().strip()

        try:
            # データベースを更新
            from database import update_store, delete_products_by_store, add_product

            # 店舗情報を更新
            if update_store(self.editing_store_id, store_name, self.selected_lat, self.selected_lng, description):
                # 既存商品を削除
                delete_products_by_store(self.editing_store_id)

                # 新しい商品を追加
                for product in products:
                    add_product(self.editing_store_id, product['name'], product['price'])

                messagebox.showinfo("成功", f"店舗「{store_name}」の情報を更新しました")
                self.cancel_edit()  # 編集モードを終了
                self.load_stores()  # 店舗一覧を更新
            else:
                messagebox.showerror("エラー", "店舗情報の更新に失敗しました")

        except Exception as e:
            messagebox.showerror("エラー", f"更新中にエラーが発生しました: {e}")

    def open_visitor_map(self):
        """来場者用マップを開く"""
        from visitor_map import create_visitor_map
        map_file = create_visitor_map()
        if map_file:
            webbrowser.open(f'file:///{os.path.abspath(map_file)}')

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()