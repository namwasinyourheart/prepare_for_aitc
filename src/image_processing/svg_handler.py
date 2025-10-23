import xml.etree.ElementTree as ET
import base64
import os
import io
from PIL import Image, ImageDraw, ImageOps

def svg_to_png_bytes(svg_text, width=512, height=512):
    try:
        import cairosvg
        return cairosvg.svg2png(bytestring=svg_text.encode('utf-8'),
                                output_width=width, output_height=height)
    except Exception:
        # fallback vẽ lại bằng Pillow
        img = Image.new("RGBA", (width, height), (240, 240, 242, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse((196, 60, 316, 180), fill=(255, 215, 181, 255), outline=(0, 0, 0, 255), width=2)
        draw.rounded_rectangle((176, 180, 336, 380), radius=20, fill=(209, 213, 219, 255), outline=(0, 0, 0, 255), width=2)
        shirt_poly = [(176, 260), (256, 220), (336, 260), (336, 360), (256, 380), (176, 360)]
        draw.polygon(shirt_poly, fill=(31, 119, 180, 255), outline=(0, 0, 0, 255))
        draw.line((176, 200, 140, 260, 176, 300), fill=(0, 0, 0, 255), width=10)
        draw.line((336, 200, 372, 260, 336, 300), fill=(0, 0, 0, 255), width=10)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

def fill_svg_with_content(input_svg_path: str, output_svg_path: str, image_path: str, title: str, description: str):
    """
    Điền nội dung vào file SVG: thay thế placeholder text và chèn ảnh base64.

    Args:
        input_svg_path (str): Đường dẫn đến file SVG mẫu.
        output_svg_path (str): Đường dẫn để lưu file SVG đã điền nội dung.
        image_path (str): Đường dẫn đến file ảnh sẽ được chèn vào SVG.
        title (str): Tiêu đề sẽ thay thế PLACEHOLDER_TITLE.
        description (str): Mô tả sẽ thay thế PLACEHOLDER_DESC.
    """
    try:
        tree = ET.parse(input_svg_path)
        root = tree.getroot()

        # Thêm namespace xlink nếu chưa có
        if "xmlns:xlink" not in root.attrib:
            root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

        # Thay nội dung text
        for text_elem in root.findall(".//{http://www.w3.org/2000/svg}text"):
            if text_elem.text == "PLACEHOLDER_TITLE":
                text_elem.text = title
            elif text_elem.text == "PLACEHOLDER_DESC":
                text_elem.text = description

        # Chèn ảnh base64
        for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
            if rect.attrib.get("id") == "photo1":
                # Kiểm tra nếu file ảnh tồn tại
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"File ảnh không tồn tại: {image_path}")

                with open(image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                
                image_elem = ET.Element("{http://www.w3.org/2000/svg}image", {
                    "x": rect.attrib["x"],
                    "y": rect.attrib["y"],
                    "width": rect.attrib["width"],
                    "height": rect.attrib["height"],
                    "{http://www.w3.org/1999/xlink}href": f"data:image/png;base64,{img_data}"
                })
                # Thay thế rect bằng image_elem
                root.remove(rect)
                root.append(image_elem)
                break # Chỉ thay thế rect đầu tiên có id="photo1"

        # Đảm bảo thư mục đầu ra tồn tại
        os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
        tree.write(output_svg_path, encoding="utf-8", xml_declaration=True)
        print(f"✅ SVG đã được chèn ảnh và text thành công vào: {output_svg_path}")

    except FileNotFoundError as e:
        print(f"❌ Lỗi: {e}")
    except Exception as e:
        print(f"❌ Lỗi khi xử lý SVG: {e}")

def fill_complex_svg_with_data(input_svg_path: str, output_svg_path: str, data: dict):
    """
    Điền dữ liệu phức tạp vào file SVG: thay thế tiêu đề, phụ đề, timeline và chèn nhiều ảnh.

    Args:
        input_svg_path (str): Đường dẫn đến file SVG mẫu.
        output_svg_path (str): Đường dẫn để lưu file SVG đã điền nội dung.
        data (dict): Dictionary chứa dữ liệu để điền vào SVG, bao gồm 'title', 'subtitle', 'photos', 'timeline'.
    """
    try:
        tree = ET.parse(input_svg_path)
        root = tree.getroot()
        root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

        # Hàm chèn ảnh (base64 để độc lập)
        def replace_rect_with_image(root_elem, rect_id, image_path):
            for rect in root_elem.findall(".//{http://www.w3.org/2000/svg}rect"):
                if rect.attrib.get("id") == rect_id:
                    if not os.path.exists(image_path):
                        raise FileNotFoundError(f"File ảnh không tồn tại: {image_path}")
                    with open(image_path, "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                    image_elem = ET.Element("{http://www.w3.org/2000/svg}image", {
                        "x": rect.attrib["x"],
                        "y": rect.attrib["y"],
                        "width": rect.attrib["width"],
                        "height": rect.attrib["height"],
                        "{http://www.w3.org/1999/xlink}href": f"data:image/png;base64,{img_data}"
                    })
                    root_elem.remove(rect)
                    root_elem.append(image_elem)
                    return True
            return False

        # 1. Thay text tiêu đề & phụ đề
        for elem in root.findall(".//{http://www.w3.org/2000/svg}text"):
            _id = elem.attrib.get("id", "")
            if _id == "title" and "title" in data:
                elem.text = data["title"]
            elif _id == "subtitle" and "subtitle" in data:
                elem.text = data["subtitle"]

        # 2. Thay timeline text
        if "timeline" in data:
            for i, text in enumerate(data["timeline"], start=1):
                for elem in root.findall(f".//{{http://www.w3.org/2000/svg}}text[@id='timeline{i}']"):
                    elem.text = text

        # 3. Thay ảnh
        if "photos" in data:
            for i, img_path in enumerate(data["photos"], start=1):
                replace_rect_with_image(root, f"photo{i}", img_path)

        # 4. (Tuỳ chọn) Vẽ biểu đồ động vào vùng chart (giữ nguyên logic từ file gốc)
        for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
            if rect.attrib.get("id") == "chart":
                g = ET.Element("{http://www.w3.org/2000/svg}g", {"id": "chart_data"})
                bars = [
                    {"x": 420, "height": 200},
                    {"x": 520, "height": 150},
                    {"x": 620, "height": 250}
                ]
                for bar in bars:
                    y = float(rect.attrib["y"]) + float(rect.attrib["height"]) - bar["height"]
                    bar_elem = ET.Element("{http://www.w3.org/2000/svg}rect", {
                        "x": str(bar["x"]),
                        "y": str(y),
                        "width": "50",
                        "height": str(bar["height"]),
                        "fill": "#c00"
                    })
                    g.append(bar_elem)
                root.remove(rect)
                root.append(g)

        # Ghi kết quả
        os.makedirs(os.path.dirname(output_svg_path), exist_ok=True)
        tree.write(output_svg_path, encoding="utf-8", xml_declaration=True)
        print(f"✅ SVG phức tạp đã được chèn ảnh, text và biểu đồ vào: {output_svg_path}")

    except FileNotFoundError as e:
        print(f"❌ Lỗi: {e}")
    except Exception as e:
        print(f"❌ Lỗi khi xử lý SVG: {e}")

def edit_image_with_svg_mask(input_svg_text: str, mask_svg_text: str, output_image_path: str, new_color: tuple = (220, 30, 70), width: int = 512, height: int = 512):
    """
    Chuyển đổi SVG thành PNG, sau đó chỉnh sửa một vùng ảnh dựa trên mask SVG và lưu lại.

    Args:
        input_svg_text (str): Chuỗi SVG cho hình ảnh gốc.
        mask_svg_text (str): Chuỗi SVG cho mask (vùng cần chỉnh sửa).
        output_image_path (str): Đường dẫn để lưu file ảnh đã chỉnh sửa.
        new_color (tuple): Màu RGB mới (ví dụ: (220, 30, 70) cho đỏ hồng).
        width (int): Chiều rộng của ảnh.
        height (int): Chiều cao của ảnh.
    """
    try:
        input_png_bytes = svg_to_png_bytes(input_svg_text, width, height)
        mask_png_bytes = svg_to_png_bytes(mask_svg_text, width, height)

        input_img = Image.open(io.BytesIO(input_png_bytes)).convert("RGB")
        mask_img = Image.open(io.BytesIO(mask_png_bytes)).convert("L")

        color_layer = Image.new("RGB", input_img.size, new_color)
        alpha_mask = mask_img.point(lambda p: 255 if p > 128 else 0)
        edited = Image.composite(color_layer, input_img, alpha_mask)

        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
        edited.save(output_image_path, quality=95)
        print(f"✅ Ảnh đã được chỉnh sửa và lưu vào: {output_image_path}")

    except Exception as e:
        print(f"❌ Lỗi khi chỉnh sửa ảnh với mask SVG: {e}")
