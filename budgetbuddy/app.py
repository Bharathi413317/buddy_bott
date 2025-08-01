from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

# Set your Gemini API key
GOOGLE_API_KEY = "AIzaSyAukUcGVZpkYyqSAAQavvhnXD9JeHOk9nk"
genai.configure(api_key=GOOGLE_API_KEY)

# Create a Gemini model session
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

app = Flask(__name__)

# Basic investment tracking data
investment_data = {
    "monthly_investment": 0,
    "warning_threshold": 1000
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_message = request.json.get('message', '')
    user_message_lower = user_message.lower()
    response = ""

    # Check if message relates to investment amount
    if "investment" in user_message_lower:
        try:
            invest_amount = int("".join(filter(str.isdigit, user_message)))
            investment_data["monthly_investment"] = invest_amount
            response = f"Your monthly investment is ${invest_amount}. I will now track this for you."
        except ValueError:
            response = "Sorry, I couldn't understand the investment amount. Please specify a number."

    # Check for warning message
    elif "warning" in user_message_lower and investment_data["monthly_investment"] > 0:
        warning_threshold = investment_data["warning_threshold"]
        monthly_investment = investment_data["monthly_investment"]

        if monthly_investment < warning_threshold:
            response = f"<span class='warning-message'>Warning: Your monthly investment of ${monthly_investment} is below your recommended threshold of ${warning_threshold}. Consider increasing it.</span>"
        else:
            response = f"Your monthly investment of ${monthly_investment} is on track! Keep up the good work."

    # Else use Gemini model to give financial advice
    else:
        try:
            gemini_response = chat.send_message(user_message)
            response = gemini_response.text
        except Exception as e:
            response = f"Error fetching response from Gemini: {str(e)}"

    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)