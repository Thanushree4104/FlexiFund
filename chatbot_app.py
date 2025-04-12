from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Define possible responses for each option
def get_chatbot_response(user_input):
    responses = {
        "📘 Learn About Micro-Loan Finance": {
            "response": "Micro-loans are small, unsecured loans that are designed to empower individuals or small businesses. They don’t require collateral and are intended to help those who don’t have access to traditional banking services.",
            "options": [
                "❓ What is a Micro-Loan?",
                "💸 How is it Different from Normal Loans?",
                "🧾 Eligibility Criteria",
                "⬅️ Back to Main Menu"
            ]
        },
        "💡 Advantages of Micro-Loan Finance": {
            "response": "Micro-loans offer numerous benefits including financial empowerment for underserved communities, opportunities for business growth, and promoting community development.",
            "options": [
                "💪 Financial Empowerment",
                "📈 Business Growth",
                "🤝 Community Development",
                "⬅️ Back to Main Menu"
            ]
        },
        "⚠️ Risk Factors of Micro-Loan Finance": {
            "response": "Some risks of micro-loans include borrower default risk, over-indebtedness, and regulatory challenges that can hinder access to these loans.",
            "options": [
                "📉 Borrower Default Risk",
                "💔 Over-Indebtedness",
                "⚖️ Regulatory Challenges",
                "⬅️ Back to Main Menu"
            ]
        },
        "❓ What is a Micro-Loan?": {
            "response": "A micro-loan is a small loan, usually under $1,000, given to an individual or small business to support entrepreneurship or alleviate poverty. These loans typically don’t require collateral.",
            "options": [
                "💸 How is it Different from Normal Loans?",
                "🧾 Eligibility Criteria",
                "⬅️ Back to Main Menu"
            ]
        },
        "💸 How is it Different from Normal Loans?": {
            "response": "Unlike traditional loans, micro-loans don't require collateral. They're also aimed at helping low-income individuals or small businesses who may not have access to conventional banking.",
            "options": [
                "❓ What is a Micro-Loan?",
                "🧾 Eligibility Criteria",
                "⬅️ Back to Main Menu"
            ]
        },
        "🧾 Eligibility Criteria": {
            "response": "Eligibility criteria for micro-loans typically include having a viable business idea or being in need of financial support. Lenders look at your ability to repay, and not your credit score.",
            "options": [
                "❓ What is a Micro-Loan?",
                "💸 How is it Different from Normal Loans?",
                "⬅️ Back to Main Menu"
            ]
        },
        "💪 Financial Empowerment": {
            "response": "Micro-loans empower individuals by providing them the capital to start or grow their businesses, even if they lack collateral or credit history.",
            "options": [
                "📈 Business Growth",
                "🤝 Community Development",
                "⬅️ Back to Main Menu"
            ]
        },
        "📈 Business Growth": {
            "response": "Micro-loans allow small businesses to grow by providing access to working capital that would otherwise be unavailable through traditional banking methods.",
            "options": [
                "💪 Financial Empowerment",
                "🤝 Community Development",
                "⬅️ Back to Main Menu"
            ]
        },
        "🤝 Community Development": {
            "response": "Micro-loans foster community development by promoting entrepreneurship, creating jobs, and empowering individuals to contribute to the economy.",
            "options": [
                "💪 Financial Empowerment",
                "📈 Business Growth",
                "⬅️ Back to Main Menu"
            ]
        },
        "📉 Borrower Default Risk": {
            "response": "If a borrower defaults, it can affect the lender’s ability to recover the loan, leading to financial losses.",
            "options": [
                "💔 Over-Indebtedness",
                "⚖️ Regulatory Challenges",
                "⬅️ Back to Main Menu"
            ]
        },
        "💔 Over-Indebtedness": {
            "response": "Borrowers may face over-indebtedness if they take on too many loans, which could impact their ability to repay.",
            "options": [
                "📉 Borrower Default Risk",
                "⚖️ Regulatory Challenges",
                "⬅️ Back to Main Menu"
            ]
        },
        "⚖️ Regulatory Challenges": {
            "response": "Regulatory challenges include lack of regulation in some regions, which can make it harder for borrowers to access loans and for lenders to manage risk.",
            "options": [
                "📉 Borrower Default Risk",
                "💔 Over-Indebtedness",
                "⬅️ Back to Main Menu"
            ]
        },
        "⬅️ Back to Main Menu": {
            "response": "What would you like to learn more about?",
            "options": [
                "📘 Learn About Micro-Loan Finance",
                "💡 Advantages of Micro-Loan Finance",
                "⚠️ Risk Factors of Micro-Loan Finance"
            ]
        },
        "Exit": {
            "response": "Thank you for chatting with us! We hope you found the information helpful.",
            "options": []
        }
    }

    # Get the response for the user's input
    return responses.get(user_input)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json['message']
    response = get_chatbot_response(user_input)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
