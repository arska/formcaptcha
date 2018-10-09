"""
Show google recaptcha challenge for form submissions matching simple heuristics
"""

import os
import logging
from flask import Flask, request, render_template, redirect
from werkzeug.urls import url_encode
from dotenv import load_dotenv
import requests


APP = Flask(__name__)
APP.config["RECAPTCHA_SITE_KEY"] = os.environ.get("RECAPTCHA_SITE_KEY")
APP.config["RECAPTCHA_SECRET_KEY"] = os.environ.get("RECAPTCHA_SECRET_KEY")

LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)


@APP.route("/", methods=["GET", "POST"])
def captcha():
    """
    test form submission and show captcha. redirect if successful
    """
    if request.method == "GET":
        form = request.args
    else:
        form = request.form

    logging.debug(form)

    filteredform = form.copy()
    filteredform.pop("g-recaptcha-response", None)
    redirecturl = (
        os.environ.get("REDIRECT_URL", "/") + "?" + url_encode(filteredform)
    )

    # simple heuristic to determine if captcha needs to be shown
    if (
        form.get("q1_control_fname", False)
        and form.get("q3_control_lname", False)
        and not form.get("q1_control_fname") == form.get("q3_control_lname")
    ):
        return redirect(redirecturl)

    if form.get("g-recaptcha-response"):
        if verifycaptcha(response=form.get("g-recaptcha-response")):
            return redirect(redirecturl)

    return render_template("template.html", form=filteredform)


def verifycaptcha(response, remote_ip=None):
    """
    verify a google recaptcha response
    """
    data = {
        "secret": APP.config["RECAPTCHA_SECRET_KEY"],
        "response": response,
        "remoteip": remote_ip or request.environ.get("REMOTE_ADDR"),
    }
    resp = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", data=data
    )
    content = resp.json()
    logging.debug(content)
    return (
        content["success"]
        or content["error-codes"][0] == "timeout-or-duplicate"
        and resp.status_code == 200
    )


if __name__ == "__main__":
    load_dotenv()
    APP.run(host="0.0.0.0", port=os.environ.get("listenport", 8080))
