from flask import request
from flask import render_template
from flask import make_response
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
        
        payment = True if request.cookies.get("payment") == "1" else False
        return render_template("home.html", paid_user=payment)

    @app.route("/search", methods=["GET"])
    async def search_route():
        term = request.args.get("term")
        suggestions = await search_by_name(term)
        return jsonify(matching_results=suggestions)
    
    @app.route("/subscribe", methods=["GET"])
    async def subscribe_route():
        return render_template("payment_modal.html")
    
    @app.route("/payment-success", methods=["POST"])
    async def payment_success_route():
        if request.method == "POST":
            # 1 is True, 0 is False
            payment = "1" if request.json.get("payment") else "0"
            resp = make_response(render_template("home.html", paid_user=(payment == "1")))
            resp.set_cookie("payment", payment)
            app.logger.info(f"Payment Successful: {payment}")
            return resp

    return app