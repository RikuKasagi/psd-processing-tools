import os
import re
from typing import Dict
from PIL import Image
import numpy as np
from psd_tools import PSDImage


def clean_layer_name(layer_name: str) -> str:
    """
    レイヤー名から制御文字を除去し、クリーンな文字列を返す。
    
    Parameters
    ----------
    layer_name : str
        元のレイヤー名
        
    Returns
    -------
    str
        制御文字が除去されたクリーンなレイヤー名
    """
    if not layer_name:
        return "Unnamed Layer"
    
    # 制御文字（ASCII 0-31, 127）を除去
    # ただし、タブ(\t)、改行(\n, \r)は空白に置換
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', layer_name)
    
    # タブと改行を空白に置換
    cleaned = re.sub(r'[\t\n\r]', ' ', cleaned)
    
    # 連続する空白を単一の空白に置換
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # 前後の空白を除去
    cleaned = cleaned.strip()
    
    # 空文字列になった場合のフォールバック
    if not cleaned:
        return "Unnamed Layer"
    
    return cleaned


def extract_layers_from_psd(psd_path: str, include_hidden: bool = True) -> Dict[str, Image.Image]:
    """
    PSDファイルからレイヤーを抽出し、レイヤー名をキーとした辞書型配列を返す。

    要件:
    - PSDファイルが存在することをチェック。
    - 各レイヤーをPIL.Imageとして抽出。
    - レイヤー名をキーとした辞書で返す。
    - エラーは例外として送出。

    Parameters
    ----------
    psd_path : str
        読み込むPSDファイルのパス。
    include_hidden : bool, optional
        非表示レイヤーも含めるかどうか（デフォルト: True）

    Returns
    -------
    Dict[str, Image.Image]
        レイヤー名をキーとし、画像データ(PIL.Image)を値とする辞書。
    """
    # 入力バリデーション
    if not os.path.exists(psd_path):
        raise FileNotFoundError(f"PSDファイルが見つかりません: {psd_path}")
    
    # 拡張子チェック
    if os.path.splitext(psd_path)[1].lower() != ".psd":
        raise ValueError(f"PSD以外のファイルが指定されました: {psd_path}")

    return _extract_with_psd_tools(psd_path, include_hidden)


