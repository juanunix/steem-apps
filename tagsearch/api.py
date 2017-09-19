from steemdata import SteemData

from flask import Flask
import re
import json
import random


def get_content(authors, tags):
    if not authors and not tags:
        return {"response": {
            "content": {
                "authors": authors,
                "tags": tags
            },
            "type": 404}
        }

    if not authors:
        if tags:
            # render selected authors.

            # load selected authors
            with open("tagsearch/selected_authors.json", "r") as selected_authors_file:
                data = json.load(selected_authors_file)

                selected_authors = []
                try:
                    for author in data["_all_tags"]:
                        username = author["username"]
                        selected_authors.append(username)
                except:
                    pass

                for tag in tags:
                    try:
                        for author in data[tag]:
                            username = author["username"]
                            selected_authors.append(username)
                    except:
                        pass

            s = SteemData()
            selected_authers_posts = s.Posts.find({
                "author": {"$in": selected_authors},
                "tags": {"$in": tags}
            }).sort([("created", -1)])

            posts = []
            for post in selected_authers_posts:
                post_payload = {
                    "url": "https://steemit.com" + post["url"],
                    "net_votes": post["net_votes"],
                    "title": post["root_title"],
                    "author": post["author"]
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
                <p><a href="%s" target="_blank"><b>Become a featured writer.</b></a></p>""" % (", ".join(tags), url_for("selected_authors")),
                    "class": "is-info"
                }
            res_dict = {
                "response": {
                    "type": "200",
                    "content": {
                        "posts": posts,
                        "tags": tags,
                        "authors": authors,
                        "showing_selected_authors": True
                    }
                }
            }
            return res_dict
        else:
            # Render failed search page
            res_dict = {
                "response": {
                    "type": "200",
                    "content": {
                        "posts": posts,
                        "tags": tags,
                        "authors": authors,
                        "showing_selected_authors": True
                    }
                }
            }
            return res_dict

    # get steemit connection
    s = SteemData()

    # render tag explorer if no tag is given
    if not tags:
        author_tags = s.Posts.aggregate([
            {"$match": {"author": authors[0]}},
            {"$project": {"tags": 1}},
            {"$unwind": "$tags"},
            {"$group": {"_id": '$tags', "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])

        notification = False
        if len(authors) > 1:
            notification = {"text": "<p>TagCloud doesn't yet support multiple authors.</p><p>Showing results for '%s' only.</p>" % (authors[0]),
                            "class": "is-danger"
                            }
        res_dict = {
            "response": {
                "type": "200",
                "content": {
                    "author_tags": [tag for tag in author_tags],
                    "authors": [authors[0]]
                }
            }
        }
        return res_dict

    # render posts with tag by author if both are given
    author_posts = s.Posts.find({
        "author": {"$in": authors},
        "tags": {"$in": tags}
    }).sort([("created", -1)])

    posts = []
    for post in author_posts:
        post_payload = {
            "url": "https://steemit.com" + post["url"],
            "net_votes": post["net_votes"],
            "title": post["root_title"],
            "author": post["author"]
        }

        try:
            image = post["json_metadata"]["image"]
        except KeyError:
            image = False

        if image:
            post_payload["image_url"] = image

        posts.append(post_payload)

    res_dict = {
        "response": {
            "type": "200",
            "content": {
                "posts": posts,
                "tags": tags,
                "authors": authors
            }
        }
    }
    return res_dict


def write_notification(response):
    pass


def extract_input(request_arguments):
    try:
        authors = re.findall(r"[\w-]+", request_arguments['authors'])
    except:
        try:
            authors = re.findall(r"[\w-]+", request_arguments['author'])
        except:
            authors = []
    try:
        tags = re.findall(r"[\w-]+", request_arguments['tags'])
    except:
        try:
            tags = re.findall(r"[\w-]+", request_arguments['tag'])
        except:
            tags = []
    return (authors, tags)
