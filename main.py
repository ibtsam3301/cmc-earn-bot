import os, asyncio, ast
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import discord

import database

load_dotenv()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

dbms = database.AirdropDatabase(database.SQLITE, dbname=os.getenv("DB_NAME"))
dbms.create_db_tables()

def main():
  # scrap data
  base_url = 'https://coinmarketcap.com/'
  r = requests.get(f'{base_url}earn/')
  soup = BeautifulSoup(r.content, 'html.parser')
  containers = soup.select('.w-dyn-item')
  
  # parse data
  projects_data = []
  for data in containers:
    project_name = data.select_one('.projecth2')
    name = project_name.text
    project_link = data.select_one('.videoplaceholder')
    link = base_url + project_link['href']
    projects_data.append({"name":name, "link":link})
  
  # check for new airdrops
  new_projects=[]
  project_names = [ast.literal_eval(d.data)['name'] for d in dbms.get_all_data(database.AIRDROPS)]
  for data in projects_data:
    if data['name'] not in project_names:
      new_airdrop = {"name":data['name'],"link":data['link']}
      new_projects.append(new_airdrop)
      query = f"""insert into airdrops (data) values ("{new_airdrop}")"""
      dbms.execute_query(query)
      
  if new_projects:
    return new_projects
  return  

async def send_info():
  # if new project is found
  data = main()
  channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
  if data:
    for d in data:
      name = d['name']
      link = d['link']
      await channel.send(f'New Airdrop Found: \n {name} \n {link}')
    
# discord bot
@client.event
async def on_ready():
  print(f'logged in as {client.user}')
  while True:
    await send_info()
    await asyncio.sleep(3600) # task runs every hour
    
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content == "$all":
    main()
    for project in dbms.get_all_data(database.AIRDROPS):
      name = ast.literal_eval(project.data)['name']
      link = ast.literal_eval(project.data)['link']
      await message.channel.send(f'Name: {name} \n Link: {link}')
  if message.content == "$latest":
    main()
    project = dbms.get_all_data(database.AIRDROPS)[-1]
    name = ast.literal_eval(project.data)['name']
    link = ast.literal_eval(project.data)['link']
    await message.channel.send(f'Name: {name} \n Link: {link}')
    
# new member joins
@client.event
async def on_member_join(member):
  channel = client.get_channel(int(os.getenv('CHANNEL_ID')))
  await channel.send(f'welcome {member.name}\n Newly added airdrops will be notified. If you want to see all the listed projects type "$all". For viewing the latest project type "$latest"')


client.run(os.getenv('TOKEN'))


  