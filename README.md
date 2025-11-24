# Badger Meal Optimizer

A web application that helps UW-Madison students optimize their dining hall meal choices based on personalized nutritional goals. The app scrapes real-time menu data from all UW-Madison dining halls and uses Google Gemini AI to generate customized meal recommendations.

## Features

- Real-time menu data from 6 UW-Madison dining halls
- AI-powered meal recommendations based on your nutritional goals
- Detailed nutritional breakdowns (calories, protein, carbs, fat)
- Alternative meal plan suggestions
- Allergen and dietary restriction information
- Mobile-responsive design with UW-Madison branding

## Supported Dining Halls

- Rheta's Market
- Gordon's Market
- Carson's Market
- Four Lakes Market
- Lowell Market
- Liz's Market

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- pip (Python package manager)

## Installation

1. Clone or download the repository:
```bash
cd /path/to/badgerMeal
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up your API key:
   - Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file and add your API key using the terminal:
     ```bash
     echo "GEMINI_API_KEY=your_actual_api_key" > .env
     ```
   - Replace `your_actual_api_key` with your real API key from Google
   - Example:
     ```bash
     echo "GEMINI_API_KEY=AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ" > .env
     ```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter your nutritional goals in the text area. Examples:
   - "I wanna get 100g of protein today, low-fat diet, under 2500 calories"
   - "High protein, vegetarian, around 2000 calories"
   - "Low carb diet, 150g protein, under 1800 calories"

4. Click "Get My Meal Plan" to receive personalized recommendations

5. Use "Show Me An Alternative Plan" to get different meal combinations that still meet your goals

## How It Works

1. **Menu Scraping**: The app fetches real-time menu data from UW-Madison's Nutrislice API for all dining halls
2. **AI Analysis**: Google Gemini AI analyzes the available menu items against your nutritional goals
3. **Recommendation Generation**: The AI creates a complete meal plan with specific items, portions, and nutritional breakdowns
4. **Display**: Results are presented in an easy-to-read format with total nutrition, explanations, and helpful tips

## Project Structure

```
badgerMeal/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env                      # Environment variables (API key) - create this file
├── templates/
│   ├── index.html           # Frontend UI
│   └── EyeNotifier/         # Separate eye reminder application
└── venv/                    # Virtual environment (created during setup)
```

**Note**: The `.env` file is not included in the repository for security reasons. You need to create it during setup (see Installation section).

## API Endpoints

- `GET /` - Main web interface
- `GET /api/scrape-menus` - Fetch current menu data from all dining halls
- `POST /api/recommend` - Generate meal recommendations
  - Request body: `{ "goals": "your nutritional goals", "alternative": false }`

## Troubleshooting

### "GEMINI_API_KEY not set" Error
- Make sure you've created a `.env` file with your API key
- Verify the API key is valid and active

### No Menu Data Retrieved
- The app includes fallback mock data if scraping fails
- Check your internet connection
- UW-Madison dining hall websites may be temporarily unavailable

### Port Already in Use
- Change the port in `app.py` (line 383):
  ```python
  app.run(debug=True, port=5001)  # Use a different port
  ```

## Dependencies

- Flask 3.0.0 - Web framework
- flask-cors 4.0.0 - Cross-origin resource sharing
- requests 2.31.0 - HTTP library
- beautifulsoup4 4.12.2 - HTML parsing
- google-generativeai - Google Gemini AI SDK
- python-dotenv 1.2.1 - Environment variable management
- lxml 4.9.3 - XML/HTML processing

## Development Notes

- The app uses Google Gemini 2.5 Flash for fast and cost-effective AI generation
- Menu data is scraped on-demand for each request to ensure freshness
- Mock data is available as a fallback if scraping fails
- The UI is built with vanilla JavaScript and responsive CSS

## Limitations

- Menu data availability depends on UW-Madison dining services' website uptime
- API rate limits may apply based on your Google Gemini API tier
- Nutritional data accuracy depends on the source data from dining halls

## Future Enhancements

- Save favorite meal plans
- Export meal plans to calendar
- Meal plan history tracking
- Support for dietary restrictions and allergies filters
- Meal plan comparison features
- Multi-day meal planning

## License

This project is for educational purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Contact

For questions or support, please open an issue in the repository.
