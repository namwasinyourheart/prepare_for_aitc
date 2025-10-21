import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, "../..")))


import pytest
from unittest.mock import patch, MagicMock
import os
import requests
import json
from utils import get_chat_completion_with_thucchien_ai, generate_image_with_thucchien_ai

# Fixture để thiết lập và gỡ bỏ biến môi trường API_KEY cho mỗi test
@pytest.fixture
def setup_api_key():
    # Thiết lập biến môi trường trước khi chạy test
    os.environ["THUCCHIEN_AI_API_KEY"] = "fake_api_key_for_testing"
    yield
    # Gỡ bỏ biến môi trường sau khi test hoàn thành
    del os.environ["THUCCHIEN_AI_API_KEY"]

def test_get_chat_completion_success(setup_api_key):
    """
    Kiểm tra trường hợp hàm trả về phản hồi thành công.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test_id",
        "choices": [
            {
                "message": {
                    "content": "Đây là phản hồi test thành công.",
                    "role": "assistant"
                }
            }
        ]
    }
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Test message"}]
        result = get_chat_completion_with_thucchien_ai(messages)

        mock_post.assert_called_once_with(
            "https://api.thucchien.ai/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer fake_api_key_for_testing"
            },
            json={"model": "gemini-2.5-flash", "messages": messages}
        )
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Đây là phản hồi test thành công."

def test_get_chat_completion_no_api_key():
    """
    Kiểm tra trường hợp không có API Key, hàm nên raise ValueError.
    """
    if "THUCCHIEN_AI_API_KEY" in os.environ:
        del os.environ["THUCCHIEN_AI_API_KEY"]
    with pytest.raises(ValueError, match="Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập."):
        get_chat_completion_with_thucchien_ai([{"role": "user", "content": "Test message"}])

def test_get_chat_completion_http_error(setup_api_key):
    """
    Kiểm tra trường hợp HTTPError (ví dụ: 400 Bad Request).
    """
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error: Bad Request for url", response=mock_response)

    with patch('requests.post', return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Test message"}]
        result = get_chat_completion_with_thucchien_ai(messages)

        assert "error" in result
        assert "400 Client Error" in result["error"]
        assert result["details"] == "Bad Request"

def test_get_chat_completion_connection_error(setup_api_key):
    """
    Kiểm tra trường hợp ConnectionError (ví dụ: không có mạng).
    """
    with patch('requests.post', side_effect=requests.exceptions.ConnectionError("Test Connection Error")) as mock_post:
        messages = [{"role": "user", "content": "Test message"}]
        result = get_chat_completion_with_thucchien_ai(messages)

        assert "error" in result
        assert "Test Connection Error" in result["error"]

def test_get_chat_completion_timeout_error(setup_api_key):
    """
    Kiểm tra trường hợp Timeout.
    """
    with patch('requests.post', side_effect=requests.exceptions.Timeout("Test Timeout Error")) as mock_post:
        messages = [{"role": "user", "content": "Test message"}]
        result = get_chat_completion_with_thucchien_ai(messages)

        assert "error" in result
        assert "Test Timeout Error" in result["error"]

def test_get_chat_completion_json_decode_error(setup_api_key):
    """
    Kiểm tra trường hợp phản hồi không phải JSON hợp lệ.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "This is not JSON"
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", mock_response.text, 0)
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Test message"}]
        result = get_chat_completion_with_thucchien_ai(messages)

        assert "error" in result
        assert "Phản hồi không phải JSON hợp lệ" in result["error"]
        assert result["details"] == "This is not JSON"

