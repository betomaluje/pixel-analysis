import aiohttp
import os
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

async def search_by_name(game_name):
    url = f"https://store.steampowered.com/search/suggest?term={game_name}&f=games&cc=US&realm=1&l=english&v=24138598&use_store_query=1&use_search_spellcheck=1&search_creators_and_tags=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            suggestions = None

            try:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                if soup.find('a', class_='match'):
                    suggestions = []
                    for result in soup.find_all('a', class_='match'):                    
                        suggestion = {}
                        suggestion["name"] = result.find('div', class_='match_name').text.replace("\'","").strip()
                        suggestion["id"] = result["data-ds-appid"]
                        suggestions.append(suggestion)

            except Exception as e:
                print(e)

            return suggestions

async def scrape_reviews(steam_id):
    url = f"https://steamcommunity.com/app/{steam_id}/reviews/?browsefilter=toprated&snr=1_5_100010_"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            reviews = None
            title = ""

            try:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                if soup.find('div', class_='apphub_CardTextContent'):
                    reviews = []
                    for review in soup.find_all('div', class_='div.apphub_CardTextContent'):
                        reviews.append(review.text)

                if soup.find('div', class_='apphub_AppName'):
                    title_div = soup.find('div', class_='apphub_AppName')
                    title = title_div.text.strip() if title_div else "Unknown Title"

            except Exception as e:
                print(e)

            return reviews, title

async def summarize_reviews(reviews, title, prompt = None, amount_for_summary = 5, characters_per_sentence = 100):
    if reviews is None:
        return None
    
    review_type = "videogame"

    if prompt is None:
        prompt = [
            {
                "role": "user", 
                "content": f"You are a helpful, knowledgeable {review_type} assistant and journalist, specialized in summarizing reviews for the game {title}."
            },
            {
                "role": "user",
                "content": f"Given the next list of reviews for a {review_type} summarize as a bullet point list the top {amount_for_summary} best and worst thing about the game. Each item should not be more than {characters_per_sentence} characters long. Do NOT return the amount of characters per item. Here is the input json file:\n"
            },
            {
                "role": "user",
                "content": f"Desired format: Top X best:\n- -||- \n- -||- \nTop X worst:\n- -||- \n- -||- \n\n"
            },
            {
                "role": "user",
                "content": f"Text: ###\n{reviews}\n###"
            }
        ]

    max_tokens = 300
    timeout = 20.0
    temperature = 0.1
    open_ai_model = "gpt-3.5-turbo-16k"

    client = AsyncOpenAI(
        # This is the default and can be omitted
        api_key = os.getenv("GPT_KEY"),
        timeout = timeout,
    )    

    completion = await client.chat.completions.create(
        model = open_ai_model,
        max_tokens = max_tokens, 
        messages = prompt,
        temperature = temperature,
    )    
    
    return completion.choices[0].message.content