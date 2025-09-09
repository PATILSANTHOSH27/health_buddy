from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your actual GitHub raw file URLs
DISEASES_URL = "https://raw.githubusercontent.com/<your-username>/<your-repo>/main/diseases.json"
SYMPTOMS_URL = "https://raw.githubusercontent.com/<your-username>/<your-repo>/main/symptoms.json"
PREVENTIONS_URL = "https://raw.githubusercontent.com/<your-username>/<your-repo>/main/disease_prevention.json"


def load_json_from_github(url):
    """Fetch JSON file from GitHub raw URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@app.route("/", methods=["POST"])
def webhook():
    """Dialogflow webhook to handle intents."""
    req = request.get_json(silent=True, force=True)
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})

    # Load data from GitHub
    diseases_data = load_json_from_github(DISEASES_URL)
    symptoms_data = load_json_from_github(SYMPTOMS_URL)
    preventions_data = load_json_from_github(PREVENTIONS_URL)

    response_text = "Sorry, I couldn’t find the information."

    # Handle CheckPreventionIntent
    if intent_name == "CheckPreventionIntent":
        disease = parameters.get("disease")
        if disease and disease in preventions_data:
            response_text = f"Prevention tips for {disease}: {', '.join(preventions_data[disease])}"
        else:
            response_text = f"Sorry, I don’t have prevention info for {disease}."

    # Handle CheckSymptomsIntent
    elif intent_name == "CheckSymptomsIntent":
        disease = parameters.get("disease")
        if disease and disease in symptoms_data:
            response_text = f"Common symptoms of {disease}: {', '.join(symptoms_data[disease])}"
        else:
            response_text = f"Sorry, I don’t have symptom info for {disease}."

    # Handle CheckSynonymsIntent
    elif intent_name == "CheckSynonymsIntent":
        disease = parameters.get("disease")
        if disease and disease in diseases_data:
            response_text = f"Synonyms for {disease}: {', '.join(diseases_data[disease])}"
        else:
            response_text = f"Sorry, I don’t have synonyms for {disease}."

    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
