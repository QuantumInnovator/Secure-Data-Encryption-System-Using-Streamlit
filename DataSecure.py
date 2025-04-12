# 🛡️ Python Assignment: Secure Data Encryption System Using Streamlit
import streamlit as st 
import hashlib
import json
import os
import time 
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac

# 🔐 Data Information of user 🔐
DATA_FILE = "secure_data.json"
SALT = b"secure_salt_value"
LOCKOUT_DURATION = 60

# 🔑 Section login details 🔑
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None
    
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "lockout_time" not in st.session_state:
    st.session_state.lockout_time = 0

# 📂 If data is load 📂
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
        return json.load(f)    
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)        

def generate_key(passkey):
    key = pbkdf2_hmac('sha256', passkey.encode(), SALT, 100000)
    return urlsafe_b64encode(key)  # Return the base64 encoded key directly

def hash_password(password):
    return hashlib.pbkdf2_hmac('sha256',password.encode(),SALT,100000).hex()

# 🔄 Cryptography functions 🔄        
def encrypt_text(text , key ):
    cipher = Fernet(key)
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypt_text,key):
    try:
        cipher = Fernet(generate_key(key)) 
        return cipher.decrypt(encrypt_text.encode()).decode()
    except:
        return None

stored_data = load_data()

# 🧭 Navigation Bar 🧭
st.title("🛡️ Secure Data Encryption System")
menu = ["🏠 Home","📝 Register","🔒 Login","💾 Store Data","📥 Retrieve Data","ℹ️ About"] 
choice = st.sidebar.selectbox("Navigation",menu)

if choice == "🏠 Home":
    st.subheader("Welcome to My Data Encryption System! 🎉")
    st.markdown(""" 
        **Objective**
        Develop a Streamlit-based secure data storage and retrieval system where:
        - Users store data with a unique passkey 🔑
        - Users decrypt data by providing the correct passkey 🔓
        - Multiple failed attempts result in a forced reauthorization ⚠️
        - The system operates entirely in memory without external databases 💾
        """)
elif choice == "📝 Register":
    st.subheader("Register New User 📝")
    userName = st.text_input("Choose UserName")
    password = st.text_input("Choose Password", type="password")

    if st.button("Register"):
        if userName and password:
            if userName in stored_data:
                st.warning("⚠️ User Already Exists")
            else:
                stored_data[userName] = {
                    "password": hash_password(password),
                    "data": []
                }
                save_data(stored_data)
                st.success("🎉 User registered successfully!")
        else:
            st.error("❌ Both Fields are required")    
elif choice == "🔒 Login":
    st.subheader("User Login 🔒")

    if time.time() < st.session_state.lockout_time:
        remaining = int(st.session_state.lockout_time - time.time())
        st.error(f"⚠️ Too many failed attempts. Please wait {remaining} seconds")
        st.stop()

    userName = st.text_input("UserName") 
    password = st.text_input("Password",type="password")

    if st.button("Login"):
        if userName in stored_data and stored_data[userName]["password"] == hash_password(password):
            st.session_state.authenticated_user = userName
            st.session_state.failed_attempts = 0
            st.success(f"🎉 Welcome {userName}!")
        else: 
            st.session_state.failed_attempts += 1 
            remaining = 3 - st.session_state.failed_attempts
            st.error(f"❌ Invalid Credentials! Attempts left: {remaining}")

            if st.session_state.failed_attempts >= 3:
                st.session_state.lockout_time = time.time() + LOCKOUT_DURATION
                st.error("⚠️ Too many attempts. Locked for 60 seconds")

# 💾 DATA STORING SECTION 💾
# 💾 DATA STORING SECTION 💾
elif choice == "💾 Store Data":
    if not st.session_state.authenticated_user:
        st.warning("⚠️ Please login first")
    else:
        st.subheader("Store Encrypted Data 💾")
        data = st.text_area("Enter data to encrypt")
        password = st.text_input("Encryption key (passphrase)", type="password")

        if st.button("Encrypt and Save"):
            if data and password:
                key = generate_key(password)  # ✅ FIXED HERE
                encrypted = encrypt_text(data, key)  # ✅ PASSED CORRECT key
                stored_data[st.session_state.authenticated_user]["data"].append(encrypted)
                save_data(stored_data)
                st.success("🎉 Data encrypted and saved successfully")     
            else:
                st.error("❌ All fields are required to fill") 
  

# 📥 Data retrieve data section 📥
elif choice == "📥 Retrieve Data":
    if not st.session_state.authenticated_user:
        st.warning("⚠️ Please login first")
    else:
        st.subheader("Retrieve Data 📥")
        user_Data = stored_data.get(st.session_state.authenticated_user, {}).get("data",[])

        if not user_Data:
            st.info("ℹ️ No Data Found")
        else:
            st.write("Encrypted Data Entries")
            for i, item in enumerate(user_Data):
                st.code(item,language="text")

        encrypted_input = st.text_area("Enter Encrypted Text")
        password = st.text_input("Enter Password To Decrypt",type="password")

        if st.button("Decrypt"):
            result = decrypt_text(encrypted_input,password)
            if result:
                st.success(f"🎉 Decrypted: {result}")             
            else:
                st.error("❌ Incorrect Passkey or corrupted data")
