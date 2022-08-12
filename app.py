#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import collections

import json
from operator import truediv
from re import T
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import db, Show, Venue, Artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
collections.Callable=collections.abc.Callable

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

#DONE --> connect to fyyurdb in cofig.py
#connect to a local postgresql database with migrate
#run flask db init to generate a migartion -->flask db migrate-->flask db upgrade for created missing columns
#Models are in models.py and imported.

migrate = Migrate(app, db)

    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------#

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  # data[]--> list to append all data
  #get metadata from the venue query to be displayed,
  ##upcoming_shows is an aggregate from a len func() on query##
  ##check for upcoming shows in shows models and check against set_time and append metatdata to list
  #set_time=datetime.now()
  
  data = []
  venueq = db.session.query(Venue.city, Venue.name, Venue.id).all()
  set_time = datetime.now()
  upcoming_showsq = db.session.query(Show.start_time).filter().filter(Show.start_time<set_time).all()
  data.append({
    'venues': venueq,
    'upcoming_shows': upcoming_showsq,
    'num_upcoming_shows': len(upcoming_showsq)
  })

  return render_template('pages/venues.html', areas=data)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  #inspired by the query Person.query.ilike(%b%) from udacity.classroom  #searchq is short search query
  #(Venue.name.ilike(f'%{search_term}%'))---->ilike(f'%{search_term}%') snippet ensures case-insensitivity
  #\len function works instead of count since searchq.count() expects exactly one arg.
  search_term = request.form.get('search_term', '')
  searchq = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {
        'data': searchq,
        'count': len(searchq)
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  data = {}
  #set_time is used to check for upcoming and past shows
  #get joined queries to obtain info about upcoming and past shows
  set_time = datetime.now()
  upcoming_showsq = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>set_time).all()
  past_showsq = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<set_time).all()
  
  data['upcoming_shows_count'] = upcoming_showsq.count()
  data['past_shows_count'] = past_showsq.count()
  data['venues'] = venue
  return render_template('pages/show_venue.html', venue=data)
  
  #data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead #Done
  # TODO: modify data to be the data object returned from db insertion
  
  #object returned is named dbbody
  dbbody={} 
  error=False
  form=VenueForm(request.form)
  if form.validate():  
    try:
      #data from form using Flask-WTF forms 'data' attribute
      venue=Venue(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  address=form.address.data,
                  phone=form.phone.data,
                  image_link=form.image_link.data,
                  genres=form.genres.data,
                  facebook_link=form.facebook_link.data,
                  website_link=form.website_link.data,
                  seeking_talent=form.seeking_talent.data,
                  seeking_description=form.seeking_description.data
                  )
      db.session.add(venue)
      db.session.commit()
      
      dbbody['name']=venue.name
      dbbody['city']=venue.city
      dbbody['state']=venue.state
      dbbody['address']=venue.address
      dbbody['phone']=venue.phone
      dbbody['image_link']=venue.image_link    
      dbbody['genres']=venue.genres
      dbbody['facebook_link']=venue.facebook_link
      dbbody['website_link']=venue.website_link
      dbbody['seeking_talent']=venue.seeking_talent
      dbbody['seeking_description']=venue.seeking_description
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return jsonify(dbbody)
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')
    
  #Done
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  #DONE
  error=False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
  if not error:
    flash('Delete successsful')
  else:
    flash('Delete unsuccessful')
    
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database 
  # #Done
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  data=Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  #Done #similar to search_venues so they have the same soln. 
  # ilike(f'%{search_term}%') snippet ensures case-insensitivity
  #\len function works instead of count since searchq.count() expects exactly one arg.
  
  search_term=request.form.get('search_term', '')
  searchq=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = {
        'data': searchq,
        'count': len(searchq)
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  #DONE
  #get artist_info and upcomming_shows
  data=Artist.query.get(artist_id)
  
  return render_template('pages/show_artist.html', artist=data)
  
  
  
  # artist=Artist.query.get(id=artist_id)
  # data1={}
  # data2={}
  # artistinfo=Artist.query.filter(seeking_venue=True).all()
  # set_time=datetime.now()
  
  # upcoming_shows=Show.query.filter(Show.start_time>set_time).all()
  # data1['upcomig_shows']=upcoming_shows.count()
  # data1['artistinfo']=artistinfo
  # print(data1)
  
  # artistinfo2=Artist.query.filter(seeking_venue=False).all()
  
  # upcoming_shows2=Show.query.filter(Show.start_time>set_time)
  # data2['upcomig_shows']=upcoming_shows2.count()
  # data2['artistinfo']=artistinfo2
  # print(data2)
  
  # data3=Artist.query.join('show')
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  form=ArtistForm(request.form)
  error=False
  if form.validate():
    try:
      artist=Artist.query.get(id=artist_id)
      artist.name=request.args.get('name')
      artist.city=request.args.get('city')
      artist.state=request.args.get('state')
      artist.phone=request.args.get('phone')
      artist.image_link=request.args.get('image_link')
      artist.genres=request.args.get('genres')
      artist.facebook_link=request.form.get('facebook_link')
      artist.website_link=request.form.get('website_link')
      artist.seeking_venue=request.args.get('seeking_venue')
      artist.seeking_description=request.args.get('seeking_description')
      db.session.commiyt()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
      flash('Edit successful')
    else:
      flash('Edit failed')
      
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  #DONE
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #Done this
 
  form = ArtistForm(request.form)
  error=False
  if form.validate():
    try:
      artist=Artist.query.get(id=artist_id)
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.image_link=form.image_link.data
      artist.genres=form.genres.data
      artist.facebook_link=form.facebook_link.data
      artist.website_link=form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      db.session.commiyt()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
      flash('Edit success')
    else:
      flash('Edit not successsful')

    return redirect(url_for('show_artist', artist_id=artist_id))
  


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  form = VenueForm(request.form)
  venue_edit=Venue.query.get(venue_id)
  error=False
  try:
    venue_edit.name=request.args.get('name')
    venue_edit.genres=request.args.get('genres')
    venue_edit.address=request.args.get('address')
    venue_edit.city=request.args.get('city')
    venue_edit.state=request.args.get('state')
    venue_edit.phone=request.args.get('phone')
    venue_edit.website_link=request.args.get('website_link')
    venue_edit.facebook_link=request.args.get('facebook_link')
    venue_edit.seeking_talent=request.args.get('seeking_talent')
    venue_edit.seeking_description=request.args.get('seeking_description')
    venue_edit.image_link=request.args.get('image_link')
    db.session.commit()
    venue=venue_edit
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
      db.session.close()
  if not error:
    flash('Edit success')
  else:
    flash('Edit not successsful')
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  
  # {
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form=VenueForm(request.form)
  venue_edit=Venue.query.get(venue_id)
  venue_edit.name=form.name.data
  venue_edit.genres=form.genres.data
  venue_edit.address=form.address.data
  venue_edit.city=form.city.data
  venue_edit.state=form.state.data
  venue_edit.phone=form.phone.data
  venue_edit.website_link=form.website_link.data
  venue_edit.facebook_link=form.facebook_link.data
  venue_edit.seeking_talent=form.seeking_talent.data
  venue_edit.seeking_description=form.seeking_description.data
  venue_edit.image_link=form.image_link.data
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #Done
  #artistobj is returend from db insertion as json
  #data from form using Flask-WTF forms'data' attribute
  
  artistobj={} 
  error=False
  form=ArtistForm(request.form)
  if form.validate():
    try:
      artist=Artist(name=form.name.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  image_link=form.image_link.data,
                  genres=form.genres.data,
                  facebook_link=form.facebook_link.data,
                  website_link=form.website_link.data,
                  seeking_venue=form.seeking_venue.data,
                  seeking_description=form.seeking_description.data
                  )
      db.session.add(artist)
      db.session.commit()
      
      artistobj['name']=artist.name
      artistobj['city']=artist.city
      artistobj['state']=artist.state
      artistobj['phone']=artist.phone
      artistobj['image_link']=artist.image_link    
      artistobj['genres']=artist.genres
      artistobj['facebook_link']=artist.facebook_link
      artistobj['website_link']=artist.website_link
      artistobj['seeking_venue']=artist.seeking_venue
      artistobj['seeking_description']=artist.seeking_description
    except:
      error=True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return jsonify(artistobj)
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')
  
  #Done
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  #modified this code segment for the datetime() dtype to be accepted into expected str, with code from stackoverflow; if isinstance(value, str):
  
  # if isinstance(value, str):
  #   date = dateutil.parser.parse(value)
  #   if format == 'full':
  #       format="EEEE MMMM, d, y 'at' h:mma"
  #   elif format == 'medium':
  #       format="EE MM, dd, y h:mma"
  #   return babel.dates.format_datetime(date, format, locale='en')
  
  data = db.session.query(
    Show.venue_id,
    Venue.name,
    Show.artist_id,
    Artist.image_link,
    Show.start_time
  ).join(Venue).join(Artist).all()

  return render_template('pages/shows.html', shows=data)


    #Done
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead 
  # 
  # #Done
  error = False
  form=ShowForm(request.form)
  if form.validate():
    try:
      show = Show(artist_id=form.artist_id.data,
                  venue_id=form.venue_id.data,
                  start_time=form.start_time.data)
                  
      db.session.add(show)
      db.session.commit()
      
    except:
      db.session.rollback()
      error=True
    finally:
      db.session.close()
    if not error:
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')
    
  return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead. #Done
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
