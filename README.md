# Dự án AI thực chiến

Dự án này được tổ chức lại để tham gia cuộc thi AI thực chiến.

## Cấu trúc thư mục

```
/prepare_for_aitc/
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   ├── api_endpoints.json
│   └── messages.yaml
├── src/
│   ├── core/
│   │   └── common_utils.py
│   ├── api_services/
│   │   └── btc_api_client.py
│   ├── crawler/
│   ├── image_processing/
│   │   ├── image_generator.py
│   │   └── svg_handler.py
│   ├── video_processing/
│   ├── text_generation/
│   └── main_app.py
├── data/
│   ├── images/
│   ├── svg_templates/
│   ├── raw/
│   └── models/
├── notebooks/
│   ├── try_gen_text.ipynb
│   └── video_postprocess_cv2.ipynb
├── outputs/
│   ├── generated_images/
│   ├── generated_svgs/
│   ├── generated_audio/
│   ├── generated_audio_gemini/
│   └── generated_videos/
└── tests/
    └── test_thucchien_ai.py
```

## Cài đặt

1.  **Clone repository:**
    ```bash
    git clone <your_repo_url>
    cd prepare_for_aitc
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Linux/macOS
    # venv\Scripts\activate  # Trên Windows
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Thiết lập API Key:**
    Tạo một file `.env` ở thư mục gốc của dự án và thêm API key của ThucChien.AI:
    ```
    THUCCHIEN_AI_API_KEY="your_thucchien_ai_api_key_here"
    ```

## Cách chạy ứng dụng

Để chạy ứng dụng Streamlit:

```bash
streamlit run src/main_app.py
```

## Phát triển

Các file mã nguồn chính nằm trong thư mục `src/`.

*   `src/api_services/btc_api_client.py`: Chứa các hàm gọi API ThucChien.AI.
*   `src/image_processing/image_generator.py`: Chứa logic để tạo và lưu hình ảnh.
*   `src/image_processing/svg_handler.py`: Chứa logic để xử lý và điền nội dung vào SVG.
*   `src/main_app.py`: Điểm khởi đầu của ứng dụng Streamlit.

Các file dữ liệu đầu vào nằm trong `data/` và các kết quả đầu ra sẽ được lưu vào `outputs/`.
