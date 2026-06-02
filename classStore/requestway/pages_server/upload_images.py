from flask import request, jsonify
import json
import os
from datetime import datetime


class Upload:
    def __init__(self):
        print('success use upload')
        data = request.get_data()
        self.data = data

    def uploadImg(self, config):
        print('This is the uploadImg')

        data = json.loads(self.data)
        image_data = data.get('image')
        filename = data.get('filename', f'img_{datetime.now().timestamp()}.jpg')

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        upload_dir = os.path.join(os.path.dirname(__file__), '../../uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)

        try:
            with open(filepath, 'wb') as f:
                f.write(image_data.encode('utf-8'))
            return jsonify({'success': True, 'path': f'/uploads/{filename}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500