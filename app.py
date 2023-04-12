#!/usr/bin/env python3
import os
import shutil
import json
import string
import secrets
import time
from slugify import slugify

import flask
import werkzeug.security
import flask_login

DEFAULT_STL_PATH = 'static/stl_src/default-amogus-ev-7393.stl'
DEFAULT_STL_URL = '/stl_src/default-amogus-ev-7393.stl'

os.makedirs('data/users', exist_ok=True)

def write_config(config):
    with open('data/config.json', 'w') as f:
        json.dump(config, f, indent=2)

try:
    with open('data/config.json', 'r') as f:
        config = json.load(f)
except:
    config = {}
    write_config(config)


if 'color_of_the_day' not in config:
    config['color_of_the_day'] = '#ff00ff'
    write_config(config)


app = flask.Flask(__name__, static_url_path='')
#app = Flask(__name__)
if 'app.secret_key' in config:
    app.secret_key = config['app.secret_key']
else:
    print('warning: app.secret_key not provided in config.json, falling back to hardcoded value')
    app.secret_key = 'Rfewi89h13uhfevrh9#$8302ieufn'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


def list_users():
    return sorted(os.listdir('data/users'))

def get_user_data(username):
    with open(f'data/users/{username}/data.json') as f:
        return json.load(f)

def set_user_data(username, user_data):
    with open(f'data/users/{username}/data.json', 'w') as f:
        json.dump(user_data, f)

def create_user(username, password):
    os.mkdir(f'data/users/{username}')
    os.mkdir(f'data/users/{username}/stl_files')
    shutil.copyfile('amogus-custom.scad', f'data/users/{username}/amogus-custom.scad')
    with open(f'data/users/{username}/data.json', 'w') as f:
        json.dump({'password': password}, f)

def random_password(length):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))


class User(flask_login.UserMixin):
    pass

def is_valid_username(username):
    return username in list_users() or username == 'admin'

@login_manager.user_loader
def user_loader(username):
    if not is_valid_username(username):
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if not is_valid_username(username):
        return

    user = User()
    user.id = username
    return user


@app.route('/')
def index():
    return flask.redirect(flask.url_for('login'))

@app.route('/user')
@flask_login.login_required
def user():
    if flask_login.current_user.id == 'admin': #don't allow the admin to access the user page
        return unauthorized_handler()
    return flask.render_template('user.html')

def scad_escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')

@app.route('/gen_stl')
@flask_login.login_required
def gen_stl():
    top_text = flask.request.args.get('top_text', '')
    bottom_text = flask.request.args.get('bottom_text', '')
    shoes = flask.request.args.get('shoes', '')
    if shoes != 'true':
        shoes = 'false'
    username = flask_login.current_user.id
    user_data = get_user_data(username)
    # print(top_text, bottom_text)
    shoes_slug = ''
    if shoes == 'true':
        shoes_slug = 'shoes'
    slug = slugify(f'amogus {top_text} {bottom_text} {shoes_slug}')
    stl_file = get_stl_path(username, slug)
    # print(stl_file)
    with open(f'data/users/{username}/parameters.scad', 'w') as f:
        f.write(f'dir = "../../.."; top_text = "{scad_escape(top_text)}"; bottom_text = "{scad_escape(bottom_text)}"; shoes = {shoes};')
    os.system(f'openscad data/users/{username}/amogus-custom.scad -o {stl_file}')
#    return send_file('{stl_file}')
    user_data['generated_stl'] = stl_file
    set_user_data(username, user_data)
    return get_stl_url_from_path(stl_file)

#TODO limit on the length of the print queue
@app.route('/submit')
@flask_login.login_required
def submit():
    username = flask_login.current_user.id
    user_data = get_user_data(username)
    if 'submitted_stl' in user_data:
        return 'already submitted'
    user_data['submitted_stl'] = user_data.get('generated_stl', DEFAULT_STL_PATH)
    user_data['submitted_time'] = int(time.time() * 1000)
    set_user_data(username, user_data)
    return 'ok'

def get_stl_path(username, filename):
    username = username.replace('/', '').replace('.', '')
    filename = filename.replace('/', '').replace('.', '')
    return f'data/users/{username}/stl_files/{filename}.stl'

def get_stl_url_from_path(filepath):
    if filepath == DEFAULT_STL_PATH:
        return DEFAULT_STL_URL
    # f'data/users/{username}/stl_files/{filename}.stl'
    username = filepath.split('/')[2]
    filename = filepath.split('/')[4].split('.')[0]
    return f'/get_stl/{username}/{filename}'

