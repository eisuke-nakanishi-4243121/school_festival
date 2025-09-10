import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import folium
import webbrowser
import os
import tempfile
from database import init_database
from store_manager import StoreManager
from locations import get_location_names, get_location_data, is_manual_input_required

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
        self.selected_location_name = None
        
        self.create_widgets()
        self.load_stores()
    
    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 地図選択セクション
        map_frame = ttk.LabelFrame(main_frame, text="店舗位置選択", padding="5")
        map_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 場所選択ドロップダウン
        ttk.Label(map_frame, text="場所:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(map_frame, textvariable=self.location_var, 
                                           values=get_location_names(), state="readonly", width=25)
        self.location_combo.grid(row=0, column=1, padx=(0, 10))
        self.location_combo.bind('<<ComboboxSelected>>', self.on_location_selected)
        
        # プレビュー地図ボタン
        ttk.Button(map_frame, text="地図プレビュー", command=self.show_preview_map).grid(row=0, column=2, padx=(0, 10))
        
        # 座標表示
        self.coord_label = ttk.Label(map_frame, text="位置が選択されていません")
        self.coord_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 手動入力フレーム（初期は非表示）
        self.manual_frame = ttk.Frame(map_frame)
        self.manual_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(self.manual_frame, text="緯度:").grid(row=0, column=0, padx=(0, 5))
        self.manual_lat_var = tk.StringVar()
        ttk.Entry(self.manual_frame, textvariable=self.manual_lat_var, width=15).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(self.manual_frame, text="経度:").grid(row=0, column=2, padx=(0, 5))
        self.manual_lng_var = tk.StringVar()
        ttk.Entry(self.manual_frame, textvariable=self.manual_lng_var, width=15).grid(row=0, column=3)
        
        ttk.Button(self.manual_frame, text="座標確定", command=self.confirm_manual_coordinates).grid(row=0, column=4, padx=(10, 0))
        
        # 初期状態では手動入力フレームを非表示
        self.manual_frame.grid_remove()
        
        # 店舗情報入力セクション
        input_frame = ttk.LabelFrame(main_frame, text="店舗情報入力", padding="5")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 店舗名
        ttk.Label(input_frame, text="店舗名:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.store_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.store_name_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 店舗説明
        ttk.Label(input_frame, text="店舗説明:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.description_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.description_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 商品情報の動的リスト
        ttk.Label(input_frame, text="商品情報:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=2)
        
        # 商品リスト用フレーム
        self.products_frame = ttk.Frame(input_frame)
        self.products_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 商品リストの管理
        self.product_entries = []
        
        # 商品追加ボタンを先に作成
        self.add_product_btn = ttk.Button(self.products_frame, text="+ 商品を追加", command=self.add_product_row)
        
        # 初期商品を追加
        self.add_product_row("クレープ", "300")
        self.add_product_row("ドリンク", "200")
        self.add_product_row("たこ焼き", "250")\
        
        # ボタンフレーム
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="店舗を登録", command=self.register_store).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="クリア", command=self.clear_form).grid(row=0, column=1)
        
        # 店舗一覧セクション
        list_frame = ttk.LabelFrame(main_frame, text="登録済み店舗一覧", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
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
        store_button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(store_button_frame, text="位置編集", command=self.edit_store_coordinates).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(store_button_frame, text="選択した店舗を削除", command=self.delete_selected_store).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(store_button_frame, text="来場者用マップを開く", command=self.open_visitor_map).grid(row=0, column=2)
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def on_location_selected(self, event=None):
        """場所が選択されたときの処理"""
        location_name = self.location_var.get()
        if not location_name:
            return
        
        self.selected_location_name = location_name
        location_data = get_location_data(location_name)
        
        if is_manual_input_required(location_name):
            # 手動入力が必要な場合
            self.manual_frame.grid()
            self.coord_label.config(text=f"選択: {location_name} - 下記に座標を入力してください")
            self.selected_lat = None
            self.selected_lng = None
        else:
            # プリセット座標を使用
            self.manual_frame.grid_remove()
            self.selected_lat = location_data["latitude"]
            self.selected_lng = location_data["longitude"]
            self.coord_label.config(text=f"選択: {location_name} ({self.selected_lat:.6f}, {self.selected_lng:.6f})")
    
    def confirm_manual_coordinates(self):
        """手動入力座標を確定"""
        try:
            lat = float(self.manual_lat_var.get())
            lng = float(self.manual_lng_var.get())
            
            self.selected_lat = lat
            self.selected_lng = lng
            location_name = self.selected_location_name or "手動入力"
            self.coord_label.config(text=f"選択: {location_name} ({lat:.6f}, {lng:.6f})")
            
        except ValueError:
            messagebox.showerror("エラー", "有効な数値を入力してください")
    
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
        
        self.location_var.set("")
        self.location_combo.selection_clear()
        self.selected_lat = None
        self.selected_lng = None
        self.selected_location_name = None
        self.manual_lat_var.set("")
        self.manual_lng_var.set("")
        self.manual_frame.grid_remove()
        self.coord_label.config(text="位置が選択されていません")
    
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