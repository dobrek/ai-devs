from flask import Flask, json, request

from .verify_flight import verify_flight


def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["POST"])
    def flight():
        data = json.loads(request.data)
        return {"description": verify_flight(data["instruction"])}

    return app


def run_server():
    app = create_app()
    app.run(port=5002)


if __name__ == "__main__":
    run_server()
