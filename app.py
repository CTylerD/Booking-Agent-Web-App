#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from wtforms import validators
from flask_wtf import Form
from forms import *
from sysconfig import sys
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import desc, distinct, func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db, compare_type=True)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy='select')


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy='select')


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    image_link = db.Column(db.String, nullable=True)
    start_time = db.Column(db.DateTime(timezone=True))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#----------------------------------------------------------------------------#
# Functions.
#----------------------------------------------------------------------------#

# Get upcoming shows count
def upcoming_shows_count(model, id):
    model_instance = model.query.get(id)
    if model == Venue:
        upcoming_shows = Show.query.filter_by(venue_id=id).all()
    elif model == Artist:
        upcoming_shows = Show.query.filter_by(artist_id=id).all()
    return upcoming_shows

# Search
def search(model, template):
    form = SearchForm()
    count = 0
    total_data = []
    response = {}
    search_terms = request.form.get('search_terms')
    terms_sql = '%{0}%'.format(search_terms)
    results = model.query.filter(func.lower(model.name).contains(func.lower(terms_sql))).all()

    if search_terms != '':
        for r in results:
            data = {}
            data["id"] = r.id
            data["name"] = r.name
            total_data.append(data)
            count += 1
        response["count"] = count
        response["data"] = total_data

    return render_template(template, form=form, results=response, search_terms=search_terms)


#Create Artist/Venue
def create_new(model_data, model_string, template, form):
    
    def attempt_submission(form):
        error = False
        try:
            model = model_data
            db.session.add(model)
            db.session.commit()
            flash(model_string.capitalize() + ' ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. ' + model_string.capitalize() + ' ' + model_string + ' could not be listed.')
        finally:
            db.session.close()
            if error == True:
                return render_template(template, form=form)
            else:
                return redirect(url_for(model_string + 's'))

    if form.validate() is False:
        errors = form.errors.items()
        for error in errors:
            print(error)
            if error[0] == 'csrf_token':
                if len(errors) == 1:
                    return attempt_submission(form)
                continue
            if hasattr(form, str(error[0])):
                flash('An error occurred in the ' + error[0] + ' field. ' + error[1][0])
        return render_template(template, form=form)
    else:
        return attempt_submission(form)


# Update Artist/Venue
def edit_submission(model_id, model_type, model_string, template, form):

    def attempt_edit():
        error = False
        try:
            model = model_type.query.filter_by(id=model_id).first()
            model.name=request.form.get('name'),
            model.genres=','.join(request.form.getlist('genres')),
            model.city=request.form.get('city'),
            model.state=request.form.get('state'),
            model.phone=request.form.get('phone'),
            model.website=request.form.get('website'),
            model.facebook_link=request.form.get('facebook_link'),
            model.seeking_description=request.form.get('seeking_description'),
            model.image_link=request.form.get('image_link')
            if model_type == Artist:
                model.seeking_venue=request.form.get('seeking_venue')
            elif model_type == Venue:
                model.address=request.form.get('address'),
                model.seeking_talent=request.form.get('seeking_talent')

            validated = validate_forms(model)
            if not validated:
                raise Exception("Validation failed")

            db.session.commit()
            flash(model_string.capitalize() + ' ' + request.form['name'] + ' was successfully listed!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. ' + model_string.capitalize() + ' ' + ' could not be listed.')
        finally:
            if error == True:
                if model_type == Venue:
                    return render_template(template, form=form, venue=model)
                elif model_type == Artist:
                    return render_template(template, form=form, artist=model)
            else:
                db.session.close()
                if model_type == Venue:
                    return redirect(url_for('venues'))
                elif model_type == Artist:
                    return redirect(url_for('artists'))
    
    if form.validate() is False:
        errors = form.errors.items()
        for error in errors:
            print(error)
            if error[0] == 'csrf_token':
                if len(errors) == 1:
                    return attempt_edit()
                continue
            if hasattr(form, str(error[0])):
                flash('An error occurred in the ' + error[0] + ' field. ' + error[1][0])
        if model_type == Venue:
            return render_template(template, form=form, venue=model)
        elif model_type == Artist:
            return render_template(template, form=form, artist=model)
    else:
        return attempt_edit()


