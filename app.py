from flask import Flask
import google.generativeai as genai
import os 
import json
genai.configure(api_key=os.environ['GEM_KEY'])


app = Flask(__name__)

def upload_file(path,mime_type=None):
    file = genai.upload_file(path=path,mime_type=mime_type)
    return file

generation_config = {
    "temperature":1,
    "top_p":0.95,
    "top_k":40,
    "max_output_tokens":8192,
    "response_mime_type":"text/plain"
}
model=genai.GenerativeModel(model_name="gemini-2.0-flash",generation_config=generation_config)

@app.route("/",methods=["GET"])
def myapp():
    files=[upload_file("output_image.jpg",mime_type="image/jpg")]
    response = model.generate_content([
        files[0],
        "extract only the text from image",
        "Image:omit any comment"
    ])
       

    return response.text

if __name__ == "__main__":
    app.run()