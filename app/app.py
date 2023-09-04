from flask import Flask, send_file, render_template

import time
import os
import yaml

os.environ['TZ'] = "Europe/Berlin"
time.tzset()


with open("config/cameras.yaml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("camera config read successful")
#print(yaml)

app = Flask(__name__) 


@app.route('/',methods = ['POST', 'GET'])
def index():
    return render_template('index.html', config=config)

@app.route('/kantine')
def get_image():
    filename = 'static/kantine.jpg'
    return send_file(filename, mimetype='image/jpg')



# main driver function
if __name__ == '__main__':
    app.run()

