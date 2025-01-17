#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#Mes importations
#from models import Venue, Artist, Show

import os
from flask_migrate import Migrate
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from models import db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


#https://stackoverflow.com/questions/9692962/flask-sqlalchemy-import-context-issue/9695045#9695045
db.init_app(app)

migrate = Migrate(app,db)

# TODO: connect to a local postgresql database/OK

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #https://fellowship.hackbrightacademy.com/materials/serft8/lectures/sql-alchemy-2/
  #on recupere d'abord tous les (city et state)

  try:
      result = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()

      data1 = []
      for rs in result:

            # on filtre maintenat a partir du (city, state)  regroupé
            #https://fellowship.hackbrightacademy.com/materials/serft8/lectures/sql-alchemy-2/
            #https://stackoverflow.com/questions/8667960/sql-alchemy-group-by-in-query
            result1 = Venue.query.filter(Venue.state == rs.state, Venue.city == rs.city).group_by(Venue.city, Venue.state, Venue.name, Venue.id)

            data_result1 = []

            # on cree la liste venues
            for v in result1:
                data_result1.append({
                    'id': v.id,
                    'name': v.name,
                    #https://stackoverflow.com/questions/41478753/setting-datetime-in-flask-app
                    'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
                })
              
            #on cree les données
            data1.append({
                          'city': rs.city,
                          'state': rs.state,
                          'venues': data_result1
                      })        
              
      return render_template('pages/venues.html', areas=data1)
  
  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()





  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  #return render_template('pages/venues.html', areas=data1);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

      #Code pris dans render_Template return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  try:    
      search_term = request.form.get('search_term', '')
      result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
      count = len(result)
      response = {
            "count": count,
            "data": result
      }
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()

  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  #return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  

  try:
      
      result = Venue.query.get_or_404(venue_id)
      #result = db.session.query(Venue).filter(Venue.id == venue_id).one()
      
      

      
      

      # on fait une jointure de 2 table pour recuperer Artist et dateShow
      #https://www.adamsmith.haus/python/answers/how-to-join-multiple-tables-together-in-sqlalchemy-in-python      
      result1 = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).filter(Show.start_time < datetime.now()).all()

      past_shows = []

      # on cree la liste show passé
      for v in result1:
            past_shows.append({
                    "artist_id": v.artist.id,
                    "artist_name": v.artist.name,
                    "artist_image_link": v.artist.image_link,
                    "start_time": str(v.start_time)
            })
      #https://www.adamsmith.haus/python/answers/how-to-join-multiple-tables-together-in-sqlalchemy-in-python
      result2 = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).filter(Show.start_time > datetime.now()).all()

      upcoming_shows = []

      # on cree la liste show à venir en fonction de l'artist
      for v in result2:
            upcoming_shows.append({
                    "artist_id": v.artist.id,
                    "artist_name": v.artist.name,
                    "artist_image_link": v.artist.image_link,
                    "start_time": str(v.start_time)
            })
        
      
      data = {
                    "id": result.id,
                    "name": result.name,
                    "genres": result.genres,
                    "address": result.address,
                    "city": result.city,
                    "state": result.state,
                    "phone": result.phone,
                    "website": result.website,
                    "facebook_link": result.facebook_link,
                    "seeking_talent": result.seeking_talent,
                    "seeking_description": result.seeking_description,
                    "image_link": result.image_link,
                    
                    "past_shows": past_shows,
                    "upcoming_shows": upcoming_shows,
                    "past_shows_count": len(past_shows),
                    "upcoming_shows_count": len(upcoming_shows)
                }
        
      
      return render_template('pages/show_venue.html', venue=data)
  
  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()









  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm()
  #https://stackoverflow.com/questions/41478753/setting-datetime-in-flask-app
  if form.validate_on_submit():

    try:
                  new_venue = Venue(
                  name = form.name.data,
                  city = form.city.data,
                  state = form.state.data,
                  address = form.address.data,
                  phone = form.phone.data,
                  genres = form.genres.data,
                  image_link = form.image_link.data,
                  facebook_link = form.facebook_link.data,
                  website = form.website_link.data,
                  seeking_talent = form.seeking_talent.data,
                  seeking_description = form.seeking_description.data)
                
                  
                  db.session.add(new_venue)
                  db.session.commit()
                  flash('Venue ' + form.name.data + ' was successfully listed!')
                  return render_template('pages/home.html')
    
    except Exception as e:
                  print(e)
                  flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
                  return render_template('pages/home.html')
                  db.session.rollback()
    
    finally:
                  db.session.close()
    
  else:
                  #flash('An error occurred. Venue ' + form.name.data + ' could nott be listed.')
                  return render_template('forms/new_venue.html', form =  form)
                  db.session.rollback()
  
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
    return render_template('pages/home.html')
  except:
    db.session.rollback()
  finally:
    db.session.close()
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database


  try:
      #https://fellowship.hackbrightacademy.com/materials/serft8/lectures/sql-alchemy-2/
      #on recupere d'abord tous les (city et state)
      result = db.session.query(Artist.id, Artist.name).all()

      data1 = []
      # on cree la liste venues
      for v in result:
        
        data1.append({
              'id': v.id,
              'name': v.name,

                })
      return render_template('pages/artists.html', artists=data1)

  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()  


  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
 # return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  try:
      
      search_term = request.form.get('search_term', '')
      result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
      num = len(result)
      response1 = {
            "count": num,
            "data": result
      }


      response={
          "count": 1,
          "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
          }]
      }
      return render_template('pages/search_artists.html', results=response1, search_term=request.form.get('search_term', ''))
  
  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()


 

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  try:
      
      result = Artist.query.get_or_404(artist_id)     
      # on fait une jointure de 2 table pour recuperer Artist et dateShow
            
      result1 = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).filter(Show.start_time < datetime.now()).all()

      past_shows = []

      # on cree la liste show passé en fonction du lieu
      for v in result1:
            past_shows.append({
                    "venue_id": v.venue.id,
                    "venue_name": v.venue.name,
                    "venue_image_link": v.venue.image_link,
                    "start_time": str(v.start_time)
            })
      
      result2 = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).filter(Show.start_time > datetime.now()).all()

      upcoming_shows = []

      # on cree la liste show à venir en fonction du lieu
      for v in result2:
            upcoming_shows.append({
                    "venue_id": v.venue.id,
                    "venue_name": v.venue.name,
                    "venue_image_link": v.venue.image_link,
                    "start_time": str(v.start_time)
            })
        
      
      data = {
                    "id": result.id,
                    "name": result.name,
                    "genres": result.genres,
                    "city": result.city,
                    "state": result.state,
                    "phone": result.phone,
                    "website": result.website,
                    "facebook_link": result.facebook_link,
                    "seeking_venue": result.seeking_venues,
                    "seeking_description": result.seeking_description,
                    "image_link": result.image_link,
                    "past_shows": past_shows,
                    "upcoming_shows": upcoming_shows,
                    "past_shows_count": len(past_shows),
                    "upcoming_shows_count": len(upcoming_shows)
              }
        
      
      return render_template('pages/show_artist.html', artist=data)
  
  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()



  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  #return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  artist1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  artist = Artist.query.get_or_404(artist_id)
  if form.validate_on_submit():
    
    
    try:
                  
                  
                  
                  
                
                  #https://devsheet.com/code-snippet/update-column-values-query-in-sqlalchemy/
                  db.session.query(Artist).filter(Artist.id == artist_id).update({'name':form.name.data,
                          'city': form.city.data,
                          'state' : form.state.data,
                          'phone' : form.phone.data,
                          'genres' : form.genres.data,
                          'image_link' : form.image_link.data,
                          'facebook_link' : form.facebook_link.data,
                          'website' : form.website_link.data,
                          'seeking_venues' : form.seeking_venue.data,
                          'seeking_description' : form.seeking_description.data})
                      
                  db.session.commit()
                  flash('Artist ' + form.name.data + ' was successfully update!')
                  return redirect(url_for('show_artist', artist_id=artist_id))
    
    except Exception as e:
                  print(e)
                  flash('An error occurred. Artist ' + form.name.data + ' could not be update.')
                  return render_template('forms/edit_artist.html', artist = artist, form =  form)
                  db.session.rollback()
    
    finally:
                  db.session.close()
    
  else:
                  #flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
                  return render_template('forms/edit_artist.html', artist = artist, form =  form)
                  db.session.rollback()

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  venue = Venue.query.get_or_404(venue_id)


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm()
  venue = Venue.query.get_or_404(venue_id)

  if form.validate_on_submit():

      try:
                                 
                                  
                    #https://devsheet.com/code-snippet/update-column-values-query-in-sqlalchemy/
                    db.session.query(Venue).filter(Venue.id == venue_id).update({'name':form.name.data,
                            'city': form.city.data,
                            'state' : form.state.data,
                            'phone' : form.phone.data,
                            'address': form.address.data,
                            'genres' : form.genres.data,
                            'image_link' : form.image_link.data,
                            'facebook_link' : form.facebook_link.data,
                            'website' : form.website_link.data,
                            'seeking_talent' : form.seeking_talent.data,
                            'seeking_description' : form.seeking_description.data})
                    
                    db.session.commit()
                    flash('Venue ' + form.name.data + ' was successfully update!')
                    return redirect(url_for('show_venue', venue_id=venue_id))
      
      except Exception as e:
                    print(e)
                    flash('An error occurred. Venue ' + form.name.data + ' could not be update.')
                    return render_template('forms/edit_venue.html', venue=venue, form = form)
                    db.session.rollback()
      
      finally:
                    db.session.close()
  else:
                    #flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
                    return render_template('forms/edit_venue.html', venue=venue, form = form)
                    db.session.rollback()



