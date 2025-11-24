from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import re
from datetime import datetime
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Dining hall URLs
DINING_HALLS = {
    "Rheta's Market": "https://wisc-housingdining.nutrislice.com/menu/rhetas-market",
    "Gordon's Market": "https://wisc-housingdining.nutrislice.com/menu/gordon-avenue-market",
    "Carson's Market": "https://wisc-housingdining.nutrislice.com/menu/carsons-market",
    "Four Lakes Market": "https://wisc-housingdining.nutrislice.com/menu/four-lakes-market",
    "Lowell Market": "https://wisc-housingdining.nutrislice.com/menu/lowell-market",
    "Liz's Market": "https://wisc-housingdining.nutrislice.com/menu/lizs-market"
}

def get_mock_menu_data():
    """Provide realistic mock data when scraping fails"""
    return [
        # Rheta's Market
        {"hall": "Rheta's Market", "name": "Scrambled Eggs", "meal_period": "Breakfast", "category": "Hot Breakfast", 
         "calories": 180, "protein": 15, "carbs": 2, "fat": 12, "allergens": ["Eggs"], "dietary_labels": []},
        {"hall": "Rheta's Market", "name": "Turkey Sausage", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 120, "protein": 14, "carbs": 1, "fat": 7, "allergens": [], "dietary_labels": []},
        {"hall": "Rheta's Market", "name": "Oatmeal", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 150, "protein": 5, "carbs": 27, "fat": 3, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Rheta's Market", "name": "Greek Yogurt", "meal_period": "Breakfast", "category": "Dairy",
         "calories": 100, "protein": 17, "carbs": 6, "fat": 0, "allergens": ["Milk"], "dietary_labels": []},
        {"hall": "Rheta's Market", "name": "Grilled Chicken Breast", "meal_period": "Lunch", "category": "Entrees",
         "calories": 165, "protein": 31, "carbs": 0, "fat": 4, "allergens": [], "dietary_labels": []},
        {"hall": "Rheta's Market", "name": "Brown Rice", "meal_period": "Lunch", "category": "Grains",
         "calories": 215, "protein": 5, "carbs": 45, "fat": 2, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Rheta's Market", "name": "Steamed Broccoli", "meal_period": "Lunch", "category": "Vegetables",
         "calories": 55, "protein": 4, "carbs": 11, "fat": 0, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Rheta's Market", "name": "Baked Salmon", "meal_period": "Dinner", "category": "Entrees",
         "calories": 280, "protein": 35, "carbs": 0, "fat": 15, "allergens": ["Fish"], "dietary_labels": []},
        {"hall": "Rheta's Market", "name": "Quinoa", "meal_period": "Dinner", "category": "Grains",
         "calories": 220, "protein": 8, "carbs": 39, "fat": 4, "allergens": [], "dietary_labels": ["Vegan"]},
        
        # Gordon's Market
        {"hall": "Gordon's Market", "name": "Egg White Omelet", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 120, "protein": 25, "carbs": 2, "fat": 0, "allergens": ["Eggs"], "dietary_labels": []},
        {"hall": "Gordon's Market", "name": "Turkey Bacon", "meal_period": "Breakfast", "category": "Proteins",
         "calories": 60, "protein": 8, "carbs": 1, "fat": 3, "allergens": [], "dietary_labels": []},
        {"hall": "Gordon's Market", "name": "Fresh Fruit Cup", "meal_period": "Breakfast", "category": "Fruit",
         "calories": 80, "protein": 1, "carbs": 20, "fat": 0, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Gordon's Market", "name": "Grilled Tilapia", "meal_period": "Lunch", "category": "Seafood",
         "calories": 145, "protein": 30, "carbs": 0, "fat": 3, "allergens": ["Fish"], "dietary_labels": []},
        {"hall": "Gordon's Market", "name": "Sweet Potato", "meal_period": "Lunch", "category": "Vegetables",
         "calories": 180, "protein": 4, "carbs": 41, "fat": 0, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Gordon's Market", "name": "Garden Salad", "meal_period": "Lunch", "category": "Salads",
         "calories": 50, "protein": 2, "carbs": 10, "fat": 0, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Gordon's Market", "name": "Lean Beef Stir Fry", "meal_period": "Dinner", "category": "Entrees",
         "calories": 320, "protein": 35, "carbs": 15, "fat": 12, "allergens": ["Soy"], "dietary_labels": []},
        
        # Carson's Market
        {"hall": "Carson's Market", "name": "Protein Pancakes", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 220, "protein": 20, "carbs": 30, "fat": 4, "allergens": ["Eggs", "Milk", "Wheat"], "dietary_labels": []},
        {"hall": "Carson's Market", "name": "Cottage Cheese", "meal_period": "Breakfast", "category": "Dairy",
         "calories": 120, "protein": 14, "carbs": 6, "fat": 5, "allergens": ["Milk"], "dietary_labels": []},
        {"hall": "Carson's Market", "name": "Grilled Chicken Wrap", "meal_period": "Lunch", "category": "Sandwiches",
         "calories": 350, "protein": 32, "carbs": 35, "fat": 8, "allergens": ["Wheat"], "dietary_labels": []},
        {"hall": "Carson's Market", "name": "Black Bean Burger", "meal_period": "Lunch", "category": "Entrees",
         "calories": 250, "protein": 18, "carbs": 40, "fat": 5, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Carson's Market", "name": "Roasted Turkey Breast", "meal_period": "Dinner", "category": "Entrees",
         "calories": 160, "protein": 30, "carbs": 0, "fat": 4, "allergens": [], "dietary_labels": []},
        {"hall": "Carson's Market", "name": "Mashed Cauliflower", "meal_period": "Dinner", "category": "Vegetables",
         "calories": 80, "protein": 3, "carbs": 12, "fat": 2, "allergens": [], "dietary_labels": ["Vegetarian"]},
        
        # Four Lakes Market
        {"hall": "Four Lakes Market", "name": "Hard Boiled Eggs", "meal_period": "Breakfast", "category": "Proteins",
         "calories": 140, "protein": 12, "carbs": 1, "fat": 10, "allergens": ["Eggs"], "dietary_labels": []},
        {"hall": "Four Lakes Market", "name": "Steel Cut Oats", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 170, "protein": 7, "carbs": 29, "fat": 3, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Four Lakes Market", "name": "Tuna Salad", "meal_period": "Lunch", "category": "Salads",
         "calories": 200, "protein": 25, "carbs": 8, "fat": 8, "allergens": ["Fish"], "dietary_labels": []},
        {"hall": "Four Lakes Market", "name": "Lentil Soup", "meal_period": "Lunch", "category": "Soups",
         "calories": 180, "protein": 12, "carbs": 30, "fat": 2, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Four Lakes Market", "name": "Grilled Shrimp", "meal_period": "Dinner", "category": "Seafood",
         "calories": 140, "protein": 28, "carbs": 2, "fat": 2, "allergens": ["Shellfish"], "dietary_labels": []},
        {"hall": "Four Lakes Market", "name": "Wild Rice", "meal_period": "Dinner", "category": "Grains",
         "calories": 165, "protein": 6, "carbs": 35, "fat": 1, "allergens": [], "dietary_labels": ["Vegan"]},
        
        # Lowell Market
        {"hall": "Lowell Market", "name": "Veggie Omelet", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 200, "protein": 18, "carbs": 8, "fat": 12, "allergens": ["Eggs", "Milk"], "dietary_labels": ["Vegetarian"]},
        {"hall": "Lowell Market", "name": "Chicken Breast Strips", "meal_period": "Lunch", "category": "Proteins",
         "calories": 180, "protein": 35, "carbs": 0, "fat": 4, "allergens": [], "dietary_labels": []},
        {"hall": "Lowell Market", "name": "Roasted Vegetables", "meal_period": "Lunch", "category": "Vegetables",
         "calories": 110, "protein": 3, "carbs": 20, "fat": 3, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Lowell Market", "name": "Baked Cod", "meal_period": "Dinner", "category": "Seafood",
         "calories": 130, "protein": 28, "carbs": 0, "fat": 2, "allergens": ["Fish"], "dietary_labels": []},
        {"hall": "Lowell Market", "name": "Asparagus", "meal_period": "Dinner", "category": "Vegetables",
         "calories": 40, "protein": 4, "carbs": 8, "fat": 0, "allergens": [], "dietary_labels": ["Vegan"]},
        
        # Liz's Market
        {"hall": "Liz's Market", "name": "Protein Smoothie Bowl", "meal_period": "Breakfast", "category": "Breakfast",
         "calories": 280, "protein": 22, "carbs": 38, "fat": 6, "allergens": ["Milk"], "dietary_labels": []},
        {"hall": "Liz's Market", "name": "Tofu Scramble", "meal_period": "Breakfast", "category": "Hot Breakfast",
         "calories": 160, "protein": 15, "carbs": 8, "fat": 8, "allergens": ["Soy"], "dietary_labels": ["Vegan"]},
        {"hall": "Liz's Market", "name": "Grilled Chicken Salad", "meal_period": "Lunch", "category": "Salads",
         "calories": 240, "protein": 35, "carbs": 10, "fat": 7, "allergens": [], "dietary_labels": []},
        {"hall": "Liz's Market", "name": "Chickpea Bowl", "meal_period": "Lunch", "category": "Entrees",
         "calories": 320, "protein": 15, "carbs": 45, "fat": 10, "allergens": [], "dietary_labels": ["Vegan"]},
        {"hall": "Liz's Market", "name": "Herb Crusted Chicken", "meal_period": "Dinner", "category": "Entrees",
         "calories": 210, "protein": 32, "carbs": 4, "fat": 7, "allergens": [], "dietary_labels": []},
        {"hall": "Liz's Market", "name": "Brussels Sprouts", "meal_period": "Dinner", "category": "Vegetables",
         "calories": 70, "protein": 4, "carbs": 13, "fat": 1, "allergens": [], "dietary_labels": ["Vegan"]},
    ]

