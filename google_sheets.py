import gspread
from google.oauth2.service_account import Credentials

# Define the scope for Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "genfox-676c0e3d8bbd.json"  # Ensure this file is in your working directory

# Authenticate and create a client
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Open the Google Sheet using its ID
SPREADSHEET_ID = "1I9lOXlJbuOzngOIZQA5F2NN9VMsZFEG0IFabiHS2b7s"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Selects the first sheet

# Example: Append a new row of data
data = ["Customer Name", "Phone Number","Mail Address", "Call Summary"]
try:
    sheet.append_row(data)
    print("✅ Data written to Google Sheets successfully!")
except Exception as e:
    print(f"❌ Failed to write data: {e}")
