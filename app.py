import os
import tempfile
import pathlib
import gradio as gr
from markitdown import MarkItDown

# Khởi tạo đối tượng MarkItDown
markitdown = MarkItDown()

def convert_document(uploaded_file):
    """
    Nhận file tải lên, chuyển đổi sang Markdown bằng MarkItDown,
    lưu file .md tạm để phục vụ download và trả về kết quả xem trước.
    """
    if uploaded_file is None:
        return (
            "⚠️ Vui lòng tải lên một tệp tài liệu trước khi bấm chuyển đổi.",
            "",
            None,
            "Chưa có tệp nào được chọn."
        )
    
    file_path = uploaded_file if isinstance(uploaded_file, str) else uploaded_file.name
    original_name = pathlib.Path(file_path).stem
    
    try:
        # Thực hiện chuyển đổi file sang Markdown
        result = markitdown.convert(file_path)
        md_content = result.text_content
        
        if not md_content or not md_content.strip():
            md_content = "_Tệp tài liệu này không chứa nội dung văn bản hoặc nội dung rỗng._"

        # Tạo file .md tạm thời với tên tương ứng để tải về
        temp_dir = tempfile.mkdtemp()
        output_filename = f"{original_name}.md"
        output_path = os.path.join(temp_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        status_msg = f"✅ Chuyển đổi thành công '{pathlib.Path(file_path).name}' ({len(result.text_content):,} ký tự)"
        
        return (
            md_content,          # Hiển thị Rendered Markdown
            result.text_content, # Hiển thị Raw Markdown Code
            output_path,         # Đường dẫn file tải về
            status_msg           # Thông báo trạng thái
        )
    except Exception as e:
        error_msg = f"❌ Lỗi trong quá trình chuyển đổi: {str(e)}"
        return (
            f"**Đã xảy ra lỗi:**\n```\n{str(e)}\n```",
            "",
            None,
            error_msg
        )

def clear_all():
    return None, "", "", None, "Đã làm mới giao diện."

# Thiết kế Giao diện Gradio
custom_css = """
.main-title { text-align: center; margin-bottom: 0.5rem; }
.sub-title { text-align: center; color: #666; margin-bottom: 1.5rem; }
.output-box { min-height: 400px; }
"""

with gr.Blocks(title="MarkItDown Web UI") as demo:
    gr.Markdown(
        """
        # 📝 MarkItDown Web Converter
        ### Chuyển đổi mọi tài liệu (PDF, Word, Excel, PowerPoint, Text, HTML...) sang Markdown
        """,
        elem_classes=["main-title", "sub-title"]
    )
    
    with gr.Row():
        # Cột trái: Tải file và các nút điều khiển
        with gr.Column(scale=1):
            file_input = gr.File(
                label="📁 Tải lên tệp tài liệu",
                file_types=[
                    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
                    ".xlsx", ".xls", ".csv", ".json", ".xml",
                    ".html", ".htm", ".txt", ".epub", ".zip"
                ],
                type="filepath"
            )
            
            with gr.Row():
                btn_convert = gr.Button("⚡ Chuyển đổi ngay", variant="primary")
                btn_clear = gr.Button("🔄 Làm mới", variant="secondary")
                
            status_output = gr.Textbox(
                label="Trạng thái",
                value="Sẵn sàng tiếp nhận tài liệu.",
                interactive=False
            )
            
            download_output = gr.File(
                label="📥 Tải xuống tệp .md",
                interactive=False
            )
            
            gr.Markdown(
                """
                > **Định dạng hỗ trợ:**
                > - **Văn phòng:** PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx)
                > - **Dữ liệu & Web:** CSV, JSON, XML, HTML
                > - **Sách & Lưu trữ:** EPUB, ZIP, TXT
                """
            )

        # Cột phải: Xem trước kết quả
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("👁️ Xem trước (Rendered Markdown)"):
                    md_preview = gr.Markdown(
                        value="_Chưa có nội dung. Vui lòng tải file và bấm chuyển đổi._",
                        elem_classes=["output-box"]
                    )
                with gr.TabItem("💻 Mã nguồn Markdown (Raw Text)"):
                    raw_preview = gr.Code(
                        label="Mã Markdown thô",
                        language="markdown",
                        lines=18,
                        interactive=False
                    )

    # Đăng ký sự kiện
    btn_convert.click(
        fn=convert_document,
        inputs=[file_input],
        outputs=[md_preview, raw_preview, download_output, status_output]
    )
    
    # Tự động chuyển đổi khi upload file xong
    file_input.upload(
        fn=convert_document,
        inputs=[file_input],
        outputs=[md_preview, raw_preview, download_output, status_output]
    )
    
    btn_clear.click(
        fn=clear_all,
        inputs=[],
        outputs=[file_input, md_preview, raw_preview, download_output, status_output]
    )

if __name__ == "__main__":
    # Cho phép public ra internet qua share=True (mặc định True để dùng được trên Colab / mạng ngoài)
    share_env = os.getenv("GRADIO_SHARE", "true").lower() in ("true", "1", "yes")
    port = int(os.getenv("PORT", 7860))
    print("Khởi chạy MarkItDown Web UI...")
    demo.launch(share=share_env, server_port=port, theme=gr.themes.Soft(), css=custom_css)
