import pandas as pd

def compute_credit_score_from_file(file_path):
    # Load data from a comma-separated TXT file
    df = pd.read_csv(file_path)

    # Define score weights
    weights = {
        "monthly_surplus": 0.3,
        "financial_diversity": 0.2,
        "merchant_txns": 0.2,
        "geo_stability": 0.15,
        "business_docs": 0.15
    }

    scores = []

    for index, row in df.iterrows():
        monthly_surplus_score = min(row["monthly_surplus"] / 10000, 1.0) * 100
        financial_diversity_score = row["financial_diversity"] * 20
        merchant_txns_score = min(row["merchant_txns"] / 20, 1.0) * 100
        geo_stability_score = 100 if row["geo_stability"] == 1 else 50
        business_docs_score = 100 if row["business_docs"] == 1 else 50

        final_score = (
            monthly_surplus_score * weights["monthly_surplus"]
            + financial_diversity_score * weights["financial_diversity"]
            + merchant_txns_score * weights["merchant_txns"]
            + geo_stability_score * weights["geo_stability"]
            + business_docs_score * weights["business_docs"]
        )

        scores.append({
            "user_id": row["user_id"],
            "credit_score": round(final_score, 2)
        })

    return scores

# Example usage
file_path = "data.txt"  # make sure this is your actual text file path
result = compute_credit_score_from_file(file_path)

for r in result:
    print(f"User {r['user_id']} - Credit Score: {r['credit_score']}")
