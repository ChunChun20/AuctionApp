import time

# from auction import app,db
from auction import app
from auction.connection import db
from datetime import datetime,timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify
from auction.models import Item,User
from auction.forms import UserRegisterForm,ItemRegisterForm,LoginForm,BidForm,CustomBidForm
from flask_login import login_user,logout_user,login_required,current_user
from auction.funcs import check_auctions
import threading
import os



@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/auctions',methods=['GET','POST'])
@login_required
def auction_page():
    bid_form = BidForm()
    custom_bid_form = CustomBidForm()
    if request.method == 'POST':
        bid_item = request.form.get('bid_item')
        bid_item_object = Item.query.filter_by(name=bid_item).first()
        if bid_item_object:
            if current_user.can_bid(bid_item_object):
                if bid_item_object.bidder_id != None:
                    #refund money if outbid
                    old_bidder = User.query.filter_by(username=bid_item_object.bidder_id).first()
                    old_bidder.budget += bid_item_object.current_bid
                #assign highest bidder
                bid_item_object.bidder_id = current_user.username
                bid_item_object.current_bid = round(bid_item_object.current_bid * bid_item_object.step,2)
                current_user.budget -= round(bid_item_object.current_bid,2)
                db.session.commit()
                flash(f"Successfully placed a bid on {bid_item_object.name}!",'success')
            else:
                flash(f"Your bid on: {bid_item_object.name} failed!",'fail')

        custom_bid_item = request.form.get('custom_bid_item')
        custom_bid_item_object = Item.query.filter_by(name=custom_bid_item).first()
        if custom_bid_item_object:
            if current_user.can_custom_bid(custom_bid_item_object,custom_bid_form.custom_bid.data):
                # refund money if outbid
                if custom_bid_item_object.bidder_id != None:
                    old_bidder = User.query.filter_by(username=custom_bid_item_object.bidder_id).first()
                    old_bidder.budget += custom_bid_item_object.current_bid
                # assign highest bidder
                custom_bid_item_object.bidder_id = current_user.username
                custom_bid_item_object.current_bid = custom_bid_form.custom_bid.data
                current_user.budget -= round(custom_bid_item_object.current_bid,2)
                db.session.commit()

                flash(f"Successfully placed a bid on {custom_bid_item_object.name}!",'success')
            else:
                flash(f"Please place a higher bid!",'fail')
        return redirect(url_for('auction_page'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        return render_template('auctions.html',items=items,bid_form=bid_form,custom_bid_form=custom_bid_form)

@app.route('/register',methods=['GET','POST'])
def register_page():
    form = UserRegisterForm()
    if form.validate_on_submit():
        create_user = User(username=form.username.data,
                           email_address=form.email_address.data,
                           password=form.password1.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash("Account created successfully!",'success')
        return redirect(url_for('auction_page'))
    if form.errors != {}: #if there are not errors from validations
        for error in form.errors.values():
            flash(error,'fail')
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user_trying_to_login = User.query.filter_by(username=form.username.data).first()
        if user_trying_to_login and user_trying_to_login.check_password(
                password_for_checking=form.password.data
        ):
            login_user(user_trying_to_login)
            flash(f'Successfully logged as {user_trying_to_login.username}!','success')
            return redirect(url_for('auction_page'))
        else:
            flash("Wrong username or password!",'fail')
    return render_template('login.html',form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("Successfully logged out!",'info')
    return redirect(url_for('login_page'))


@app.route('/create',methods=['GET','POST'])
def create_page():
    current_time = datetime.now()

    form = ItemRegisterForm()
    if form.validate_on_submit():
        image_file = save_image(form.photo.data)
        create_item = Item(name=form.name.data,
                           description=form.description.data,
                           start=current_time.strftime("%m/%d/%Y, %H:%M:%S"),
                           end=(current_time + timedelta(minutes=form.duration.data)).strftime("%m/%d/%Y, %H:%M:%S"),
                           current_bid=form.current_bid.data,
                           step=1.10,
                           image=image_file,
                           seller_id = current_user.id
                           )



        db.session.add(create_item)
        db.session.commit()


        flash(f"Successfully created {create_item.name}",'success')

        return redirect(url_for('auction_page'))

    if form.errors != {}: #if there are not errors from validations
        for error in form.errors.values():
            flash(error,'fail')
    return render_template('create.html',form=form)

def save_image(picture_file):
    picture=picture_file.filename
    picture_path = os.path.join(app.root_path,'static/images',picture)
    picture_file.save(picture_path)
    return picture


@app.route('/owned_items')
def owned_items_page():
    owned_items = Item.query.filter_by(owner=current_user.id)
    return render_template('owned_items.html',owned_items=owned_items)






thread = threading.Thread(target=check_auctions)
thread.start()
