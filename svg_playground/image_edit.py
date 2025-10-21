import os, io, sys, traceback
from PIL import Image, ImageDraw, ImageOps

# === 0. Thiết lập thư mục làm việc ===
wk_dir = '/home/nampv1/projects/prepare_for_aitc/svg_playground'
os.makedirs(wk_dir, exist_ok=True)
os.chdir(wk_dir)
print("Working directory:", os.getcwd())

# === 1. Tạo SVG đầu vào và mask ===
input_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">
  <rect width="100%" height="100%" fill="#f0f0f2"/>
  <!-- simple person: head, body, shirt -->
  <circle cx="256" cy="120" r="60" fill="#ffd7b5" stroke="#000" stroke-width="2"/>
  <!-- body/torso -->
  <rect x="176" y="180" width="160" height="200" rx="20" ry="20" fill="#d1d5db" stroke="#000" stroke-width="2"/>
  <!-- shirt -->
  <path d="M176,260 Q256,220 336,260 L336,360 Q256,380 176,360 Z"
        fill="#1f77b4" stroke="#000" stroke-width="2"/>
  <!-- arms -->
  <path d="M176,200 Q140,260 176,300" stroke="#000" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="M336,200 Q372,260 336,300" stroke="#000" stroke-width="10" fill="none" stroke-linecap="round"/>
</svg>
'''

mask_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512">
  <rect width="100%" height="100%" fill="black"/>
  <!-- vùng cần chỉnh (áo) -->
  <path d="M176,260 Q256,220 336,260 L336,360 Q256,380 176,360 Z" fill="white"/>
</svg>
'''

# === 2. Hàm chuyển SVG -> PNG ===
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

# === 3. Sinh ảnh gốc và mask ===
input_png_bytes = svg_to_png_bytes(input_svg)
mask_png_bytes = svg_to_png_bytes(mask_svg)

with open("input.svg", "w") as f: f.write(input_svg)
with open("mask.svg", "w") as f: f.write(mask_svg)
with open("input.png", "wb") as f: f.write(input_png_bytes)
with open("mask.png", "wb") as f: f.write(mask_png_bytes)

input_img = Image.open(io.BytesIO(input_png_bytes)).convert("RGB")
mask_img = Image.open(io.BytesIO(mask_png_bytes)).convert("L")

# === 4. Chỉnh vùng áo (theo mask) ===
new_shirt_color = (220, 30, 70)  # đỏ hồng
color_layer = Image.new("RGB", input_img.size, new_shirt_color)
alpha_mask = mask_img.point(lambda p: 255 if p > 128 else 0)
edited = Image.composite(color_layer, input_img, alpha_mask)
edited.save("edited_preview.jpg", quality=95)

print("✅ Files saved in:", wk_dir)
print(" - input.svg / input.png / mask.svg / mask.png / edited_preview.jpg")
