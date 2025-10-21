import os
import json
import base64
from utils import generate_image_with_thucchien_ai

def main():
    # Prompt mô tả lá cờ Việt Nam tung bay trên đỉnh Everest
    prompt = """Vietnamese national flag flying proudly on the summit of Mount Everest, 
    red flag with yellow star, waving in strong mountain winds, 
    snow-capped peaks in background, dramatic mountain landscape, 
    clear blue sky, professional photography style, high quality, 
    patriotic and majestic atmosphere"""
    
    model = "imagen-4"
    aspect_ratio = "16:9"  # Tỷ lệ khung hình rộng để thể hiện cảnh núi non

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
                
                # Lưu hình ảnh vào file
                try:
                    image_bytes = base64.b64decode(image_b64)
                    output_filename = "vietnam_flag_everest.png"
                    with open(output_filename, "wb") as f:
                        f.write(image_bytes)
                    print(f"✅ Hình ảnh đã được lưu vào: {output_filename}")
                    print("🎌 Lá cờ tổ quốc Việt Nam tung bay trên đỉnh Everest đã được tạo thành công!")
                    
                except Exception as e:
                    print(f"❌ Không thể giải mã hoặc lưu hình ảnh: {e}")

            elif "url" in first_image_data and first_image_data["url"]:
                image_url = first_image_data["url"]
                print(f"\n✅ Đã nhận được URL hình ảnh: {image_url}")
                print("🎌 Bạn có thể tải hình ảnh từ URL này.")
            else:
                print("\n❌ Phản hồi hình ảnh không chứa b64_json hoặc url hợp lệ.")
                print(json.dumps(response, indent=2, ensure_ascii=False))
                
        elif "error" in response:
            print(f"\n❌ Đã xảy ra lỗi khi sinh ảnh: {response['error']}")
            if "details" in response:
                print(f"Chi tiết: {response['details']}")
        else:
            print("\n❌ Không nhận được phản hồi hợp lệ cho việc sinh ảnh.")
            print(json.dumps(response, indent=2, ensure_ascii=False))

    except ValueError as e:
        print(f"❌ Lỗi cấu hình: {e}")
        print("💡 Hãy đảm bảo bạn đã thiết lập biến môi trường THUCCHIEN_AI_API_KEY")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()
