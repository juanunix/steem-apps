from flask import Blueprint, render_template, url_for, abort, request, jsonify
import re

# import API
from .api import extract_input
from .api import get_content

tagsearch = Blueprint("tagsearch", __name__)

@tagsearch.route('/')
def index():
	authors, tags = extract_input(request.args)

	content = get_content(authors, tags)

	return render_template('tagsearch/index.html', **content)

@tagsearch.route('/api/')
def api():
	try:
		authors, tags = extract_input(request.args)
	except:
		abort(404)

	return jsonify(get_content(authors, tags))

@tagsearch.route("/selected-authors")
def selected_authors():
	return render_template("tagsearch/selected_authors.html")

@tagsearch.route("/changelog")
def whats_new():
	return render_template("tagsearch/whats_new.html")
