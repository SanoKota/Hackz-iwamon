"""Simple Flask app template

Run with:
  pip install flask
  python -m template.flask.app

The app serves `templates/index.html` and `static/style.css`.
"""
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def index():
    return render_template("index.html", title="Gemini Template")


@app.route("/run_gemini")
def run_gemini_route():
    """Trigger Gemini run and render result on the page."""
    try:
        # import here so that template package imports resolve relative to project root
        from template.gemini.run_gemini import run_gemini as run_gemini_func
    except Exception as e:
        result = f"Import error: {e}"
    return render_template("index.html", title="Gemini Template", result=result)

    try:
        result = run_gemini_func()
    except Exception as e:
        result = f"Runtime error: {e}"

        return render_template("index.html", title="Gemini Template", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
