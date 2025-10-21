import xml.etree.ElementTree as ET
import base64

# --- Đọc SVG gốc ---
tree = ET.parse("complex.svg")
root = tree.getroot()
root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

# --- Dữ liệu giả lập (thường lấy từ AI hoặc JSON) ---
data = {
    "title": "CHÀO MỪNG 80 NĂM QUỐC KHÁNH 2/9/2025",
    "subtitle": "Các hoạt động kỷ niệm trên khắp cả nước",
    "photos": [
        "images/1.jpg", 
        "images/2.jpg", 
        "images/3.jpg"
    ],
    "timeline": [
        "30/8 – Khai mạc Triển lãm thành tựu 80 năm",
        "1/9 – Diễu hành nghệ thuật tại Hà Nội",
        "2/9 – Lễ kỷ niệm cấp Quốc gia tại Quảng trường Ba Đình"
    ],
}

# --- Hàm chèn ảnh (base64 để độc lập) ---
def replace_rect_with_image(root, rect_id, image_path):
    for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
        if rect.attrib.get("id") == rect_id:
            img_data = base64.b64encode(open(image_path, "rb").read()).decode()
            image_elem = ET.Element("{http://www.w3.org/2000/svg}image", {
                "x": rect.attrib["x"],
                "y": rect.attrib["y"],
                "width": rect.attrib["width"],
                "height": rect.attrib["height"],
                "{http://www.w3.org/1999/xlink}href": f"data:image/png;base64,{img_data}"
            })
            root.remove(rect)
            root.append(image_elem)
            return True
    return False

# --- 1. Thay text tiêu đề & phụ đề ---
for elem in root.findall(".//{http://www.w3.org/2000/svg}text"):
    _id = elem.attrib.get("id", "")
    if _id == "title":
        elem.text = data["title"]
    elif _id == "subtitle":
        elem.text = data["subtitle"]

# --- 2. Thay timeline text ---
for i, text in enumerate(data["timeline"], start=1):
    for elem in root.findall(f".//{{http://www.w3.org/2000/svg}}text[@id='timeline{i}']"):
        elem.text = text

# --- 3. Thay ảnh ---
for i, img_path in enumerate(data["photos"], start=1):
    replace_rect_with_image(root, f"photo{i}", img_path)

# --- 4. (Tuỳ chọn) Vẽ biểu đồ động vào vùng chart ---
for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
    if rect.attrib.get("id") == "chart":
        # tạo nhóm <g> và thêm 3 cột mô phỏng thống kê
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

# --- Ghi kết quả ---
tree.write("complex_filled.svg", encoding="utf-8", xml_declaration=True)
print("✅ SVG phức tạp đã được chèn ảnh, text và biểu đồ!")
