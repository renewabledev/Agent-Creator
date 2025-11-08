import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import json
import tweepy
import re
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bearer_token = os.getenv('bearer_token')
bearertokendobby = os.getenv('bearertokendobby')

client = tweepy.Client(bearer_token)

async def get_user_text(user_id):
    user_id = str(user_id)

    with open("texts.json", "r") as file:
        users_texts = json.load(file)

    if user_id not in users_texts.keys():
        users_texts[user_id] = {"text": "None"}

    with open("texts.json", "w") as file:
        json.dump(users_texts, file)

    return users_texts[user_id]

async def set_user_text(user_id, parameter, new_value):
    user_id = str(user_id)

    with open("texts.json", "r") as file:
        users_texts = json.load(file)

    if user_id not in users_texts.keys():
        users_texts[user_id] = {"text": "None"}

    users_texts[user_id][parameter] = new_value

    with open("texts.json", "w") as file:
        json.dump(users_texts, file)
        
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def get_first_link(text):
  regex = r"https?://\S+"
  match = re.search(regex, text)
  if match:
    return match.group(0)
  else:
    return None

def extract_tweet_id(url):
    match = re.search(r"x\.com/[^/]+/status/(\d+)", url)
    if match:
        return match.group(1)
    else:
        return None

def agentmessage(user_text):
    if user_text["text"] == "None":
        return "You currently don't have any agent text set. Set it using the 'Settings' button."
    else:
        return f"The text you set is: '{user_text["text"]}'. Use the buttons below to continue working."

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Ready!')
    
@bot.command()
async def summary(ctx, *, link):
    tweet_id = extract_tweet_id(get_first_link(link))
    print(extract_tweet_id(get_first_link(link)))
    try:
        response = client.get_tweet(tweet_id, expansions="author_id", tweet_fields=['created_at', 'text'])
        tweet = response.data
        text = tweet.text

    except tweepy.TweepyException as e:
        print(f"Error while receiving tweet: {e}")
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Make a summary of this X post. Don't add anything of your own, make a summary of all the text I give you. Try to include absolutely all the important details. The text itself: {text}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        print(text)
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.command()
async def comment(ctx, *, link):
    tweet_id = extract_tweet_id(get_first_link(link))
    try:
        response = client.get_tweet(tweet_id, expansions="author_id", tweet_fields=['created_at', 'text'])
        tweet = response.data
        text = tweet.text

    except tweepy.TweepyException as e:
        print(f"Error while receiving tweet: {e}")
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Below I have left the text from the Twitter post. Study the post and try to understand what it means. Imagine that you absolutely need to comment on this post and add something to it, think about what is missing in the post. Write your comment to me, try to write it as fully and culturally as possible, without swearing. The post itself: {text}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.command()
async def dobby(ctx, *, msg):
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"{msg}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.command()
async def doctor(ctx, *, msg):
    spis = msg.split()
    temp = spis[0]
    spis.pop(0)
    symp = ' '.join(spis)
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Hello, please help me. My temperature is - {temp}. My symptoms are - {symp}. First of all, tell me my most probable diagnosis based on my symptoms. If there are several symptoms, then list them after the most probable in the next sentence. Then explain in great detail how I should be treated for the most probable diagnosis and, if necessary, tell me what medications I need to tak, what will happen to me if I do not get treatment, and contraindications.",
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")
    msg = await ctx.reply('Did you like the bots answer? Please rate its work.')
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    def check(reaction, user):
        return user == ctx.author and reaction.message == msg
    reaction, user = await bot.wait_for('reaction_add', check=check)
    if str(reaction.emoji) == '👍':
        print(f'{ctx.author} voted for "Like"')
        await ctx.reply("Thank you for your rating!")
    elif str(reaction.emoji) == '👎':
        print(f'{ctx.author} voted for "Dislike"')
        await ctx.reply("Thank you for your rating!")

