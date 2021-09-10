import os
import flask
import time
from src.db import DB, STATS_COLLECTION, ObjectId
from flask_assets import Environment
from flask_compress import Compress
from flask_talisman import Talisman, ALLOW_FROM

from src.stats import Stats


ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'K2YdnAfHLw2e7hJG'
IS_ADMIN = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG_MODE = True
DO_CACHE = False
TALISMAN = Talisman()
COMPRESS = Compress()

MAIN_ROUTE = flask.Blueprint('main', __name__, template_folder='.')


@MAIN_ROUTE.route('/')
def index_route():
    return flask.send_file('index.html')


@MAIN_ROUTE.route('/ref')
def ref_route():
    action_url, type, name = flask.request.args.get('u'), flask.request.args.get('t'), flask.request.args.get('n')

    if action_url == None or name == None or type == None:
        return flask.redirect('/')

    s = Stats(timestamp=time.time(), type=type, name=name, action_url=action_url)
    STATS_COLLECTION.insert_one(s.get_json())
    return flask.redirect(action_url, code=302, Response=None)


@MAIN_ROUTE.route('/admin', methods=['GET', 'POST'])
def admin_route():
    global IS_ADMIN

    def get_data():
        stats = STATS_COLLECTION.find({})
        counter = {}
        for stat in stats:
            if stat['name'] in counter.keys():
                counter[stat['name']]['clicks'] += 1
            else:
                counter[stat['name']] = {
                    'clicks': 1,
                    'url': stat['action_url']
                }
        return sorted(counter.items(), key=lambda d: d[1]['clicks'], reverse=True)

    if IS_ADMIN:
        return flask.render_template('admin.html', logged_in=True, table=get_data())  

    if flask.request.method == 'POST':
        if flask.request.form['username'] == ADMIN_USERNAME and flask.request.form['password'] == ADMIN_PASSWORD:
            IS_ADMIN = True
            return flask.render_template('admin.html', logged_in=True, table=get_data())
        else:
            IS_ADMIN = False

    return flask.render_template('admin.html', logged_in=False)


def create_app():
    app = flask.Flask(__name__,
                        static_url_path='', 
                        static_folder='',
                        template_folder='')
    app.config.from_object(os.getenv('APP_SETTINGS'))
    # app.json_encoder = JSONEncoder

    # Set up extensions
    #DB.init_app(app)

    if not DEBUG_MODE:  # Prevent https on localhost
        TALISMAN.init_app(app)
    COMPRESS.init_app(app)

    assets_env = Environment(app)
    for path in os.listdir('.'):
        print(' * ADDING ASSETS ->', os.path.join(BASE_DIR, path))
        assets_env.append_path(os.path.join(BASE_DIR, path))

    # Assign routes
    app.register_blueprint(MAIN_ROUTE)
    return app


APP = create_app()


@APP.template_filter('datetime')
def _jinja2_filter_datetime(date):
    return date.strftime('%d. %m. %Y')


APP.jinja_env.auto_reload = True
APP.config['TEMPLATES_AUTO_RELOAD'] = True
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


if __name__ == '__main__':

    APP.config.update(dict(
        SECRET_KEY="127ehasdlifh983h12ejewabdfags",
        WTF_CSRF_SECRET_KEY="29138hjbsadfksgfjds7f"
    ))

    if not DO_CACHE:
        @APP.after_request
        def no_cache(r):
            """
            Add headers to both force latest IE rendering engine or Chrome Frame,
            and also to cache the rendered page for 10 minutes.
            """
            APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
            r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            r.headers['Pragma'] = 'no-cache'
            r.headers['Expires'] = '0'
            r.headers['Cache-Control'] = 'public, max-age=0'
            return r


        if APP.config.get('DEBUG'):
            os.system('set FLASK_ENV=development')
            os.system('set FLASK_DEBUG=1')

    APP.run(debug=DEBUG_MODE)