# Determine Upcoming/Past Shows
def get_shows(id, model_type):
    error = False
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if model_type == Artist:
        shows_list = db.session.query(Show.id.label('show_id'), Show.artist_id.label('artist_id'), Show.venue_id.label('venue_id'), Show.start_time, Venue.image_link.label('image_link'), Artist.name.label('artist_name'), Venue.name.label('venue_name')).filter_by(artist_id=id).join(Artist).join(Venue).order_by(desc(Show.start_time)).all()
    elif model_type == Venue:
        shows_list = db.session.query(Show.id.label('show_id'), Show.artist_id.label('artist_id'), Show.venue_id.label('venue_id'), Show.start_time, Artist.image_link.label('image_link'), Artist.name.label('artist_name'), Venue.name.label('venue_name')).filter_by(venue_id=id).join(Artist).join(Venue).order_by(desc(Show.start_time)).all()
    upcoming_shows = []
    past_shows = []

    for show in shows_list:
        new_show = {}
        new_show["show_id"] = show[0]
        new_show["artist_id"] = show[1]
        new_show["venue_id"] = show[2]
        new_show["start_time"] = str(show[3])
        new_show["image_link"] = show[4]
        new_show["artist_name"] = show[5]
        new_show["venue_name"] = show[6]
        print(new_show)
        if str(show.start_time) > today:
            upcoming_shows.append(new_show)
        else:
            past_shows.append(new_show)
    upcoming_shows_count = len(upcoming_shows)
    past_shows_count = len(past_shows)

    shows = {}
    shows["past_shows"] = past_shows
    shows["upcoming_shows"] = upcoming_shows
    shows["upcoming_shows_count"] = upcoming_shows_count
    shows["past_shows_count"] = past_shows_count
    return shows

def validate_forms(model):

    def validate_phone():
        if isinstance(model, Artist):
            num = model.phone[0]
        elif isinstance(model, Venue):
            num = model.phone
        return len(num) == 12 and num[0:2].isdigit() and num[3] == '-' and num[4:6].isdigit() and num[7] == '-' and num[8:11].isdigit()

    def validate_genres():
        if isinstance(model, Artist):
            genres = model.genres[0].split(',')
        elif isinstance(model, Venue):
            genres = model.genres.split(',')
        valid = True
        genres = model.genres.split(',')
        for genre in genres:
            print(genre)
            if (genre, genre) not in form_genres_list:
                print("bad" + genre)
                valid = False
                break
        return valid  
          

    def validate_entries():
        valid = True
        if not validate_phone():
            flash("Please make sure the phone number is correctly formatted. (###-###-####)")
            valid = False
        if not validate_genres():
            flash("There was an error in the genre field.")
            valid = False
        return valid

    return validate_entries()


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: figure out a more efficient way to do this
    venue_data = []
    cities_states = db.session.query(Venue.city, Venue.state).distinct()
    for c_s in sorted(cities_states):
        city_dict = {}
        city_dict["city"] = c_s[0]
        city_dict["state"] = c_s[1]
        city_dict["venues"] = []
        venue_data.append(city_dict)

    venues = db.session.query(Venue.city, Venue.state, Venue.id, Venue.name)
    for v in venues:
        v_dict = {}
        v_dict["id"] = v[2]
        v_dict["name"] = v[3]
        v_dict["upcoming_shows_count"] = upcoming_shows_count(Venue, v[2])
        for c_s in venue_data:
            if c_s["city"] == v[0] and c_s["state"] == v[1]:
                c_s["venues"].append(v_dict)

    return render_template('pages/venues.html', areas=venue_data);

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = db.session.query(Venue).filter_by(id=venue_id).first()
    shows = get_shows(venue_id, Venue)
    venue.genres = venue.genres.split(",")
    return render_template('pages/show_venue.html', venue=venue, shows=shows)

@app.route('/venues/search', methods=['GET', 'POST'])
def search_venues():
    model = Venue
    template = 'pages/search_venues.html'
    return search(model, template)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    model_string = "venue"
    template = 'forms/new_venue.html'
    model_data = Venue(name=request.form.get('name'),
                      address=request.form.get('address'),
                      genres=','.join(request.form.getlist('genres')),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      phone=request.form.get('phone'),
                      website=request.form.get('website'),
                      facebook_link=request.form.get('facebook_link'),
                      seeking_talent=request.form.get('seeking_talent'),
                      seeking_description=request.form.get('seeking_description'),
                      image_link=request.form.get('image_link'))
    validated = validate_forms(model_data)
    if validated == True:
        return create_new(model_data, model_string, template, form)
    else:
        return render_template(template, form=form)


