#!/usr/bin/python3

import os
import discord
from discord.ext import commands
import requests
import urllib.parse
from lxml import etree
import sys
import yaml
#from operator import itemgetter, attrgetter

#
# utility functions
#

def load_yaml(filename, mode):

	with open(filename, mode) as f:
		try:
			data = yaml.load(f, Loader=yaml.FullLoader)
		except Exception as e:
			sys.exit(e)
		finally:
			f.close()
	return data

#
# load config, setup
#

config = load_yaml('.config.yaml', 'r')

try:
	TOKEN	= config['token']
	PREFIX	= config['prefix']
	groups	= config['groups']
except:
	sys.exit('broken .config.yaml')


# create sessions and login

sessions = {}

for altname, altpass in config['alts'].items():

	url = 'http://urbandead.com/map.cgi?username=' + altname + '&password=' + altpass
	try:
		sessions[altname] = requests.session()
		r = sessions[altname].get(url)
	except Exception as e:
		raise SystemExit(e)

# load item data
items = load_yaml('items.yaml', 'r')
abbrevs = load_yaml('item-abbrev.yaml', 'r')

# load mall data
malls = load_yaml('malls.yaml', 'r')

intents = discord.Intents.all()
#client = discord.Client(intents=intents)

#
# end of setup
#

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

#
# group-related commands
#

@bot.command(name='listgroups', help='list currently supported groups')
#@commands.has_role(ALLOWED)
async def cmd_listgroups(ctx):

	fmt = '```\nsupported groups:\n\n{}\n```'
	await ctx.send(fmt.format( '\n'.join(groups) ))

@bot.command(name='active', help='active group members')
#@commands.has_role(ALLOWED)
async def cmd_active(ctx, group_arg="tkn"):

	group = groups.get(group_arg)
	if group is None:
		await ctx.send("I don't know that group.")
		return

	session = sessions[group['alt']]

	try:
		r = session.get('http://urbandead.com/contacts.cgi')
	except Exception as e:
		await ctx.send('Connection error to urbandead.com', e)
		return
		
	tree = etree.HTML(r.text)

	msg = ''

	# the path below catches both active and MIA alts
	# if nothing is found the contact list may be empty
	path = '//a[contains(@class,"' + group['color'] +'") and not(strike)]'
	r = tree.xpath(path)

	if len(r) == 0:
		await ctx.send('No active members of that group found.')
		return

	for i in range(len(r)):
		msg += r[i].text+'\n'

	embed = discord.Embed(
		title=group['name'],
		url=group['url'],
		description=msg,
		color=0xFF5733)

	await ctx.send(embed=embed)


@bot.command(name='mia', help='MIA alts')
#@commands.has_role(ALLOWED)
async def cmd_mia(ctx, group_arg="tkn"):

	group = groups.get(group_arg)
	if group is None:
		await ctx.send("I don't know that group.")
		return

	session = sessions[group['alt']]

	try:
		r = session.get('http://urbandead.com/contacts.cgi')
	except Exception as e:
		await ctx.send('Connection error to urbandead.com', e)
		return
		
	tree = etree.HTML(r.text)

	msg = ''

	path = '//a[contains(@class,"' + group['color'] +'")]/strike'
	r = tree.xpath(path)
	if len(r) == 0:
		await ctx.send('All members of this group are active.')
		return

	for i in range(len(r)):
		# TODO test for "can't happen" instead?
		if r[i].text != None:
			msg += r[i].text+'\n'

	embed = discord.Embed(
		title=group['name'],
		url=group['url'],
		description=msg,
		color=0xFF5733)

	await ctx.send(embed=embed)



@bot.command(name='group', help='group overview')
#@commands.has_role(ALLOWED)
async def cmd_group(ctx, group_arg="tkn"):

	group = groups.get(group_arg)
	if group is None:
		await ctx.send("I don't know that group.")
		return

	session = sessions[group['alt']]

	try:
		r = session.get('http://urbandead.com/contacts.cgi')
	except Exception as e:
		await ctx.send('Connection error to urbandead.com'. e)
		return
		
	tree = etree.HTML(r.text)

	active = []
	mia = []

	path = '//a[contains(@class,"' + group['color'] +'")]'
	r = tree.xpath(path)
	if len(r) == 0:
		await ctx.send('No members found.')
		return

	for i in range(len(r)):
		name = r[i].text
		if name == None:
			name = r[i].getchildren()[0].text
			assert name != None, "name of MIA alt not found"
			mia += [name]
		else:
			active += [name]

	embed = discord.Embed(
		title=group['name'],
		url=group['url'],
		description="Group overview",
		color=0xFF5733)

	if len(active) != 0:
		embed.add_field(name="Active", value='\n'.join(active), inline=True)
	if len(mia) != 0:
		embed.add_field(name="MIA", value='\n'.join(mia), inline=True)

	await ctx.send(embed=embed)

