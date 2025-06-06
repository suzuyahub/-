# ascii_converter.py
from PIL import Image

def resize_image(image, new_width=100):
    width, height = image.size
    if width == 0 or height == 0: # ゼロ除算を避ける
        return image.resize((new_width, max(1, new_width // 2)))

    ratio = height / width / 1.65
    new_height = int(new_width * ratio)
    if new_height < 1:
        new_height = 1
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def get_ascii_chars(custom_chars):
    return custom_chars if custom_chars else "@%#*+=-:. "

def image_to_ascii(image_path, new_width=100, ascii_chars=None):
    ascii_chars_list = get_ascii_chars(ascii_chars)
    try:
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
    except Exception as e:
        raise RuntimeError(f"画像の読み込みに失敗しました: {e}")

    image_resized = resize_image(image, new_width)

    gray_image = grayify(image_resized)
    pixels = list(gray_image.getdata())
    color_pixels = list(image_resized.getdata())
    width, height = image_resized.size

    ascii_str = ""
    color_matrix = []

    for y in range(height):
        line = ""
        color_line = []
        for x in range(width):
            i = y * width + x
            pixel_brightness = pixels[i]
            original_color = color_pixels[i]
            
            char_index = pixel_brightness * len(ascii_chars_list) // 256
            if char_index >= len(ascii_chars_list):
                char_index = len(ascii_chars_list) - 1
            
            char = ascii_chars_list[char_index]
            line += char
            color_line.append(original_color)
        ascii_str += line + "\n"
        color_matrix.append(color_line)

    return ascii_str.strip(), color_matrix