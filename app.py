from flask import Flask, request, jsonify
from PIL import Image
import requests
import os
import io
import time
from threading import Thread
from urllib.parse import urlparse

image_request_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.taobao.com/",
}

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/webptojpg', methods=['GET'])
def webptojpg():
    webp_url = request.args.get('webpurl')
    if not webp_url:
        return jsonify({'error': "Missing 'webpurl' parameter"}), 400

    try:
        parsed_url = urlparse(webp_url)
        original_filename = os.path.basename(parsed_url.path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        filename = f"{filename_without_ext}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(filepath):
            return jsonify({'filename': filename, 'status': 'already_exists'}), 200

        response = requests.get(webp_url, headers=image_request_headers)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))

        image.convert('RGB').save(filepath, format='JPEG')

        return jsonify({'filename': filename, 'status': 'success'}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Failed to download image: {str(e)}"}), 400
    except Exception as e:
        return jsonify({'error': f"Failed to process image: {str(e)}"}), 500

def cleanup_static_folder():
    while True:
        time.sleep(3600)
        try:
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Удалён файл: {file_path}")
        except Exception as e:
            print(f"Ошибка при очистке папки: {e}")

if __name__ == '__main__':
    cleanup_thread = Thread(target=cleanup_static_folder, daemon=True)
    cleanup_thread.start()

    app.run(host='0.0.0.0', port=5000)