def scrape_nutrislice_menu(url, hall_name):
    """Scrape menu data from Nutrislice website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Extract the menu slug from URL
        slug = url.split('/menu/')[1]
        
        # Try the Nutrislice API v3 endpoint
        today = datetime.now().strftime('%Y-%m-%d')
        api_url = f"https://wisc-housingdining.nutrislice.com/menu/api/digest/school/uw-housing-dining/menu-type/{slug}/date/{today}/"
        
        print(f"Trying API URL: {api_url}")
        api_response = requests.get(api_url, headers=headers, timeout=15)
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"Successfully got API data for {hall_name}")
            return parse_nutrislice_api_v3(data, hall_name)
        else:
            print(f"API returned status {api_response.status_code} for {hall_name}")
            return []
            
    except Exception as e:
        print(f"Error scraping {hall_name}: {str(e)}")
        return []

def parse_nutrislice_api_v3(data, hall_name):
    """Parse Nutrislice API v3 response"""
    menu_items = []
    
    try:
        # The structure might be: data -> menu_periods -> categories -> menu_items
        menu_periods = data.get('menu_periods', [])
        
        for period in menu_periods:
            period_name = period.get('name', 'Unknown')
            categories = period.get('categories', [])
            
            for category in categories:
                category_name = category.get('name', 'Unknown')
                items = category.get('menu_items', [])
                
                for item in items:
                    food = item.get('food', {})
                    nutrition = food.get('rounded_nutrition_info', {})
                    
                    food_item = {
                        'hall': hall_name,
                        'name': food.get('name', 'Unknown'),
                        'meal_period': period_name,
                        'category': category_name,
                        'calories': nutrition.get('calories'),
                        'protein': nutrition.get('protein'),
                        'carbs': nutrition.get('carbs'),
                        'fat': nutrition.get('fat'),
                        'serving_size': food.get('serving_size'),
                        'allergens': [a.get('name') for a in food.get('allergens', [])],
                        'dietary_labels': [l.get('name') for l in food.get('dietary_labels', [])]
                    }
                    menu_items.append(food_item)
                    
        print(f"Parsed {len(menu_items)} items from {hall_name}")
    except Exception as e:
        print(f"Error parsing API data for {hall_name}: {str(e)}")
    
    return menu_items

def scrape_all_dining_halls():
    """Scrape all dining halls"""
    all_menus = []
    
    for hall_name, url in DINING_HALLS.items():
        print(f"Scraping {hall_name}...")
        items = scrape_nutrislice_menu(url, hall_name)
        all_menus.extend(items)
        print(f"Found {len(items)} items at {hall_name}")
    
    # If scraping failed completely, use mock data
    if len(all_menus) == 0:
        print("Scraping failed for all halls, using mock data...")
        all_menus = get_mock_menu_data()
    
    return all_menus

def generate_recommendations(menu_data, user_goals, alternative=False):
    """Generate meal recommendations using Google Gemini"""
    
    # Initialize Gemini
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "error": "GEMINI_API_KEY not set. Please set your API key in environment variables.",
            "recommendation_title": "Configuration Error",
            "dining_strategy": "API key missing"
        }
    
    genai.configure(api_key=api_key)
    
    # Prepare menu data for the prompt
    menu_text = json.dumps(menu_data[:100], indent=2)  # Limit to first 100 items to avoid token limits
    
    alternative_instruction = ""
    if alternative:
        alternative_instruction = """
        IMPORTANT: This is a request for an ALTERNATIVE recommendation. 
        You must provide a COMPLETELY DIFFERENT meal combination than what would be the most obvious choice.
        Choose different dining halls, different food items, and a different strategy while still meeting the goals.
        Be creative and offer variety!
        """
    
    prompt = f"""You are a nutrition expert helping UW-Madison students optimize their dining hall meals.