@app.route('/get_stl/<username>/<filename>')
@flask_login.login_required
def get_stl(username, filename):
    filepath = get_stl_path(username, filename)
    return flask.send_file(filepath)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = flask.request.form.get('username', flask.request.args.get('username'))
    password = flask.request.form.get('password', flask.request.args.get('password'))
    user = User()
    user.id = username
    if username == 'admin' and werkzeug.security.check_password_hash(config['admin_password_hash'], password):
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('admin'))
    if username in list_users():
        user_data = get_user_data(username)
        if user_data.get('password') == password:
            flask_login.login_user(user)
            user_data['logged_in'] = True
            set_user_data(username, user_data)
            return flask.redirect(flask.url_for('user'))
    return flask.render_template('login.html')


@app.route('/user_stl_and_team')
@flask_login.login_required
def user_stl_and_team():
    username = flask_login.current_user.id
    user_data = get_user_data(username)
    team = user_data.get('team', 'FTC 0000')
    if 'submitted_stl' in user_data:
        return json.dumps([team, 'submitted', get_stl_url_from_path(user_data['submitted_stl'])])
    if 'generated_stl' in user_data:
        return json.dumps([team, 'generated', get_stl_url_from_path(user_data['generated_stl'])])
    return json.dumps([team, 'default', DEFAULT_STL_URL])

@app.route('/team')
@flask_login.login_required
def team():
    username = flask_login.current_user.id
    team = flask.request.args.get('team')
    user_data = get_user_data(username)
    user_data['team'] = team
    set_user_data(username, user_data)
    return 'ok'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))
    # return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

@app.route('/admin')
@flask_login.login_required
def admin():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    return flask.render_template('admin.html')


@app.route('/admin/user_creds')
@flask_login.login_required
def admin_user_creds():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    user_creds = {}
    for username in list_users():
        user_creds[username] = get_user_data(username)
        if 'submitted_stl' in user_creds[username]:
            user_creds[username]['submitted_stl_url'] = get_stl_url_from_path(user_creds[username]['submitted_stl'])
    return user_creds


@app.route('/admin/new_users')
@flask_login.login_required
def admin_new_users():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    num_new_users = int(flask.request.args.get('num'))
    new_usernames = []
    for i in range(num_new_users):
        config['user_num'] = 1 + config.get('user_num', 0)
        write_config(config)
        username = str(config['user_num']).zfill(8)
        create_user(username, random_password(16))
        new_usernames.append(username)
    return json.dumps(new_usernames)

@app.route('/admin/delete_user')
@flask_login.login_required
def admin_delete_user():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    username = flask.request.args.get('username').replace('.', '')
    shutil.rmtree(f'data/users/{username}', ignore_errors=True)
    return 'ok'


@app.route('/admin/print_done')
@flask_login.login_required
def admin_print_done():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    username = flask.request.args.get('username')
    user_data = get_user_data(username)
    user_data['printed'] = True
    set_user_data(username, user_data)
    #TODO send a text/email?
    return 'ok'

@app.route('/admin/taken')
@flask_login.login_required
def admin_taken():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    username = flask.request.args.get('username')
    user_data = get_user_data(username)
    user_data['taken'] = True
    set_user_data(username, user_data)
    return 'ok'

@app.route('/is_printed_and_not_taken')
@flask_login.login_required
def is_printed_and_not_taken():
    username = flask_login.current_user.id
    user_data = get_user_data(username)
    printed = user_data.get('printed', False)
    taken = user_data.get('taken', False)
    return json.dumps(printed and not taken)

@app.route('/color_of_the_day')
def color_of_the_day():
    return config['color_of_the_day']

@app.route('/admin/set_color_of_the_day')
@flask_login.login_required
def admin_set_color_of_the_day():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    config['color_of_the_day'] = flask.request.args['color_of_the_day']
    write_config(config)
    return 'ok'

#TODO max char length on server and client
#TODO don't accept requests when busy generating an STL already
#TODO cache the stl files based on exact top/bottom text and avoid rebuilding

# @app.route('/stl_gen/<path:path>')
# def send_stl_gen(path):
#     return send_from_directory('stl_gen', path)

@app.route('/base_url')
def get_base_url():
    return config['base_url']

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)
