from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
import logging
import time
import pickledb
from pymongo import MongoClient, DESCENDING
import datetime
import pprint


from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
db = pickledb.load('subscribers.db', True)
client = MongoClient('mongodb://localhost:27017')

db_sensors = client['troja_sensors']
posts = db_sensors.posts

app = Flask(__name__, static_folder='web/static', template_folder='web/templates', static_url_path='')
viber = Api(BotConfiguration(
    name='Troja',
    avatar='https://www.highmowingseeds.com/media/catalog/product/cache/image/675x675/e9c3970ab036de70892d86c6d221abfe/2/4/2419.jpg',

))

def keep_a_live():
    # get lates record date
    keep_a_live_alert = 10
    time_before = datetime.datetime.now() - datetime.timedelta(minutes=keep_a_live_alert)
    for post in posts.find({"timestamp": {"$gt": time_before}}).sort("timestamp", DESCENDING):
        logger.info("Latest record found: " + str(post))
        return
    logger.warn("Latest record not found!")
    broadcast_message("Data not received from sensors. Please check connectivity") 

def report_status():
    keep_a_live_alert = 10
    hours_before = datetime.datetime.now() - datetime.timedelta(minutes=keep_a_live_alert)
    for post in posts.find({"timestamp": {"$gt": hours_before}}).sort("timestamp", DESCENDING).limit(1):
        timestamp = str(post['timestamp'])[:-7]
        sensor_value1 = post['sensor_value1']
        broadcast_message("Temprature on the moment: {0} is {1}°C".format(timestamp, sensor_value1))

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        # message = viber_request.message
        # lets echo back
        # viber.send_messages(viber_request.sender.id, [
        #     message
        # ])
        report_status()
        if viber_request.sender.id in db.getall():
            pass
        else:
            db.set(viber_request.sender.id, viber_request.sender.id)
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text="Welcome to Trojanda")
            ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        db.set(viber_request.user.id, viber_request.user.id)
        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Welcome to Trojanada")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)

# @app.route('/send', methods=['GET'])
def broadcast_message(message_text):
    subscribers = db.getall()
    for subscriber in subscribers:
        logger.info("Sending message to: {0} to client {1}".format(message_text, subscriber))
        try:
            viber.send_messages(subscriber, [
                TextMessage(text=message_text)
            ])

        except:
            logger.error("Unable to send message to {0} id".format(subscriber))
        logger.info("Sending message completed")
    return 

@app.route('/push_sensor_data', methods=['GET'])
def push_sensor_data():
    sensor_id1 = request.args.get('id1')
    sensor_value1 = request.args.get('val1')
    sensor_id2 = request.args.get('id2')
    sensor_value2 = request.args.get('val2')
    sensor_id3 = request.args.get('id3')
    sensor_value3 = request.args.get('val3')
    sensor_id4 = request.args.get('id4')
    sensor_value4 = request.args.get('val4')
    save_sensor(sensor_id1, sensor_value1, sensor_id2, sensor_value2, sensor_id3, sensor_value3, sensor_id4, sensor_value4)
    return '''Sensor {0}:{1} {2}:{3} {4}:{5} {6}:{7} '''.format(sensor_id1, sensor_value1, sensor_id2, sensor_value2, sensor_id3, sensor_value3, sensor_id4, sensor_value4)

@app.route('/pull_sensor_data', methods=['GET'])
def pull_sensor_data():
    hours = request.args.get('hours')
    hours_before = datetime.datetime.now() - datetime.timedelta(hours=int(hours))
    result = "timestamp,sensor_value1,sensor_value2,sensor_value3,sensor_value4\n"
    for post in posts.find({"timestamp": {"$gt": hours_before}}).sort("timestamp"):
        # posts.delete_one(post)
        timestamp = str(post['timestamp'])[:-7]
        sensor_id1 = post['sensor_id1']
        sensor_value1 = post['sensor_value1']
        sensor_id2 = post['sensor_id2']
        sensor_value2 = post['sensor_value2']
        sensor_id3 = post['sensor_id3']
        sensor_value3 = post['sensor_value3']
        sensor_id4 = post['sensor_id4']
        sensor_value4 = post['sensor_value4']
        try:
            result = result + "{0},{1},{2},{3},{4}\n".format(timestamp, str(float(sensor_value1)), str(float(sensor_value2)), str(float(sensor_value3)), str(float(sensor_value4)))
        except:
            logger.error("Unable to parse data: " + str(post))
        # result = result + str(post['timestamp']) + "\n"
    return result

@app.route('/init', methods=['GET'])
def init_viber_webhook():
    viber.set_webhook('https://viber.evvide.com:443/')
    return '''<h1>Init webhook completed</h1>'''

# @app.route('/.well-known/acme-challenge/<challenge>')
def letsencrypt_check(challenge):
    challenge_response = {
        challenge : "wExQShRMoO0"
    }
    return Response(challenge_response[challenge], mimetype='text/plain')

@app.route('/', methods=['GET'])
def ui():
    return app.send_static_file('ui_graph.html')

def save_sensor(sensor_id1, sensor_value1, sensor_id2, sensor_value2, sensor_id3, sensor_value3, sensor_id4, sensor_value4):
    post_data = {
        'timestamp': datetime.datetime.now(),
        'sensor_id1': sensor_id1,
        'sensor_value1': sensor_value1,
        'sensor_id2': sensor_id2,
        'sensor_value2': sensor_value2,
        'sensor_id3': sensor_id3,
        'sensor_value3': sensor_value3,
        'sensor_id4': sensor_id4,
        'sensor_value4': sensor_value4
    }
    result = posts.insert_one(post_data)
    logger.info('Saved data to DB: {0}'.format(result.inserted_id))

scheduler.add_job(func=keep_a_live, trigger="interval", seconds=600)
scheduler.add_job(func=report_status, trigger="interval", seconds=1800)

scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":

    context = ('/home/eugen/newcert/domain-crt.txt', '/home/eugen/newcert/domain-key.txt')
    app.run(host='0.0.0.0', port=443, threaded=True, debug=True, ssl_context=context)