#return redirect(url_for('show_venue', venue_id=venue_id))

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

  form = ArtistForm()

  if form.validate_on_submit():

    try:
                  new_art = Artist(
                  name = form.name.data,
                  city = form.city.data,
                  state = form.state.data,
                  phone = form.phone.data,
                  genres = form.genres.data,
                  image_link = form.image_link.data,
                  facebook_link = form.facebook_link.data,
                  website = form.website_link.data,
                  seeking_venues = form.seeking_venue.data,
                  seeking_description = form.seeking_description.data)
                
                  print(new_art)
                  db.session.add(new_art)
                  db.session.commit()
                  flash('Artist ' + form.name.data + ' was successfully listed!')
                  return render_template('pages/home.html')
    
    except Exception as e:
                  print(e)
                  flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
                  return render_template('pages/home.html')
                  db.session.rollback()
    
    finally:
                  db.session.close()
    
  else:
                  #flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
                  return render_template('forms/new_artist.html', form =  form)
                  db.session.rollback()
            

  
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #https://www.adamsmith.haus/python/answers/how-to-join-multiple-tables-together-in-sqlalchemy-in-python

  try:
      
      result = data = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()
      data1 = []

      for s in result:
        data1.append({

          "venue_id": s.venue_id,
          "venue_name": s.venue.name,
          "artist_id": s.artist_id,
          "artist_name": s.artist.name,
          "artist_image_link": s.artist.image_link,
          "start_time": str(s.start_time)

        })
      
      return render_template('pages/shows.html', shows=data1)
  
  except Exception as e:
      print(e)
      db.session.rollback()
    
  finally:
      db.session.close()



  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  #return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm()

  if form.validate_on_submit():

    try:
                  new_show = Show(
                  venue_id = form.venue_id.data,
                  artist_id = form.artist_id.data,
                  start_time = form.start_time.data)

                  db.session.add(new_show)
                  db.session.commit()
                  flash('Show was successfully listed!')
                  return render_template('pages/home.html')
    
    except Exception as e:
                  print(e)
                  flash('An error occurred. Show could not be listed.')
                  return render_template('pages/home.html')
                  db.session.rollback()
    
    finally:
                  db.session.close()
    
  else:
                  flash('An error occurred. Show could not be listed.')
                  return render_template('pages/home.html')
                  db.session.rollback()

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

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
'''
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

