import os
import base64
import json
from src.api_services.btc_api_client import sinh_hinh_anh


def generate_and_save_image(
    prompt: str,
    output_filename: str,
    model: str = "imagen-4",
    aspect_ratio: str = "16:9",
    n: int = 1
) -> dict:
    """
    Gửi yêu cầu đến ThucChien.AI để sinh hình ảnh dựa trên prompt và lưu vào file.

    Args:
        prompt (str): Mô tả văn bản để AI dựa vào đó sinh hình ảnh.
        output_filename (str): Tên file để lưu hình ảnh (ví dụ: "my_image.png").
        model (str): Tên của mô hình AI muốn sử dụng (mặc định là "imagen-4").
        aspect_ratio (str): Tỷ lệ khung hình của hình ảnh (ví dụ: "1:1", "16:9").
        n (int): Số lượng hình ảnh muốn sinh (mặc định là 1).

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI chứa dữ liệu hình ảnh hoặc thông báo lỗi.
    """
    print(f"Đang yêu cầu sinh ảnh với prompt: \"{prompt}\"")
    print(f"Mô hình: {model}, Tỷ lệ khung hình: {aspect_ratio}")

    try:
        response = sinh_hinh_anh(
            prompt=prompt,
            model=model,
            n=n,
            aspect_ratio=aspect_ratio
        )

        if "data" in response and response["data"]:
            first_image_data = response["data"][0]
            if "b64_json" in first_image_data and first_image_data["b64_json"]:
                image_b64 = first_image_data["b64_json"]
                print(f"\nĐã nhận được dữ liệu hình ảnh Base64 (dài {len(image_b64)} ký tự).")
                
                try:
                    image_bytes = base64.b64decode(image_b64)
                    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
                    with open(output_filename, "wb") as f:
                        f.write(image_bytes)
                    print(f"Hình ảnh đã được lưu vào: {output_filename}")
                    return {"success": True, "filepath": output_filename}
                except Exception as e:
                    print(f"Không thể giải mã hoặc lưu hình ảnh: {e}")
                    return {"error": f"Không thể giải mã hoặc lưu hình ảnh: {e}"}

            elif "url" in first_image_data and first_image_data["url"]:
                image_url = first_image_data["url"]
                print(f"\nĐã nhận được URL hình ảnh: {image_url}")
                print("Bạn có thể tải hình ảnh từ URL này.")
                return {"success": True, "url": image_url}
            else:
                print("\nPhản hồi hình ảnh không chứa b64_json hoặc url hợp lệ.")
                print(json.dumps(response, indent=2, ensure_ascii=False))
                return {"error": "Phản hồi hình ảnh không chứa b64_json hoặc url hợp lệ.", "details": response}
        elif "error" in response:
            print(f"\nĐã xảy ra lỗi khi sinh ảnh: {response['error']}")
            if "details" in response:
                print(f"Chi tiết: {response['details']}")
            return {"error": response['error'], "details": response.get("details")}
        else:
            print("\nKhông nhận được phản hồi hợp lệ cho việc sinh ảnh.")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            return {"error": "Không nhận được phản hồi hợp lệ cho việc sinh ảnh.", "details": response}

    except ValueError as e:
        print(f"Lỗi cấu hình: {e}")
        return {"error": f"Lỗi cấu hình: {e}"}
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
        return {"error": f"Lỗi không mong muốn: {e}"}

def generate_page_cover(output_filename: str):
    prompt = """Vietnamese national flag, red with a yellow star, flying proudly above Ba Dinh Square in Hanoi during a grand national day celebration. The flag is waving majestically against a clear blue sky. Below, a glimpse of Ba Dinh Square, conveying a sense of solemnity and festive atmosphere. Professional photography style, high quality, vibrant colors, majestic, patriotic."""
    model = "imagen-4"
    aspect_ratio = "16:9"
    return generate_and_save_image(
        prompt=prompt,
        output_filename=output_filename,
        model=model,
        aspect_ratio=aspect_ratio
    )

