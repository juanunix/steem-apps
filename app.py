from steemdata import SteemData

from flask import Flask, url_for, request, render_template, jsonify
import re
import json

app = Flask(__name__)


# Loading papa-pepper tags
# Before: 31-28 = 3s
# After: <1s


@app.route("/")
def index():
	try:
		authors = re.findall(r"[\w-]+", request.args['author'])
		tags = re.findall(r"[\w-]+", request.args['tag'])
	except KeyError:
		return render_template("index.html")

	
	
	if not authors:
		if tags:
			# render selected authors.

			# load selected authors
			with open("selected_authors.json", "r") as selected_authors_file:
				data = json.load(selected_authors_file)

				selected_authors = []
				try:
					selected_authors.extend(data["all_tags"])
				except:
					pass

				for tag in tags:
					try:
						selected_authors.extend(data[tag])
					except:
						pass 

			s = SteemData()
			selected_authers_posts = s.Posts.find({
				"author": {"$in": selected_authors}, 
				"tags":{"$in": tags}
			}).sort([("created", -1)])

			posts = []
			for post in selected_authers_posts:
				post_payload = {
					"url" : "https://steemit.com"+post["url"],
					"net_votes" : post["net_votes"],
					"title" : post["root_title"],
					"author" : post["author"]
				}

				try: 
					image = post["json_metadata"]["image"]
				except KeyError:
					image = False

				if image:
					post_payload["image_url"] = image
					
				posts.append(post_payload)

			notification = False
			if not posts:
				notification = {
				"text": """<p>Sorry. There's currently no <b>featured authors</b> for '%s'.</p>
				<p><a href="%s" target="_blank"><b>Become a featured writer.</b></a></p>""" %(", ".join(tags), url_for("selected_authors")),
				"class": "is-info"
				}
			return render_template("index.html", posts=posts, tag=" ".join(tags), showing_selected_authors=True, notification = notification)
		else:
			# Render failed search page
			return render_template("index.html", notification={"text":"""<p>Oops. That was embarrassing.</p><p>Your search criteria didn't yield any results.</p>""",
																"class":"is-danger"})



	# get steemit connection
	s = SteemData()
	


	# render tag explorer if no tag is given
	if not tags:
		author_tags = s.Posts.aggregate([
			{"$match": {"author": authors[0]}},
			{"$project": {"tags":1}},
			{"$unwind": "$tags"},
			{"$group": { "_id": '$tags', "count" : {"$sum" : 1}}},
			{"$sort": {"count" : -1}}
		])

		notification = False
		if len(authors) > 1:
			notification = {"text":"<p>TagCloud doesn't yet support multiple authors.</p><p>Showing results for '%s' only.</p>" %(authors[0]),
			"class": "is-danger"
			}
		return render_template("index.html", all_author_tags=author_tags, author=" ".join(authors), notification=notification)


	# render posts with tag by author if both are given
	author_posts = s.Posts.find({
		"author": {"$in": authors}, 
		"tags":{"$in": tags}
	}).sort([("created", -1)])

	posts = []
	for post in author_posts:
		post_payload = {
			"url" : "https://steemit.com"+post["url"],
			"net_votes" : post["net_votes"],
			"title" : post["root_title"],
			"author" : post["author"]
		}

		try: 
			image = post["json_metadata"]["image"]
		except KeyError:
			image = False

		if image:
			post_payload["image_url"] = image
			
		posts.append(post_payload)

	if not posts:
		notification = {"text":"""<p>Oops. That was embarrassing.</p>
          	<p>Your search criteria didn't yield any results.</p>""","class":"is-danger"}
		return render_template("index.html", 
		notification=notification, 
		author=" ".join(authors), 
		tag=" ".join(tags))

	return render_template("index.html", 
		posts=posts, 
		author=" ".join(authors), 
		tag=" ".join(tags))


@app.route("/selected-authors")
def selected_authors():
	return render_template("selected_authors.html")

@app.route("/changelog")
def whats_new():
	return render_template("whats_new.html")

if __name__ == "__main__":
	app.config.update(
	DEBUG=True,
	TEMPLATES_AUTO_RELOAD=True,
	)
	app.run()
