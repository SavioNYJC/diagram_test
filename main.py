import os
import base64
from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

client = OpenAI(
    api_key = os.environ['OPENAI_API_KEY']
)

app = Flask(__name__)
CORS(app)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    #Gets the relative (subject to change) image path. Include a better system in website in the future. (deprecated)
    #image_path = 'test_chart2.jpeg'
    
    image = request.files['image']
    text_input = request.form['prompt']

    if not image or not prompt:
        return jsonify({"error": "Missing image or prompt"}), 400

    #Encode the image into base64
    base64_image = encode_image(image)

    #Gets the text prompt. Adds some parameters to the prompt.
    text_prompt = text_input + "Please provide a response that explains the graph in a straightforward manner, using only text and avoiding any formatting."

    #Sends the api request for the AI.
    response = client.chat.completions.create(
        model = "gpt-4o",
        temperature = 0.3,
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
        max_tokens = 500,  
    )

    output_text = resposne.choices[0].text.strip()

    return jsonify({
        "message": output_text,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Flask runs by default on port 5000
