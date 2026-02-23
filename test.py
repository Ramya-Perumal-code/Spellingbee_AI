from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Recipe Dataset
# -----------------------------
recipes = [
    {
        "name": "Tomato Onion Curry",
        "ingredients": "tomato onion garlic oil salt",
        "diet": "vegetarian"
    },
    {
        "name": "Chicken Fried Rice",
        "ingredients": "chicken rice onion soy sauce oil",
        "diet": "non-vegetarian"
    },
    {
        "name": "Vegetable Salad",
        "ingredients": "cucumber tomato carrot lettuce salt",
        "diet": "vegan"
    },
    {
        "name": "Garlic Rice",
        "ingredients": "rice garlic oil salt",
        "diet": "vegetarian"
    }
]

# -----------------------------
# User Input
# -----------------------------
user_ingredients = input("Enter available ingredients (comma separated): ")
user_ingredients = user_ingredients.replace(",", " ")

# -----------------------------
# Prepare Data
# -----------------------------
recipe_texts = [recipe["ingredients"] for recipe in recipes]
print(recipe_texts)
recipe_texts.append(user_ingredients)
print(recipe_texts) 

# -----------------------------
# TF-IDF Vectorization
# -----------------------------
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(recipe_texts)

# -----------------------------
# Cosine Similarity
# -----------------------------
similarity_scores = cosine_similarity(
    tfidf_matrix[-1],  # user input
    tfidf_matrix[:-1]  # recipes
)[0]

# -----------------------------
# Display Results
# -----------------------------
print("\nRecommended Recipes:\n")

for index, score in enumerate(similarity_scores):
    if score > 0:
        print(f"🍽 {recipes[index]['name']}  | Match Score: {round(score, 2)}")

if max(similarity_scores) == 0:
    print("❌ No matching recipes found.")
