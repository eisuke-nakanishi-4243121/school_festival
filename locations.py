"""
学園祭会場の事前定義場所リスト

盛岡市大通を中心とした校内主要場所の座標定義
"""

PRESET_LOCATIONS = {
    
    # 大通り北側の等間隔店舗位置（5店舗）
    "大通り北側・店舗1": {
        "latitude": 39.7034,
        "longitude": 141.1434,
        "description": "大通り北側・西端"
    },
    "大通り北側・店舗3": {
        "latitude": 39.7034,
        "longitude": 141.13555,
        "description": "大通り北側・西寄り"
    },
    "大通り北側・店舗5": {
        "latitude": 39.7034,
        "longitude": 141.1437,
        "description": "大通り北側・中央"
    },
    "大通り北側・店舗7": {
        "latitude": 39.7034,
        "longitude": 141.13885,
        "description": "大通り北側・東寄り"
    },
    "大通り北側・店舗9": {
        "latitude": 39.7034,
        "longitude": 141.1440,
        "description": "大通り北側・東端"
    },
    # 大通り南側の等間隔店舗位置（5店舗）
    "大通り南側・店舗2": {
        "latitude": 39.7032,
        "longitude": 141.1434,
        "description": "大通り南側・西端"
    },
    "大通り南側・店舗4": {
        "latitude": 39.7032,
        "longitude": 141.13555,
        "description": "大通り南側・西寄り"
    },
    "大通り南側・店舗6": {
        "latitude": 39.7032,
        "longitude": 141.1437,
        "description": "大通り南側・中央"
    },
    "大通り南側・店舗8": {
        "latitude": 39.7032,
        "longitude": 141.13885,
        "description": "大通り南側・東寄り"
    },
    "大通り南側・店舗10": {
        "latitude": 39.7032,
        "longitude": 141.1440,
        "description": "大通り南側・東端"
    },
    "その他（手動入力）": {
        "latitude": None,
        "longitude": None,
        "description": "座標を手動で入力"
    }
}

def get_location_names():
    """場所名のリストを取得"""
    return list(PRESET_LOCATIONS.keys())

def get_location_data(location_name):
    """指定された場所名の座標データを取得"""
    return PRESET_LOCATIONS.get(location_name, None)

def add_custom_location(name, latitude, longitude, description=""):
    """カスタム場所を追加（将来の機能拡張用）"""
    PRESET_LOCATIONS[name] = {
        "latitude": latitude,
        "longitude": longitude,
        "description": description
    }

def is_manual_input_required(location_name):
    """手動入力が必要かどうかを判定"""
    location = get_location_data(location_name)
    return location and (location["latitude"] is None or location["longitude"] is None)

# テスト関数
if __name__ == "__main__":
    print("=== 学園祭会場 事前定義場所一覧 ===")
    for name, data in PRESET_LOCATIONS.items():
        if data["latitude"] is not None:
            print(f"{name}: ({data['latitude']}, {data['longitude']}) - {data['description']}")
        else:
            print(f"{name}: 手動入力 - {data['description']}")
    
    print(f"\n総場所数: {len(PRESET_LOCATIONS)} 箇所")
    print(f"手動入力オプション: {'あり' if is_manual_input_required('その他（手動入力）') else 'なし'}")