#!/usr/bin/python3

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
import urllib.parse
from lxml import etree
import sys
import yaml

# TODO for future upgrades, use .config.yaml instead
# in particular:
#
#  groups:
#    - GROUP_NAME_1:
#      alt_name: ALT_NAME
#      alt_pass: ALT_PASS
#      group_color: COLOR_NUMBER for group
#      auth_role: AUTHORIZED role
#      auth_users:
#        - user1
#        - ...

load_dotenv()
TOKEN   = os.getenv('DISCORD_TOKEN')
GUILD   = os.getenv('DISCORD_GUILD')
ALTNAME = urllib.parse.quote( os.getenv('ALT_NAME') )
ALTPASS = urllib.parse.quote( os.getenv('ALT_PASS') )
ALLOWED = os.getenv('ALLOWED_ROLE')
PREFIX  = os.getenv('COMMAND_PREFIX')
GROUP   = os.getenv('GROUP_NAME')
URL     = os.getenv('GROUP_URL')

intents = discord.Intents.all()
#client = discord.Client(intents=intents)

# TODO proper error handling for all web requests

url = 'http://urbandead.com/map.cgi?username=' + ALTNAME + '&password=' + ALTPASS
try:
	session = requests.session()
	r = session.get(url)
except Exception as e:
    raise SystemExit(e)
#if r.status_code != 200:
#	errmsg = 'failed to establish session, status ' + str(r.status_code)
#	sys.exit(errmsg)


with open('items.yaml', 'r') as f:
	try:
		items = yaml.load(f, Loader=yaml.FullLoader)
	except Exception as e:
		sys.exit(e)
	finally:
		f.close()

with open('item-abbrev.yaml', 'r') as f:
	try:
		abbrevs = yaml.load(f, Loader=yaml.FullLoader)
	except Exception as e:
		sys.exit(e)
	finally:
		f.close()


bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_ready():
	# Setting `Playing ` status
	await bot.change_presence(activity=discord.Game(name=PREFIX+'help'))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

# TODO ignore commands if sender is the bot (can happen?)

@bot.command(name='ping', help='ping request')
async def cmd_ping(ctx):
	await ctx.send('pong')

# TODO DRY
# TODO "paginate" if output is too long
# TODO check for empty contact list

# TODO use predicate function to authenticate from DM
# TODO once multiple groups are supported, do not default group when DMd

@bot.command(name='active', help='active group members')
@commands.has_role(ALLOWED)
async def cmd_active(ctx):

	try:
		r = session.get('http://urbandead.com/contacts.cgi')
	except requests.exceptions.RequestException as e:
		await ctx.send('Connection error to urbandead.com')
		return
	if r.status_code != 200:
		await ctx.send('Bad status code while retrieving the contacts')
		return
		
	tree = etree.HTML(r.text)

	msg = ''

	# the path below catches both active and MIA alts
	# if nothing is found the contact list may be empty
	path = '//a[contains(@class,"con1")]'
	r = tree.xpath(path)
	if len(r) == 0:
		await cts.send('Please have the bot herder check if the contact list is empty.')
		return

	for i in range(0,len(r)):
		if r[i].text != None:
			msg += r[i].text+'\n'

	if msg == '':
		await ctx.send('Sorry, no active players found.')
		return

	embed  =discord.Embed(
		title=GROUP,
		url=URL,
		description=msg,
		color=0xFF5733)

	await ctx.send(embed=embed)


@bot.command(name='mia', help='MIA alts')
@commands.has_role(ALLOWED)
async def cmd_mia(ctx):

	try:
		r = session.get('http://urbandead.com/contacts.cgi')
	except requests.exceptions.RequestException as e:
		await ctx.send('Connection error to urbandead.com')
		return
	if r.status_code != 200:
		await ctx.send('Bad status code while retrieving the contacts')
		return
		
	tree = etree.HTML(r.text)

	msg = ''

	path = '//a[contains(@class,"con1")]/strike'
	r = tree.xpath(path)
	if len(r) == 0:
		await cts.send('No MIAs found.')
		return

	for i in range(0,len(r)):
		# TODO test for "can't happen" instead?
		if r[i].text != None:
			msg += r[i].text+'\n'

	embed  =discord.Embed(
		title=GROUP,
		url=URL,
		description=msg,
		color=0xFF5733)

	await ctx.send(embed=embed)



@bot.command(name='group', help='group overview')
@commands.has_role(ALLOWED)
async def cmd_group(ctx):

	try:
		r = session.get('http://urbandead.com/contacts.cgi')
	except requests.exceptions.RequestException as e:
		await ctx.send('Connection error to urbandead.com')
		return
	if r.status_code != 200:
		await ctx.send('Bad status code while retrieving the contacts')
		return
		
	tree = etree.HTML(r.text)

	active = ''

	# the path below catches both active and MIA alts
	# if nothing is found the contact list may be empty
	path = '//a[contains(@class,"con1")]'
	r = tree.xpath(path)
	if len(r) == 0:
		await cts.send('Please have the bot herder check if the contact list is empty.')
		return

	# TODO if r[i].text is None, do an xpath to the strike element instead
	for i in range(0,len(r)):
		if r[i].text != None:
			active += r[i].text+'\n'

	mia = ''

	path = '//a[contains(@class,"con1")]/strike'
	r = tree.xpath(path)
	if len(r) != 0:
		for i in range(0,len(r)):
			# TODO test for "can't happen" instead?
			if r[i].text != None:
				mia += r[i].text+'\n'

	# build the embed

	embed  =discord.Embed(
		title=GROUP,
		url=URL,
		description="Group overview",
		color=0xFF5733)

	embed.add_field(name="Active", value=active, inline=True)
	embed.add_field(name="MIA", value=mia, inline=True)

	await ctx.send(embed=embed)

@bot.command(name='item', help='item quick-info')
async def cmd_item(ctx, *args):
	# don't require quoting
	item = ' '.join(args)
	await ctx.send(item)

bot.run(TOKEN)
