import random
from datetime import datetime


# Response dictionary
RESPONSES = {
    "greeting": [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Hey! Need help finding something?",
        "Hello! I'm here to assist you."
    ],
    "morning": [
        "Good morning! How can I help you today?"
    ],
    "afternoon": [
        "Good afternoon! How can I help you today?"
    ],
    "evening": [
        "Good evening! How can I help you today?"
    ],
    "how_are_you": [
        "I'm doing great! How can I assist you?",
        "I'm functioning perfectly! What can I help you with?",
        "All systems operational! How may I help?"
    ],
    "thanks": [
        "You're welcome!",
        "Happy to help!",
        "Anytime!",
        "Glad I could help!"
    ],
    "goodbye": [
        "Goodbye! Have a great day!",
        "See you soon!",
        "Take care!",
        "Bye! Come back anytime!"
    ],
    "bot": [
        "I'm your shopping assistant. I can help you find products and answer your questions.",
        "I'm an AI assistant here to help you with shopping.",
        "I help with product search, FAQs, and general queries."
    ],
    "fallback": [
        "I'm here to help! Please let me know what you need.",
        "How can I assist you today?",
        "Feel free to ask me anything about products or orders."
    ]
}


def get_time_based_greeting():

    hour = datetime.now().hour

    if hour < 12:
        return random.choice(RESPONSES["morning"])

    elif hour < 18:
        return random.choice(RESPONSES["afternoon"])

    else:
        return random.choice(RESPONSES["evening"])



def handle_smalltalk(query: str) -> str:

    query = query.lower().strip()

    # Time greetings
    time_keywords = ("good morning", "good afternoon", "good evening")

    if any(keyword in query for keyword in time_keywords):
        return get_time_based_greeting()


    # Basic greetings
    if any(word in query for word in ["hello", "hi", "hey"]):
        return random.choice(RESPONSES["greeting"])


    # How are you
    if "how are you" in query:
        return random.choice(RESPONSES["how_are_you"])


    # Thanks
    if any(word in query for word in ["thank you", "thanks"]):
        return random.choice(RESPONSES["thanks"])


    # Goodbye
    if any(word in query for word in ["bye", "goodbye"]):
        return random.choice(RESPONSES["goodbye"])


    # Bot identity
    if any(word in query for word in ["who are you", "what are you"]):
        return random.choice(RESPONSES["bot"])


    # fallback
    return random.choice(RESPONSES["fallback"])