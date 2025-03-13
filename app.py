import gspread
import requests
import json
import os
from google.oauth2.service_account import Credentials
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Google Sheets Setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1I9lOXlJbuOzngOIZQA5F2NN9VMsZFEG0IFabiHS2b7s"

# Initialize globals for Google Sheets
client = None
sheet = None

# Try to load credentials from the service account file directly
try:
    SERVICE_ACCOUNT_FILE = "genfox-676c0e3d8bbd.json"
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Loading credentials from file: {SERVICE_ACCOUNT_FILE}")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        print("✅ Google Sheets connection successful!")
    else:
        print(f"❌ Service account file {SERVICE_ACCOUNT_FILE} not found")
except Exception as e:
    print(f"❌ Error setting up Google Sheets: {str(e)}")

# Bland AI API Config
BLAND_AI_API_URL = "https://api.bland.ai/call"
BLAND_AI_API_KEY = "org_ac9f8688ba89fd9fbfb009082ba78088a65bdb3493eab0e2d286d3c43ebf19df76cf1b80f08967ab6e8c69"

def initiate_bland_ai_call(phone_number, customer_name):
    """Initiate a call via Bland AI to gather requirements."""
    payload = {
        "phone_number": phone_number,
        "name": customer_name,
        "task": "Gather customer requirements for GenFox consulting services",
        "message": "Hello! Please describe your requirements. Also, here's a brief about our services..."
    }
    headers = {
        "Authorization": f"Bearer {BLAND_AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to Bland AI: {payload}")
    try:
        response = requests.post(BLAND_AI_API_URL, json=payload, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to initiate call: {response.text}"}
    except Exception as e:
        print(f"Exception during API call: {str(e)}")
        return {"error": f"Exception: {str(e)}"}

def append_call_data(customer_name, phone_number, mail_address, call_summary):
    """Append call details to Google Sheets."""
    global sheet
    
    if sheet is None:
        print("❌ Google Sheets not initialized")
        return False
    
    try:
        data = [customer_name, phone_number, mail_address, call_summary]
        sheet.append_row(data)
        print(f"✅ Data written for {customer_name} successfully!")
        return True
    except Exception as e:
        print(f"❌ Error appending data: {str(e)}")
        return False

@app.route("/submit-inquiry", methods=["POST"])
def handle_inquiry():
    """Handles incoming inquiries from the website form."""
    data = request.json
    customer_name = data.get("name")
    phone_number = data.get("phone")
    mail_address = data.get("email", "Not provided")  # Added mail address field
    
    if not customer_name or not phone_number:
        return jsonify({"error": "Missing name or phone number"}), 400
    
    # Initiate a call via Bland AI
    call_response = initiate_bland_ai_call(phone_number, customer_name)
    
    if "error" in call_response:
        return jsonify(call_response), 500
    
    # Extract transcription (Modify based on actual API response)
    call_summary = call_response.get("transcription", "No transcription available.")
    
    # Store details in Google Sheets if possible
    sheets_success = append_call_data(customer_name, phone_number, mail_address, call_summary)
    
    # Return success even if sheets fails, since the call was initiated
    response_message = "Call initiated successfully!"
    if not sheets_success:
        response_message += " (Note: Data could not be stored in Google Sheets)"
    
    return jsonify({"message": response_message}), 200

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    status = {
        "service": "GenFox Inquiry API",
        "status": "up",
        "google_sheets": "connected" if sheet is not None else "disconnected",
    }
    return jsonify(status)

if __name__ == "__main__":
    app.run(debug=True, port=5000)