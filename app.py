# from flask import Flask, request, jsonify
# from twilio.twiml.messaging_response import MessagingResponse
# import requests
# import os

# app = Flask(__name__)

# # ----------------- GitHub JSON URLs -----------------
# DISEASES_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/diseases.json"
# SYMPTOMS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/symptoms.json"
# PREVENTIONS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/preventions.json"

# # Your deployed Dialogflow webhook URL
# DIALOGFLOW_WEBHOOK_URL = "https://health-buddy-4425.onrender.com/webhook"

# # ----------------- Utility Functions -----------------
# def load_json_from_github(url):
#     """Fetch JSON from GitHub raw URL and return lowercase keys."""
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         return {k.lower(): v for k, v in data.items()}
#     except Exception as e:
#         print(f"Error loading {url}: {e}")
#         return {}

# # ----------------- Dialogflow Webhook -----------------
# @app.route("/webhook", methods=["POST"])
# def dialogflow_webhook():
#     """Dialogflow webhook for all intents."""
#     req = request.get_json(silent=True, force=True)
#     intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
#     parameters = req.get("queryResult", {}).get("parameters", {})

#     disease_param = (
#         parameters.get("disease")
#         or parameters.get("symptoms")
#         or parameters.get("preventions")
#         or parameters.get("synonyms")
#     )
#     disease = disease_param[0] if isinstance(disease_param, list) and disease_param else disease_param
#     disease_lower = disease.lower() if disease else None

#     diseases_data = load_json_from_github(DISEASES_URL)
#     symptoms_data = load_json_from_github(SYMPTOMS_URL)
#     preventions_data = load_json_from_github(PREVENTIONS_URL)

#     response_text = "Sorry, I couldn’t find the information."

#     if intent_name == "CheckSymptomsIntent" and disease_lower in symptoms_data:
#         response_text = f"Symptoms of {disease.title()}: {', '.join(symptoms_data[disease_lower])}."
#     elif intent_name == "CheckPreventionIntent" and disease_lower in preventions_data:
#         response_text = f"Preventions for {disease.title()}: {', '.join(preventions_data[disease_lower])}."
#     elif intent_name == "CheckSynonymsIntent" and disease_lower in diseases_data:
#         response_text = f"Synonyms for {disease.title()}: {', '.join(diseases_data[disease_lower])}."
#     elif disease:
#         response_text = f"Sorry, I don’t have info for {disease.title()}."

#     return jsonify({"fulfillmentText": response_text})

# # ----------------- Twilio WhatsApp / SMS Webhook -----------------
# @app.route("/sms", methods=["POST"])
# def sms_reply():
#     """Receive SMS/WhatsApp via Twilio, forward to Dialogflow, reply."""
#     incoming_msg = request.form.get("Body", "").lower()
#     sender = request.form.get("From")
#     print(f"Message from {sender}: {incoming_msg}")

#     # Load diseases from GitHub
#     diseases_data = load_json_from_github(DISEASES_URL)

#     # 1️⃣ Detect disease in message
#     detected_disease = None
#     for disease in diseases_data.keys():
#         if disease in incoming_msg:
#             detected_disease = disease
#             break

#     # 2️⃣ Detect intent based on keywords
#     if any(word in incoming_msg for word in ["symptom", "feel", "signs"]):
#         intent = "CheckSymptomsIntent"
#     elif any(word in incoming_msg for word in ["prevent", "avoid", "protection"]):
#         intent = "CheckPreventionIntent"
#     elif any(word in incoming_msg for word in ["also called", "synonym", "other name"]):
#         intent = "CheckSynonymsIntent"
#     else:
#         intent = "CheckSymptomsIntent"  # default fallback

#     # 3️⃣ Build Dialogflow request
#     df_request = {
#         "queryResult": {
#             "queryText": incoming_msg,
#             "intent": {"displayName": intent},
#             "parameters": {"disease": detected_disease or ""}
#         }
#     }

#     # 4️⃣ Send to Dialogflow webhook
#     try:
#         response = requests.post(DIALOGFLOW_WEBHOOK_URL, json=df_request, timeout=10)
#         response.raise_for_status()
#         df_response = response.json()
#         reply_text = df_response.get("fulfillmentText", "Sorry, I couldn’t understand that.")
#     except Exception as e:
#         print(f"Error contacting Dialogflow webhook: {e}")
#         reply_text = "Sorry, could not process your request."

