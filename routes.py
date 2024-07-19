from flask import request, render_template, make_response, jsonify, redirect, url_for, flash, session
from scraper import summarize_reviews, search_by_name
from forms import LoginForm, AccountForm, RegistrationForm
from main import app, users_collection

def is_key_session(key):        
    return session and key in session and session[key] is not None and session[key]    

def update_user_session(user_name):
    user = users_collection.find_one({"username":user_name})
    if user:
        session['username'] = user['username']
        session['paid_user'] = user['paid_user']

@app.route("/", methods=["GET", "POST"])
async def home_route():
    if request.method == "POST":
        steam_id = request.json.get("steam_id")
        custom_prompt = request.json.get("prompt")
        title = request.json.get("title")

        amount_for_summary = 10 if is_key_session('paid_user') else 3
        amount_reviews_to_search = 40 if is_key_session('paid_user') else 10
        
        summary = await summarize_reviews(
            steam_id=steam_id, 
            title=title, 
            to_search=amount_reviews_to_search, 
            custom_prompt=custom_prompt, 
            amount_for_summary=amount_for_summary
        )

        return {"title": title, "summary": summary}        
    loggedin = is_key_session('username')
    if loggedin:
        update_user_session(session['username'])
    return render_template("home.html", loggedin=loggedin)

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

# ACCOUNTS
@app.route('/login', methods=['GET', 'POST'])
async def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        user = users_collection.find_one({"username":form.username.data, "password":form.password.data})
        if user:
            update_user_session(user['username'])
            flash('Logged in successfully.')
            return redirect(url_for('home_route'))
        flash('Invalid username or password')
    return render_template('login.html', title='Sign In', form=form)    

@app.route('/register', methods=['GET', 'POST'])
async def register_route():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        existing_user = users_collection.find_one({"username":username})
        existing_email = users_collection.find_one({"email":email})
        if existing_user or existing_email:
            flash('Username or email already exists. Please choose a different one.')
            return render_template('register.html', title='Register', form=form)            
        # Add user to MongoDB
        if users_collection is not None:
            users_collection.insert_one({
                'username': username,
                'password': password,
                'email': email,
                "paid_user": False
            })            
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login_route'))        
    return render_template('register.html', title='Register', form=form)

@app.route('/account', methods=['GET', 'POST'])
async def account_route():
    if 'username' not in session:
        return redirect(url_for('login_route'))        
    update_user_session(session['username'])
    user = users_collection.find_one({"username":session['username']})
    form = AccountForm()
    if request.method == 'GET':
        if user is not None:
            form.populate(user)                        
    elif request.method == 'POST':
        if form.logout.data:              
            session.clear()
            flash('Successfuly logged out')
            return redirect(url_for('home_route'))
        elif form.delete.data:
            if (users_collection is not None):
                users_collection.delete_one({'username': user['username']})
                flash('Successfuly deleted your account')
                return redirect(url_for('home_route'))
        elif form.update.data:
            oldPassword = user['password']
            oldEmail = user['email']                
            new_email = form.email.data
            new_password = form.password.data
            # Update MongoDB
            if users_collection is not None:
                if new_password:
                    myquery = {"email": oldEmail, "password": oldPassword}
                    newvalues = { "$set": { "email": new_email, 'password': new_password } }
                    users_collection.update_one(
                        myquery,
                        newvalues,
                        upsert=True
                    )
                else:
                    myquery = {"email": oldEmail}
                    newvalues = { "$set": { "email": new_email } }
                    users_collection.update_one(
                        myquery,
                        newvalues,
                        upsert=True
                    )                
            flash('Your changes have been saved.')
            return redirect(url_for('home_route'))        
    return render_template('account.html', title='Account', form=form)