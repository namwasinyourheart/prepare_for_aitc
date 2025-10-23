from dotenv import load_dotenv

load_dotenv()

import requests
import os
import json
import base64
import io
from pydub import AudioSegment
import logging
import datetime
import uuid
from functools import wraps
import traceback
import inspect # Thêm import

# --- Cấu hình Logger --- #
LOG_DIR = "logs/api_interactions"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Chỉ cấu hình handlers một lần để tránh trùng lặp
if not logger.handlers:
    # File handler để ghi log vào file hàng ngày
    log_filename = datetime.datetime.now().strftime("api_interactions_%Y-%m-%d.log")
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_filename), encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    # Console handler để hiển thị log ra màn hình
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

# --- Hàm tiện ích ghi log --- #
def log_api_interaction(interaction_type: str, api_function_name: str, data: dict, interaction_id: str, level=logging.INFO):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "interaction_id": interaction_id,
        "type": interaction_type,
        "api_function": api_function_name,
        "data": data
    }
    log_message = json.dumps(log_entry, ensure_ascii=False)
    logger.log(level, log_message)

# --- Decorator cho API calls --- #
def log_api_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        interaction_id = str(uuid.uuid4())
        api_function_name = func.__name__

        # Lấy api_key từ os.environ.get để tránh lộ thông tin trong log
        api_key = os.environ.get("THUCCHIEN_AI_API_KEY")

        # Chuẩn bị headers cho log (loại bỏ API key)
        log_headers = {}
        if 'headers' in kwargs and isinstance(kwargs['headers'], dict):
            log_headers = {k: v for k, v in kwargs['headers'].items() if k.lower() not in ['authorization', 'x-goog-api-key']}
        # Đặc biệt cho 'kiem_tra_chi_tieu' và các hàm GET/download có headers đặc biệt
        if api_function_name == "kiem_tra_chi_tieu" or api_function_name == "tai_xuong_video_hoan_thanh" or api_function_name == "kiem_tra_trang_thai_video":
            # Đối với các hàm này, headers là một dict được tạo trong hàm, không phải từ kwargs
            # Cần lấy headers từ logic bên trong hàm nếu cần log headers cụ thể.
            pass # Sẽ xử lý trong từng hàm nếu cần log headers cụ thể

        # --- Tái cấu trúc logic ghi log payload ---
        log_payload = {}
        try:
            # Lấy chữ ký của hàm gốc
            sig = inspect.signature(func)
            # Liên kết các đối số đã truyền với chữ ký để lấy tên tham số
            bound_args = sig.bind(*args, **kwargs).arguments
            
            # Tạo payload từ các đối số đã liên kết
            log_payload = bound_args.copy()
            
            # Loại bỏ các tham số không phải là payload khỏi log
            log_payload.pop('self', None) # Bỏ 'self' nếu là phương thức của class
            log_payload.pop('file_path', None) # file_path được log riêng
            
            # Nếu hàm có **kwargs, gom các tham số phụ vào một mục
            if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
                main_params = {p.name for p in sig.parameters.values() if p.kind != inspect.Parameter.VAR_KEYWORD}
                additional_kwargs = {k: v for k, v in log_payload.items() if k not in main_params}
                
                # Giữ lại các tham số chính và gom phần còn lại
                log_payload = {k: v for k, v in log_payload.items() if k in main_params}
                if additional_kwargs:
                    log_payload['additional_kwargs'] = additional_kwargs

        except Exception as e:
            # Nếu có lỗi trong quá trình inspect, quay lại phương pháp cũ hơn
            if 'payload' in kwargs and isinstance(kwargs['payload'], dict):
                log_payload = kwargs['payload']
            elif 'json' in kwargs and isinstance(kwargs['json'], dict):
                log_payload = kwargs['json']
            log_payload['logging_error'] = f"Could not inspect args: {e}"


        # Bổ sung file_path nếu có trong kwargs
        log_data_for_request = {
            "url": kwargs.get("url") if "url" in kwargs else "(URL not available for logging)",
            "headers": log_headers,
            "payload": log_payload,
        }
        if "file_path" in kwargs:
            log_data_for_request["file_path"] = kwargs["file_path"]
        elif 'file_path' in log_payload: # Xử lý trường hợp file_path là đối số vị trí
             log_data_for_request["file_path"] = log_payload.get('file_path')

        # Ghi log request
        log_api_interaction("request", api_function_name, log_data_for_request, interaction_id)

        try:
            result = func(*args, **kwargs)
            # Ghi log response thành công
            log_data_for_response = {
                "status": "success",
                "result": result
            }

            # Cắt ngắn dữ liệu base64 trong log nếu có
            if isinstance(result, dict):
                # For sinh_hinh_anh, sinh_hinh_anh_voi_chat, sinh_sua_hinh_anh_voi_google_gemini
                if "response_data" in result and isinstance(result["response_data"], dict):
                    response_data_for_log = json.loads(json.dumps(result["response_data"])) # Deep copy for modification
                    # Handle sinh_hinh_anh response structure
                    if "data" in response_data_for_log and isinstance(response_data_for_log["data"], list) and response_data_for_log["data"]:
                        for idx, item in enumerate(response_data_for_log["data"]):
                            if "b64_json" in item:
                                response_data_for_log["data"][idx]["b64_json"] = "..." + item["b64_json"][-50:] + " (truncated)"
                    # Handle sinh_hinh_anh_voi_chat and sinh_sua_hinh_anh_voi_google_gemini response structure
                    if "choices" in response_data_for_log and isinstance(response_data_for_log["choices"], list) and response_data_for_log["choices"]:
                        for choice_idx, choice in enumerate(response_data_for_log["choices"]):
                            if "message" in choice and "images" in choice["message"] and isinstance(choice["message"]["images"], list) and choice["message"]["images"]:
                                for img_idx, image_data in enumerate(choice["message"]["images"]):
                                    if "image_url" in image_data and "url" in image_data["image_url"] and image_data["image_url"]["url"].startswith("data:") and ";base64," in image_data["image_url"]["url"]:
                                        full_url = image_data["image_url"]["url"]
                                        parts = full_url.split(";base64,")
                                        truncated_b64 = "..." + parts[1][-50:] + " (truncated)"
                                        response_data_for_log["choices"][choice_idx]["message"]["images"][img_idx]["image_url"]["url"] = parts[0] + ";base64," + truncated_b64
                            if "content" in choice and "parts" in choice["content"] and isinstance(choice["content"]["parts"], list) and choice["content"]["parts"]:
                                 for part_idx, part in enumerate(choice["content"]["parts"]):
                                    if "inlineData" in part and "data" in part["inlineData"] and isinstance(part["inlineData"]["data"], str):
                                        if part["inlineData"]["data"].startswith("iVBORw") or part["inlineData"]["data"].startswith("UklGR"): # Common image/audio base64 starts
                                            response_data_for_log["choices"][choice_idx]["content"]["parts"][part_idx]["inlineData"]["data"] = "..." + part["inlineData"]["data"][-50:] + " (truncated)"


                    # For chuyen_van_ban_thanh_giong_noi_voi_google response structure
                    # The actual base64 is not in `response_data` directly but processed into a file
                    # However, if any base64 was passed as `contents` for other Gemini calls, it should be truncated in `log_payload`
                    
                    log_data_for_response["result"]["response_data"] = response_data_for_log
                
                # For chuyen_van_ban_thanh_giong_noi_voi_google, the base64 is handled internally before returning.
                # The result itself is a success message. No direct base64 in `result`.

            if "file_path" in kwargs and os.path.exists(kwargs["file_path"]):
                log_data_for_response["saved_file"] = kwargs["file_path"]

            log_api_interaction("response", api_function_name, log_data_for_response, interaction_id)
            return result
        except requests.exceptions.RequestException as e:
            error_details = {
                "status": "error",
                "error_message": str(e),
                "response_text": getattr(e.response, "text", "N/A"),
                "status_code": getattr(e.response, "status_code", "N/A")
            }
            log_api_interaction("error_response", api_function_name, error_details, interaction_id, level=logging.ERROR)
            raise # Re-raise the exception after logging
        except Exception as e:
            error_details = {
                "status": "exception",
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            log_api_interaction("exception", api_function_name, error_details, interaction_id, level=logging.CRITICAL)
            raise # Re-raise the exception after logging

    return wrapper

# --- Hàm API gốc (được sửa đổi để chấp nhận decorator) --- #


@log_api_call
def sinh_phan_hoi_tro_chuyen(
    messages: list[dict],
    model: str = "gemini-2.5-flash",
    **kwargs
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
        "messages": messages,
        **kwargs # Unpack kwargs into the payload
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


@log_api_call
def sinh_hinh_anh(
    prompt: str,
    file_path: str,
    model: str = "imagen-4",
    n: int = 1,
    aspect_ratio: str = "1:1",
    **kwargs
) -> dict:
    """
    Gửi yêu cầu đến ThucChien.AI để sinh hình ảnh dựa trên prompt và lưu vào file.

    Args:
        prompt (str): Mô tả văn bản để AI dựa vào đó sinh hình ảnh.
        file_path (str): Đường dẫn đầy đủ để lưu file hình ảnh (ví dụ: "./output_images/my_image.png").
        model (str): Tên của mô hình AI muốn sử dụng (mặc định là "imagen-4").
        n (int): Số lượng hình ảnh muốn sinh (mặc định là 1).
        aspect_ratio (str): Tỷ lệ khung hình của hình ảnh (ví dụ: "1:1", "16:9").

    Returns:
        dict: Một dictionary chứa thông báo thành công hoặc lỗi.
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
        "aspect_ratio": aspect_ratio,
        **kwargs  # Unpack kwargs into the payload
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # print(f"[DEBUG ERROR] API Error Response: {e.response.text}") # Debug print removed
        raise  # Re-raise the exception after printing debug info
    response_json = response.json()

    if "data" in response_json and response_json["data"]:
        first_image_data = response_json["data"][0]
        if "b64_json" in first_image_data and first_image_data["b64_json"]:
            image_b64 = first_image_data["b64_json"]
            try:
                image_bytes = base64.b64decode(image_b64)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                return {"success": True, "message": f"Hình ảnh đã được lưu vào: {file_path}", "response_data": response_json}
            except Exception as e:
                return {"error": f"Không thể giải mã hoặc lưu hình ảnh: {e}", "response_data": response_json}
        elif "url" in first_image_data and first_image_data["url"]:
            # Trong trường hợp trả về URL, bạn có thể tải xuống ở đây hoặc chỉ trả về URL
            # Để đơn giản, hiện tại tôi sẽ chỉ trả về URL và message.
            return {"success": True, "message": f"Đã nhận được URL hình ảnh: {first_image_data['url']}. Bạn có thể tải từ đây.", "url": first_image_data['url'], "response_data": response_json}
    return {"error": "Không nhận được dữ liệu hình ảnh hợp lệ từ phản hồi API.", "response_data": response_json}


@log_api_call
def sinh_hinh_anh_voi_chat(
    messages: list[dict],
    file_path: str,
    model: str = "gemini-2.5-flash-image-preview",
    modalities: list[str] = ["image"],
    **kwargs
) -> dict:
    """
    Tạo hình ảnh trong một cuộc hội thoại bằng cách sử dụng mô hình đa phương thức của ThucChien.AI và lưu vào file.

    Args:
        messages (list[dict]): Danh sách các đối tượng tin nhắn, message cuối cùng nên chứa prompt để tạo ảnh.
                                Ví dụ: [{"role": "user", "content": "A breathtaking scene "}]
        file_path (str): Đường dẫn đầy đủ để lưu file hình ảnh (ví dụ: "./output_images/my_image.png").
        model (str): ID của mô hình đa phương thức sẽ sử dụng (mặc định là "gemini-2.5-flash-image-preview").
        modalities (list[str]): Chỉ định ["image"] để yêu cầu trả về dữ liệu hình ảnh.
        **kwargs: Các tham số bổ sung khác có thể truyền vào payload của API.

    Returns:
        dict: Một dictionary chứa thông báo thành công hoặc lỗi.
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
        "messages": messages,
        "modalities": modalities,
        **kwargs
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_json = response.json()

    if "choices" in response_json and response_json["choices"]:
        for choice in response_json["choices"]:
            if "message" in choice and "images" in choice["message"] and choice["message"]["images"]:
                first_image_data_wrapper = choice["message"]["images"][0]
                if "image_url" in first_image_data_wrapper and "url" in first_image_data_wrapper["image_url"]:
                    full_image_data_url = first_image_data_wrapper["image_url"]["url"]
                    
                    if full_image_data_url.startswith("data:") and ";base64," in full_image_data_url:
                        parts = full_image_data_url.split(";base64,")
                        mime_type_part = parts[0]
                        image_b64 = parts[1]
                        mime_type = mime_type_part.split(":")[1] if ":" in mime_type_part else "image/png"

                        try:
                            image_bytes = base64.b64decode(image_b64)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            extension = "." + mime_type.split('/')[-1] if '/' in mime_type else ".png"
                            final_file_path = os.path.splitext(file_path)[0] + extension
                            with open(final_file_path, "wb") as f:
                                f.write(image_bytes)
                            return {"success": True, "message": f"Hình ảnh đã được lưu vào: {final_file_path}", "response_data": response_json}
                        except Exception as e:
                            return {"error": f"Không thể giải mã hoặc lưu hình ảnh: {e}", "response_data": response_json}
                    else:
                        return {"success": True, "message": f"Đã nhận được URL hình ảnh không phải base64: {full_image_data_url}. Bạn có thể tải từ đây.", "url": full_image_data_url, "response_data": response_json}
    return {"error": "Không nhận được dữ liệu hình ảnh hợp lệ từ phản hồi API.", "response_data": response_json}


@log_api_call
def kiem_tra_chi_tieu() -> dict:
    """
    Lấy thông tin chi tiết về API key và mức độ sử dụng hiện tại từ ThucChien.AI.

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI chứa thông tin chi tiết về API key và mức sử dụng, hoặc thông báo lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = "https://api.thucchien.ai/key/info"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


@log_api_call
def sinh_sua_hinh_anh_voi_google_gemini(
    contents: list[dict],
    file_path: str,
    generation_config: dict = None,
    **kwargs
) -> dict:
    """
    Tạo hình ảnh hoặc sửa hình ảnh bằng cách sử dụng endpoint pass through tới Google Gemini của ThucChien.AI và lưu vào file.

    Args:
        contents (list[dict]): Nội dung của yêu cầu, bao gồm prompt văn bản và tùy chọn dữ liệu hình ảnh base64.
                                Ví dụ: [{"parts": [{"text": "A photo ..."}]}]
                                Hoặc để chỉnh sửa ảnh: [{"parts": [{"text": "Remove background"}, {"inline_data": {"mime_type": "image/png", "data": "<base64_image_data>"}}]}]
        file_path (str): Đường dẫn đầy đủ để lưu file hình ảnh (ví dụ: "./output_images/my_image.png").
        generation_config (dict): Cấu hình cho việc sinh nội dung, bao gồm imageConfig với aspectRatio.
                                  Ví dụ: {"imageConfig": {"aspectRatio": "9:16"}}
        **kwargs: Các tham số bổ sung khác có thể truyền vào payload của API.

    Returns:
        dict: Một dictionary chứa thông báo thành công hoặc lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = "https://api.thucchien.ai/gemini/v1beta/models/gemini-2.5-flash-image-preview:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    payload = {
        "contents": contents,
    }
    if generation_config:
        payload["generationConfig"] = generation_config
    payload.update(kwargs)

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_data = response.json()

    if "candidates" in response_data and response_data["candidates"]:
        for candidate in response_data["candidates"]:
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "inlineData" in part and part["inlineData"] and "data" in part["inlineData"]:
                        image_b64 = part["inlineData"]["data"]
                        mime_type = part["inlineData"]["mimeType"]

                        try:
                            image_bytes = base64.b64decode(image_b64)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            extension = "." + mime_type.split('/')[-1] if '/' in mime_type else ".png"
                            final_file_path = os.path.splitext(file_path)[0] + extension
                            with open(final_file_path, "wb") as f:
                                f.write(image_bytes)
                            return {"success": True, "message": f"Hình ảnh đã được lưu vào: {final_file_path}", "response_data": response_data}
                        except Exception as e:
                            return {"error": f"Không thể giải mã hoặc lưu hình ảnh: {e}", "response_data": response_data}
    return {"error": "Không nhận được dữ liệu hình ảnh hợp lệ từ phản hồi API.", "response_data": response_data}


@log_api_call
def tao_video(
    model: str,
    prompt: str,
    image: dict = None,
    negative_prompt: str = None,
    aspect_ratio: str = "16:9",
    duration_seconds: int = None,
    sample_count: int = None,
    resolution: str = None,
    person_generation: str = None,
    **kwargs
) -> dict:
    """
    Gửi một yêu cầu chứa mô tả (prompt) để bắt đầu quá trình tạo video với ThucChien.AI và Google Gemini.

    Args:
        model (str): Mô hình sẽ sử dụng để tạo video (ví dụ: "veo-3.0-generate-001").
        prompt (str): Mô tả chi tiết về video cần tạo.
        image (dict): Một hình ảnh ban đầu để tạo hiệu ứng hoạt hình. Bao gồm 'bytesBase64Encoded' và 'mimeType'.
        negative_prompt (str): Mô tả những gì không nên có trong video.
        aspect_ratio (str): Tỷ lệ khung hình của video (mặc định "16:9").
        duration_seconds (int): Thời gian của video (từ 5-8 giây, chỉ cho Veo 2).
        sample_count (int): Số lượng mẫu video cần tạo (mặc định 1, tối đa 2, chỉ cho Veo 2).
        resolution (str): Độ phân giải của video (ví dụ: "720p", "1080p" cho Veo 3).
        person_generation (str): Kiểm soát việc tạo ra hình ảnh con người.
        **kwargs: Các tham số bổ sung khác có thể truyền vào payload của API.

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI chứa `operation_name` để theo dõi trạng thái, hoặc thông báo lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = f"https://api.thucchien.ai/gemini/v1beta/models/{model}:predictLongRunning"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    instances_payload = {"prompt": prompt}
    if image:
        instances_payload["image"] = image

    parameters_payload = {}
    if negative_prompt:
        parameters_payload["negativePrompt"] = negative_prompt
    if aspect_ratio:
        parameters_payload["aspectRatio"] = aspect_ratio
    if duration_seconds is not None:
        parameters_payload["durationSeconds"] = duration_seconds
    if sample_count is not None:
        parameters_payload["sampleCount"] = sample_count
    if resolution:
        parameters_payload["resolution"] = resolution
    if person_generation:
        parameters_payload["personGeneration"] = person_generation

    payload = {
        "instances": [instances_payload]
    }
    if parameters_payload:
        payload["parameters"] = parameters_payload

    payload.update(kwargs)

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


@log_api_call
def kiem_tra_trang_thai_video(
    operation_name: str
) -> dict:
    """
    Kiểm tra trạng thái của quá trình tạo video bằng cách sử dụng operation_name nhận được từ hàm tao_video.

    Args:
        operation_name (str): Tên của tác vụ (operation) cần kiểm tra. Ví dụ: "models/veo-3.0-generate-001/operations/idrk08ltkg0a".

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI chứa trạng thái của tác vụ, hoặc thông báo lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = f"https://api.thucchien.ai/gemini/v1beta/{operation_name}"

    headers = {
        "x-goog-api-key": api_key
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


@log_api_call
def tai_xuong_video_hoan_thanh(
    video_id: str,
    file_path: str
) -> dict:
    """
    Tải video đã tạo về máy tính cục bộ từ endpoint mới.

    Args:
        video_id (str): ID của video cần tải về, được trích xuất từ uri ở Bước 2. Ví dụ: "fw30jj2nse1z".
        file_path (str): Đường dẫn đầy đủ để lưu file video (ví dụ: "./video_output/my_video.mp4").

    Returns:
        dict: Một dictionary chứa thông báo thành công hoặc lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = f"https://api.thucchien.ai/gemini/download/v1beta/files/{video_id}:download?alt=media"

    headers = {
        "x-goog-api-key": api_key
    }

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()  # Nâng lỗi cho các mã trạng thái HTTP không thành công

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):\
            f.write(chunk)

    return {"success": True, "message": f"Video đã được tải về thành công tại: {file_path}"}


@log_api_call
def chuyen_van_ban_thanh_giong_noi(
    model: str,
    input_text: str,
    voice: str,
    file_path: str,
    **kwargs
) -> dict:
    """
    Chuyển đổi một đoạn văn bản thành file âm thanh có giọng nói tự nhiên với ThucChien.AI.

    Args:
        model (str): ID của mô hình text-to-speech sẽ sử dụng (ví dụ: "gemini-2.5-flash-preview-tts").
        input_text (str): Đoạn văn bản cần chuyển đổi thành giọng nói.
        voice (str): Giọng nói sẽ sử dụng (ví dụ: "Zephyr", "Puck", "Charon").
        file_path (str): Đường dẫn đầy đủ để lưu file âm thanh (ví dụ: "./audio_output/my_speech.mp3").
        **kwargs: Các tham số bổ sung khác có thể truyền vào payload của API.

    Returns:
        dict: Một dictionary chứa thông báo thành công hoặc lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = "https://api.thucchien.ai/audio/speech"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "input": input_text,
        "voice": voice,
        **kwargs
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()  # Nâng lỗi cho các mã trạng thái HTTP không thành công

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return {"success": True, "message": f"File âm thanh đã được tải về thành công tại: {file_path}"}


@log_api_call
def chuyen_van_ban_thanh_giong_noi_voi_google(
    model: str,
    contents: list[dict],
    file_path: str,
    generation_config: dict = None,
    **kwargs
) -> dict:
    """
    Chuyển văn bản thành giọng nói với Google Gemini thông qua ThucChien.AI gateway.

    Args:
        model (str): ID của mô hình sẽ sử dụng (ví dụ: "gemini-2.5-flash-preview-tts").
        contents (list[dict]): Nội dung của yêu cầu, bao gồm prompt văn bản.
                                Ví dụ một người nói: [{"parts": [{"text": "Say cheerfully: Have a wonderful day!"}]}]
                                Ví dụ nhiều người nói: [{"parts": [{"text": "Speaker1: So... what's on the agenda today? Speaker2: You're never going to guess!"}]}]
        file_path (str): Đường dẫn đầy đủ để lưu file âm thanh (ví dụ: "./audio_output/gemini_speech.mp3").
        generation_config (dict): Cấu hình cho việc sinh nội dung, bao gồm responseModalities và speechConfig.
                                  Ví dụ: {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}}
        **kwargs: Các tham số bổ sung khác có thể truyền vào payload của API.

    Returns:
        dict: Một dictionary chứa thông báo thành công hoặc lỗi.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = f"https://api.thucchien.ai/gemini/v1beta/models/{model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    payload = {
        "contents": contents,
    }
    if generation_config:
        payload["generationConfig"] = generation_config
    payload.update(kwargs)

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Nâng lỗi cho các mã trạng thái HTTP không thành công

    response_data = response.json()
    # Trích xuất dữ liệu âm thanh base64 và mime_type
    audio_part = response_data["candidates"][0]["content"]["parts"][0]["inlineData"]
    audio_data_base64 = audio_part["data"]
    mime_type = audio_part["mimeType"]
    decoded_audio_data = base64.b64decode(audio_data_base64)

    # Chuyển đổi dữ liệu âm thanh sang MP3 bằng pydub
    # Giả định: audio/L16;codec=pcm;rate=24000 -> raw PCM, 16-bit, 1 kênh, 24000Hz
    # Nếu mime_type chỉ ra định dạng khác, cần điều chỉnh from_file hoặc from_wav/from_raw
    try:
        # Sử dụng BytesIO để pydub đọc dữ liệu nhị phân đã giải mã
        audio_segment = AudioSegment.from_file(io.BytesIO(decoded_audio_data), format="raw",
                                               frame_rate=24000, channels=1, sample_width=2)
        # Lưu dưới dạng MP3
        new_file_path = os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0] + ".mp3")
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        audio_segment.export(new_file_path, format="mp3")
        message = f"File âm thanh đã được tải về và chuyển đổi thành công sang MP3 tại: {new_file_path}"
        return {"success": True, "message": message}
    except Exception as pydub_err:
        return {"error": "Lỗi chuyển đổi định dạng âm thanh sang MP3", "details": str(pydub_err)}


@log_api_call
def chuyen_am_thanh_thanh_van_ban(
    audio_file_path: str,
    prompt: str = "Please transcribe the following audio.",
    model: str = "gemini-2.5-flash",
    **kwargs
) -> dict:
    """
    Chuyển đổi file âm thanh thành văn bản (transcript) sử dụng ThucChien.AI.

    Args:
        audio_file_path (str): Đường dẫn đến file âm thanh cần chuyển đổi.
        prompt (str): Prompt hướng dẫn cho mô hình (tùy chọn).
        model (str): ID của mô hình sẽ sử dụng.
        **kwargs: Các tham số bổ sung khác có thể truyền vào payload của API.

    Returns:
        dict: Phản hồi JSON từ ThucChien.AI chứa transcript.
    """
    api_key = os.environ.get("THUCCHIEN_AI_API_KEY")
    if not api_key:
        raise ValueError("Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    url = "https://api.thucchien.ai/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        with open(audio_file_path, "rb") as audio_file:
            audio_b64 = base64.b64encode(audio_file.read()).decode('utf-8')
    except FileNotFoundError:
        return {"error": f"File not found at {audio_file_path}"}
    
    # Xác định mime_type dựa trên phần mở rộng của file
    file_extension = os.path.splitext(audio_file_path)[1].lower()
    mime_types = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".m4a": "audio/m4a",
    }
    mime_type = mime_types.get(file_extension, "application/octet-stream")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "audio_url",
                        "audio_url": {
                            "url": f"data:{mime_type};base64,{audio_b64}"
                        }
                    }
                ]
            }
        ],
        **kwargs
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
