# -*- encoding: utf-8 -*-
from app import app, db 
from flask_cors import CORS, cross_origin

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
