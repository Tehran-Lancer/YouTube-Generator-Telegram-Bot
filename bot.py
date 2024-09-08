from telebot import *
import requests
from collections import Counter
import re
import random
from typing import List, Tuple, Optional, Dict
import nltk  # Text analysis
from nltk.corpus import stopwords  # deletes extra words such as "the a an or in"
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import ngrams
from textblob import TextBlob
import spacy  # Text analysis

# Initialize the bot with the given token
bot = telebot.TeleBot('7502451883:AAFucmIF0k1SyTU8jrMYeFOHxwOs1ZTZvR8')

# Define a keyboard with a single button
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

api_key = 'AIzaSyDd_JZeWCun9KfjYMO26nX64jh2jYhNu8g'
# Updated YouTube categories and their corresponding emotional trigger words
youtube_caregories = {
    "Film & Animation": ["unbelievable", "groundbreaking", "must-watch", "incredible", "stunning", "amazing",
                         "breathtaking", "epic", "masterpiece", "awesome"],
    "Autos & Vehicles": ["unbelievable", "groundbreaking", "must-see", "incredible", "amazing", "shocking",
                         "revolutionary", "top", "best", "ultimate"],
    "Music": ["unbelievable", "groundbreaking", "must-listen", "incredible", "amazing", "epic", "breathtaking",
              "awesome", "top", "best"],
    "Pets & Animals": ["adorable", "heartwarming", "must-see", "incredible", "amazing", "cute", "unbelievable",
                       "awesome", "top", "best"],
    "Sports": ["unbelievable", "shocking", "amazing", "incredible", "ultimate", "insane", "must-see", "top", "crazy",
               "best"],
    "Travel & Events": ["breathtaking", "unbelievable", "must-see", "incredible", "amazing", "stunning", "awesome",
                        "top", "best", "ultimate"],
    "Gaming": ["unbelievable", "groundbreaking", "must-play", "incredible", "amazing", "epic", "awesome", "top", "best",
               "ultimate"],
    "People & Blogs": ["heartwarming", "inspiring", "must-watch", "incredible", "amazing", "unbelievable", "awesome",
                       "top", "best", "emotional"],
    "Comedy": ["hilarious", "funny", "unbelievable", "must-watch", "incredible", "amazing", "laugh-out-loud", "awesome",
               "top", "best"],
    "Entertainment": ["hilarious", "shocking", "unbelievable", "crazy", "amazing", "insane", "must-see", "incredible",
                      "top", "best"],
    "News & Politics": ["shocking", "unbelievable", "must-see", "incredible", "breaking", "exclusive", "urgent", "top",
                        "best", "critical"],
    "Howto & Style": ["life-changing", "transformative", "essential", "amazing", "unmissable", "ultimate", "proven",
                      "incredible", "must-try", "fantastic"],
    "Education": ["proven", "unbelievable", "essential", "amazing", "ultimate", "must-know", "top", "effective",
                  "secret", "best"],
    "Science & Technology": ["unbelievable", "groundbreaking", "shocking", "incredible", "amazing", "secret",
                             "ultimate", "must-see", "top", "best"],
    "Nonprofits & Activism": ["inspiring", "heartwarming", "must-see", "incredible", "amazing", "unbelievable",
                              "awesome", "top", "best", "uplifting"],
    "Movies": ["unbelievable", "must-watch", "incredible", "stunning", "epic", "masterpiece", "awesome",
               "groundbreaking", "top", "best"],
    "Shows": ["binge-worthy", "must-watch", "incredible", "amazing", "addictive", "unbelievable", "awesome", "top",
              "best", "unmissable"]
}

default_category = "Film & Animation"


# find the best category related to the keyword
def identify_category(keyword: str) -> str:
    max_similarity = 0
    best_category = default_category

    for category, trigger_words in youtube_caregories.items():
        similarity = len(set(keyword.lower().split()) & set(
            map(str.lower, trigger_words)))  # map: Convert each item in the list to a string
        if similarity > max_similarity:
            max_similarity = similarity
            best_category = category
    return best_category