def generate_page_two_frames(output_filename_frame1: str, output_filename_frame2: str):
    prompt_frame1 = """Historical photo of Ho Chi Minh reading the Declaration of Independence at Ba Dinh Square in Hanoi, September 2, 1945. Black and white or sepia tone, capturing the solemn and historic moment. Crowds of people listening attentively."""
    prompt_frame2 = """A montage or timeline of images representing Vietnam's 80 years of development: soldiers marching during wartime, workers building infrastructure, farmers in rice fields, modern cityscapes with skyscrapers. Bright and evolving colors, showing progress and resilience."""

    generate_and_save_image(prompt_frame1, output_filename_frame1)
    generate_and_save_image(prompt_frame2, output_filename_frame2)

def generate_page_three_frames(output_filename_frame1: str, output_filename_frame2: str, output_filename_frame3: str):
    prompt_frame1 = """A wide shot of Ba Dinh Square in Hanoi, crowded with people and various military and civilian forces gathering for a national day celebration. The atmosphere is solemn and expectant. Flags and banners are visible. Bright daylight."""
    prompt_frame2 = """A traditional torch relay ceremony in Vietnam, with a torch being carried by a person in official attire. The torch represents the revolutionary fire and the will for independence. Focus on the torch and the solemnity of the moment."""
    prompt_frame3 = """A solemn flag-raising ceremony at Ba Dinh Square. Leaders of the Party and State, along with the entire populace, stand at attention, saluting the Vietnamese national flag as it is raised. Respectful and patriotic atmosphere. Clear blue sky."""

    generate_and_save_image(prompt_frame1, output_filename_frame1)
    generate_and_save_image(prompt_frame2, output_filename_frame2)
    generate_and_save_image(prompt_frame3, output_filename_frame3)

def generate_page_four_frames(output_filename_frame1: str, output_filename_frame2: str, output_filename_frame3: str):
    prompt_frame1 = """A high-angle shot of a Vietnamese political leader delivering a speech at Ba Dinh Square during a national celebration. The leader is at a podium, with a large banner or screen behind emphasizing 80 years of independence and national development. The crowd is respectfully listening. Formal and inspiring atmosphere."""
    prompt_frame2 = """A military parade at Ba Dinh Square in Hanoi. The Vietnamese People's Army marching in formation, showing strength and solemnity. Soldiers in crisp uniforms, carrying flags and weapons. Majestic and powerful scene, clear day."""
    prompt_frame3 = """A police parade at Ba Dinh Square in Hanoi. The Vietnamese People's Public Security Force marching in formation, demonstrating order and discipline. Officers in their distinctive uniforms. Reflecting their role in maintaining peace and order."""

    generate_and_save_image(prompt_frame1, output_filename_frame1)
    generate_and_save_image(prompt_frame2, output_filename_frame2)
    generate_and_save_image(prompt_frame3, output_filename_frame3)

def generate_page_five_frames(output_filename_frame1: str, output_filename_frame2: str, output_filename_frame3: str):
    prompt_frame1 = """A grand military parade at Ba Dinh Square in Hanoi, featuring various branches of the Vietnamese armed forces: Navy sailors, Air Force personnel, Border Guards, and Coast Guard units, marching in perfect synchronization. Emphasize their determination to protect national sovereignty. Bright, clear day."""
    prompt_frame2 = """A vibrant civilian parade at Ba Dinh Square, with various social organizations and people from all walks of life: workers, farmers, youth, women, intellectuals, marching together with flags, flowers, and banners. Show unity and collective effort in national development. Joyful and patriotic atmosphere."""
    prompt_frame3 = """A formation of military helicopters flying over Ba Dinh Square, carrying large Party and National flags. The helicopters are soaring gracefully against a clear blue sky, creating a majestic and patriotic spectacle. Professional aerial photography."""

    generate_and_save_image(prompt_frame1, output_filename_frame1)
    generate_and_save_image(prompt_frame2, output_filename_frame2)
    generate_and_save_image(prompt_frame3, output_filename_frame3)

def generate_vietnam_flag_on_everest(output_filename: str):
    prompt = """Vietnamese national flag flying proudly on the summit of Mount Everest, red flag with yellow star, waving in strong mountain winds, snow-capped peaks in background, dramatic mountain landscape, clear blue sky, professional photography style, high quality, patriotic and majestic atmosphere."""
    model = "imagen-4"
    aspect_ratio = "16:9"
    return generate_and_save_image(
        prompt=prompt,
        output_filename=output_filename,
        model=model,
        aspect_ratio=aspect_ratio
    )
