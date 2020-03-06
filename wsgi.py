# -*- encoding: utf-8 -*-
from app import app, db 
from flask_cors import CORS, cross_origin

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
    # socketio.run(app, host='0.0.0.0', port=3000, debug=True)  #cors_allowed_origins="*", 
