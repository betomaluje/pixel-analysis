import json
import os
import requests
from bs4 import BeautifulSoup
from abilities import llm_prompt

import aiohttp
import asyncio

async def scrape_reviews(steam_id):
    url = f"https://steamcommunity.com/app/{steam_id}/reviews/?browsefilter=toprated&snr=1_5_100010_"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            reviews = []
            for review in soup.find_all('div', class_='div.apphub_CardTextContent'):
                reviews.append(review.text)
            title_div = soup.find('div', class_='apphub_AppName')
            title = title_div.text.strip() if title_div else "Unknown Title"
            return reviews, title

async def summarize_reviews(reviews, title, amount_for_summary = 5, characters_per_sentence = 100):
    review_type = "videogame"

    prompt = (
        f"You are a helpful, knowledgeable {review_type} assistant that summarizes reviews for this game.\n"
        f"Given the next list of reviews for a {review_type} summarize as a bullet point list the top {amount_for_summary} best and worst thing about the game. Each item should not be more than {characters_per_sentence} characters long. Do NOT return the amount of characters per item. Here is the input json file:\n"
        f"Desired format: Top X best:\n- -||- \n- -||- \nTop X worst:\n- -||- \n- -||- \n\n"
        f"Text: ###\n{reviews}\n###"
    )

    response = llm_prompt(prompt, model="gpt-3.5-turbo", temperature=0.1)
    return response

async def search_by_name(game_name):
    url = f"https://store.steampowered.com/search/suggest?term={game_name}&f=games&cc=US&realm=1&l=english&v=24138598&use_store_query=1&use_search_spellcheck=1&search_creators_and_tags=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            suggestions = []
            for result in soup.find_all('a', class_='match'):
                suggestion = {}
                suggestion["name"] = result.find('div', class_='match_name').text.replace("\'","").strip()
                suggestion["id"] = result["data-ds-appid"]
                suggestions.append(suggestion)
            return suggestions