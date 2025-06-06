# ascii_renderer.py
from PIL import Image, ImageDraw, ImageFont
import os

def get_default_font_path():
    """システムに応じたデフォルトの等幅フォントパスを返す"""
    if os.name == 'nt':
        possible_paths = [
            "C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/cour.ttf",
        ]
    elif os.name == 'posix':
        possible_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/Library/Fonts/Andale Mono.ttf",
            "/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
        ]
    else:
        possible_paths = []
    for path in possible_paths:
        if os.path.exists(path): return path
    try:
        ImageFont.truetype("monospace", 10); return "monospace"
    except IOError: pass
    try:
        ImageFont.truetype("Consolas", 10); return "Consolas"
    except IOError: pass
    return None

def ascii_to_image(ascii_text, color_data, font_size=10, bg_color=(0, 0, 0), font_path=None,
                   aspect_ratio_option="AAデフォルト補正", original_image_size=None): # aspect_ratio_option 復活
    if font_path is None: font_path = get_default_font_path()
    
    font = None
    if not font_path:
        try: font = ImageFont.load_default()
        except Exception: raise FileNotFoundError("適切な等幅フォントが見つかりませんでした。")
        print("警告: 等幅フォントが見つからず、Pillowのデフォルトフォントを使用します。")
    else:
        try: font = ImageFont.truetype(font_path, font_size)
        except IOError:
            fp_fallback = get_default_font_path()
            if fp_fallback and fp_fallback != font_path:
                print(f"警告: フォント '{font_path}' が見つからず。'{fp_fallback}' を試みます。")
                try: font = ImageFont.truetype(fp_fallback, font_size)
                except IOError: raise FileNotFoundError(f"フォント '{font_path}' も代替フォントも失敗。")
            else: raise FileNotFoundError(f"フォント '{font_path}' 読み込み失敗。")
        except Exception as e: raise RuntimeError(f"フォント '{font_path}' 読み込み中エラー: {e}")
    if font is None: raise RuntimeError("フォントオブジェクト初期化失敗。")

    lines = ascii_text.split('\n')
    if not lines: return Image.new("RGB", (1,1), bg_color)
    num_chars_wide = max(len(line) for line in lines) if any(lines) else 0
    num_lines_high = len(lines)
    if num_chars_wide == 0 or num_lines_high == 0: return Image.new("RGB", (1,1), bg_color)

    char_pixel_width, char_pixel_height_font_defined = 0, 0
    if hasattr(font, 'getbbox'):
        try:
            bbox = font.getbbox("A"); char_pixel_width, char_pixel_height_font_defined = bbox[2]-bbox[0], bbox[3]-bbox[1]
        except Exception: pass
    if char_pixel_width == 0 or char_pixel_height_font_defined == 0:
        dummy_img = Image.new("RGB",(1,1)); draw_obj = ImageDraw.Draw(dummy_img)
        try:
            bbox = draw_obj.textbbox((0,0),"A",font=font); char_pixel_width, char_pixel_height_font_defined = bbox[2]-bbox[0], bbox[3]-bbox[1]
        except AttributeError:
            try: size=font.getsize("A"); char_pixel_width, char_pixel_height_font_defined = size[0],size[1]
            except AttributeError: pass
        except Exception: pass
    if char_pixel_width <= 0: char_pixel_width = max(1, int(font_size*0.6)) # 0.5から少し変更
    if char_pixel_height_font_defined <= 0: char_pixel_height_font_defined = max(1, font_size)
    
    final_char_pixel_height = char_pixel_height_font_defined

    # アスペクト比オプションに応じた処理
    if aspect_ratio_option == "元のアスペクト比" and original_image_size:
        original_w, original_h = original_image_size
        if original_w > 0 and original_h > 0 and num_lines_high > 0 and char_pixel_width > 0:
            target_img_px_w = char_pixel_width * num_chars_wide
            target_img_px_h = target_img_px_w * (original_h / float(original_w))
            final_char_pixel_height = target_img_px_h / num_lines_high
        else: 
            # 元のアスペクト比が選択されたが、サイズ情報が無効な場合はフォールバック
            print("警告: 「元のアスペクト比」処理のため元画像サイズ情報が無効です。AAデフォルト補正を適用します。")
            final_char_pixel_height = int(char_pixel_height_font_defined * 1.8) 
    elif aspect_ratio_option == "AAデフォルト補正":
        final_char_pixel_height = int(char_pixel_height_font_defined * 1.8) # 経験的な補正値
    else: # 未知のオプションが渡された場合 (GUIからは通常発生しない)
        print(f"警告: 未知のアスペクト比オプション '{aspect_ratio_option}'。AAデフォルト補正を適用。")
        final_char_pixel_height = int(char_pixel_height_font_defined * 1.8)
    
    final_char_pixel_height = max(1, int(final_char_pixel_height))

    img_width = char_pixel_width * num_chars_wide
    img_height = final_char_pixel_height * num_lines_high
    
    if img_width <=0 or img_height <=0:
        if isinstance(font, ImageFont.ImageFont): # Pillowのデフォルトフォントの場合
            est_char_w, est_char_h = 6, 10
            img_width = max(1, est_char_w * num_chars_wide)
            img_height = max(1, est_char_h * num_lines_high * int(1.8 if aspect_ratio_option == "AAデフォルト補正" else 1.0))
        else:
            img_width, img_height = max(100, img_width if img_width > 0 else 100), max(100, img_height if img_height > 0 else 100)
        print(f"警告: 画像サイズが無効または小さすぎるため調整: {img_width}x{img_height}")

    MAX_DIM = 16384 
    if img_width > MAX_DIM or img_height > MAX_DIM:
        raise ValueError(f"生成画像サイズが大きすぎ ({img_width}x{img_height})。幅を小さくして下さい。")

    image = Image.new("RGB", (int(img_width), int(img_height)), bg_color)
    draw = ImageDraw.Draw(image)

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            char_color = (255,255,255)
            if y < len(color_data) and x < len(color_data[y]): char_color = color_data[y][x]
            draw.text((x * char_pixel_width, y * final_char_pixel_height), char, font=font, fill=char_color)
    return image