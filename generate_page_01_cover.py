import os
import json
import base64
from utils import generate_image_with_thucchien_ai

def main():
    prompt = """Vietnamese national flag, red with a yellow star, flying proudly above Ba Dinh Square in Hanoi during a grand national day celebration. The flag is waving majestically against a clear blue sky. Below, a glimpse of Ba Dinh Square, conveying a sense of solemnity and festive atmosphere. Professional photography style, high quality, vibrant colors, majestic, patriotic."""
    
    model = "imagen-4"
    aspect_ratio = "16:9"
    output_filename = "page_01_cover.png"

    print(f"Đang yêu cầu sinh ảnh cho Trang Bìa với prompt: \"{prompt}\"")
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
                print(f"Đã nhận được dữ liệu hình ảnh Base64 (dài {len(image_b64)} ký tự).")
                
                try:
                    image_bytes = base64.b64decode(image_b64)
                    with open(output_filename, "wb") as f:
                        f.write(image_bytes)
                    print(f"✅ Hình ảnh Trang Bìa đã được lưu vào: {output_filename}")
                    
                except Exception as e:
                    print(f"❌ Không thể giải mã hoặc lưu hình ảnh: {e}")

            elif "url" in first_image_data and first_image_data["url"]:
                image_url = first_image_data["url"]
                print(f"✅ Đã nhận được URL hình ảnh Trang Bìa: {image_url}")
                print(f"Bạn có thể tải hình ảnh từ URL này.")
            else:
                print("❌ Phản hồi hình ảnh Trang Bìa không chứa b64_json hoặc url hợp lệ.")
                print(json.dumps(response, indent=2, ensure_ascii=False))
                
        elif "error" in response:
            print(f"❌ Đã xảy ra lỗi khi sinh ảnh Trang Bìa: {response['error']}")
            if "details" in response:
                print(f"Chi tiết: {response['details']}")
        else:
            print("❌ Không nhận được phản hồi hợp lệ cho việc sinh ảnh Trang Bìa.")
            print(json.dumps(response, indent=2, ensure_ascii=False))

    except ValueError as e:
        print(f"❌ Lỗi cấu hình: {e}")
        print("💡 Hãy đảm bảo bạn đã thiết lập biến môi trường THUCCHIEN_AI_API_KEY")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
