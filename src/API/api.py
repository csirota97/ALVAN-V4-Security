from flask import Flask, render_template, Response, jsonify
import cv2
import socket

app = Flask(__name__)
camera=cv2.VideoCapture(0)
hostname = socket.gethostbyname(socket.gethostname())

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

@app.route("/networkScan")
def networkScan():

  response = jsonify( {"success": hostname})
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

if __name__ == "__main__":
  app.run(hostname, port=5001, debug=True)