def _extract_with_psd_tools(psd_path: str, include_hidden: bool = True) -> Dict[str, Image.Image]:
    """psd-toolsライブラリを使用してレイヤーを抽出"""
    try:
        psd = PSDImage.open(psd_path)
        layers_dict: Dict[str, Image.Image] = {}
        
        # PSDの全体サイズを取得
        canvas_width = psd.width
        canvas_height = psd.height
        print(f"📐 PSDキャンバスサイズ: {canvas_width}x{canvas_height}")
        
        def process_layer(layer, layer_path=""):
            """レイヤーを再帰的に処理（グループレイヤー対応）"""
            raw_layer_name = layer.name if layer.name else "Unnamed Layer"
            layer_name = clean_layer_name(raw_layer_name)  # 制御文字を除去
            full_name = f"{layer_path}/{layer_name}" if layer_path else layer_name
            
            # グループレイヤーの場合は子レイヤーを処理
            if hasattr(layer, '__iter__'):
                try:
                    for child in layer:
                        process_layer(child, full_name)
                except:
                    # イテレーション不可能な場合は通常レイヤーとして処理
                    pass
            
            # 通常のレイヤーの処理
            try:
                # レイヤーが可視かどうかをチェック
                is_visible = getattr(layer, 'visible', True)
                
                # 可視レイヤーか、非表示レイヤーも含める設定の場合に処理
                if is_visible or include_hidden:
                    # レイヤーを全キャンバスサイズで合成
                    try:
                        # レイヤーの可視性状態を表示
                        visibility_status = "表示中" if is_visible else "非表示"
                        
                        # 非表示レイヤーでも画像データを取得するため、topil()を優先的に使用
                        layer_img = None
                        
                        # 1. まずtopil()メソッドを試行（可視性を無視して画像データを取得）
                        if hasattr(layer, 'topil'):
                            try:
                                layer_img = layer.topil()
                            except Exception as e:
                                print(f"⚠️ レイヤー '{full_name}' でtopil()エラー: {e}")
                        
                        # 2. topil()が失敗した場合、composite()を試行（表示レイヤーのみ有効）
                        if layer_img is None and hasattr(layer, 'composite') and is_visible:
                            try:
                                layer_img = layer.composite()
                            except Exception as e:
                                print(f"⚠️ レイヤー '{full_name}' でcomposite()エラー: {e}")
                        
                        # 画像データが取得できた場合の処理
                        if layer_img and layer_img.size[0] > 0 and layer_img.size[1] > 0:
                            # キャンバス全体サイズの画像を作成
                            canvas_img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
                            
                            # レイヤーの位置を取得
                            bbox = getattr(layer, 'bbox', (0, 0, layer_img.size[0], layer_img.size[1]))
                            if isinstance(bbox, tuple) and len(bbox) >= 4:
                                left, top, right, bottom = bbox[:4]
                            else:
                                left, top = 0, 0
                            
                            # レイヤーをキャンバスの正しい位置に配置
                            if layer_img.mode != 'RGBA':
                                layer_img = layer_img.convert('RGBA')
                            
                            canvas_img.paste(layer_img, (left, top), layer_img)
                            
                            # RGBAモードのまま保存
                            if canvas_img.mode != 'RGBA':
                                canvas_img = canvas_img.convert('RGBA')
                            
                            layers_dict[full_name] = canvas_img
                            print(f"✅ レイヤー '{full_name}' を抽出しました ({visibility_status}) (キャンバスサイズ: {canvas_width}x{canvas_height}, レイヤー実サイズ: {layer_img.size[0]}x{layer_img.size[1]})")
                        else:
                            print(f"⚠️ レイヤー '{full_name}' ({visibility_status}) の画像データが取得できませんでした")
                                
                    except Exception as e:
                        print(f"⚠️ レイヤー '{full_name}' の画像取得でエラー: {e}")
                else:
                    print(f"⚠️ レイヤー '{full_name}' は非表示です（スキップ）")
                    
            except Exception as e:
                print(f"⚠️ レイヤー '{full_name}' の処理でエラー: {e}")
        
        # 全レイヤーを処理
        for layer in psd:
            process_layer(layer)
        
        print(f"✅ 合計 {len(layers_dict)} レイヤーを抽出しました")
        return layers_dict
        
    except Exception as e:
        raise ValueError(f"PSDファイルの読み込みに失敗しました (psd-tools): {psd_path} -> {e}")


if __name__ == "__main__":
    """
    テスト用:
    - 指定したPSDファイルからレイヤーを抽出
    - 各レイヤーをレイヤー名をファイル名としてPNGで保存
    """
    # ---- ここをあなたの環境に合わせて編集してください ----
    test_psd_path = r"./test_files/psd_files/test.psd"
    test_output_dir = r"./test_files/png_files"
    # -------------------------------------------------------
    
    try:
        # PSDからレイヤーを抽出
        layers = extract_layers_from_psd(test_psd_path, include_hidden=True)
        
        if not layers:
            print("❌ レイヤーが見つかりませんでした。")
        else:
            # 出力ディレクトリを作成
            if not os.path.exists(test_output_dir):
                os.makedirs(test_output_dir, exist_ok=True)
                print(f"📁 出力ディレクトリを作成しました: {test_output_dir}")
            
            # 各レイヤーをPNGとして保存
            for layer_name, image in layers.items():
                # ファイル名として使えない文字を置換（制御文字は既に除去済み）
                safe_filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in layer_name)
                safe_filename = safe_filename.strip()  # 前後の空白のみ除去
                if not safe_filename:
                    safe_filename = "unnamed_layer"
                
                output_path = os.path.join(test_output_dir, f"{safe_filename}.png")
                
                # 同名ファイルがあれば上書き保存
                image.save(output_path)
                print(f"💾 保存完了: {layer_name} -> {output_path}")
            
            print(f"✅ 全ての抽出が完了しました。出力先: {test_output_dir}")
    
    except Exception as e:
        print(f"❌ エラー: {e}")