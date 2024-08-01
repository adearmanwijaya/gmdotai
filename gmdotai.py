import requests
from colorama import Fore, Style, init
import json

# Initialize colorama
init()

# Function to get quest list
def get_quest_list(headers, category):
    url = f'https://mini-app-api.gm.ai/users/quests?take=40&page=1&sort_field=order&sort_type=ASC&category={category}'
    response = requests.get(url, headers=headers)
    return response.json()

# Function to get balance
def get_balance(headers):
    url = 'https://mini-app-api.gm.ai/users/profile'
    response = requests.get(url, headers=headers)
    return response.json()

# Function to complete a quest
def complete_quest(quest_id, quest_title, headers, telegram_name):
    url = 'https://mini-app-api.gm.ai/users/user-quest'
    data = {
        'quest_id': quest_id
    }
    response = requests.put(url, headers=headers, json=data)
    completion_response = response.json()
    if completion_response.get('error') == 'Bad Request' and completion_response.get('message') == 'Quest already completed' and completion_response.get('statusCode') == 400:
        print(Fore.GREEN + Style.BRIGHT + f"{telegram_name} | Quest already completed {quest_title}" + Style.RESET_ALL)
    elif completion_response.get('messages') == 'Success':
        print(Fore.GREEN + Style.BRIGHT + f"{telegram_name} | Successfully completed quest {quest_title}" + Style.RESET_ALL)
    elif completion_response.get('message') == 'User not connect twitter':
        print(Fore.RED + f"{telegram_name} | Quest not connected to Twitter" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"{telegram_name} | {quest_title} : {completion_response.get('message')}" + Style.RESET_ALL)
    return completion_response

# Function to process quests
def process_quests(headers, category, telegram_name):
    quest_list_response = get_quest_list(headers, category)
    if 'data' in quest_list_response and 'data' in quest_list_response['data']:
        quest_list = quest_list_response['data']['data']
        if isinstance(quest_list, list):
            for quest in quest_list:
                if isinstance(quest, dict) and 'id' in quest:
                    quest_id = quest['id']
                    quest_title = quest['title']
                    # print(quest)
                    complete_quest(quest_id, quest_title, headers, telegram_name)
                else:
                    print(Fore.RED + f"Unexpected quest format: {quest}" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Unexpected quest list format: ", quest_list, Style.RESET_ALL)
    else:
        print(Fore.RED + "Unexpected quest list response format: ", quest_list_response, Style.RESET_ALL)

# Function to get token using requests
def get_token(auth_data):
    url = 'https://mini-app-api.gm.ai/users/login'
    params = {
        'auth_data': auth_data
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'en,id-ID;q=0.9,id;q=0.8,en-US;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://mini-app.gm.ai',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://mini-app.gm.ai/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; M2012K11AG Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.186 Mobile Safari/537.36',
        'x-requested-with': 'org.telegram.messenger.web'
    }
    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    return response_json['data']['accessToken'], response_json['data']['user']['telegram_name']  # Adjust this line based on the actual response structure

# Function to process an account
def check_and_create_wallet(headers, telegram_name):
    url = 'https://mini-app-api.gm.ai/users/quests?take=40&page=1&sort_field=order&sort_type=ASC&category=onboarding'
    response = requests.get(url, headers=headers)
    quest_list_response = response.json()

    if 'data' in quest_list_response and 'data' in quest_list_response['data']:
        quest_list = quest_list_response['data']['data']
        for quest in quest_list:
            if quest['id'] == '7371196e-3ff6-4c25-bcce-b566cf7ee118':
                if quest['user_quest_status'] == 'success':
                    print(Fore.GREEN + f"{telegram_name} | Wallet already connected" + Style.RESET_ALL)
                    return
                break

    # Create new wallet
    url = 'https://mini-app-api.gm.ai/users/wallet'
    response = requests.post(url, headers=headers)
    wallet_response = response.json()

    if wallet_response.get('messages') == 'Success':
        mnemonic = wallet_response['data']['mnemonic']
        print(Fore.GREEN + f"{telegram_name} | Wallet created: {mnemonic}" + Style.RESET_ALL)

        # Confirm wallet
        url = 'https://mini-app-api.gm.ai/users/wallet/confirm'
        response = requests.post(url, headers=headers)
        confirm_response = response.json()

        if confirm_response.get('messages') == 'Success':
            print(Fore.GREEN + f"{telegram_name} | Wallet confirmed" + Style.RESET_ALL)
            with open('account_details.txt', 'a') as file:
                file.write(f"{telegram_name} | {mnemonic}\n")
        else:
            print(Fore.RED + f"{telegram_name} | Wallet confirmation failed" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"{telegram_name} | Wallet creation failed" + Style.RESET_ALL)

# Function to process an account
def process_account(auth_data):
    # Get token and telegram_name
    token, telegram_name = get_token(auth_data)

    # Set headers
    headers = {
        'accept': '*/*',
        'accept-language': 'en,id-ID;q=0.9,id;q=0.8,en-US;q=0.7',
        'authorization': f'Bearer {token}',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://mini-app.gm.ai',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://mini-app.gm.ai/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Android WebView";v="126"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; M2012K11AG Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.186 Mobile Safari/537.36',
        'x-requested-with': 'org.telegram.messenger.web'
    }

    # Check and create wallet if necessary
    check_and_create_wallet(headers, telegram_name)

    # Process basic quests
    process_quests(headers, 'basic', telegram_name)

    # Process daily quests
    process_quests(headers, 'daily', telegram_name)

    # Get balance and Telegram name after completing all quests
    balance_response = get_balance(headers)
    if 'data' in balance_response:
        user_data = balance_response['data']
        telegram_name = user_data.get('telegram_name', 'N/A')
        balance = user_data.get('total_point', 0)
        print(f"{Fore.YELLOW + Style.BRIGHT}{telegram_name} | Balance: {balance}\n\n")
    else:
        print(Fore.RED + "Unexpected balance response format: ", balance_response, Style.RESET_ALL)

# Read auth_data from query.txt and process each account
with open('query.txt', 'r') as file:
    for line in file:
        auth_data = line.strip()
        if auth_data:
            process_account(auth_data)