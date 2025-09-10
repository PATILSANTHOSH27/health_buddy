from flask import Flask, request, jsonify
import requests, random

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
    disease_lower = disease.lower() if disease else None

    # Load JSON data from GitHub
    diseases_data = load_json_from_github(DISEASES_URL)
    symptoms_data = load_json_from_github(SYMPTOMS_URL)
    preventions_data = load_json_from_github(PREVENTIONS_URL)

    # Default response
    response_text = "Sorry, I couldn’t find the information."

    # Handle intents with 5–10 varied responses
    if intent_name == "CheckSymptomsIntent":
        if disease_lower and disease_lower in symptoms_data:
            symptoms = ", ".join(symptoms_data[disease_lower])
            responses = [
                f"Here are the common symptoms of {disease.title()}: {symptoms}.",
                f"People with {disease.title()} often show these symptoms: {symptoms}.",
                f"If you suspect {disease.title()}, watch out for: {symptoms}.",
                f"Typical signs of {disease.title()} include {symptoms}.",
                f"Symptoms linked to {disease.title()} are: {symptoms}.",
                f"Doctors usually notice these symptoms for {disease.title()}: {symptoms}.",
                f"Patients suffering from {disease.title()} may experience: {symptoms}.",
                f"Some warning signs of {disease.title()} are {symptoms}.",
                f"Here’s what usually happens in {disease.title()}: {symptoms}.",
                f"The following are indicators of {disease.title()}: {symptoms}."
            ]
            response_text = random.choice(responses)
        elif disease:
            response_text = f"Sorry, I don’t have symptom info for {disease.title()}."
        else:
            response_text = "Please tell me the disease name to check its symptoms."

    elif intent_name == "CheckPreventionIntent":
        if disease_lower and disease_lower in preventions_data:
            preventions = ", ".join(preventions_data[disease_lower])
            responses = [
                f"Prevention tips for {disease.title()}: {preventions}.",
                f"To reduce the risk of {disease.title()}, follow these steps: {preventions}.",
                f"Here’s how you can prevent {disease.title()}: {preventions}.",
                f"Avoid {disease.title()} by doing this: {preventions}.",
                f"Doctors recommend these measures against {disease.title()}: {preventions}.",
                f"These are some effective ways to avoid {disease.title()}: {preventions}.",
                f"Want to stay safe from {disease.title()}? Try: {preventions}.",
                f"To keep {disease.title()} away, follow: {preventions}.",
                f"Helpful prevention methods for {disease.title()} include: {preventions}.",
                f"Some protective steps against {disease.title()} are: {preventions}."
            ]
            response_text = random.choice(responses)
        elif disease:
            response_text = f"Sorry, I don’t have prevention info for {disease.title()}."
        else:
            response_text = "Please tell me the disease name to check prevention tips."

    elif intent_name == "CheckSynonymsIntent":
        if disease_lower and disease_lower in diseases_data:
            synonyms = ", ".join(diseases_data[disease_lower])
            responses = [
                f"Synonyms for {disease.title()} include: {synonyms}.",
                f"Other names for {disease.title()} are: {synonyms}.",
                f"You might also hear {disease.title()} called {synonyms}.",
                f"People often refer to {disease.title()} as {synonyms}.",
                f"{disease.title()} is also known as: {synonyms}.",
                f"Alternative terms for {disease.title()} are: {synonyms}.",
                f"In medical texts, {disease.title()} may be written as: {synonyms}.",
                f"Laypeople sometimes call {disease.title()} by names like: {synonyms}.",
                f"{disease.title()} can also be described as {synonyms}.",
                f"Some common nicknames for {disease.title()} are: {synonyms}."
            ]
            response_text = random.choice(responses)
        elif disease:
            response_text = f"Sorry, I don’t have synonyms for {disease.title()}."
        else:
            response_text = "Please tell me the disease name to check synonyms."

    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
