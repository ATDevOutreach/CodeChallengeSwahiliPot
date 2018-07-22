import json
import logging
import os
import threading
import time
from functools import wraps

from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import Blueprint, make_response, current_app
from flask import g, request

from . import redis

main = Blueprint('main', __name__)


##############################################
############ africastalking configuration ####
##############################################
class Gateway(AfricasTalkingGateway):
    @classmethod
    def init_gateway(cls):
        username = os.environ.get('AT_USERNAME', 'sandbox')
        apiKey = os.environ.get('AT_APIKEY', "your api key")
        environment = os.environ.get('AT_ENVIRONMENT', 'sandbox')
        return cls(apiKey=apiKey, username=username, environment=environment)


gateway = Gateway.init_gateway()


###############################################
############# Decorators #######################
################################################
def async(f):
    """
    Decorator to run fucntion as a backgorund thread
    :param f:
    :return:
    """

    def wrapper(*args, **kwargs):
        thr = threading.Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


def validate_ussd_user(func):
    """
    Parse request from Africastalking
    track user session_id and level
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # get user response
        text = request.values.get("text", "default")
        user_response = text.split("*").pop()
        # get phone number
        phone_number = request.values.get("phoneNumber")
        # get session id
        session_id = request.values.get("sessionId")
        # get session
        session = redis.get(session_id)
        if session is None:
            session = {"level": 0, "session_id": session_id}
            redis.set(session_id, json.dumps(session))
        else:
            session = json.loads(session.decode())
        # add user, response and session to the request variable g
        g.user_response = user_response
        g.session = session
        g.phoneNumber = phone_number
        g.session_id = session_id
        logging.info("level {}".format(g.session.get('level')))
        return func(*args, **kwargs)

    return wrapper


#####################################################
################ Utility functions ##################
#####################################################
@async
def send_airtime(app, phoneNumber, amount, cb):
    # send airtime via africastalking api
    with app.app_context():
        recipients = [{"phoneNumber": phoneNumber,
                       "amount": "KES {}".format(amount)}]
        try:
            responses = gateway.sendAirtime(recipients)
            for response in responses:
                phoneNumber = response['phoneNumber']
                amount = response['amount']
                status = response['status']
                while status != "Failed":
                    app.logger.info("Airtime sent with status: "+status)
                    return cb(app=app, to_=phoneNumber, text="We have sent you {amount} of Airtime".format(amount=amount))
        except AfricasTalkingGatewayException as e:
            app.logger.error("Encountered error when sending airtime: ", e)
            return -1


@async
def send_mobile_checkout(app, phoneNumber, amount):
    """
    sends mobile money checkout
    :param current_app:
    :param phoneNumber:
    :param amount:
    :return:
    """
    time.sleep(5)  # wait for ussd session to end
    with app.app_context():
        try:
            # Initiate the checkout. If successful, you will get back a transactionId
            transactionId = gateway.initiateMobilePaymentCheckout(
                productName_=app.config["AT_PRODUCT_NAME"],
                providerChannel_=app.config["AT_PROVIDER_CHANNEL"],
                phoneNumber_=phoneNumber,
                currencyCode_="KES",
                amount_=amount,
                metadata_={"name": "Nerd Payment",
                           "reason": "Checkout"})
            app.logger.info(transactionId)
            return 1
        except AfricasTalkingGatewayException as exc:
            app.logger.error(str(exc))
            return -1


@async
def send_sms(app, text, to_):
    """send an sms via AT"""
    with app.app_context():
        try:
            resp = gateway.sendMessage(to_=to_, from_=app.config["AT_SENDER_ID"], message_=text)
            app.logger.info(resp)
            return 1
        except AfricasTalkingGatewayException as exc:
            app.logger.error(str(exc))
            return -1


def make_response_(text, prefix="CON"):
    """
    create a http response object
    :param text:
    :param prefix:
    :return:
    """
    menu_text = " ".join([prefix.strip(), text.strip()])
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


###########################################
################## routes  #################
################################################
@main.route('/')
def index():
    return make_response("echo back", 200)


@main.route('/ussd', methods=["POSt"])
@validate_ussd_user
def ussd():
    """
    :return:
    """
    session_id = g.session_id
    phoneNumber = g.phoneNumber
    session = g.session
    user_response = g.user_response
    if session["level"] == 1:
        if user_response == str(1):
            session["level"] = 10
            text = "Buy airtime\nPlease select amount\n"
            redis.set(session_id, json.dumps(session))
            return make_response_(text)
        if user_response == str(2):
            session["level"] = 5
            text = "Mobile Checkout\nPlease select amount"
            redis.set(session_id, json.dumps(session))
            return make_response_(text)
    if session["level"] == 10 and user_response.isdigit():
        text = "You will receive airtime worth KES {amount} shortly.".format(amount=user_response)
        send_airtime(app=current_app._get_current_object(), amount=float(user_response), phoneNumber=phoneNumber, cb=send_sms)

        return make_response_(text, "END")
    if session["level"] == 5 and user_response.isdigit():
        text = "We are sending you a mobile checkout of KES {} shortly".format(user_response)
        send_mobile_checkout(app=current_app._get_current_object(), phoneNumber=phoneNumber, amount=float(user_response))
        return make_response_(text, "END")
    else:
        text = "Welcome to PotHub USSD\n1. Buy airtime.\n2. Send mobile money checkout.\n"
        session["level"] = 1
        redis.set(session_id, json.dumps(session))
        return make_response_(text)