@bot.command()
async def rephrase(ctx, *, msg):
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"I will send you the text now, you will have to rephrase it. The words you rephrase should be very similar in meaning to those you replaced. Try not to lose the meaning of the sentence, and so that when reading it before and after the rephrase, the meaning is equally clear. The text itself: {msg}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")


@bot.command()
async def texttv(ctx, *, msg):
    print("1")
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Now I will send you a news clipping. Imagine that you are a TV announcer and make a text from it that is ready to be read directly on the news. It should contain a greeting, interesting and informative text about the clipping. The clipping itself: {msg}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.TextInput(label="Your text", placeholder="Enter your text here..."))

    async def on_submit(self, interaction: discord.Interaction):
        if "{message}" in self.children[0].value:
            await set_user_text(author_id, "text", f"{self.children[0].value}")
            await interaction.response.send_message(f"Your text has been saved successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("Your text does not contain {message}, please correct it and resend.", ephemeral=True)

class MyModal1(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.TextInput(label="Your message", placeholder="Enter your message here..."))

    async def on_submit(self, interaction: discord.Interaction):
        global message
        message = self.children[0].value

class ButtonsStart(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Use again",style=discord.ButtonStyle.primary)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await button.response.edit_message(embed=discord.Embed(title="Sentient AI Agent Creator",description=agentmessage(await get_user_text(author_id))),view=Buttons())

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Start Agent", style=discord.ButtonStyle.green)
    async def button_callback(self,button:discord.ui.Button,interaction:discord.Interaction):
        fulltext = await get_user_text(author_id)
        if fulltext['text'] != "None":
            modal = MyModal1(title="Enter your message")
            await button.response.send_modal(modal)
        else:
            await button.response.send_message(f"To start, you need to set the text in the 'Settings'",
                                                    ephemeral=True)

        @bot.event
        async def on_interaction(interaction):
            if interaction.type == discord.InteractionType.modal_submit:
                payload = {
                    "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
                    "max_tokens": 16384,
                    "top_p": 1,
                    "top_k": 40,
                    "presence_penalty": 0,
                    "frequency_penalty": 0,
                    "temperature": 0.6,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"{((await get_user_text(author_id))["text"]).replace("{message}", f"{message}")}"
                        }
                    ]
                }
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {bearertokendobby}"
                }
                response1 = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions",
                                             headers=headers,
                                             data=json.dumps(payload))
                if response1.status_code == 200:
                    data = json.loads(response1.text)
                    answer = data.get('choices', [{}])[0].get('message', {}).get('content',
                                                                                 'Unable to get response from AI')
                    await interaction.response.edit_message(embed=discord.Embed(title="Answer from AI", description=f"{answer}"), view=ButtonsStart())
                else:
                    print(f"Error {response1.status_code}: {response1.text}")
    @discord.ui.button(label="Settings",style=discord.ButtonStyle.primary)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await button.response.edit_message(embed=discord.Embed(title="Settings",
                          description="Enter your static request, which will be sent automatically each time. Also use {message} for the dynamic part of the message. (For example, 'Give a clear answer to my question, answer it in as much detail as possible. The question itself: {message}.')"), view=ButtonsEdit())

    @discord.ui.button(label="Manager", style=discord.ButtonStyle.primary)
    async def gray_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await button.response.edit_message(embed=discord.Embed(title="Manager",
                                                               description=()),
                                           view=ButtonsEdit())


class ButtonsEdit(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Edit Text", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MyModal(title="Enter your text")
        await interaction.response.send_modal(modal)
    @discord.ui.button(label="Return",style=discord.ButtonStyle.gray)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await button.response.edit_message(embed=discord.Embed(title="Sentient AI Agent Creator",description=agentmessage(await get_user_text(author_id))),view=Buttons())

@bot.command()
async def agentcreator(ctx):
    global author_id
    author_id = ctx.author.id
    await ctx.send(embed=discord.Embed(title="Sentient AI Agent Creator",description=agentmessage(await get_user_text(author_id))),view=Buttons())

bot.run(token, log_handler=handler, log_level=logging.DEBUG)