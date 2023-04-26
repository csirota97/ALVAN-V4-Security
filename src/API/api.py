from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
import socket
import uuid
import pickle

try:
  with open('data.pickle', 'rb') as f:
    data = pickle.load(f)
    deviceKey = data['deviceKey']
    registered = data['registered']
    homeId = data['homeId']
except:
  deviceKey = str(uuid.uuid1())
  data = {
    'deviceKey': deviceKey,
    'homeId': None,
    'registered': False,
  }

  homeId = None
  registered = False

  with open('data.pickle', 'wb') as f:
    pickle.dump(data, f)

print(deviceKey)
app = Flask(__name__)
CORS(app)

try:
  camera=cv2.VideoCapture(0)
  print("Camera Started")
except:
  print("Could not start camera")

hostname = socket.gethostbyname(socket.gethostname())
hostname = "192.168.1.169"

def generate_frames():
  while True:
    success, frame = camera.read()
    if not success:
      break
    else:
      ret, buffer = cv2.imencode('.png', frame)
      frame = buffer.tobytes()
      # return frame

    yield(b'--frame\r\n' b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def index():
  return render_template('index.html')

@app.route("/video")
def video():
  return Response(generate_frames(),  mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/networkScan/<id>")
def networkScan(id):
  headers = ('Access-Control-Allow-Origin', '*')
  if not registered:
    return jsonify({'response': 'Device not registered', 'deviceKey': deviceKey, 'status': 401}), 401
  if id != homeId:
    return jsonify({'response':"User not authorized", 'deviceKey': deviceKey, 'status': 403}), 403

  response = jsonify( {"success": hostname, 'deviceKey': deviceKey, 'status': 200})
  return response
  # return Response(status=200, response=response)

@app.route("/register/<localHomeId>")
def registerDevice(localHomeId):
  global homeId, registered
  data = {
    'deviceKey': deviceKey,
    'homeId': localHomeId,
    'registered': True,
  }
  homeId = localHomeId
  registered = True

  with open('data.pickle', 'wb') as f:
    pickle.dump(data, f)


  return jsonify({'homeId': homeId, 'deviceKey': deviceKey, 'status': 200})


if __name__ == "__main__":
  app.run(hostname, port=5001, debug=False)