# retern best titles to chose.(5 titles)
def generate_titles(keyword: str, category: str) -> List[str]:
    emotional_triggers = youtube_caregories.get(category, youtube_caregories[default_category])
    titles = []
    for _ in range(5):
        title_structure = [
            random.choice(emotional_triggers),
            keyword.title(),
            random.choice(["Secrets", "Adventures", "Discoveries", "Explorations"]),
            f"({random.choice(emotional_triggers)} Tips)"
        ]
        new_title = ' '.join(title_structure)
        titles.append(new_title[:70].strip())
    return titles


# gets top 5 videos from youtube:
def get_top_videos(api_key: str, query: str, max_results: int = 50) -> Optional[List[dict]]:
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults={max_results}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.RequestException as e:
        print(f"Error fetching videos: {e}")
        return None


# replace all occurrences of a pattern with a new string.
def preprocess_text(text: str) -> str:
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.lower().split())


# adjust the description with users keyword and selected category
def generate_description(keyword: str, category: str, title: str) -> str:
    emotional_triggers = youtube_caregories.get(category, youtube_caregories[default_category])
    intro = f"{random.choice(emotional_triggers)}! {title} 🚀"
    content_details = f"Embark on an extraordinary journey into the world of {keyword}. Discover hidden gems, expert insights, and breathtaking experiences that will leave you in awe."
    cta = f"🔔 {random.choice(emotional_triggers)}! SUBSCRIBE now for {random.choice(emotional_triggers)} {keyword} content!"
    engagement = f"👇 Share your {random.choice(emotional_triggers)} thoughts! What's your experience with {keyword}?"
    outro = f"Don't miss out on our upcoming videos about {keyword} and related topics. Stay tuned for more {random.choice(emotional_triggers)} content!"

    description = f"{intro}\n\n{content_details}\n\n{cta}\n\n{engagement}\n\n{outro}"

    return description[:2000].strip()


# find the best tags related to the keyword
def generate_tags(keyword: str, category: str) -> List[str]:
    emotional_triggers = youtube_caregories.get(category, youtube_caregories[default_category])
    base_tags = keyword.split()
    related_terms = emotional_triggers[:10]  # Use top 10 emotional triggers as related terms

    tags = [keyword] + base_tags + related_terms
    tags += [f"{keyword} {term}" for term in related_terms]
    tags += [f"{term} {keyword}" for term in related_terms]

    # Remove duplicates and limit to 30 tags
    return list(dict.fromkeys(tags))[:30]


# find the best and related hashtags
def generate_hashtags(tags: List[str], keyword: str) -> List[str]:
    hashtags = [f"#{tag.replace(' ', '')}" for tag in tags[:14] if len(tag) > 2]
    keyword_hashtag = f"#{keyword.replace(' ', '')}"
    if keyword_hashtag not in hashtags:
        hashtags.insert(0, keyword_hashtag)
    return list(dict.fromkeys(hashtags))[:15]


# calculate the seo score depended to the tags, hashtags, description and the title.
def calculate_seo_score(title: str, description: str, tags: List[str], hashtags: List[str]) -> int:
    score = 0
    if len(title) <= 70:
        score += 20
    if 500 <= len(description) <= 2000:
        score += 30
    score += min(len(tags), 30)
    score += min(len(hashtags) * 2, 20)
    return min(score, 100)


