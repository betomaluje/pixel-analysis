import aiohttp
import os
from flask import json
import requests
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
import time
from token_counter import TokenBuffer

OPEN_AI_MODEL = "gpt-4o-mini"
MAX_REVIEWS_ALLOWED = 500

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

        if response['success'] != 1:
            return None        

        cursor = response['cursor']

        for r in response['reviews']:
            if r['review'] and len(r['review']) > review_length_threshold:
                reviews.append(r['review'])

        if len(response['reviews']) < num_reviews_per_page: break

    end = time.time()

    if len(reviews) > MAX_REVIEWS_ALLOWED:
        reviews = reviews[:MAX_REVIEWS_ALLOWED]
    
    print(f"Found {len(reviews)} reviews in {end - start} seconds")
    return reviews    

async def summarize_reviews(steam_id, title, to_search = 10, custom_prompt = None, amount_for_summary = 3, characters_per_sentence = 100):
    reviews = await get_n_reviews(steam_id, to_search)

    if reviews is None:
        return (0, f"Error: We are having a problem getting the Steam reviews for {title}. Please try again later.")
    
    review_type = "videogame"    

    if not custom_prompt:
        prompt = [
            {
                "role": "system", 
                "content": f"You are a helpful, expert {review_type} assistant and journalist, specialized in summarizing reviews for the videogame {title}."
            },
            {
                "role": "user", 
                "content": f"Now I'll give you a list of reviews that you will use them as reference for your review analysis."
            },
            {
                "role": "user",
                "content": f"Given the next list of reviews for a {review_type} summarize as a bullet point list the main ideas of each, highlighting the {amount_for_summary} best and worst things. Each item should not be more than {characters_per_sentence} characters long. Do NOT return the amount of characters per item.\n"
            },
            {
                "role": "user",
                "content": f"Use Plain Text. Desired format: Top X best:\n- -||- \n- -||- \nTop X worst:\n- -||- \n- -||- \n\n"
            },
            {
                "role": "user",
                "content": f"Input reviews come below with the format ###\n[INPUT]\n### where [INPUT] is a list of the reviews"
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

    timeout = 20.0
    temperature = 0.1

    client = AsyncOpenAI(
        # This is the default and can be omitted
        api_key = os.getenv("GPT_KEY"),
        timeout = timeout,
    )

    total_reviews = len(reviews)
    current_reviews = 0
    total_response = []

    while current_reviews < total_reviews:
        # we need to create a sublist of the remaining reviews items
        reviews_sublist = reviews[current_reviews : ]
        if len(reviews_sublist) <= 0:
            break
        (next_index, response) = await get_list_from_openai(client, reviews_sublist, prompt)
        if response is None:
            break
        total_response.append(response)
        current_reviews += next_index
        time.sleep(4)

    # print(f"Total response:\n{total_response}\n")

    model_max_tokens = get_input_length(OPEN_AI_MODEL)

    timeout = 20.0
    temperature = 0.1

    more_prompt = [
        {
            "role": "assistant",
            "content": f"{json.dumps(total_response)}"
        },
        {
            "role": "user",
            "content": f"Group and summarize this text in {amount_for_summary} bullet points for best and worst highlights."
        },
        {
            "role": "user",
            "content": f"Use clear separation between the Top X Best and Top X Worst characteristics. Use html formatting."
        }
    ]
    
    buffer = TokenBuffer(max_tokens = model_max_tokens)
    for item in more_prompt:
        buffer.update(item["role"])
        buffer.update(item["content"])
   
    try:
        completion = await client.chat.completions.create(
            model = OPEN_AI_MODEL,
            max_tokens = min(model_max_tokens, buffer.token_count), 
            messages = prompt,
            temperature = temperature,
        )    
        
        return (current_reviews, completion.choices[0].message.content)        
    except Exception as e:
        print(e)
        if len(total_response) > 0:
            return (current_reviews, "Error: We can't generate a perfect summary now. Please try again in a minute or so.\nThis is what we gathered so far:\n\n" + total_response[0])
        else:
            return (0, "Error: We can't generate a perfect summary now. Please try again in a minute or so.\n")

async def get_list_from_openai(openAIClient: AsyncOpenAI, reviews: list, prompt: list):    
   
    model_max_tokens = get_input_length(OPEN_AI_MODEL)
    buffer = TokenBuffer(max_tokens = model_max_tokens)
    
    for item in prompt:
        buffer.update(item["role"])
        buffer.update(item["content"])

    text_reviews = ""
    review_index = 0

    for review in reviews:
        if buffer.token_count < model_max_tokens - 5: # we put an extra 5 tokens for the last instruction
            text_reviews += str(review) + "\n"
            buffer.update(str(review))
        else:
            break
        review_index += 1

    last_instruction = {
        "role": "user",
        "content": f"[INPUT]: {text_reviews}"
    }

    prompt.append(last_instruction)

    temperature = 0.1

    try:
        completion = await openAIClient.chat.completions.create(
            model = OPEN_AI_MODEL,
            max_tokens = buffer.token_count, 
            messages = prompt,
            temperature = temperature,
        )    
        
        return (review_index, completion.choices[0].message.content + "\n")
    except Exception as e:
        print(e)
        return (review_index, None)

def get_input_length(model):
    if model == "gpt-3.5-turbo-0125":
        return 4096
    elif model == "gpt-4o-mini":
        return 16384
    # Add additional model context windows here.
    else:
        raise ValueError(f"No context length known for model: {model}")