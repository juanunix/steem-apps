from flask import Flask, url_for, request, render_template, redirect, abort

app = Flask(__name__)

# import apps
from tagsearch.app import tagsearch

# register apps
app.register_blueprint(tagsearch, url_prefix="/tagsearch")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
    )
    app.run()
