import streamlit as st

# Set page config
st.set_page_config(
    page_title="Máy tính tổng 2 số tự nhiên",
    page_icon="🧮",
    layout="centered"
)

# Title
st.title("🧮 Máy tính tổng 2 số tự nhiên")

# Description
st.markdown("Nhập hai số tự nhiên để tính tổng:")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    number1 = st.number_input(
        "Số thứ nhất:",
        min_value=0,
        value=0,
        step=1,
        help="Nhập số tự nhiên đầu tiên"
    )

with col2:
    number2 = st.number_input(
        "Số thứ hai:",
        min_value=0,
        value=0,
        step=1,
        help="Nhập số tự nhiên thứ hai"
    )

# Calculate button
if st.button("Tính tổng", type="primary"):
    result = number1 + number2
    st.success(f"Tổng của {int(number1)} và {int(number2)} là: **{int(result)}**")

# Display current inputs
st.markdown("---")
st.markdown("### Thông tin hiện tại:")
st.write(f"**Số thứ nhất:** {int(number1)}")
st.write(f"**Số thứ hai:** {int(number2)}")
st.write(f"**Tổng:** {int(number1 + number2)}")

# Footer
st.markdown("---")
st.markdown("*Ứng dụng được tạo bằng Streamlit*")
