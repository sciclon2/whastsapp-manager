from flask import Flask, request, jsonify
from src.whatsapp import WhatsAppManager
from src.logger import Logger

app = Flask(__name__)
wa_manager = WhatsAppManager()
logger = Logger()




@app.route('/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        return handle_validation()
    else:
        return handle_message()

def handle_validation():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    config = wa_manager.config
    if mode == 'subscribe' and token == getattr(config, 'WA_VERIFY_TOKEN', 'my_verify_token'):
        logger.info("Webhook validated successfully.")
        return challenge, 200
    else:
        logger.info("Webhook validation failed.")
        return "Invalid token", 403

def handle_message():
    data = request.get_json()
    logger.debug(f"Webhook received: {data}")
    try:
        reply = wa_manager.handle_message(data)
        if reply:
            return jsonify(reply), 200
        else:
            return jsonify({"status": "ignored"}), 200
    except Exception as e:
        logger.info(f"Error handling message: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    port = getattr(wa_manager.config, 'WA_SERVICE_PORT', 7999)
    app.run(host="0.0.0.0", port=port)

# For production, run with:
# gunicorn -w 4 -b 0.0.0.0:7999 src.server:app
