from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/rank', methods=['POST'])
def summarize_text():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        timestamp = data.get("timestamp")
        key_types = data.get("key_types", []) 
        raw_transcript = data.get("raw_transcript")

        if not raw_transcript:
            return jsonify({"error": "Transcript is missing"}), 400

        summary = "this is the sumary"
        response = {
            "user_id": user_id,
            "timestamp": timestamp,
            "key_types": key_types,
            "summarized_transcript": summary
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