@app.route('/venues/delete/<venue_id>')
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
      error = False
      db.session.delete(venue)
      db.session.commit()
      flash("Venue successfully deleted!")
  except:
      error = True
      db.session.rollback()
      flash("Venue deletion failed.")
  finally:
      db.session.close()
  if error == True:
      return redirect('/venues/' + str(venue_id))
  else:
      return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artist_data = []
    artists = db.session.query(Artist.id, Artist.name)
    for a in sorted(artists):
        artist_dict = {}
        artist_dict["id"] = a[0]
        artist_dict["name"] = a[1]
        artist_data.append(artist_dict)
    return render_template('pages/artists.html', artists=artist_data)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    shows = get_shows(artist_id, Artist)
    return render_template('pages/show_artist.html', artist=artist, shows=shows)

@app.route('/artists/search', methods=['GET', 'POST'])
def search_artists():
    model = Artist
    template = 'pages/search_artists.html'
    return search(model, template)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    model = Artist
    model_string = 'artist'
    template = 'forms/edit_artist.html'
    form = ArtistForm()
    return edit_submission(artist_id, model, model_string, template, form)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    model = Venue
    model_string = 'venue'
    template = 'forms/edit_venue.html'
    form = VenueForm()
    return edit_submission(venue_id, model, model_string, template, form)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    model_string = "artist"
    template = '/artists/create.html'
    model_data = Artist(name=request.form.get('name'),
                  genres=','.join(request.form.getlist('genres')),
                  city=request.form.get('city'),
                  state=request.form.get('state'),
                  phone=request.form.get('phone'),
                  website=request.form.get('website'),
                  facebook_link=request.form.get('facebook_link'),
                  seeking_venue=request.form.get('seeking_venue'),
                  image_link=request.form.get('image_link'))
    validated = validate_forms(model_data)
    if validated == True:
        return create_new(model_data, model_string, template, form)
    else:
        return render_template(template, form=form)
    
   
#  Shows
#  ----------------------------------------------------------------
# TODO: figure out a cleaner way to do this
@app.route('/shows')
def shows():
    shows_list = []
    shows = db.session.query(Show).all()
    
    print(datetime.now)
    for show in shows:
        if str(show.start_time) > str(datetime.now()):
            artist = Artist.query.get(show.artist_id)
            venue = Venue.query.get(show.venue_id)
            new_show = {}
            new_show["venue_id"] = show.venue_id
            new_show["venue_name"] = venue.name
            new_show["artist_id"] = show.artist_id
            new_show["artist_name"] = artist.name
            new_show["image_link"] = artist.image_link
            new_show["start_time"] = str(show.start_time)
            shows_list.append(new_show)
    shows_list = sorted(shows_list, key=lambda x: x["start_time"])

    return render_template('pages/shows.html', shows=shows_list)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()

    def validate_show_submission():
        if Artist.query.get(request.form.get('artist_id')) is None or Venue.query.get(request.form.get('venue_id')) is None:
            flash('Please ensure your artist and venue IDs are valid.')
            return False
        if form.validate() is False:
            errors = form.errors.items()
            for error in errors:
                print(error)
                if error[0] == 'csrf_token':
                    if len(errors) == 1:
                        return True
                    continue
                if hasattr(form, str(error[0])):
                    flash('An error occurred in the ' + error[0] + ' field. ' + error[1][0])
            return False
        return True

    def add_show_to_db():
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        artist = db.session.query(Artist).filter_by(id=artist_id).first()
        venue = db.session.query(Venue).filter_by(id=venue_id).first()
        image_link = artist.image_link
        
        show =  Show(artist_id=artist_id,
                          venue_id=venue_id,
                          start_time=start_time)
        
        try:
            error = False
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            error = True
            db.session.rollback()
            flash('An error occurred. Show could not be listed. Please ensure your artist and venue IDs are valid.')
        finally:
          db.session.close()
          if error == True:
              return render_template('forms/new_show.html', form=form)
          else:
              return redirect(url_for('create_show_submission'))

    if validate_show_submission() is True:
        return add_show_to_db()
    else:
        return render_template('forms/new_show.html', form=form)


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
