from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Extract the data from the incoming request
    data = request.get_json()

    # Print the received data to the console
    print("Received data:", data)

    # Respond to acknowledge receipt of data
    return jsonify({"status": "success", "received_data": data})

if __name__ == '__main__':
    app.run(port=5050, host='0.0.0.0', debug=True)