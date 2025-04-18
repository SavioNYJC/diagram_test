import os
import base64
from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin

client = OpenAI(
    api_key = os.environ['OPENAI_API_KEY']
)

app = Flask(__name__)
CORS(app, resources={r"/process": {"origins": "*"}})

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
@cross_origin()
def process():
    #Gets the relative (subject to change) image path. Include a better system in website in the future. (deprecated)
    #image_path = 'test_chart2.jpeg'
    
    image = request.files['image']
    text_input = request.form['prompt']

    if not image or not text_input:
        return jsonify({"error": "Missing image or prompt"}), 400

    #Encode the image into base64
    base64_image = base64.b64encode(image.read()).decode("utf-8")

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

    output_text = response.choices[0].message.content.strip()

    return jsonify({
        'message': 'Success!',
        'filename': image.filename,
        'prompt': text_input,
        'response': output_text
    })