User's Nutritional Goals: {user_goals}

{alternative_instruction}

Available Menu Data from UW-Madison Dining Halls Today (sample):
{menu_text}

Please analyze this data and provide a detailed meal recommendation that meets the user's goals.

Your response MUST be ONLY valid JSON in the following format. Do not wrap it in markdown code blocks.
{{
    "recommendation_title": "A catchy title for this meal plan",
    "dining_strategy": "Brief overview of the strategy",
    "meals": [
        {{
            "dining_hall": "Name of dining hall",
            "meal_period": "Breakfast/Lunch/Dinner",
            "items": [
                {{
                    "name": "Food item name",
                    "quantity": "serving size or quantity",
                    "calories": 200,
                    "protein": 25,
                    "carbs": 30,
                    "fat": 5
                }}
            ]
        }}
    ],
    "total_nutrition": {{
        "calories": 2000,
        "protein": 100,
        "carbs": 200,
        "fat": 50
    }},
    "explanation": "Detailed explanation of how this meets the user's goals",
    "tips": ["Helpful tip 1", "Helpful tip 2"],
    "allergen_warnings": ["Any relevant allergen information"],
    "dietary_notes": ["Any dietary restriction notes"]
}}

Be specific with actual menu items from the data provided, realistic portions, and accurate nutritional calculations.
"""

    try:
        # Configure the model with JSON MIME type for structured output
        generation_config = {
            "temperature": 0.4, # Lowered slightly for more deterministic JSON
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        # Using a model from your available list
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
        )

        response = model.generate_content(prompt)
        
        # Clean up the response text before parsing
        # Sometimes models wrap JSON in markdown blocks even when asked not to
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        text_response = text_response.strip()
        
        return json.loads(text_response)
            
    except json.JSONDecodeError as je:
        print(f"JSON Decode Error: {str(je)}")
        print(f"Raw response text: {response.text if 'response' in locals() else 'No response'}")
        return {
            "error": f"Failed to parse AI response: {str(je)}",
            "recommendation_title": "Processing Error",
            "dining_strategy": "We received data but couldn't read it. Please try again.",
            "explanation": f"Raw text received (first 200 chars): {response.text[:200] if 'response' in locals() else 'None'}"
        }
    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        return {
            "error": str(e),
            "recommendation_title": "Error Generating Recommendation",
            "dining_strategy": "There was an error processing your request"
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape-menus', methods=['GET'])
def scrape_menus():
    """Endpoint to scrape all dining hall menus"""
    try:
        menus = scrape_all_dining_halls()
        return jsonify({
            'success': True,
            'data': menus,
            'count': len(menus)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Endpoint to generate recommendations"""
    try:
        data = request.json
        user_goals = data.get('goals', '')
        alternative = data.get('alternative', False)
        
        # Scrape menus
        menu_data = scrape_all_dining_halls()
        
        if len(menu_data) == 0:
            return jsonify({
                'success': False,
                'error': 'Could not retrieve menu data from any dining hall'
            }), 500
        
        # Generate recommendations
        recommendation = generate_recommendations(menu_data, user_goals, alternative)
        
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'menu_data_count': len(menu_data)
        })
    except Exception as e:
        print(f"Error in recommend endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)