#     # 5️⃣ Reply via Twilio
#     resp = MessagingResponse()
#     if detected_disease is None:
#         reply_text = "Please specify the disease name so I can help you."
#     resp.message(reply_text)
#     return str(resp)

# # ----------------- Run Flask App -----------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=False)


from flask import Flask, request, jsonify, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# ----------------- GitHub JSON URLs -----------------
DISEASES_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/diseases.json"
SYMPTOMS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/symptoms.json"
PREVENTIONS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/preventions.json"

# Dialogflow webhook URL
DIALOGFLOW_WEBHOOK_URL = "https://health-buddy-4425.onrender.com/webhook"

# ----------------- Utility -----------------
def load_json_from_github(url):
    """Fetch JSON from GitHub raw URL and return lowercase keys."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {str(k).lower(): v for k, v in data.items()}
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return {}

# ----------------- Dialogflow Webhook -----------------
@app.route("/webhook", methods=["POST"])
def dialogflow_webhook():
    """Dialogflow webhook for all intents."""
    req = request.get_json(silent=True, force=True)
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    disease_param = (
        parameters.get("disease")
        or parameters.get("symptoms")
        or parameters.get("preventions")
        or parameters.get("synonyms")
    )

    disease = disease_param[0] if isinstance(disease_param, list) and disease_param else disease_param
    disease_lower = disease.lower() if isinstance(disease, str) else None

    diseases_data = load_json_from_github(DISEASES_URL)
    symptoms_data = load_json_from_github(SYMPTOMS_URL)
    preventions_data = load_json_from_github(PREVENTIONS_URL)

    response_text = "Sorry, I couldn’t find the information."

    if intent_name == "CheckSymptomsIntent" and disease_lower in symptoms_data:
        response_text = f"Symptoms of {disease.title()}: {', '.join(symptoms_data[disease_lower])}."
    elif intent_name == "CheckPreventionIntent" and disease_lower in preventions_data:
        response_text = f"Preventions for {disease.title()}: {', '.join(preventions_data[disease_lower])}."
    elif intent_name == "CheckSynonymsIntent" and disease_lower in diseases_data:
        response_text = f"Synonyms for {disease.title()}: {', '.join(diseases_data[disease_lower])}."
    elif disease:
        response_text = f"Sorry, I don’t have info for {disease.title()}."

    return jsonify({"fulfillmentText": response_text})

# ----------------- Twilio SMS Webhook -----------------
@app.route("/sms", methods=["POST"])
def sms_reply():
    """Receive SMS from Twilio, forward to Dialogflow, and reply."""
    incoming_msg = request.form.get("Body", "").strip().lower()
    sender = request.form.get("From")   # For SMS: +91XXXXXXXXXX
    print(f"SMS from {sender}: {incoming_msg}")

    # Load disease names
    diseases_data = load_json_from_github(DISEASES_URL)

    # Detect disease in the message
    detected_disease = None
    for disease in diseases_data.keys():
        if disease in incoming_msg:
            detected_disease = disease
            break

    # Detect intent
    if any(word in incoming_msg for word in ["symptom", "feel", "signs"]):
        intent = "CheckSymptomsIntent"
    elif any(word in incoming_msg for word in ["prevent", "avoid", "protection"]):
        intent = "CheckPreventionIntent"
    elif any(word in incoming_msg for word in ["also called", "synonym", "other name"]):
        intent = "CheckSynonymsIntent"
    else:
        intent = "CheckSymptomsIntent"  # default

    # If no disease detected, respond directly
    if not detected_disease:
        reply_text = "Please specify the disease name so I can help you."
        resp = MessagingResponse()
        resp.message(reply_text)
        return Response(str(resp), mimetype="application/xml")

    # Build fake Dialogflow request
    df_request = {
        "queryResult": {
            "queryText": incoming_msg,
            "intent": {"displayName": intent},
            "parameters": {"disease": detected_disease}
        }
    }

    # Send to Dialogflow webhook
    try:
        response = requests.post(DIALOGFLOW_WEBHOOK_URL, json=df_request, timeout=10)
        response.raise_for_status()
        df_response = response.json()
        reply_text = df_response.get("fulfillmentText", "Sorry, I couldn’t understand that.")
    except Exception as e:
        print(f"Error contacting Dialogflow webhook: {e}")
        reply_text = "Sorry, could not process your request."

    # Final SMS response
    resp = MessagingResponse()
    resp.message(reply_text)
    return Response(str(resp), mimetype="application/xml")

# ----------------- Run Flask App -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