def test_generate_image_success(setup_api_key):
    """
    Kiểm tra trường hợp hàm generate_image_with_thucchien_ai trả về phản hồi thành công.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "created": 1761018371,
        "data": [
            {
                "b64_json": "fake_base64_image_data",
                "url": "https://example.com/fake_image.png"
            }
        ],
        "usage": {"total_tokens": 0}
    }
    mock_response.raise_for_status.return_value = None

    with patch('requests.post', return_value=mock_response) as mock_post:
        prompt = "a digital render of a massive skyscraper, modern, grand, epic with a beautiful sunset in the background "
        result = generate_image_with_thucchien_ai(prompt)

        mock_post.assert_called_once_with(
            "https://api.thucchien.ai/images/generations",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer fake_api_key_for_testing"
            },
            json={
                "model": "imagen-4",
                "prompt": prompt,
                "n": 1,
                "aspect_ratio": "1:1"
            }
        )
        assert "data" in result
        assert len(result["data"]) > 0
        assert result["data"][0]["b64_json"] == "fake_base64_image_data"
        assert result["data"][0]["url"] == "https://example.com/fake_image.png"

def test_get_chat_completion_real_api_call():
    """
    Kiểm tra hàm bằng cách gửi yêu cầu thực đến API ThucChien.AI.
    Bài kiểm thử này sẽ bị bỏ qua nếu biến môi trường 'THUCCHIEN_AI_API_KEY' không được thiết lập.
    """
    api_key = os.getenv("THUCCHIEN_AI_API_KEY")
    if not api_key:
        pytest.skip("Bỏ qua bài kiểm thử API thực: Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    # Sử dụng một tin nhắn đơn giản để kiểm tra
    messages = [
        {"role": "user", "content": "Chào bạn, bạn có khỏe không?"}
    ]

    print(f"\nĐang gửi yêu cầu thực đến ThucChien.AI với mô hình: gemini-2.5-flash...")
    result = get_chat_completion_with_thucchien_ai(messages)
    print(f"Phản hồi thô từ API: {result}")

    # Kiểm tra phản hồi
    print("Kiểm tra 'choices' trong phản hồi...")
    assert "choices" in result, f"Phản hồi không chứa 'choices': {result}"
    print("'choices' đã tìm thấy. Kiểm tra xem có ít nhất một lựa chọn...")
    assert len(result["choices"]) > 0, "Không có lựa chọn nào trong phản hồi."
    print("Đã tìm thấy ít nhất một lựa chọn. Kiểm tra 'message' trong lựa chọn đầu tiên...")
    assert "message" in result["choices"][0], f"Lựa chọn không chứa 'message': {result['choices'][0]}"
    print("'message' đã tìm thấy. Kiểm tra 'content' trong tin nhắn...")
    assert "content" in result["choices"][0]["message"], f"Tin nhắn không chứa 'content': {result['choices'][0]['message']}"

    response_content = result["choices"][0]["message"]["content"]
    print(f"Nội dung phản hồi từ API thực (100 ký tự đầu): {response_content[:100]}...") # In một phần nội dung

    # Kiểm tra nội dung phản hồi không rỗng
    print("Kiểm tra nội dung phản hồi không rỗng...")
    assert len(response_content) > 0, "Nội dung phản hồi từ API thực bị rỗng."
    print("Nội dung phản hồi không rỗng.")
    print("Bài kiểm thử API thực thành công!")

def test_generate_image_real_api_call():
    """
    Kiểm tra hàm generate_image_with_thucchien_ai bằng cách gửi yêu cầu thực đến API ThucChien.AI.
    Bài kiểm thử này sẽ bị bỏ qua nếu biến môi trường 'THUCCHIEN_AI_API_KEY' không được thiết lập.
    """
    api_key = os.getenv("THUCCHIEN_AI_API_KEY")
    if not api_key:
        pytest.skip("Bỏ qua bài kiểm thử API sinh ảnh thực: Biến môi trường 'THUCCHIEN_AI_API_KEY' chưa được thiết lập.")

    prompt = "A majestic lion standing on a rock, roaring, in a savanna during sunset, realistic, detailed."
    model = "imagen-4"
    aspect_ratio = "1:1"

    print(f"\nĐang gửi yêu cầu thực đến ThucChien.AI để sinh ảnh với prompt: '{prompt[:70]}...'")
    print(f"Mô hình: {model}, Tỷ lệ khung hình: {aspect_ratio}")
    result = generate_image_with_thucchien_ai(prompt, model=model, aspect_ratio=aspect_ratio)
    print(f"Phản hồi thô từ API: {result}")

    # Kiểm tra phản hồi
    print("Kiểm tra 'data' trong phản hồi...")
    assert "data" in result, f"Phản hồi không chứa 'data': {result}"
    print("'data' đã tìm thấy. Kiểm tra xem có ít nhất một hình ảnh...")
    assert len(result["data"]) > 0, "Không có hình ảnh nào trong phản hồi."
    print("Đã tìm thấy ít nhất một hình ảnh. Kiểm tra 'b64_json' hoặc 'url' trong dữ liệu hình ảnh đầu tiên...")
    
    first_image_data = result["data"][0]
    assert ("b64_json" in first_image_data and first_image_data["b64_json"]) or \
           ("url" in first_image_data and first_image_data["url"]), \
           f"Dữ liệu hình ảnh đầu tiên không chứa 'b64_json' hoặc 'url': {first_image_data}"

    if "b64_json" in first_image_data and first_image_data["b64_json"]:
        print(f"Đã nhận được dữ liệu hình ảnh base64 (dài {len(first_image_data['b64_json'])} ký tự).")
    elif "url" in first_image_data and first_image_data["url"]:
        print(f"Đã nhận được URL hình ảnh: {first_image_data['url']}")

    print("Bài kiểm thử API sinh ảnh thực thành công!")