#
# item-related commands
#

@bot.command(name='item', help='item quick-info')
async def cmd_item(ctx, *args):

	arg = ' '.join(args)

	fields = [ "locations", "encumbrance", "accuracy", "damage", "notes"]

	arg = abbrevs.get(arg,arg)

	item = items.get(arg)
	if item == None:
		await ctx.send(arg + ' not found')
		return

	embed  =discord.Embed(
		title=arg,
		url=item['wiki'],
		description="Here's what I know about " + arg + ":",
		color=0xFF5733)

	for f in fields:
		val = item.get(f)
		if val != None:
			embed.add_field(name=f, value=val, inline=False)

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


@bot.command(name='links', help='interesting links')
async def cmd_links(ctx):

	with open('links.yaml', 'r') as f:
		try:
			links = yaml.load(f, Loader=yaml.FullLoader)
		except Exception as e:
			await ctx.send("couldn't read links.yaml:",e)
			return
		finally:
			f.close()	
	
	await ctx.send(links['text'])

def splitcoords(coords):
	s = coords.split(',',1)
	try:
		x = int(s[0])
		y = int(s[1])
	except:
		x = -1
		y = -1
	return (x,y)

def cardinals(dx,dy):
	ew = ''
	ns = ''
	if dx > 0:
		ew = 'W'
	elif dx < 0:
		ew = 'E'
	if dy > 0:
		ns = 'N'
	elif dy < 0:
		ns = 'S'
	return ns + ew

def walkdirections(fx, fy, tx, ty):
	# cardinal distances
	dx = fx - tx
	dy = fy - ty
	# there already?
	if (dx == 0) and (dy == 0):
		return "you are there already"
	steps = ''
	# diagnonal steps?
	diags = min(abs(dx),abs(dy))
	if diags != 0:
		steps += str(diags) + ' ' + cardinals(dx,dy)
		if dx > 0:
			dx -= diags
		else:
			dx += diags
		if dy > 0:
			dy -= diags
		else:
			dy += diags
	assert((dx == 0) or (dy == 0))
	hv = abs(dx+dy)
	if hv != 0:
		if diags != 0:
			steps += ', '
		steps += str(hv) + ' ' + cardinals(dx,dy)

	return steps



@bot.command(name='malls', help='print distance to malls from given coords')
async def cmd_links(ctx,*args):

	arg = ','.join(args)
	(x,y) = splitcoords(arg)

	if x == -1:
		msg = "usage: 'malls x y' or 'mall x,y"
		await ctx.send(msg)
		return

	mdist = {}
	bestcorner = {}

	for mallname, corners in malls.items():

		distance = 100

		for coords in corners.values():
			(mx, my) = splitcoords(coords)
			dcorner = max(abs(x-mx),abs(y-my))
			dold = distance
			distance = min(distance,dcorner)
			if dcorner == 0:
				bestcorner[mallname] = coords
				mdist[mallname] = 0
				break
			elif dold > distance:
				bestcorner[mallname] = coords
			elif (dold == distance) and ((x == mx) or (y == my)):
				bestcorner[mallname] = coords

		mdist[mallname] = distance

	dsort = sorted(mdist.items(), key=lambda kv: int(kv[1]))

	msg = "\n```\nDistance to malls:\n\n"

	fmt = '\n{0:12} {1:2} ( {2} )'

	for n in range(len(dsort)):
		mallname = dsort[n][0]
		distance = dsort[n][1]
		(mx, my) = splitcoords( bestcorner[mallname] )
		msg += fmt.format(mallname,str(distance), walkdirections(x,y,mx,my))

	msg += '\n```'

	await ctx.send(msg)

@bot.command(name='steps', help='steps from a,b to c,d')
async def cmd_links(ctx,fxy,txy):

	(fx,fy) = splitcoords(fxy)
	(tx,ty) = splitcoords(txy)

	if (fx == -1) or (tx == -1):
		msg = "usage: 'steps a,b c,d'"
		await ctx.send(msg)
		return

	await ctx.send(walkdirections(fx,fy,tx,ty))

#
# *** actually run the bot ***
#

bot.run(TOKEN)
