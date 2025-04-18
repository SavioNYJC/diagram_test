import os
import base64
from openai import OpenAI
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize OpenAI client
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

@app.route('/')
def index():
    return "Backend API running"  # Simple message to show the server is working

@app.route("/process", methods=["POST"])
def process():
    try:
        # Check if files are in the request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        # Get image and text from request
        image = request.files['image']
        
        # Check if prompt is in the request
        if 'prompt' not in request.form:
            return jsonify({"error": "No prompt provided"}), 400
            
        text_input = request.form['prompt']

        # Validate image file
        if not image.filename:
            return jsonify({"error": "No image selected"}), 400

        # Encode the image into base64
        image_data = image.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # Build the prompt with additional instructions
        text_prompt = text_input + " Please provide a response that explains the graph in a straightforward manner, using only text and avoiding any formatting."

        # Send the API request to OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful analyst. Always explain things with clear logic, structured steps, and practical examples when needed."
                    },
                    {
                        "role": "user",
                        "content":[
                            { "type": "text", "text": text_prompt},
                            {
                                "type": "image_url",    
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,  
            )
            
            # Extract the response text correctly
            output_text = response.choices[0].message.content.strip()
            
            return jsonify({
                'message': 'Success!',
                'filename': image.filename,
                'prompt': text_input,
                'response': output_text
            })
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))