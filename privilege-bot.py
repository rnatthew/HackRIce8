# Python libraries that we need to import for our bot
from flask import Flask, request
from pymessenger.bot import Bot  # pymessenger is a Python wrapper for the Facebook Messenger API
# from fbmessenger import quick_replies

app = Flask(__name__)  # This is how we create an instance of the Flask class for our app

ACCESS_TOKEN = 'EAAGwXwbT9OgBAH2tHLCHgQJsKxsDLwcIk4hZBMJPvsjPG9568ywVjnV7qxelvSJoKw2tph9fOY9EHOpaT9wZBD6khEjT7ZBxlrGrskXyA6MZCMZBPpBZCUfdI3uFEegepNJBBpfmjiUdfUBDOTMey9s66axxwY1T2aMyIfffsLXwZDZD' ## Replace 'ACCESS_TOKEN' with your access token
VERIFY_TOKEN = 'TESTINGTOKEN'  # Replace 'VERIFY_TOKEN' with your verify token
bot = Bot(ACCESS_TOKEN)  # Create an instance of the bot

app.config["state"] = 0
app.config["index"] = 0
# list of privilege questions to check how much privilege you have
app.config["questions"] = ['Are new products designed with your social class in mind?',
                           'Are you able to go grocery shopping as needed, and are you able to buy healthy foods as '
                           'you please?',
                           'Are people easily able to pronounce your name?',
                           'Are people of your race widely represented in media, both positively and negatively?',
                           'Can you use public facilities (bathrooms, locker rooms, etc.) without the threat of '
                           'being attacked or harassed?',
                           'Do people know how to refer to you (pronouns) as you prefer without asking you?',
                           'Would you have immediate access to your loved one in case of emergency or accident?',
                           'Are you able to talk openly and publicly about your relationship and family planning?',
                           'Are you able to go to a new space and know that you will be able to move throughout the '
                           'space?',
                           'Are you able to assume that people are willing and able to communicate with you?',
                           'Can you afford to visit a healthcare professional multiple times per year?',
                           'Do you have access to transportation to get you where you need to go?',
                           'Can you expect to see many students and professors of your race on campus?',
                           'Do you not have to worry about being chosen last for a job or housing due to your race or '
                           'ethnicity?',
                           'Can you reasonably assume that your ability to work, rent an apartment, or secure a loan'
                           ' will not be denied on the basis of your gender identity/expression?',
                           'Is your gender an option on legal forms?',
                           'Do you expect to receive promotions as frequently and be paid the same amount as your '
                           'equally qualified colleagues?',
                           'Can you enter public spaces without being harassed?',
                           'Do you feel comfortable going somewhere alone or going on a date with someone new?',
                           'Do people not view you as an invader or threat because of your native language?'
                           ]
app.config["score"] = 0

def verify_fb_token(token_sent):
    ## Verifies that the token sent by Facebook matches the token sent locally
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

## Send text message to recipient
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response) ## Sends the 'response' parameter to the user
    return "Message sent"

## This endpoint will receive messages
@app.route("/", methods=['GET', 'POST'])

def receive_message():

    ## Handle GET requests
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token") ## Facebook requires a verify token when receiving messages
        return verify_fb_token(token_sent)

    ## Handle POST requests
    else:
       output = request.get_json() ## get whatever message a user sent the bot
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                recipient_id = message['sender']['id'] ## Facebook Messenger ID for user so we know where to send response back to

                ## If user sends text
                if "restart" in message['message'].get('text').lower():
                    app.config["state"] = 0
                    app.config["index"] = 0
                    app.config["score"] = 0
                elif app.config["state"] == 0 and ('hello' or 'hey' or 'hi' in message['message'].get('text').lower()):
                    response_sent_text = "Hi! I am Privilege Bot. Would you like check your privilege?"
                    app.config["state"] += 1
                    send_message(recipient_id, response_sent_text)
                elif app.config["state"] == 1:
                    if 'yes' in message['message'].get('text').lower():
                        send_message(recipient_id, "Great! Let's get started. Please respond with 'yes' or 'no' to "
                                                   "each question.")
                        response_sent_text = app.config["questions"][app.config["index"]]
                        send_message(recipient_id, response_sent_text)
                        app.config["index"] += 1
                        app.config["state"] += 1
                    else:
                        send_message(recipient_id, "Please come back if you would like to check your privilege! "
                                                   "Respond with 'restart' to start again!")
                elif app.config["state"] == 2:
                    if 'yes' in message['message'].get('text').lower() and app.config["index"] != 1:
                        app.config["score"] += 1
                    elif 'no' in message['message'].get('text').lower() and app.config["index"] != 1:
                        app.config["score"] += 0
                    elif 'yes' and 'no' not in message['message'].get('text').lower() and app.config["index"] != 1:
                        send_message(recipient_id, "Please respond with 'yes' or 'no'!")
                        app.config["index"] -= 1
                    response_sent_text = app.config["questions"][app.config["index"]]
                    app.config["index"] += 1
                    send_message(recipient_id, response_sent_text)

                    if app.config["index"] == len(app.config["questions"]):
                        if 'yes' in message['message'].get('text').lower():
                            app.config["score"] += 1
                        app.config["state"] += 1
                else:
                    if 'yes' in message['message'].get('text').lower() and app.config["index"] > 2:
                        app.config["score"] += 1
                    response_sent_text = "Thank you so much for checking your privilege! Your score is " \
                                         + str(app.config["score"]) + " out of " + str(len(app.config["questions"])) + \
                                         " privilege points. Each point is a privilege that you have that others may " \
                                         "not. Check out https://everydayfeminism.com/2014/09/what-is-" \
                                         "privilege/ if you want to learn more about privilege! If you want to check " \
                                         "again, respond with 'restart' to start again!"
                    send_message(recipient_id, response_sent_text)
                    app.config["state"] = 0

    return "Message Processed"



## Ensures that the below code is only evaluated when the file is executed, and ignored if the file is imported
if __name__ == "__main__":
    app.run() ## Runs application