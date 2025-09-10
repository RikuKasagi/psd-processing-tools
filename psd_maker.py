import os
from typing import List
from PIL import Image
import numpy as np
from collections import OrderedDict
from pytoshop import PsdFile, enums
from pytoshop.layers import LayerRecord, LayerInfo, ChannelImageData, LayerAndMaskInfo


def _create_layer(img: Image.Image, name: str) -> LayerRecord:
    """
    PIL.Image を受け取り、pytoshop の LayerRecord を返す。
    """
    img = img.convert("RGBA")
    width, height = img.size
    data = np.array(img)  # (H, W, 4)

    channels = OrderedDict({
        enums.ChannelId.red: ChannelImageData(image=data[:, :, 0]),
        enums.ChannelId.green: ChannelImageData(image=data[:, :, 1]),
        enums.ChannelId.blue: ChannelImageData(image=data[:, :, 2]),
        enums.ChannelId.transparency: ChannelImageData(image=data[:, :, 3]),
    })

    return LayerRecord(
        top=0, left=0, bottom=height, right=width,
        name=name,
        channels=channels,
        opacity=255,
        blend_mode=enums.BlendMode.normal,
        visible=True,
    )


def save_images_as_psd(
    image_paths: List[str],
    layer_names: List[str],
    save_path: str
) -> None:
    """
    画像配列（PNG）を受け取り、画像順に下→上のレイヤとしてPSDを書き出す。

    要件:
    - 画像は PNG 固定。拡張子/実体ともにPNGであることをチェック。
    - すべての画像の縦横が一致していることをチェック。
    - レイヤ名配列が不足している場合は、レイヤ番号で補完（最下層=1）。
      ※画像の並び: image_paths[0] が「一番下」のレイヤ
    - レイヤ名配列が画像数より多い場合は先頭から必要数のみ使用（警告を出力）。
    - エラーは例外(ValueError / FileNotFoundError など)として送出。
    - 戻り値なし（成功時は関数内で PSD を保存）。

    Parameters
    ----------
    image_paths : List[str]
        レイヤとして積むPNG画像のパス配列。先頭が最下層。
    layer_names : List[str]
        レイヤ名の配列。不足分は「'1','2',...（最下層=1）」で補完。
    save_path : str
        出力PSDファイルのフルパス。
    """
    # 入力バリデーション
    if not image_paths:
        raise ValueError("画像配列が空です。少なくとも1枚のPNGを指定してください。")

    # 画像存在 & PNGチェック
    pil_images: List[Image.Image] = []
    for p in image_paths:
        if not os.path.exists(p):
            raise FileNotFoundError(f"画像が見つかりません: {p}")
        # 拡張子チェック（.png固定）
        if os.path.splitext(p)[1].lower() != ".png":
            raise ValueError(f"PNG以外が含まれています（PNG固定の要件）: {p}")
        try:
            img = Image.open(p)
            # 実ファイルがPNGかどうかの追加チェック（形式判定）
            if getattr(img, "format", None) != "PNG":
                raise ValueError(f"実ファイル形式がPNGではありません: {p} (format={img.format})")
            pil_images.append(img.convert("RGBA"))
        except Exception as e:
            raise ValueError(f"画像の読み込みに失敗しました: {p} -> {e}")

    # サイズ一致チェック
    base_w, base_h = pil_images[0].size
    for p, im in zip(image_paths, pil_images):
        if im.size != (base_w, base_h):
            raise ValueError(
                "画像サイズが一致していません。\n"
                f"基準サイズ: {(base_w, base_h)}, 問題画像: {p}, そのサイズ: {im.size}"
            )

    # レイヤ名の整備
    n = len(image_paths)
    if len(layer_names) < n:
        # 画像に対してレイヤ名が少ない場合、（最下層=1）で欠番を補完
        # 既存の layer_names を尊重しつつ、足りない分を番号で埋める
        supplemented = layer_names[:]
        for idx in range(len(layer_names), n):
            # idx は 0-based。最下層=1 なので、画像順の番号は idx+1
            supplemented.append(str(idx + 1))
        layer_names = supplemented
    elif len(layer_names) > n:
        # 多い場合は使用しない分がある旨を警告（例外ではない）
        print(f"⚠️ レイヤ名が画像数より多いため、先頭 {n} 件のみ使用します（余剰 {len(layer_names)-n} 件は無視）。")
        layer_names = layer_names[:n]

    # レイヤ生成（画像順 = 下→上。pytoshop はこの配列順で積層されます）
    layers: List[LayerRecord] = []
    for name, img in zip(layer_names, pil_images):
        layers.append(_create_layer(img, name))

    # PSD 構築と保存
    width, height = base_w, base_h
    layer_info = LayerInfo(layer_records=layers, use_alpha_channel=True)
    layer_and_mask_info = LayerAndMaskInfo(layer_info)

    psd = PsdFile(
        width=width,
        height=height,
        num_channels=4,
        color_mode=enums.ColorMode.rgb,
        layer_and_mask_info=layer_and_mask_info,
        depth=enums.ColorDepth.depth8,
    )

    # 出力先ディレクトリ作成
    out_dir = os.path.dirname(save_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(save_path, "wb") as f:
        psd.write(f)

    print(f"✅ PSD 保存完了: {save_path}")


if __name__ == "__main__":
    """
    Rikuによる簡易テスト:
    - 画像は先頭が最下層、後続が上に重なる。
    - レイヤ名は不足分を番号で補完（最下層=1）。
    """
    # ---- ここをあなたの環境に合わせて編集してください ----
    test_image_paths = [
        r"./test_files/png_files/original_.png",   # 最下層
        r"./test_files/png_files/mask_.png",
        r"./test_files/png_files/ペイントレイヤー_1_.png",
    ]
    test_layer_names = [
        "Mask",                 # bottom.png に対応
        "Original",           # top.png に対応
    ]
    test_save_path = r"./test_files/psd_files/test.psd"
    # -------------------------------------------------------

    try:
        save_images_as_psd(
            image_paths=test_image_paths,
            layer_names=test_layer_names,
            save_path=test_save_path
        )
    except Exception as e:
        # 仕様に従い、エラーは出力（戻り値なし）
        print(f"❌ エラー: {e}")