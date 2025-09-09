from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# GitHub raw JSON URLs
DISEASES_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/diseases.json"
SYMPTOMS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/symptoms.json"
PREVENTIONS_URL = "https://raw.githubusercontent.com/PATILSANTHOSH27/health_buddy/main/preventions.json"


def load_json_from_github(url):
    """Fetch JSON from GitHub raw URL and return dictionary with lowercase keys for case-insensitive matching."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Convert keys to lowercase for case-insensitive matching
        return {k.lower(): v for k, v in data.items()}
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return {}


@app.route("/webhook", methods=["POST"])
def webhook():
    """Dialogflow webhook for all intents."""
    req = request.get_json(silent=True, force=True)
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    # Get the disease parameter and normalize to lowercase
    disease = parameters.get("disease") or parameters.get("symptoms") or parameters.get("preventions") or parameters.get("synonyms")
    if disease:
        disease_lower = disease.lower()
    else:
        disease_lower = None

    # Load JSON data from GitHub
    diseases_data = load_json_from_github(DISEASES_URL)
    symptoms_data = load_json_from_github(SYMPTOMS_URL)
    preventions_data = load_json_from_github(PREVENTIONS_URL)

    response_text = "Sorry, I couldn’t find the information."

    # Handle intents
    if intent_name == "CheckSymptomsIntent":
        if disease_lower and disease_lower in symptoms_data:
            response_text = f"Common symptoms of {disease.title()}: {', '.join(symptoms_data[disease_lower])}"
        else:
            response_text = f"Sorry, I don’t have symptom info for {disease.title()}."

    elif intent_name == "CheckPreventionIntent":
        if disease_lower and disease_lower in preventions_data:
            response_text = f"Prevention tips for {disease.title()}: {', '.join(preventions_data[disease_lower])}"
        else:
            response_text = f"Sorry, I don’t have prevention info for {disease.title()}."

    elif intent_name == "CheckSynonymsIntent":
        if disease_lower and disease_lower in diseases_data:
            response_text = f"Synonyms for {disease.title()}: {', '.join(diseases_data[disease_lower])}"
        else:
            response_text = f"Sorry, I don’t have synonyms for {disease.title()}."

    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
