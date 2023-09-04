from flask import Flask, send_file, render_template

import time
import os
import yaml

os.environ['TZ'] = "Europe/Berlin"
time.tzset()

app = Flask(__name__) 


@app.route('/',methods = ['GET'])
def index():
    return render_template('index.html')


# main driver function
if __name__ == '__main__':
    app.run()

