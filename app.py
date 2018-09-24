"""
Show google recaptcha challenge for form submissions matching simple heuristics
"""

import os
import pprint
from flask import Flask, request, render_template
from dotenv import load_dotenv
from flask_google_recaptcha import GoogleReCaptcha


APP = Flask(__name__)  # Standard Flask app
APP.config["RECAPTCHA_SITE_KEY"] = os.environ.get("RECAPTCHA_SITE_KEY")
APP.config["RECAPTCHA_SECRET_KEY"] = os.environ.get("RECAPTCHA_SECRET_KEY")
RECAPTCHA = GoogleReCaptcha(app=APP)


@APP.route("/", methods=["GET", "POST"])
def hello():
    """
    Hello world on root path
    """
    if request.method == "GET":
        form = request.args
    else:
        form = request.form

    if form.get("g-recaptcha-response"):
        if RECAPTCHA.verify(response=form.get("g-recaptcha-response")):
            return "success"
    return render_template("template.html", form=form)


if __name__ == "__main__":
    load_dotenv()
    APP.run(host="0.0.0.0", port=os.environ.get("listenport", 8080))
