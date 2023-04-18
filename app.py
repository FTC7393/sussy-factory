#!/usr/bin/env python3
import os
import platform
import shutil
import json
import string
import secrets
import time
from slugify import slugify
import xmpp
import phonenumbers

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

if 'queue_limit' not in config:
    config['queue_limit'] = 12
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


#may throw an exception
def standardize_phone_number(number):
    # convert phone number to +12345678900 format
    return phonenumbers.format_number(phonenumbers.parse(number, 'US'), phonenumbers.PhoneNumberFormat.E164)

#may throw a variety of exceptions (phone # format, failed to send sms, etc.)
def send_sms(number, message):
    number = standardize_phone_number(number)

    jabberid = config['xmpp_user'] #"user@chatterboxtown.us"
    password = config['xmpp_pass']
    receiver = f'{number}@cheogram.com' #"+12345678900@cheogram.com"

    jid = xmpp.protocol.JID(jabberid)
    connection = xmpp.Client(server=jid.getDomain()) #, debug=debug)
    connection.connect()
    connection.auth(user=jid.getNode(), password=password, resource=jid.getResource())
    connection.send(xmpp.protocol.Message(to=receiver, body=message))


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
    user_data['generated_stl_options'] = {'top_text': top_text, 'bottom_text': bottom_text, 'shoes': shoes}
    # print(top_text, bottom_text)
    shoes_slug = ''
    if shoes == 'true':
        shoes_slug = 'shoes'
    slug = slugify(f'amogus {top_text} {bottom_text} {shoes_slug}')
    stl_file = get_stl_path(username, slug)
    # print(stl_file)
    with open(f'data/users/{username}/parameters.scad', 'w') as f:
        f.write(f'dir = "../../.."; top_text = "{scad_escape(top_text)}"; bottom_text = "{scad_escape(bottom_text)}"; shoes = {shoes};')

    if platform.system() == "Darwin":
        os.system(f'/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD data/users/{username}/amogus-custom.scad -o {stl_file}')
    else:
        os.system(f'openscad data/users/{username}/amogus-custom.scad -o {stl_file}')
#    return send_file('{stl_file}')
    user_data['generated_stl'] = stl_file
    set_user_data(username, user_data)
    return get_stl_url_from_path(stl_file)

@app.route('/submit')
@flask_login.login_required
def submit():
    username = flask_login.current_user.id
    user_data = get_user_data(username)
    if 'submitted_stl' in user_data:
        return 'already submitted'
    if calculate_queue_length() >= config['queue_limit']:
        user_data['submit_but_queue_full'] = True
        set_user_data(username, user_data)
        return 'queue full'
    user_data['submit_but_queue_full'] = False
    # config['queue_length'] += 1
    write_config(config)
    user_data['submitted_stl'] = user_data.get('generated_stl', DEFAULT_STL_PATH)
    if 'generated_stl_options' in user_data:
        user_data['submitted_stl_options'] = user_data['generated_stl_options']
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
    if flask_login.current_user.id == username or flask_login.current_user.id == 'admin':
        filepath = get_stl_path(username, filename)
        return flask.send_file(filepath)
    else:
        return unauthorized_handler()


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


@app.route('/user/info')
@flask_login.login_required
def user_info():
    username = flask_login.current_user.id
    user_data = get_user_data(username)

    if 'submitted_stl' in user_data:
        status = 'submitted'
        stl_url = get_stl_url_from_path(user_data['submitted_stl'])
        stl_options = user_data.get('submitted_stl_options', {})
    elif 'generated_stl' in user_data:
        status = 'generated'
        stl_url = get_stl_url_from_path(user_data['generated_stl'])
        stl_options = user_data.get('generated_stl_options', {})
    else:
        status = 'default'
        stl_url = DEFAULT_STL_URL
        stl_options = {}
    return json.dumps({
        'team': user_data.get('team', ''),
        'phone': user_data.get('phone', ''),
        'status': status,
        'stl_url': stl_url,
        'stl_options': stl_options,
        'printed': user_data.get('printed', False),
        'taken': user_data.get('taken', False)
    })

@app.route('/team')
@flask_login.login_required
def team():
    username = flask_login.current_user.id
    team = flask.request.args.get('team')
    phone = flask.request.args.get('phone', '')
    user_data = get_user_data(username)
    user_data['team'] = team

    phone_return = ''
    if phone == '':
        if 'phone' in user_data:
            del user_data['phone']
    else:
        try:
            user_data['phone'] = standardize_phone_number(phone)
        except Exception as e:
            print(f'error reading phone number: {e}')
            phone_return = 'invalid'
            if 'phone' in user_data:
                del user_data['phone']
    set_user_data(username, user_data)
    return user_data.get('phone', phone_return)


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
    user_data = get_user_data(username)
    # if 'submitted_stl' in user_data:
    #     if not ('printed' in user_data and user_data['printed']):
    #         config['queue_length'] -= 1
    write_config(config)
    shutil.rmtree(f'data/users/{username}', ignore_errors=True)
    return 'ok'


@app.route('/admin/print_done')
@flask_login.login_required
def admin_print_done():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    username = flask.request.args.get('username')
    user_data = get_user_data(username)
    if 'printed' in user_data and user_data['printed']:
        return 'already set as done'
    # config['queue_length'] -= 1
    write_config(config)
    user_data['printed'] = True
    if 'phone' in user_data:
        try:
            send_sms(user_data['phone'], "Your custom among us figure is done 3D printing! Come pick it up from FTC 7393's pit area.")
        except Exception as e:
            print(f'error sending SMS: {e}')
    set_user_data(username, user_data)
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

@app.route('/queue_limit')
@flask_login.login_required
def queue_limit():
    return str(config['queue_limit'])

@app.route('/queue_length')
@flask_login.login_required
def queue_length():
    return str(calculate_queue_length())

@app.route('/queue_status')
@flask_login.login_required
def queue_status():
    queue_length = calculate_queue_length()
    queue_limit = config['queue_limit']
    return f'{queue_length}/{queue_limit}'

@app.route('/queue_spots_left')
@flask_login.login_required
def queue_spots_left():
    queue_length = calculate_queue_length()
    queue_limit = config['queue_limit']
    spots_left = queue_limit - queue_length
    return str(spots_left)

def calculate_queue_length():
    queue_length = 0
    for username in list_users():
        user_data = get_user_data(username)
        if 'submitted_stl' in user_data and not 'printed' in user_data:
            queue_length += 1
    return queue_length

@app.route('/admin/set_queue_limit')
@flask_login.login_required
def admin_set_queue_limit():
    if flask_login.current_user.id != 'admin':
        return unauthorized_handler()
    try:
        config['queue_limit'] = int(flask.request.args['queue_limit'])
        write_config(config)
    except Exception as e:
        print(f'queue_limit error: {e}')
        return 'error'
    return str(config['queue_limit'])

#TODO max char length on server and client
#TODO don't accept requests when busy generating an STL already
#TODO cache the stl files based on exact top/bottom text and avoid rebuilding



@app.route('/user')
@flask_login.login_required
def user():
    if flask_login.current_user.id == 'admin': #don't allow the admin to access the user page
        return unauthorized_handler()
    return flask.send_from_directory('frontend/dist', 'index.html')
    # return flask.render_template('user.html')

@app.route('/assets/<path:path>')
@flask_login.login_required
def send_svelte(path):
    if flask_login.current_user.id == 'admin': #don't allow the admin to access the user page
        return unauthorized_handler()
    return flask.send_from_directory('frontend/dist/assets', path)

@app.route('/base_url')
def get_base_url():
    return config['base_url']

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', debug=True)
