from flask import request
from flask import render_template
from flask import current_app as app
from flask import Flask
from flask import jsonify
from scraper import scrape_reviews, summarize_reviews, search_by_name

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
    
    @app.route("/", methods=["GET", "POST"])
    async def home_route():
        if request.method == "POST":
            steam_id = request.json.get("steam_id")
            custom_prompt = request.json.get("prompt")
            reviews, title = await scrape_reviews(steam_id)
            summary = await summarize_reviews(reviews, title, custom_prompt)
            return {"title": title, "summary": summary}
        return render_template("home.html")

    @app.route("/search", methods=["GET"])
    async def search_route():
        term = request.args.get("term")
        suggestions = await search_by_name(term)
        return jsonify(matching_results=suggestions)
    
    @app.route("/subscribe", methods=["GET"])
    async def subscribe_route():
        return render_template("payment_modal.html")

    return app