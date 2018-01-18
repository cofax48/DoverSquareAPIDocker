# app.py
from flask import Flask
from flask import request, render_template, jsonify
import json
from sqlalchemy import create_engine
from time import time, strftime
import datetime
from db_config import SQLALCHEMY_DATABASE_URI
import os
from werkzeug.contrib.fixers import ProxyFix

from datetime import datetime

#Connects to my database
engine = create_engine(SQLALCHEMY_DATABASE_URI)
conn = engine.connect()

app = Flask(__name__)

#make the returned list have datafields
def listing_jsonifier(inputted_list):
    listing_list_to_send = []
    for listing in inputted_list:
        id_to_send = listing[0]
        user = listing[1]
        title = listing[2]
        description = listing[3]
        expiration = listing[4]
        X_Location = listing[5]
        Y_Location = listing[6]
        listing_list_to_send.append({"user": user, "title":title, \
        "description":description, "expiration":expiration, "location":{"x":X_Location, "y":Y_Location}})
    return listing_list_to_send

#Homepage initilizes table
@app.route("/tableInitializer")
def homepage():
    conn.execute('''CREATE TABLE IF NOT EXISTS "BNB Listings" ("id" varchar(100) NOT NULL, PRIMARY KEY ("id"));''')
    conn.execute('''CREATE INDEX IF NOT EXISTS id_idx ON "BNB Listings" USING btree (id);''')
    conn.execute('''ALTER TABLE "BNB Listings" ADD COLUMN "user" TEXT;''')
    conn.execute('''ALTER TABLE "BNB Listings" ADD COLUMN "title" TEXT;''')
    conn.execute('''ALTER TABLE "BNB Listings" ADD COLUMN "description" TEXT;''')
    conn.execute('''ALTER TABLE "BNB Listings" ADD COLUMN "expiration" varchar(100);''')
    conn.execute('''ALTER TABLE "BNB Listings" ADD COLUMN "X_Location" varchar(100);''')
    conn.execute('''ALTER TABLE "BNB Listings" ADD COLUMN "Y_Location" varchar(100);''')
    return json.dumps("Data Table Initialized"), 200, {'ContentType':'application/json'}

#**POST** - Create New Listing
#Adds a new listing to the system.
@app.route('/api/listings/add_new_listing', methods=['POST'])
def add_new_listing():
    #adds new listing
    data = json.loads(request.data.decode())
    dt = datetime.now()
    #makes the id the timestamp to the microsecond
    id_inputted = str(time.time()) + str(dt.microsecond)

    user_name = data["user"]
    title = data["title"]
    description = data["description"]
    expiration = data["expiration"]
    location = data["location"]
    X_Location = location["x"]
    Y_Location = location["y"]

    #SQL Statement inputting the data
    conn.execute('''INSERT INTO "BNB Listings" VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');'''.format(id_inputted, user_name, title, description, expiration, X_Location, Y_Location))

    #returns the id_inputted variable if succsful
    return json.dumps({'id':id_inputted}), 200, {'ContentType':'application/json'}

#queries all listings in the system
@app.route('/api/listings/get', methods=['GET'])
def get_listings():
    if 'active' in request.args:
        active_listings = request.args["active"]
        if int(active_listings) == 1:
            #* `?active=1` returns only listings that have not expired
            #Checks against the current time
            current_time_to_check_expiration = datetime.fromtimestamp(
                int(time())
            ).strftime("%Y-%m-%d%H:%M:%S")

            active_query = conn.execute('''SELECT * FROM "BNB Listings" WHERE "expiration" < '{}';'''.format(current_time_to_check_expiration))
            active_query_list = active_query.cursor.fetchall()

            #make the returned list have datafields
            active_query_list_to_send = listing_jsonifier(active_query_list)

            #returns the active listings variable if succsful
            return json.dumps(active_query_list_to_send), 200, {'ContentType':'application/json'}

    if 'length' in request.args:
        listings_length = request.args["length"] #length of query
        pagination_begin = request.args["page"] #starts qury at

        pagination_query = conn.execute('''SELECT * FROM "BNB Listings" WHERE id > '{}' LIMIT {};'''.format(pagination_begin, listings_length))
        pagination_query_list = sorted(pagination_query.cursor.fetchall())

        #make the returned list have datafields
        pagination_query_list_to_send = listing_jsonifier(pagination_query_list)

        return json.dumps(pagination_query_list_to_send), 200, {'ContentType':'application/json'}

    else:
        active_query = conn.execute('''SELECT * FROM "BNB Listings";''')
        active_query_list = sorted(active_query.cursor.fetchall())

        #make the returned list have datafields
        active_query_list_to_send = listing_jsonifier(active_query_list)

        #returns the active listings variable if succsful
        return json.dumps(active_query_list_to_send), 200, {'ContentType':'application/json'}

