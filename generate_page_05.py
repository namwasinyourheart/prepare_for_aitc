import os
import json
import base64
from utils import generate_image_with_thucchien_ai

def generate_frame(prompt: str, output_filename: str, aspect_ratio: str = "16:9"):
    model = "imagen-4"

    print(f"Đang yêu cầu sinh ảnh cho khung hình: {output_filename} với prompt: \"{prompt}\"")
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
                    print(f"✅ Hình ảnh {output_filename} đã được lưu thành công.")
                    
                except Exception as e:
                    print(f"❌ Không thể giải mã hoặc lưu hình ảnh {output_filename}: {e}")

            elif "url" in first_image_data and first_image_data["url"]:
                image_url = first_image_data["url"]
                print(f"✅ Đã nhận được URL hình ảnh cho {output_filename}: {image_url}")
                print(f"Bạn có thể tải hình ảnh từ URL này.")
            else:
                print(f"❌ Phản hồi hình ảnh cho {output_filename} không chứa b64_json hoặc url hợp lệ.")
                print(json.dumps(response, indent=2, ensure_ascii=False))
                
        elif "error" in response:
            print(f"❌ Đã xảy ra lỗi khi sinh ảnh cho {output_filename}: {response['error']}")
            if "details" in response:
                print(f"Chi tiết: {response['details']}")
        else:
            print(f"❌ Không nhận được phản hồi hợp lệ cho việc sinh ảnh {output_filename}.")
            print(json.dumps(response, indent=2, ensure_ascii=False))

    except ValueError as e:
        print(f"❌ Lỗi cấu hình: {e}")
        print("💡 Hãy đảm bảo bạn đã thiết lập biến môi trường THUCCHIEN_AI_API_KEY")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")

def main():
    # Khung hình 1: Các khối diễu binh của các lực lượng vũ trang khác
    prompt_frame1 = """A grand military parade at Ba Dinh Square in Hanoi, featuring various branches of the Vietnamese armed forces: Navy sailors, Air Force personnel, Border Guards, and Coast Guard units, marching in perfect synchronization. Emphasize their determination to protect national sovereignty. Bright, clear day."""
    output_filename_frame1 = "page_05_frame_01.png"
    generate_frame(prompt_frame1, output_filename_frame1)

    # Khung hình 2: Các khối diễu hành của đoàn thể và nhân dân
    prompt_frame2 = """A vibrant civilian parade at Ba Dinh Square, with various social organizations and people from all walks of life: workers, farmers, youth, women, intellectuals, marching together with flags, flowers, and banners. Show unity and collective effort in national development. Joyful and patriotic atmosphere."""
    output_filename_frame2 = "page_05_frame_02.png"
    generate_frame(prompt_frame2, output_filename_frame2)

    # Khung hình 3: Biên đội máy bay trực thăng mang cờ Đảng, cờ Tổ quốc
    prompt_frame3 = """A formation of military helicopters flying over Ba Dinh Square, carrying large Party and National flags. The helicopters are soaring gracefully against a clear blue sky, creating a majestic and patriotic spectacle. Professional aerial photography."""
    output_filename_frame3 = "page_05_frame_03.png"
    generate_frame(prompt_frame3, output_filename_frame3)

if __name__ == "__main__":
    main()
