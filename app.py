from flask import Flask, jsonify, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/message', methods=['GET'])
def get_message():
    return jsonify({"message": "You get me"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
