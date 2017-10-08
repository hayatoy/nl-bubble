# -*- coding: utf-8 -*-
# admin page 
from google.appengine.api.app_identity import get_application_id
from flask import Flask, render_template
app = Flask(__name__)


@app.route('/admin')
def adminpage():
    app_id = get_application_id()
    return render_template("admin.html", app_id=app_id)
