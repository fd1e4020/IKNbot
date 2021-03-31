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


def open_yaml(filename, mode):

	with open(filename, mode) as f:
		try:
			data = yaml.load(f, Loader=yaml.FullLoader)
		except Exception as e:
			sys.exit(e)
		finally:
			f.close()
	return data



config = open_yaml('.config.yaml', 'r')
#with open('.config.yaml', 'r') as f:
#	try:
#		config = yaml.load(f, Loader=yaml.FullLoader)
#	except Exception as e:
#		sys.exit(e)
#	finally:
#		f.close()

try:
	TOKEN	= config['token']
	PREFIX	= config['prefix']
	groups	= config['groups']

except:
	sys.exit('broken .config.yaml')

intents = discord.Intents.all()
#client = discord.Client(intents=intents)

# TODO proper error handling for all web requests

sessions = {}

for altname, altpass in config['alts'].items():

	url = 'http://urbandead.com/map.cgi?username=' + altname + '&password=' + altpass
	try:
		sessions[altname] = requests.session()
		r = sessions[altname].get(url)
	except Exception as e:
		raise SystemExit(e)

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

# currently not needed

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You failed a check somewhere.')

# TODO *** DRY DRY DRY ***
#	The %active, %mia, and %groups commands need some
#	serious refactoring

# TODO "paginate" if output is too long


@bot.command(name='listgroups', help='list currently supported groups')
#@commands.has_role(ALLOWED)
async def cmd_listgroups(ctx):

	msg = '```\nsupported groups:\n\n' + '\n'.join(groups) + '\n```'
	await ctx.send(msg)

@bot.command(name='active', help='active group members')
#@commands.has_role(ALLOWED)
async def cmd_active(ctx, group_arg="tkn"):

	try:
		group = groups[group_arg]
	except:
		await ctx.send("I don't know that group")
		return

	altname = group['alt']
	session = sessions[altname]

	GROUP 	= group['name']
	URL 	= group['url']
	COLOR	= group['color']

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
	path = '//a[contains(@class,"' + COLOR +'")]'
	r = tree.xpath(path)
	if len(r) == 0:
		await cts.send('Please have the bot herder check if the contact list is empty.')
		return

	# TODO can use range(len(r))?
	for i in range(0,len(r)):
		if r[i].text != None:
			msg += r[i].text+'\n'

	if msg == '':
		await ctx.send('Sorry, no active players of that group found.')
		return

	embed = discord.Embed(
		title=GROUP,
		url=URL,
		description=msg,
		color=0xFF5733)

	await ctx.send(embed=embed)


@bot.command(name='mia', help='MIA alts')
#@commands.has_role(ALLOWED)
async def cmd_mia(ctx, group_arg="tkn"):

	try:
		group = groups[group_arg]
	except:
		await ctx.send("I don't know that group")
		return

	altname = group['alt']
	session = sessions[altname]

	GROUP 	= group['name']
	URL 	= group['url']
	COLOR	= group['color']

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

	path = '//a[contains(@class,"' + COLOR +'")]/strike'
	r = tree.xpath(path)
	if len(r) == 0:
		await cts.send('All members of this group are active.')
		return

	for i in range(0,len(r)):
		# TODO test for "can't happen" instead?
		if r[i].text != None:
			msg += r[i].text+'\n'

	embed = discord.Embed(
		title=GROUP,
		url=URL,
		description=msg,
		color=0xFF5733)

	await ctx.send(embed=embed)



@bot.command(name='group', help='group overview')
#@commands.has_role(ALLOWED)
async def cmd_group(ctx, group_arg="tkn"):

	try:
		group = groups[group_arg]
	except:
		await ctx.send("I don't know that group")
		return

	altname = group['alt']
	session = sessions[altname]

	GROUP 	= group['name']
	URL 	= group['url']
	COLOR	= group['color']

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
	path = '//a[contains(@class,"' + COLOR +'")]'
	r = tree.xpath(path)
	if len(r) == 0:
		await cts.send('Please have the bot herder check if the contact list is empty.')
		return

	# TODO if r[i].text is None, do an xpath to the strike element instead
	for i in range(0,len(r)):
		if r[i].text != None:
			active += r[i].text+'\n'

	mia = ''

	path = '//a[contains(@class,"' + COLOR +'")]/strike'
	r = tree.xpath(path)
	if len(r) != 0:
		for i in range(0,len(r)):
			# TODO test for "can't happen" instead?
			if r[i].text != None:
				mia += r[i].text+'\n'

	# build the embed

	embed = discord.Embed(
		title=GROUP,
		url=URL,
		description="Group overview",
		color=0xFF5733)

	if active != '':
		embed.add_field(name="Active", value=active, inline=True)
	if mia != '':
		embed.add_field(name="MIA", value=mia, inline=True)

	await ctx.send(embed=embed)

@bot.command(name='item', help='item quick-info')
async def cmd_item(ctx, *args):
	# don't require quoting
	arg = ' '.join(args)

	fields = [ "locations", "encumbrance", "accuracy", "damage", "notes"]

	try:
		arg = abbrevs[arg]
	except:
		pass

	try:
		item = items[arg]
	except:
		await ctx.send(arg + ' not found')
		return

	embed  =discord.Embed(
		title=arg,
		url=item['wiki'],
		description="Here's what I know about " + arg + ":",
		color=0xFF5733)

	for f in fields:
		try:
			val = item[f]
			embed.add_field(name=f, value=val, inline=False)
		except:
			pass

	await ctx.send(embed=embed)


@bot.command(name='listitems', help='items I Know Nothing about')
async def cmd_listitems(ctx):

	msg_items = '\n'.join(items)
	msg_abbrev = '\n'.join('{}: {}'.format(key, value) for key, value in abbrevs.items())

	fmt = '''
```
known items:

{}

abbreviations:

{}
```
'''

	await ctx.send(fmt.format(msg_items, msg_abbrev))


bot.run(TOKEN)
