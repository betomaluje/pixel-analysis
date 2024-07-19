import aiohttp
import os
import requests
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
import time
from token_counter import TokenBuffer

async def search_by_name(game_name):
    if not game_name:
        return []
    
    url = f"https://store.steampowered.com/search/suggest?term={game_name}&f=games&cc=US&realm=1&l=english&v=24138598&use_store_query=1&use_search_spellcheck=1&search_creators_and_tags=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            suggestions = []

            try:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                if soup.find('a', class_='match'):                    
                    for result in soup.find_all('a', class_='match'):                    
                        suggestion = {}
                        suggestion["name"] = result.find('div', class_='match_name').text.replace("\'","").strip()
                        suggestion["id"] = result["data-ds-appid"]
                        suggestions.append(suggestion)

            except Exception as e:
                print(e)

            return suggestions

def get_reviews(steam_id, params = {'json' : 1}):
        url = f'https://store.steampowered.com/appreviews/{steam_id}'
        response = requests.get(url = url, params = params, headers = {'User-Agent': 'Mozilla/5.0'})
        return response.json()
    
async def get_n_reviews(steam_id, n):
    reviews = []
    cursor = '*'
    params = {
            'json' : 1,
            'filter' : 'recent',
            'language' : 'english',
            'day_range' : 365,
            'review_type' : 'all',
            'purchase_type' : 'all'
            }

    num_reviews_per_page = min(n, 100)

    start = time.time()
    review_length_threshold = 50

    while n > 0:
        params['cursor'] = cursor.encode()
        params['num_per_page'] = num_reviews_per_page
        n -= 1

        response = get_reviews(str(steam_id), params)
        
        cursor = response['cursor']
        for r in response['reviews']:
            if r['review'] and len(r['review']) > review_length_threshold:
                reviews.append(r['review'])

        if len(response['reviews']) < num_reviews_per_page: break

    end = time.time()
    print(f"Time: {end - start} (s) | total reviews: {len(reviews)}\n")

    return reviews    

async def summarize_reviews(steam_id, title, to_search = 10, custom_prompt = None, amount_for_summary = 3, characters_per_sentence = 100):
    reviews = await get_n_reviews(steam_id, to_search)

    if reviews is None:
        return None
    
    review_type = "videogame"    

    if not custom_prompt:
        prompt = [
            {
                "role": "system", 
                "content": f"You are a helpful, expert {review_type} assistant and journalist, specialized in summarizing reviews for the game {title}."
            },
            {
                "role": "user", 
                "content": f"Now I'll give you a list of reviews that you will use them as reference for your review analysis."
            },
            {
                "role": "user",
                "content": f"Given the next list of reviews for a {review_type} summarize as a bullet point list the top {amount_for_summary} best and worst thing about the game. Each item should not be more than {characters_per_sentence} characters long. Do NOT return the amount of characters per item.\n"
            },
            {
                "role": "user",
                "content": f"Desired format: Top X best:\n- -||- \n- -||- \nTop X worst:\n- -||- \n- -||- \n\n"
            },
            {
                "role": "user",
                "content": f"Input Text is coming below with the format ###\n[INPUT]\n### where [INPUT] is a list of the reviews"
            }
        ]
    else:
        prompt = [
            {
                "role": "user",
                "content": f"###\n{custom_prompt}\n###"
            },
            {
                "role": "user",
                "content": f"Use this {review_type} title name: {title} as a reference for your answer."
            }
        ]

    open_ai_model = "gpt-4o-mini"

    model_max_tokens = get_context_length(open_ai_model)
    print(f"model_max_tokens: {model_max_tokens}")

    buffer = TokenBuffer(max_tokens = model_max_tokens)
    if prompt is str:
        buffer.update(prompt)
    else:    
        for item in prompt:
            # print(f"{item['role']}: {item['content']}")
            buffer.update(item["role"])
            buffer.update(item["content"])
    
    print(f"Before adding reviews: {buffer.token_count} tokens")

    text_reviews = ""
    for review in reviews:
        if buffer.token_count < model_max_tokens - 5: # we put an extra 5 tokens for the last instruction
            # print(f"Adding review: {review}")
            text_reviews += review + "\n"
            buffer.update(review)
            # print(f"Buffer: {buffer.token_count} tokens")
        else:
            break

    last_instruction = {
        "role": "user",
        "content": f"[INPUT]: {text_reviews}"
    }

    prompt.append(last_instruction)

    print(f"After adding reviews: {buffer.token_count} tokens")

    timeout = 20.0
    temperature = 0.1

    client = AsyncOpenAI(
        # This is the default and can be omitted
        api_key = os.getenv("GPT_KEY"),
        timeout = timeout,
    )    
    try:
        completion = await client.chat.completions.create(
            model = open_ai_model,
            max_tokens = buffer.token_count, 
            messages = prompt,
            temperature = temperature,
        )    
        
        return completion.choices[0].message.content

    except Exception as e:
        print(e)
        return "We can't generate a summary now. Please try again in a minute or so.\n"

def get_context_length(model):
    if model == "gpt-3.5-turbo-0613":
        return 4096
    elif model == "gpt-4o-mini":
        return 16384
    # Add additional model context windows here.
    else:
        raise ValueError(f"No context length known for model: {model}")