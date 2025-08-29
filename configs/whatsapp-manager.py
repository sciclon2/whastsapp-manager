# WhatsApp Manager Configs

SENTIMETOR_PROXY_URL = "http://localhost:8000/route"
WHISPER_SERVER_URL = "http://ec2-54-77-89-193.eu-west-1.compute.amazonaws.com:9000/transcribe"
# optional: 
TIMEOUT_SECONDS = 120
LOG_LEVEL = "INFO"  # or "DEBUG"

# WhatsApp API credentials and tokens
WA_VERIFY_TOKEN = "dev-verify"  # Used for webhook validation, set to a secure random string
WA_WABA_TOKEN = "EAARw3s66QwUBPDjqKZBg3nY5tWphQOvfxDSWvvVtiTIjnCLZBnf7AOrGAYRGG8YPZCbZC1lRnVGSf2NivloV6U1QIPnakRH56y8sfOpo1PAcX5cZAjRXyO2cBZCc6N0nVgfZBDM4lXZApYMLhlOgrvlUnM8XokUDhyI7KCaeY5yGv6c98iX7TYPiq7zZBmkzEFaD7ZCgZDZD"  # WhatsApp Business Account access token
WA_WABA_PHONE_ID = "733190389884668"  # WhatsApp Business Account phone number ID

# Service port
WA_SERVICE_PORT = 7999  # Port to run the Flask service on

# Add more configs as needed
LOG_LEVEL = "DEBUG"