def generate_seo_content(query: str) -> Tuple[str, str, List[str], List[str], int, Dict[str, int], str]:
    category = identify_category(query)
    titles = generate_titles(query, category)

    print("\nGenerated Titles:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    while True:
        try:
            title_choice = int(input("\nSelect a title (1-5): ")) - 1
            selected_title = titles[title_choice]
            break
        except IndexError:
            print("Invalid choice. Please try again.")
        except:
            print("Invalid choice. Please try again.")
    new_description = generate_description(query, category, selected_title)
    new_tags = generate_tags(query, category)
    new_hashtags = generate_hashtags(new_tags, query)

    seo_score = calculate_seo_score(selected_title, new_description, new_tags, new_hashtags)

    return selected_title, new_description, new_tags, new_hashtags, seo_score, category


# returns the final seo content
def process_keyword(keyword: str) -> None:
    print(f"\nGenerating SEO Content for '{keyword}'...")
    title, description, tags, hashtags, seo_score, category = generate_seo_content(keyword)
    print(f"\n{'=' * 80}\nSEO Content\n{'=' * 80}")
    print(f"\nIdentified Category: {category}")
    print(f"\nSelected Title:\n{title}")
    print(f"\nDescription:\n{description}")
    print(f"\nTags:\n{', '.join(tags)}")
    print(f"\nHashtags:\n{' '.join(hashtags)}")
    print(f"\nSEO Score: {seo_score}/100")

    # Fetch top 5 videos
    top_videos = get_top_videos(api_key, keyword)
    if top_videos:
        print(f"\nTop 5 Related Videos:")
        for i, video in enumerate(top_videos[:5], 1):
            print(f"{i}. {video['snippet']['title']}")


class States:
    WAITING_FOR_KEYWORD = 'waiting_for_keyword'
    WAITING_FOR_TITLE_SELECTION = 'waiting_for_title_selection'


user_states = {}


@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    user_states[user_id] = {'keyword': '', 'state': States.WAITING_FOR_KEYWORD}
    bot.send_message(message.chat.id, "به YouTube SEO Generator خوش آمدید!", reply_markup=keyboard)
    bot.send_message(message.chat.id, "یک کلمه کلیدی برای تولید محتوای سئو وارد کنید:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.chat.id
    user_message = message.text

    if user_states.get(user_id).get('state') == States.WAITING_FOR_KEYWORD:
        user_states[user_id]['keyword'] = user_message
        user_states[user_id]['state'] = States.WAITING_FOR_TITLE_SELECTION

        category = identify_category(user_message)
        titles = generate_titles(user_message, category)

        keyboard = types.InlineKeyboardMarkup()
        for title in titles:
            button = types.InlineKeyboardButton(text=title, callback_data=title)
            keyboard.add(button)

        bot.send_message(message.chat.id, "لطفاً یکی از عناوین را انتخاب کنید:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.from_user.id
    user_state = user_states.get(user_id)
    keyword = user_state.get('keyword')

    if user_state.get('state') == States.WAITING_FOR_TITLE_SELECTION:
        selected_title = call.data

        category = identify_category(keyword)
        description = generate_description(keyword, category, selected_title)
        tags = generate_tags(keyword, category)
        hashtags = generate_hashtags(tags, keyword)
        seo_score = calculate_seo_score(selected_title, description, tags, hashtags)

        response_message = (
            "SEO Content:\n"
            f"Category: {category}\n"
            f"Title: {selected_title}\n"
            f"Description: {description}\n\n"
            f"Tags: {', '.join(tags)}\n\n"
            f"Hashtags: {' '.join(hashtags)}\n\n"
            f"SEO Score: {seo_score}\n"
        )

        top_videos = get_top_videos(api_key, keyword)
        if top_videos:
            response_message += "\nTop 5 Related Videos:\n"
            for i, video in enumerate(top_videos[:5], 1):
                response_message += f"{i}. {video['snippet']['title']}\n"

        bot.send_message(call.message.chat.id, response_message)
        user_states[user_id] = {'keyword': '', 'state': States.WAITING_FOR_KEYWORD}
    else:
        bot.send_message(call.message.chat.id, "یک خطا رخ داده است. لطفاً دوباره امتحان کنید.")


bot.polling()
