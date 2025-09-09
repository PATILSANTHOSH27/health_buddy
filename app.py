from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# GitHub raw JSON URLs
DISEASES_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/diseases.json"
SYMPTOMS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/symptoms.json"
PREVENTIONS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/preventions.json"


def load_json_from_github(url):
    """Fetch JSON from GitHub raw URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return {}


@app.route("/webhook", methods=["POST"])
def webhook():
    """Dialogflow webhook for all intents."""
    req = request.get_json(silent=True, force=True)
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    # Get the disease parameter (consistent across all intents)
    disease = parameters.get("disease") or parameters.get("symptoms") or parameters.get("preventions") or parameters.get("synonyms")
    disease = disease.title() if disease else None  # Capitalize to match JSON keys

    # Load data from GitHub
    diseases_data = load_json_from_github(DISEASES_URL)
    symptoms_data = load_json_from_github(SYMPTOMS_URL)
    preventions_data = load_json_from_github(PREVENTIONS_URL)

    response_text = "Sorry, I couldn’t find the information."

    # Handle intents
    if intent_name == "CheckSymptomsIntent":
        if disease and disease in symptoms_data:
            response_text = f"Common symptoms of {disease}: {', '.join(symptoms_data[disease])}"
        else:
            response_text = f"Sorry, I don’t have symptom info for {disease}."

    elif intent_name == "CheckPreventionIntent":
        if disease and disease in preventions_data:
            response_text = f"Prevention tips for {disease}: {', '.join(preventions_data[disease])}"
        else:
            response_text = f"Sorry, I don’t have prevention info for {disease}."

    elif intent_name == "CheckSynonymsIntent":
        if disease and disease in diseases_data:
            response_text = f"Synonyms for {disease}: {', '.join(diseases_data[disease])}"
        else:
            response_text = f"Sorry, I don’t have synonyms for {disease}."

    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
