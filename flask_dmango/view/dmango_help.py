#-*- coding: utf-8 -*-
from flask import request, Blueprint, render_template
dmango_help = Blueprint('dmango_help', __name__, template_folder='../templates', static_folder='../static_folder')

@dmango_help.route('/')
def index():
    return render_template('dmango/index.html')