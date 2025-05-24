import streamlit as st
import qrcode
import urllib.parse
from io import BytesIO
import base64
import datetime

# --- Configuration ---
MERCHANT_UPI_ID = "costacoffee@upi" # Replace with your actual Costa Coffee UPI ID
MERCHANT_NAME = "Costa Coffee"

# --- Helper Function to Generate UPI Link ---
def generate_upi_link(upi_id, name, amount):
    """
    Generates a UPI payment link.
    Args:
        upi_id (str): The UPI ID of the recipient.
        name (str): The name of the recipient.
        amount (float): The transaction amount.
    Returns:
        str: The generated UPI payment link, or None if inputs are invalid.
    """
    if not (upi_id and name and amount is not None and amount > 0):
        return None
    # Encode the name for URL safety
    encoded_name = urllib.parse.quote(name)
    return f"upi://pay?pa={upi_id}&pn={encoded_name}&am={amount:.2f}&cu=INR"

# --- Helper Function to Generate QR Code as Base64 Image ---
def generate_qr_code_base64(data):
    """
    Generates a QR code for the given data and returns it as a base64 encoded string.
    Args:
        data (str): The data to encode in the QR code (e.g., UPI link).
    Returns:
        str: Base64 encoded PNG image data.
    """
    if not data:
        return None
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# --- Streamlit App Layout ---
st.set_page_config(
    page_title="Costa Coffee UPI Scanner",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to bottom right, #f0f4f8, #e0e7ef);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        background-color: #e67e22; /* Amber-like color */
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #d35400; /* Darker amber */
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 0.75rem;
        font-size: 1rem;
    }
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 0.75rem;
        font-size: 1rem;
    }
    .receipt-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    .receipt-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
        text-align: center;
        margin-bottom: 1rem;
    }
    .receipt-item {
        margin-bottom: 0.5rem;
        font-size: 1rem;
        color: #555;
    }
    .receipt-item strong {
        color: #222;
    }
    .thank-you {
        text-align: center;
        margin-top: 1.5rem;
        font-style: italic;
        color: #777;
    }
    .qr-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1rem;
        background-color: #f8f8f8;
        border-radius: 10px;
        margin-top: 1.5rem;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.05);
    }
    .qr-container p {
        font-size: 1.1rem;
        font-weight: 500;
        color: #444;
        margin-bottom: 1rem;
    }
    .qr-image {
        border: 5px solid white;
        border-radius: 5px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title(f"<span style='color:#e67e22;'>Costa</span> <span style='color:#333;'>Coffee</span> UPI", unsafe_allow_html=True)
st.markdown("---")

# --- Input Fields ---
st.header("Transaction Details")
amount = st.number_input("Enter Amount (INR)", min_value=0.01, format="%.2f", step=0.01)
customer_upi_id = st.text_input("Customer UPI ID (Optional, for direct request)")

# --- Action Buttons ---
col1, col2 = st.columns(2)

with col1:
    if st.button("Generate QR Code"):
        if amount and amount > 0:
            upi_link = generate_upi_link(MERCHANT_UPI_ID, MERCHANT_NAME, amount)
            if upi_link:
                st.session_state['upi_link'] = upi_link
                st.session_state['show_qr'] = True
                st.session_state['show_receipt'] = False
                st.session_state['transaction_done'] = False
                st.session_state['payment_method'] = 'QR Code Scan'
                st.success("QR Code generated!")
            else:
                st.error("Could not generate UPI link. Please check inputs.")
        else:
            st.error("Please enter a valid amount to generate a QR code.")

with col2:
    if st.button("Send Request (UPI ID)"):
        if amount and amount > 0 and customer_upi_id:
            upi_link = generate_upi_link(customer_upi_id, MERCHANT_NAME, amount)
            if upi_link:
                st.session_state['upi_link'] = upi_link
                st.session_state['show_qr'] = False
                st.session_state['show_receipt'] = False
                st.session_state['transaction_done'] = False
                st.session_state['payment_method'] = 'UPI ID Request'
                st.info(f"Simulating request sent to {customer_upi_id} for ₹{amount:.2f}.")
            else:
                st.error("Could not generate UPI link. Please check inputs.")
        else:
            st.error("Please enter a valid amount and customer UPI ID to send a request.")

# --- QR Code Display ---
if 'show_qr' in st.session_state and st.session_state['show_qr'] and 'upi_link' in st.session_state:
    st.markdown("<div class='qr-container'>", unsafe_allow_html=True)
    st.markdown("<p>Scan this QR Code to Pay</p>", unsafe_allow_html=True)
    qr_base64 = generate_qr_code_base64(st.session_state['upi_link'])
    if qr_base64:
        st.image(f"data:image/png;base64,{qr_base64}", use_column_width=False, output_format="PNG", caption="Payment QR Code", width=250)
        st.markdown(f"<p style='font-size:0.85rem; color:#666; word-break: break-all;'>UPI Link: {st.session_state['upi_link']}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

# --- Generate Receipt Button ---
if ('upi_link' in st.session_state and st.session_state['upi_link'] and
    'transaction_done' not in st.session_state or not st.session_state['transaction_done']):
    if st.button("Generate Receipt"):
        st.session_state['transaction_done'] = True
        st.session_state['show_receipt'] = True
        st.session_state['receipt_details'] = {
            "transaction_id": f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{datetime.datetime.now().microsecond}",
            "date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": f"₹{amount:.2f}",
            "payment_method": st.session_state.get('payment_method', 'N/A'),
            "customer_upi_id": customer_upi_id if customer_upi_id else "N/A",
            "shop_name": MERCHANT_NAME
        }
        st.success("Receipt generated!")
        st.session_state['upi_link'] = None # Clear UPI link after receipt generation
        st.session_state['show_qr'] = False # Hide QR after receipt generation

# --- Receipt Display ---
if 'show_receipt' in st.session_state and st.session_state['show_receipt'] and 'receipt_details' in st.session_state:
    details = st.session_state['receipt_details']
    st.markdown("<div class='receipt-box'>", unsafe_allow_html=True)
    st.markdown("<p class='receipt-header'>Payment Receipt</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='receipt-item'><strong>Shop:</strong> {details['shop_name']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='receipt-item'><strong>Transaction ID:</strong> {details['transaction_id']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='receipt-item'><strong>Date & Time:</strong> {details['date_time']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='receipt-item'><strong>Amount:</strong> {details['amount']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='receipt-item'><strong>Payment Method:</strong> {details['payment_method']}</p>", unsafe_allow_html=True)
    if details['customer_upi_id'] != 'N/A':
        st.markdown(f"<p class='receipt-item'><strong>Customer UPI ID:</strong> {details['customer_upi_id']}</p>", unsafe_allow_html=True)
    st.markdown("<p class='thank-you'>Thank you for your purchase!</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Reset Button ---
st.markdown("---")
if st.button("New Transaction"):
    # Clear all session states to reset the app
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun() # Rerun the app to clear inputs and display
