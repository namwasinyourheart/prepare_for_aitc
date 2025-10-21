import os
import json
import base64
from utils import generate_image_with_thucchien_ai

def main():
    prompt = "A futuristic city with flying cars and tall skyscrapers at night, cyberpunk style, neon lights."
    model = "imagen-4"
    aspect_ratio = "16:9" # Hoặc "1:1", "3:2", "4:3", "21:9", "9:16"

    print(f"Đang yêu cầu sinh ảnh với prompt: \"{prompt}\"")
    print(f"Mô hình: {model}, Tỷ lệ khung hình: {aspect_ratio}")

    try:
        response = generate_image_with_thucchien_ai(
            prompt=prompt,
            model=model,
            n=1,
            aspect_ratio=aspect_ratio
        )

        if "data" in response and response["data"]:
            first_image_data = response["data"][0]
            if "b64_json" in first_image_data and first_image_data["b64_json"]:
                image_b64 = first_image_data["b64_json"]
                print(f"\nĐã nhận được dữ liệu hình ảnh Base64 (dài {len(image_b64)} ký tự).")
                
                # Ví dụ: Lưu hình ảnh vào file (có thể cần thư viện như Pillow để xử lý tốt hơn)
                # Lưu ý: Đây chỉ là ví dụ cơ bản. Trong thực tế, bạn có thể cần kiểm tra định dạng ảnh
                # và sử dụng thư viện chuyên dụng để giải mã và lưu.
                try:
                    image_bytes = base64.b64decode(image_b64)
                    output_filename = "generated_image.png"
                    with open(output_filename, "wb") as f:
                        f.write(image_bytes)
                    print(f"Hình ảnh đã được lưu vào: {output_filename}")
                except Exception as e:
                    print(f"Không thể giải mã hoặc lưu hình ảnh: {e}")

            elif "url" in first_image_data and first_image_data["url"]:
                image_url = first_image_data["url"]
                print(f"\nĐã nhận được URL hình ảnh: {image_url}")
                print("Bạn có thể tải hình ảnh từ URL này.")
            else:
                print("\nPhản hồi hình ảnh không chứa b64_json hoặc url hợp lệ.")
                print(json.dumps(response, indent=2, ensure_ascii=False))
        elif "error" in response:
            print(f"\nĐã xảy ra lỗi khi sinh ảnh: {response['error']}")
            if "details" in response:
                print(f"Chi tiết: {response['details']}")
        else:
            print("\nKhông nhận được phản hồi hợp lệ cho việc sinh ảnh.")
            print(json.dumps(response, indent=2, ensure_ascii=False))

    except ValueError as e:
        print(f"Lỗi cấu hình: {e}")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
