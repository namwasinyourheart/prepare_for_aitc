from dotenv import load_dotenv

load_dotenv()

import requests
import os
import json

def get_chat_completion_with_thucchien_ai(
    messages: list[dict],
    model: str = "gemini-2.5-flash"
) -> dict:
    """
    Gửi yêu cầu đến ThucChien.AI để nhận phản hồi từ mô hình trò chuyện.

    Args:
        messages (list[dict]): Danh sách các đối tượng tin nhắn, mỗi đối tượng có 'role' và 'content'.
                                Ví dụ: [{"role": "system", "content": "Bạn là một trợ lý ảo"},
                                          {"role": "user", "content": "Hãy viết một câu giới thiệu về Việt Nam."}]
        model (str): Tên của mô hình AI muốn sử dụng (mặc định là "gemini-2.5-flash").

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI hoặc thông báo lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = "https://api.thucchien.ai/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Nâng lỗi cho các mã trạng thái HTTP không thành công
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP xảy ra: {http_err}")
        print(f"Phản hồi từ server: {response.text}")
        return {"error": str(http_err), "details": response.text}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Lỗi kết nối xảy ra: {conn_err}")
        return {"error": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Lỗi timeout xảy ra: {timeout_err}")
        return {"error": str(timeout_err)}
    except requests.exceptions.RequestException as req_err:
        print(f"Lỗi không xác định xảy ra: {req_err}")
        return {"error": str(req_err)}
    except json.JSONDecodeError as json_err:
        print(f"Lỗi phân tích cú pháp JSON: {json_err}")
        print(f"Phản hồi không phải JSON: {response.text}")
        return {"error": "Phản hồi không phải JSON hợp lệ", "details": response.text}

def generate_image_with_thucchien_ai(
    prompt: str,
    model: str = "imagen-4",
    n: int = 1,
    aspect_ratio: str = "1:1"
) -> dict:
    """
    Gửi yêu cầu đến ThucChien.AI để sinh hình ảnh dựa trên prompt.

    Args:
        prompt (str): Mô tả văn bản để AI dựa vào đó sinh hình ảnh.
        model (str): Tên của mô hình AI muốn sử dụng (mặc định là "imagen-4").
        n (int): Số lượng hình ảnh muốn sinh (mặc định là 1).
        aspect_ratio (str): Tỷ lệ khung hình của hình ảnh (ví dụ: "1:1", "16:9").

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI chứa dữ liệu hình ảnh (b64_json) hoặc URL, hoặc thông báo lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = "https://api.thucchien.ai/images/generations"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "aspect_ratio": aspect_ratio
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Nâng lỗi cho các mã trạng thái HTTP không thành công
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP xảy ra: {http_err}")
        print(f"Phản hồi từ server: {response.text}")
        return {"error": str(http_err), "details": response.text}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Lỗi kết nối xảy ra: {conn_err}")
        return {"error": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Lỗi timeout xảy ra: {timeout_err}")
        return {"error": str(timeout_err)}
    except requests.exceptions.RequestException as req_err:
        print(f"Lỗi không xác định xảy ra: {req_err}")
        return {"error": str(req_err)}
    except json.JSONDecodeError as json_err:
        print(f"Lỗi phân tích cú pháp JSON: {json_err}")
        print(f"Phản hồi không phải JSON: {response.text}")
        return {"error": "Phản hồi không phải JSON hợp lệ", "details": response.text}
