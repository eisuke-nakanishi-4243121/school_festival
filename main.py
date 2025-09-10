"""
学園祭店舗管理システム

運営者向け：Tkinterアプリで店舗登録・管理
来場者向け：Foliumで作成されるWebマップ表示

使用方法:
1. 運営者画面を開く場合: python main.py admin
2. 来場者向けマップを作成・表示する場合: python main.py visitor  
3. 引数なしの場合: 運営者画面がデフォルトで開きます
"""

import sys
import os

def show_usage():
    print(__doc__)
    print("使用例:")
    print("  python main.py admin    # 運営者画面を開く")
    print("  python main.py visitor  # 来場者向けマップを作成・表示")
    print("  python main.py          # 運営者画面を開く（デフォルト）")

def run_admin_app():
    """運営者向けTkinterアプリを起動"""
    try:
        import tkinter as tk
        from admin_app import AdminApp
        
        print("=== Festival Store Management System - Admin Interface ===")
        print("Starting store registration and management...")
        
        root = tk.Tk()
        app = AdminApp(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"Error: Required library not found - {e}")
        print("Please check if the virtual environment is activated")
        return False
    except Exception as e:
        print(f"Error occurred while starting admin interface: {e}")
        return False
    
    return True

def run_visitor_map():
    """来場者向けマップを作成・表示"""
    try:
        from visitor_map import open_visitor_map
        
        print("=== Festival Store Map - Visitor Interface ===")
        print("Creating visitor map...")
        
        open_visitor_map()
        print("Map opened in browser!")
        
    except ImportError as e:
        print(f"Error: Required library not found - {e}")
        print("Please install the library with the following command:")
        print("pip install folium")
        return False
    except Exception as e:
        print(f"Error occurred while creating map: {e}")
        return False
    
    return True

def main():
    # 引数をチェック
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "help" or mode == "--help" or mode == "-h":
            show_usage()
            return
        elif mode == "admin":
            run_admin_app()
        elif mode == "visitor":
            run_visitor_map()
        else:
            print(f"Unknown option: {mode}")
            show_usage()
    else:
        # デフォルトは運営者画面
        run_admin_app()

if __name__ == "__main__":
    main()