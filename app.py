import streamlit as st
import google.generativeai as genai

# 1. Cấu hình giao diện trang web
st.set_page_config(page_title="Hỗ trợ Dịch vụ công Cấp xã", page_icon="chính_quyền_icon")
st.title("🏛️ Trợ lý Thủ tục Hành chính Cấp xã")
st.caption("Hỗ trợ tra cứu thủ tục, hồ sơ trên Cổng Dịch vụ công Quốc gia")

# 2. Cấu hình API Key (Lấy từ hệ thống bảo mật của Streamlit)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.warning("Vui lòng cấu hình API Key trong phần Secrets của Streamlit để bắt đầu.")
    st.stop()

# 3. THIẾT LẬP VAI TRÒ (SYSTEM INSTRUCTION) - PHẦN QUAN TRỌNG NHẤT
# Đây là nơi bạn dạy cho Gemini cách làm việc
system_instruction = """
Bạn là một chuyên gia tư vấn pháp lý và thủ tục hành chính với 10 năm kinh nghiệm làm việc tại bộ phận "Một cửa" cấp xã (UBND Xã/Phường/Thị trấn). Bạn am hiểu sâu sắc về quy trình trên Cổng dịch vụ công quốc gia (dichvucong.gov.vn).

Nhiệm vụ của bạn là hướng dẫn người dân thực hiện các thủ tục hành chính cấp xã một cách chính xác, dễ hiểu và tuân thủ pháp luật hiện hành.

Khi người dùng hỏi về một thủ tục, bạn PHẢI trả lời theo cấu trúc chuẩn sau đây:

1. TÊN THỦ TỤC HÀNH CHÍNH:
   - Nêu chính xác tên thủ tục theo quy định.

2. THÀNH PHẦN HỒ SƠ (Cần chuẩn bị để Scan/Chụp ảnh):
   - Liệt kê các giấy tờ bắt buộc (ví dụ: Tờ khai, Giấy chứng sinh, CMND/CCCD...).
   - Ghi rõ bản chính hay bản sao.

3. ĐIỀU KIỆN BẮT BUỘC & KÊ KHAI:
   - Các điều kiện tiên quyết (ví dụ: Phải là công dân thường trú tại địa bàn, thực hiện trong vòng 60 ngày...).
   - Các trường thông tin quan trọng không được bỏ trống trong tờ khai điện tử.

4. LƯU Ý KHI NỘP HỒ SƠ ONLINE:
   - Hướng dẫn về định dạng file (PDF/JPG), dung lượng file.
   - Lưu ý về chữ ký số (nếu cần) hoặc mang bản gốc đối chiếu khi nhận kết quả.
   - Lệ phí (nếu có).

LƯU Ý QUAN TRỌNG: Chỉ tư vấn các thủ tục thuộc thẩm quyền CẤP XÃ. Nếu người dân hỏi thủ tục cấp Huyện/Tỉnh, hãy lịch sự từ chối và hướng dẫn họ đến cơ quan phù hợp. Giọng văn cần trang trọng, ân cần, rõ ràng, đúng chuẩn mực cán bộ nhà nước.
"""

# Khởi tạo model với vai trò đã gán
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=system_instruction
)

# 4. Xử lý lịch sử chat (Để bot nhớ ngữ cảnh câu hỏi trước)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị hội thoại cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Xử lý khi người dùng nhập câu hỏi
if prompt := st.chat_input("Nhập tên thủ tục bạn cần hỗ trợ (VD: Khai sinh, Kết hôn...)..."):
    # Hiển thị câu hỏi người dùng
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gửi đến Gemini và nhận câu trả lời
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Tạo đoạn chat bao gồm lịch sử
            chat = model.start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            response = chat.send_message(prompt)
            full_response = response.text
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Đã có lỗi xảy ra: {e}")
            full_response = "Hệ thống đang bận, vui lòng thử lại sau."
    
    st.session_state.messages.append({"role": "model", "content": full_response})
