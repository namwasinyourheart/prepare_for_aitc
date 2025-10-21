import xml.etree.ElementTree as ET
import base64

tree = ET.parse("sample.svg")
root = tree.getroot()

# Thêm namespace xlink nếu chưa có
root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

# Thay nội dung text
for text_elem in root.findall(".//{http://www.w3.org/2000/svg}text"):
    if text_elem.text == "PLACEHOLDER_TITLE":
        text_elem.text = "KỶ NIỆM 80 NĂM QUỐC KHÁNH 2/9/2025"
    elif text_elem.text == "PLACEHOLDER_DESC":
        text_elem.text = "Hoạt động chào mừng trên toàn quốc"

# Chèn ảnh base64
for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
    if rect.attrib.get("id") == "photo1":
        img_data = base64.b64encode(open("images.png", "rb").read()).decode()
        image_elem = ET.Element("{http://www.w3.org/2000/svg}image", {
            "x": rect.attrib["x"],
            "y": rect.attrib["y"],
            "width": rect.attrib["width"],
            "height": rect.attrib["height"],
            "{http://www.w3.org/1999/xlink}href": f"data:image/png;base64,{img_data}"
        })
        root.remove(rect)
        root.append(image_elem)

tree.write("sample_filled.svg", encoding="utf-8", xml_declaration=True)
print("✅ SVG đã được chèn ảnh và text thành công!")
