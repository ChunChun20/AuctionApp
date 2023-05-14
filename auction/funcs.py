import time
from datetime import datetime

from flask import redirect, url_for

from auction.models import Item,User
# from auction import db,app
from auction import app
from auction.connection import db

# def check_auction(item_obj):
#     today = date.today()
#     now = today.strftime("%m/%d/%Y, %H:%M:%S")
#     if now >= item_obj.end:
#         new_owner = User.query.filter_by(username=item_obj.bidder_id).first()
#         item_obj.owner = new_owner.id
#         db.session.commit()
#
# schedule.every(1).seconds.do(check_auction)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

# def check_auction(item_obj):
#     current_date = datetime.now()
#     current_date1 = datetime.strftime(current_date, "%m/%d/%Y, %H:%M:%S")
#     if current_date1 > item_obj.end:
#         new_owner = User.query.filter_by(username=item_obj.bidder_id).first()
#         item_obj.owner = new_owner.id
#         db.session.commit()


def check_auctions():
    while True:
        with app.app_context():
            items = Item.query.filter_by(owner=None)

            for item in items:
                current_date = datetime.now()
                current_date1 = datetime.strftime(current_date, "%m/%d/%Y, %H:%M:%S")
                if current_date1 > item.end and item.bidder_id == None:
                    db.session.delete(item)
                    db.session.commit()

                elif current_date1 > item.end and item.bidder_id != None:
                    prev_owner = User.query.filter_by(id=item.seller_id).first()
                    new_owner = User.query.filter_by(username=item.bidder_id).first()
                    item.owner = new_owner.id
                    prev_owner.budget += item.current_bid
                    db.session.commit()

        time.sleep(2)

