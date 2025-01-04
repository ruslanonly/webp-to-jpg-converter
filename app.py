from flask import Flask, request, send_file
from PIL import Image
import requests
import io

app = Flask(__name__)

@app.route('/webptojpg', methods=['GET'])
def webptojpg():
    webp_url = request.args.get('webpurl')
    if not webp_url:
        return "Missing 'webpurl' parameter", 400
    
    response = requests.get(webp_url)

    error_counter = 0

    while response.status_code >= 400:
        error_counter += 1
        if error_counter == 3:
            return "Failed to download image", response.status_code

        time.sleep(1)
        webp_url = request.args.get('webpurl')
        response = requests.get(webp_url)

    
    image = Image.open(io.BytesIO(response.content))
    img_byte_arr = io.BytesIO()
    image.convert('RGB').save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/jpeg', as_attachment=True, download_name='converted.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
