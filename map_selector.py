"""
地図座標選択ウィンドウ
Tkinter + 一時HTMLファイル + ブラウザ起動による地図選択インターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import os
import tempfile
import json
import time
import threading


class MapSelector:
    """地図から座標を選択するためのウィンドウクラス"""
    
    def __init__(self):
        self.selected_coordinates = None
        self.temp_html_path = None
        self.temp_coords_path = None
        self.root = None
        
    def show_map_selector(self, callback=None):
        """
        地図選択ウィンドウを表示
        
        Args:
            callback: 座標選択完了時に呼ばれるコールバック関数 callback(lat, lng)
        
        Returns:
            tuple: (latitude, longitude) or None if cancelled
        """
        self.callback = callback
        self.selected_coordinates = None
        
        try:
            # 一時HTMLファイルを作成
            self._create_temp_html()
            
            # Tkinter ダイアログを作成
            self.root = tk.Toplevel()
            self.root.title("🗺️ 地図から座標選択")
            self.root.geometry("480x380")
            self.root.resizable(False, False)
            self.root.grab_set()  # モーダルウィンドウに
            
            self._create_dialog_widgets()
            
            # ブラウザで地図を開く（Windowsパス形式で）
            file_url = f"file:///{self.temp_html_path.replace(os.sep, '/')}"
            print(f"地図を開いています: {file_url}")
            webbrowser.open(file_url)
            
            # 座標監視を開始
            self._start_coordinate_monitoring()
            
            # ダイアログを表示
            self.root.wait_window()
            
        except Exception as e:
            print(f"地図選択ウィンドウの表示中にエラーが発生しました: {e}")
            return None
        finally:
            # 一時ファイルを削除
            self._cleanup_temp_files()
        
        return self.selected_coordinates
    
    def _create_dialog_widgets(self):
        """ダイアログのウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 説明ラベル
        instruction_frame = ttk.Frame(main_frame)
        instruction_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(instruction_frame, text="🌐", font=("", 16)).pack()
        ttk.Label(instruction_frame, text="ブラウザで詳細地図が開きます", 
                 font=("", 11, "bold"), justify=tk.CENTER).pack(pady=(5, 3))
        ttk.Label(instruction_frame, text="1. 地図上をクリックして位置を選択\n2. 「この位置で確定」ボタンをクリック\n3. このダイアログで「座標貼り付け」または「確定」", 
                 font=("", 9), justify=tk.CENTER).pack()
        
        # 現在の座標表示
        coord_display_frame = ttk.LabelFrame(main_frame, text="📍 選択座標", padding="10")
        coord_display_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.coord_var = tk.StringVar(value="座標: 未選択")
        self.coord_label = ttk.Label(coord_display_frame, textvariable=self.coord_var, font=("", 10, "bold"))
        self.coord_label.pack()
        
        # 手動入力フレーム
        manual_frame = ttk.LabelFrame(main_frame, text="✏️ 手動座標入力", padding="12")
        manual_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 緯度
        ttk.Label(manual_frame, text="緯度:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.lat_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.lat_var, width=15).grid(row=0, column=1, padx=(0, 10))
        
        # 経度
        ttk.Label(manual_frame, text="経度:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.lng_var = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.lng_var, width=15).grid(row=0, column=3)
        
        # 手動入力確定ボタン
        ttk.Button(manual_frame, text="手動入力確定", command=self._manual_input_confirm).grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # 座標貼り付けボタン
        ttk.Button(manual_frame, text="📋 座標貼り付け", command=self._paste_coordinates).grid(row=1, column=2, columnspan=2, pady=(8, 0))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 確定ボタン（強調）
        confirm_btn = ttk.Button(button_frame, text="✅ 確定", command=self._confirm_selection)
        confirm_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # キャンセルボタン
        cancel_btn = ttk.Button(button_frame, text="❌ キャンセル", command=self._cancel_selection)
        cancel_btn.pack(side=tk.LEFT)
        
        # ウィンドウを中央に配置
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def _create_temp_html(self):
        """一時HTMLファイルを作成"""
        try:
            # 座標保存用の一時ファイルパスを作成
            temp_fd, self.temp_coords_path = tempfile.mkstemp(suffix='.json')
            os.close(temp_fd)
            
            # ユニークIDを生成（キャッシュ回避）
            import time
            unique_id = str(int(time.time() * 1000))
            print(f"生成されたユニークID: {unique_id}")
            
            # HTMLテンプレートを作成
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>店舗位置選択 - {unique_id}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css?v={unique_id}" />
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        .info-box {{
            position: absolute; top: 10px; right: 10px; background: white;
            padding: 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            z-index: 1000; font-size: 14px; max-width: 320px; min-width: 280px;
        }}
        .coordinates {{ font-weight: bold; color: #2c5aa0; margin: 10px 0; }}
        .instructions {{ color: #333; margin-bottom: 15px; line-height: 1.4; }}
        .confirm-btn {{
            background: #4CAF50; color: white; border: none; padding: 12px 16px;
            border-radius: 4px; cursor: pointer; margin-top: 10px; width: 100%;
            font-size: 14px; font-weight: bold;
        }}
        .confirm-btn:hover {{ background: #45a049; }}
        .confirm-btn:disabled {{ background: #ccc; cursor: not-allowed; }}
        .status {{ 
            margin-top: 10px; padding: 8px; background: #f0f0f0; 
            border-radius: 4px; font-size: 12px; 
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info-box">
        <div class="instructions">地図上をクリックして店舗の位置を選択してください<br>
        <small>ズーム・移動で詳細な位置を確認できます</small></div>
        <div class="coordinates" id="coordinates">座標: 未選択</div>
        <button class="confirm-btn" id="confirmBtn" disabled onclick="confirmSelection()">この位置で確定</button>
        <div class="status" id="status">マップをクリックして位置を選択...</div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js?v={unique_id}"></script>
    <script>
        console.log('地図選択画面が読み込まれました - {unique_id}');
        
        // 盛岡市中心部の座標
        var morioka = [39.7033, 141.1436];
        var map = L.map('map').setView(morioka, 17);
        
        // OpenStreetMapタイルレイヤーを追加
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
            maxNativeZoom: 18
        }}).addTo(map);
        
        var selectedMarker = null;
        var selectedCoordinates = null;
        
        // 地図が完全に読み込まれた後の処理
        map.whenReady(function() {{
            console.log('地図の読み込み完了');
            document.getElementById('status').textContent = '地図をクリックして位置を選択してください';
            
            // 地図クリックイベントを設定
            map.on('click', function(e) {{
                console.log('地図がクリックされました:', e.latlng);
                
                var lat = e.latlng.lat;
                var lng = e.latlng.lng;
                
                // 既存のマーカーを削除
                if (selectedMarker) {{
                    map.removeLayer(selectedMarker);
                }}
                
                // 新しいマーカーを追加（デフォルトアイコン使用）
                selectedMarker = L.marker([lat, lng]).addTo(map);
                
                // 座標を保存
                selectedCoordinates = {{lat: lat, lng: lng}};
                
                // 座標表示を更新
                document.getElementById('coordinates').textContent = 
                    `座標: ${{lat.toFixed(6)}}, ${{lng.toFixed(6)}}`;
                
                // ステータス更新
                document.getElementById('status').textContent = '位置が選択されました！';
                
                // 確定ボタンを有効化
                document.getElementById('confirmBtn').disabled = false;
                
                console.log('選択された座標:', selectedCoordinates);
            }});
        }});
        
        // 地図読み込みエラーハンドリング
        map.on('baselayererror', function(e) {{
            console.error('地図読み込みエラー:', e);
            document.getElementById('status').textContent = '地図の読み込みに失敗しました';
        }});
        
        function confirmSelection() {{
            if (selectedCoordinates) {{
                console.log('座標確定:', selectedCoordinates);
                
                var lat = selectedCoordinates.lat.toFixed(6);
                var lng = selectedCoordinates.lng.toFixed(6);
                
                // 座標をクリップボードにコピー
                var coordText = lat + ',' + lng;
                
                // クリップボードAPI使用
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(coordText).then(function() {{
                        alert(`座標がクリップボードにコピーされました!\\n\\n緯度: ${{lat}}\\n経度: ${{lng}}\\n\\n座標形式: ${{coordText}}\\n\\nPythonアプリケーションの緯度・経度欄に貼り付けてください。`);
                    }}).catch(function() {{
                        showCoordCopyDialog(lat, lng, coordText);
                    }});
                }} else {{
                    showCoordCopyDialog(lat, lng, coordText);
                }}
                
                // ステータス更新
                document.getElementById('status').textContent = 'クリップボードにコピーされました。Pythonアプリに貼り付けてください。';
            }} else {{
                alert('座標が選択されていません。\\n地図上をクリックして位置を選択してください。');
            }}
        }}
        
        function showCoordCopyDialog(lat, lng, coordText) {{
            // 手動コピー用のダイアログを表示
            var copyText = `座標が選択されました!\\n\\n緯度: ${{lat}}\\n経度: ${{lng}}\\n\\n以下の座標をコピーしてPythonアプリに貼り付けてください:\\n${{coordText}}\\n\\n(緯度,経度の形式)`;
            
            // テキストエリアを作成してコピー
            var textArea = document.createElement('textarea');
            textArea.value = coordText;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {{
                document.execCommand('copy');
                alert(copyText + '\\n\\n※クリップボードにコピーされました');
            }} catch (err) {{
                alert(copyText);
            }} finally {{
                document.body.removeChild(textArea);
            }}
        }}
        
        // 定期的に座標をlocalStorageに保存
        setInterval(function() {{
            if (selectedCoordinates) {{
                var coords = {{
                    lat: selectedCoordinates.lat,
                    lng: selectedCoordinates.lng,
                    timestamp: Date.now()
                }};
                localStorage.setItem('selectedCoordinates', JSON.stringify(coords));
            }}
        }}, 2000);
        
        // デバッグ用: クリックイベントテスト
        document.addEventListener('click', function(e) {{
            console.log('ページ内クリック:', e.target);
        }});
    </script>
</body>
</html>'''
            
            # ユニークなファイル名で一時ファイルを作成（キャッシュ回避）
            suffix = f'_map_{unique_id}.html'
            print(f"使用するsuffix: {suffix}")
            temp_fd, self.temp_html_path = tempfile.mkstemp(suffix=suffix)
            print(f"作成されたファイルパス: {self.temp_html_path}")
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                temp_file.write(html_content)
                
        except Exception as e:
            print(f"一時HTMLファイルの作成に失敗しました: {e}")
            raise
    
    def _start_coordinate_monitoring(self):
        """座標の監視を開始"""
        def monitor_coordinates():
            # 簡易的な座標取得（実装を簡素化）
            pass
        
        thread = threading.Thread(target=monitor_coordinates, daemon=True)
        thread.start()
    
    def _manual_input_confirm(self):
        """手動入力の確定"""
        try:
            lat = float(self.lat_var.get())
            lng = float(self.lng_var.get())
            
            # 盛岡市近辺の座標かチェック（簡易）
            if not (39.6 <= lat <= 39.8 and 141.0 <= lng <= 141.3):
                if not messagebox.askyesno("確認", "盛岡市から離れた座標が入力されています。続行しますか？"):
                    return
            
            self.selected_coordinates = (lat, lng)
            self.coord_var.set(f"座標: {lat:.6f}, {lng:.6f}")
            
        except ValueError:
            messagebox.showerror("エラー", "有効な数値を入力してください")
    
    def _paste_coordinates(self):
        """クリップボードから座標を貼り付け"""
        try:
            # クリップボードからテキストを取得
            clipboard_text = self.root.clipboard_get()
            
            # コンマ区切りの座標を分割
            if ',' in clipboard_text:
                parts = clipboard_text.strip().split(',')
                if len(parts) == 2:
                    lat_str = parts[0].strip()
                    lng_str = parts[1].strip()
                    
                    # 数値として解析
                    lat = float(lat_str)
                    lng = float(lng_str)
                    
                    # 入力欄に設定
                    self.lat_var.set(f"{lat:.6f}")
                    self.lng_var.set(f"{lng:.6f}")
                    
                    # 自動で確定
                    self._manual_input_confirm()
                    
                    messagebox.showinfo("成功", f"座標が貼り付けられました\\n緯度: {lat:.6f}\\n経度: {lng:.6f}")
                else:
                    messagebox.showerror("エラー", "クリップボードの形式が正しくありません。\\n'緯度,経度' の形式で貼り付けてください。")
            else:
                messagebox.showerror("エラー", "クリップボードに座標データが見つかりません。\\n'緯度,経度' の形式で貼り付けてください。")
                
        except tk.TclError:
            messagebox.showerror("エラー", "クリップボードにテキストデータがありません。")
        except ValueError as e:
            messagebox.showerror("エラー", f"座標の変換に失敗しました: {e}\\n有効な数値を確認してください。")
    
    def _confirm_selection(self):
        """選択を確定"""
        if self.selected_coordinates:
            if self.callback:
                self.callback(self.selected_coordinates[0], self.selected_coordinates[1])
            self.root.destroy()
        else:
            messagebox.showwarning("警告", "座標が選択されていません。\\n地図上でクリックするか、手動入力を使用してください。")
    
    def _cancel_selection(self):
        """選択をキャンセル"""
        self.selected_coordinates = None
        self.root.destroy()
    
    def _cleanup_temp_files(self):
        """一時ファイルを削除"""
        for path in [self.temp_html_path, self.temp_coords_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except Exception as e:
                    print(f"一時ファイルの削除に失敗しました: {e}")


def select_coordinates_from_map(callback=None):
    """
    地図から座標を選択する関数
    
    Args:
        callback: 座標選択完了時に呼ばれるコールバック関数 callback(lat, lng)
    
    Returns:
        tuple: (latitude, longitude) or None if cancelled
    """
    selector = MapSelector()
    return selector.show_map_selector(callback)


# テスト用のメイン関数
if __name__ == "__main__":
    def on_coordinates_selected(lat, lng):
        print(f"選択された座標: 緯度={lat}, 経度={lng}")
    
    print("地図から座標を選択してください...")
    coordinates = select_coordinates_from_map(on_coordinates_selected)
    
    if coordinates:
        print(f"最終的な座標: {coordinates}")
    else:
        print("座標の選択がキャンセルされました")