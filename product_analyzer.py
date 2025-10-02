from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

# Mock Product Data
MOCK_PRODUCTS = [
    {"name": "Dell XPS 13 Laptop", "store": "TechMart", "price": 899, "category": "Laptops"},
    {"name": "HP Pavilion 15 Laptop", "store": "ElectroHub", "price": 649, "category": "Laptops"},
    {"name": "MacBook Air M2", "store": "Apple Store", "price": 1199, "category": "Laptops"},
    {"name": "Lenovo ThinkPad X1", "store": "BusinessTech", "price": 1050, "category": "Laptops"},
    {"name": "Samsung Galaxy S23 Phone", "store": "MobileWorld", "price": 799, "category": "Phones"},
    {"name": "iPhone 14 Pro Phone", "store": "Apple Store", "price": 999, "category": "Phones"},
    {"name": "Google Pixel 7 Phone", "store": "TechMart", "price": 599, "category": "Phones"},
    {"name": "OnePlus 11 Phone", "store": "ElectroHub", "price": 699, "category": "Phones"},
    {"name": "Sony WH-1000XM5 Headphones", "store": "AudioPro", "price": 399, "category": "Headphones"},
    {"name": "Bose QuietComfort 45 Headphones", "store": "SoundCity", "price": 329, "category": "Headphones"},
    {"name": "Apple AirPods Max Headphones", "store": "Apple Store", "price": 549, "category": "Headphones"},
    {"name": "JBL Live 660NC Headphones", "store": "AudioPro", "price": 149, "category": "Headphones"},
    {"name": "LG UltraWide Monitor 34\"", "store": "DisplayWorld", "price": 449, "category": "Monitors"},
    {"name": "Dell U2723DE Monitor 27\"", "store": "TechMart", "price": 599, "category": "Monitors"},
]

API_KEY = "AIzaSyBKYR9YJwfQlslbnQz8pvZuzt2oHo1fGcw"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Analyzer & Price Comparator</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen py-8 px-4">
    <div class="max-w-5xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-indigo-900 mb-2">Product Analyzer</h1>
            <p class="text-gray-600 text-lg">AI-Powered Shopping Assistant & Price Comparator</p>
        </div>

        <!-- Main Card -->
        <div class="bg-white rounded-2xl shadow-xl p-8 mb-6">
            <form id="analyzerForm" class="space-y-6">
                <!-- Requirements Input -->
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                        Your Requirements
                    </label>
                    <textarea 
                        id="requirements" 
                        name="requirements"
                        rows="4"
                        placeholder="Example: I need a durable phone for hiking with great battery life, maximum budget $300"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                        required
                    ></textarea>
                </div>

                <!-- Budget Input -->
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                        Maximum Budget ($)
                    </label>
                    <input 
                        type="number" 
                        id="budget" 
                        name="budget"
                        placeholder="500"
                        min="0"
                        step="1"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        required
                    />
                </div>

                <!-- Submit Button -->
                <button 
                    type="submit"
                    class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 shadow-lg hover:shadow-xl"
                >
                    Analyze Products
                </button>
            </form>
        </div>

        <!-- Loading Indicator -->
        <div id="loading" class="hidden text-center py-8">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p class="mt-4 text-gray-600">Analyzing your requirements...</p>
        </div>

        <!-- Results Section -->
        <div id="results" class="hidden space-y-6">
            <!-- AI Analysis -->
            <div class="bg-white rounded-2xl shadow-xl p-8">
                <h2 class="text-2xl font-bold text-indigo-900 mb-4 flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                    AI Expert Recommendation
                </h2>
                <div id="aiAnalysis" class="text-gray-700 leading-relaxed bg-indigo-50 p-6 rounded-lg"></div>
            </div>

            <!-- Price Comparison -->
            <div class="bg-white rounded-2xl shadow-xl p-8">
                <h2 class="text-2xl font-bold text-indigo-900 mb-4 flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                    Available Products
                </h2>
                <div id="productList" class="space-y-3"></div>
                <div id="noProducts" class="hidden text-center py-8 text-gray-500">
                    No products found matching your budget and requirements.
                </div>
            </div>
        </div>

        <!-- Error Message -->
        <div id="error" class="hidden bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg"></div>
    </div>

    <script>
        document.getElementById('analyzerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const requirements = document.getElementById('requirements').value;
            const budget = document.getElementById('budget').value;
            
            // Show loading, hide results and errors
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('results').classList.add('hidden');
            document.getElementById('error').classList.add('hidden');
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        requirements: requirements,
                        budget: parseFloat(budget)
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Display AI Analysis
                document.getElementById('aiAnalysis').textContent = data.ai_analysis;
                
                // Display Products
                const productList = document.getElementById('productList');
                const noProducts = document.getElementById('noProducts');
                
                if (data.products.length > 0) {
                    productList.innerHTML = data.products.map(product => `
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-200">
                            <div class="flex justify-between items-start">
                                <div class="flex-1">
                                    <h3 class="font-semibold text-lg text-gray-800">${product.name}</h3>
                                    <p class="text-sm text-gray-500 mt-1">${product.store} • ${product.category}</p>
                                </div>
                                <div class="text-right">
                                    <p class="text-2xl font-bold text-indigo-600">$${product.price}</p>
                                </div>
                            </div>
                        </div>
                    `).join('');
                    productList.classList.remove('hidden');
                    noProducts.classList.add('hidden');
                } else {
                    productList.classList.add('hidden');
                    noProducts.classList.remove('hidden');
                }
                
                // Show results
                document.getElementById('results').classList.remove('hidden');
                
            } catch (error) {
                document.getElementById('error').textContent = 'Error: ' + error.message;
                document.getElementById('error').classList.remove('hidden');
            } finally {
                document.getElementById('loading').classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""

def call_gemini_api(user_requirements):
    """Call Gemini API with Google Search grounding"""
    if not API_KEY:
        return "API key not configured. Please add your Gemini API key to use AI analysis."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
    
    system_instruction = "You are a professional product analyst and shopping advisor. Based on the user's requirements and budget, provide a single, detailed paragraph recommending the specific product type or features they should prioritize, explaining why. Do not mention price comparison, just give advice."
    
    payload = {
        "contents": [{
            "parts": [{"text": user_requirements}]
        }],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "tools": [{
            "google_search": {}
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Unable to generate analysis. Please try again."
    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

def find_matching_products(requirements, max_budget):
    """Find products matching user requirements and budget"""
    requirements_lower = requirements.lower()
    
    # Extract keywords from requirements
    keywords = ['laptop', 'phone', 'headphone', 'monitor', 'computer', 'mobile', 'audio', 'display']
    detected_keywords = [kw for kw in keywords if kw in requirements_lower]
    
    # Filter products
    matching_products = []
    for product in MOCK_PRODUCTS:
        # Check if product is within budget
        if product['price'] > max_budget:
            continue
        
        # Check if product matches any keyword
        product_name_lower = product['name'].lower()
        if any(kw in product_name_lower for kw in detected_keywords):
            matching_products.append(product)
    
    # Sort by price
    matching_products.sort(key=lambda x: x['price'])
    
    return matching_products

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        requirements = data.get('requirements', '')
        budget = data.get('budget', 0)
        
        if not requirements or budget <= 0:
            return jsonify({'error': 'Please provide valid requirements and budget'}), 400
        
        # Get AI analysis from Gemini
        ai_analysis = call_gemini_api(f"User requirements: {requirements}. Maximum budget: ${budget}")
        
        # Find matching products
        products = find_matching_products(requirements, budget)
        
        return jsonify({
            'ai_analysis': ai_analysis,
            'products': products
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
