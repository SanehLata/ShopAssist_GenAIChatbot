from semantic_router import Route
from semantic_router import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        "Do you accept cash or card?",
        "Do you have return policy for defective products ?",
        "Do you have return policy for women accessories like jewellery ?",
        "What if the received jewellery items are defective"

    ],
    score_threshold=0.3
)

sql = Route(
    name='sql',
    utterances=[
        "I want to buy women shoes that have 50% discount.",
        "Are there any shoes under 30$",
        "Do you have formal shoes in size 9?",
        "Are there any wedding shoes on sale?",
        "What is the price of man's running shoes?",
        "Sports shoes for men in white color"
        "Necklace for women",
        "rings for women",
        "ear rings for women",
        "jewellery for women",
        "accessories for women for wedding and parties",
        "wedding accessories for women",
        "party accessories for women",
        "jewellery for women for wedding and parties",
        "necklace for women for wedding and parties",
        "ear rings for women for wedding and parties",
        "rings for women for wedding and parties",
    ],
    score_threshold=0.3
)

smalltalk = Route(
    name='smalltalk',
    utterances=[
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "what are you",
        "who are you",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
        "nice to meet you"
    ],
    score_threshold=0.3
)

router = SemanticRouter(encoder=encoder, routes=[faq, sql,smalltalk], auto_sync="local")

if __name__ == "__main__":
    print(router("What is your policy on defective product?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000").name)