#Delete all listings
@app.route('/api/listings/delete_all_listings', methods=['DELETE'])
def delete_all_listings():

    #deletes all data from the table, but keeps table initialized
    conn.execute('''TRUNCATE TABLE "BNB Listings";''')
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


#Gets info for a single listing
@app.route('/api/listings/<id>', methods=['GET'])
def get_single_listing(id):
    print(id)
    if id:
        single_id_get = conn.execute('''SELECT * FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
        single_id_get_list = single_id_get.cursor.fetchall()
        #make the returned list have datafields
        listing_list_to_send = listing_jsonifier(single_id_get_list)

        #returns the active listings variable if succsful
        return json.dumps(listing_list_to_send), 200, {'ContentType':'application/json'}

#Changes info for a single listing
@app.route('/api/listings/<id>', methods=['PUT'])
def put_single_listing(id):
    print(id)
    if id:
        data = json.loads(request.data.decode())
        for field in data:
            print(field)
            if field == "title":
                print('146', field, data)
                title = field["title"]
                conn.execute('''UPDATE "BNB Listings" SET "title" = '{}' WHERE "id" = '{}';'''.format(title, id))
                single_id_get = conn.execute('''SELECT * FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
                single_id_get_list = single_id_get.cursor.fetchall()
                listing_list_to_send = listing_jsonifier(single_id_get_list)

                #returns the active listings variable if succsful
                return json.dumps(listing_list_to_send), 200, {'ContentType':'application/json'}

            elif field == "description":
                print('157', field, data)
                description = field
                conn.execute('''UPDATE "BNB Listings" SET "description" = '{}' WHERE "id" = '{}';'''.format(description, id))
                single_id_get = conn.execute('''SELECT * FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
                single_id_get_list = single_id_get.cursor.fetchall()
                listing_list_to_send = listing_jsonifier(single_id_get_list)

                #returns the active listings variable if succsful
                return json.dumps(listing_list_to_send), 200, {'ContentType':'application/json'}
            elif field == "expiration":
                expiration = field
                conn.execute('''UPDATE "BNB Listings" SET "expiration" = '{}' WHERE "id" = '{}';'''.format(expiration, id))
                single_id_get = conn.execute('''SELECT * FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
                single_id_get_list = single_id_get.cursor.fetchall()
                listing_list_to_send = listing_jsonifier(single_id_get_list)

                #returns the active listings variable if succsful
                return json.dumps(listing_list_to_send), 200, {'ContentType':'application/json'}

            elif field == "location":
                location = field
                for xy in location:
                    if xy == "x":
                        X_Location = xy
                        conn.execute('''UPDATE "BNB Listings" SET "X_Location" = '{}' WHERE "id" = '{}';'''.format(X_Location, id))
                        single_id_get = conn.execute('''SELECT * FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
                        single_id_get_list = single_id_get.cursor.fetchall()
                        listing_list_to_send = listing_jsonifier(single_id_get_list)

                        #returns the active listings variable if succsful
                        return json.dumps(listing_list_to_send), 200, {'ContentType':'application/json'}

                    elif xy == "y":
                        Y_Location = xy
                        conn.execute('''UPDATE "BNB Listings" SET "Y_Location" = '{}' WHERE "id" = '{}';'''.format(Y_Location, id))
                        single_id_get = conn.execute('''SELECT * FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
                        single_id_get_list = single_id_get.cursor.fetchall()
                        listing_list_to_send = listing_jsonifier(single_id_get_list)

                        #returns the active listings variable if succsful
                        return json.dumps(listing_list_to_send), 200, {'ContentType':'application/json'}

#Deletes info for a single listing
@app.route('/api/listings/<id>', methods=['DELETE'])
def delete_single_listing(id):
    if id:
        conn.execute('''DELETE FROM "BNB Listings" WHERE "id" = '{}';'''.format(id))
        #returns the id_inputted variable if succsful
        return json.dumps({'id':id_inputted}), 200, {'ContentType':'application/json'}


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run(debug=True)
