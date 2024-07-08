from flask import Flask, jsonify, Response, request
from prometheus_client import Counter, generate_latest, start_http_server

app = Flask(__name__)
REQUEST_COUNTER = Counter(
    "http_requests_total", "Total number of HTTP requests", ["status_code"]
)


# Change response output based on the input message
@app.route("/")
def index():

    # Get message sent to API
    flag = request.args.get("flag")
    if flag == "1":
        REQUEST_COUNTER.labels(status_code="200").inc()
        return jsonify({"message": "OK"}), 200
    else:
        REQUEST_COUNTER.labels(status_code="429").inc()
        return jsonify({"message": "Too Many Requests"}), 429


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")


if __name__ == "__main__":
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    # Run the Flask app on port 5000
    app.run(host="0.0.0.0", port=5000)
