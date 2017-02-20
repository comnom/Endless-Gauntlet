# Copyright (c) 2017 by Frederick Goy IV
#
# Endless Gauntlet is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# Endless Gauntlet is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

import os
import sys
import hashlib
import random
import math
import time
import shutil

import PARAMS

def GetSources(gamePath, pluginPath):
	try:
		sourceList = []
		homePath = os.path.normpath(os.getcwd())
		
		if gamePath:
			fileList = GetFiles(gamePath)
			sourceList += fileList
		
		if pluginPath:
			for subDir in os.listdir(pluginPath):
				subDirPath = os.path.normpath(pluginPath + '/' + subDir)
				
				if subDirPath == homePath:
					continue
				
				fileList = GetFiles(subDirPath)
				sourceList += fileList
		
		return sourceList
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def GetFiles(dirPath):
	try:
		fileList = []
		
		fullPath = os.path.normpath(dirPath + '/data')
		
		if os.path.isdir(fullPath):
			for dataFile in os.listdir(fullPath):
				filePath = os.path.normpath(fullPath + '/' + dataFile)
				
				if filePath not in fileList:
					fileList.append(filePath)
		
		return fileList
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def GetHash(filePath):
	try:
		dataFile = open(filePath, 'rb')
		
		fileHash = hashlib.sha1()
		fileBuffer = dataFile.read()
		
		fileHash.update(fileBuffer)
		
		dataFile.close()
		return fileHash.hexdigest()
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def CheckHash(sourceTuple):
	try:
		for i in range(len(sourceTuple)):
			filePath = sourceTuple[i][0]
			fileHash = sourceTuple[i][1]
			
			if os.path.isfile(filePath):
				if fileHash != GetHash(filePath):
					return 0
			else:
				return 0
		
		return 1
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def GetData(filePath):
	try:
		dataFile = open(filePath, 'rb')
		
		lineCount = 0
		for line in dataFile:
			lineCount += 1
		
		dataFile.seek(0)
		
		shipList = []
		variantList = []
		ammoList = []
		
		endNode = ('ship ', 'outfit ', 'mission ', 'event ', 'effect ', 'trade ', 'conversation ', 'government ', '"landing message" ', 'galaxy ', 'system ', 'planet ', 'phrase ', 'tip ', '\tdescription', '\t"description"')
		
		for i in range(lineCount):
			currentLine = dataFile.readline()
			
			if currentLine.startswith('ship '):
				if currentLine.count('"') <= 2:
					name = currentLine.partition(' ')[2].strip()
					cate = ''
					hitp = 0
					dron = 0
					figt = 0
					
					for j in range(100):
						walkLine = dataFile.readline()
						pos = dataFile.tell()
						
						if walkLine.startswith(tuple(endNode)) or walkLine == '':
							ship = [name, cate, hitp, figt, dron]
							shipList.append(ship)
							dataFile.seek(pos)
							break
							
						elif walkLine.startswith('\t\t"category"') or walkLine.startswith('\t\tcategory'):
							cate = walkLine.partition(' ')[2].strip()
							
						elif walkLine.startswith('\t\t"shields"') or walkLine.startswith('\t\tshields'):
							hitp += int(walkLine.partition(' ')[2])
							
						elif walkLine.startswith('\t\t"hull"') or walkLine.startswith('\t\thull'):
							hitp += int(walkLine.partition(' ')[2])
							
						elif walkLine.startswith('\t"fighter"') or walkLine.startswith('\tfighter'):
							figt += 1
							
						elif walkLine.startswith('\t"drone"') or walkLine.startswith('\tdrone'):
							dron += 1
						
				else:
					variantList.append(currentLine.partition(' ')[2].strip())
			
			elif currentLine.startswith('outfit '):
				name = currentLine.partition(' ')[2].strip()
				isAmmo = False
				hasAmmo = False
				
				for j in range(100):
					walkLine = dataFile.readline()
					pos = dataFile.tell()
					
					if walkLine.startswith(tuple(endNode)) or walkLine == '':
						if isAmmo:
							if not hasAmmo:
								ammoList.append(name)
						
						dataFile.seek(pos)
						break
					
					elif walkLine.startswith('\t"category"') or walkLine.startswith('\tcategory'):
						cate = walkLine.partition(' ')[2].strip()
						
						if cate == '"Ammunition"' or cate == 'Ammunition':
							isAmmo = True
					
					elif walkLine.startswith('\t"ammo"') or walkLine.startswith('\tammo'):
						hasAmmo = True
		
		dataFile.close()
		return shipList, variantList, ammoList
		
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def GetDataList(sourceList):
	shipList = []
	variantList = []
	excludeList = PARAMS.EXCLUDE
	ammoList = []
	
	for filePath in sourceList:
		dataTuple = GetData(filePath)
		shipList += dataTuple[0]
		variantList += dataTuple[1]
		ammoList += dataTuple[2]
	
	shipList = FormatShip(shipList)
	shipList += FormatVariant(shipList, variantList)
	
	for entry in excludeList:
		for ship in shipList[:]:
			if entry == ship[0]:
				shipList.remove(ship)
	
	return shipList, ammoList

def FormatShip(shipList):
	tierLookup = {
		'"Heavy Warship"': (45000, 180000, 540000, 1080000),
		'"Medium Warship"': (15000, 75000, 300000, 900000),
		'"Light Warship"': (8500, 45000, 170000, 510000),
		'"Interceptor"': (4500, 18000, 45000, 90000),
		'"Fighter"': (1500, 4500, 14000, 42000),
		'"Drone"': (1500, 4500, 14000, 42000),
		'"Heavy Freighter"': (12000, 75000, 300000, 600000),
		'"Light Freighter"': (4200, 18000, 28000, 84000),
		'"Transport"': (7500, 23000, 57000, 140000)}
	formattedList = []
	
	for ship in shipList:
		tier = 1
		category = ship[1]
		hitpoints = ship[2]
		
		if ship[1] == '':
			continue
		
		if hitpoints <= tierLookup[category][0]:
			tier = 1
			
		elif hitpoints <= tierLookup[category][1]:
			tier = 2
		
		elif hitpoints <= tierLookup[category][2]:
			tier = 3
		
		elif hitpoints <= tierLookup[category][3]:
			tier = 4
		
		else:
			tier = 5
		
		ship[2] = tier
		
		formattedList.append(ship)
	
	return formattedList

def FormatVariant(shipList, variantList):
	formattedList = []
	
	for variant in variantList:
		for ship in shipList:
			if variant.startswith(ship[0]):
				formattedShip = [
					variant.partition('" ')[2], ship[1], ship[2], ship[3], ship[4]]
				
				formattedList.append(formattedShip)
	
	return formattedList

def SplitShipList(shipList):
	fighterList = []
	droneList = []
	
	for ship in shipList[:]:
		if ship[1] == '"Fighter"':
			fighterList.append(ship)
			shipList.remove(ship)
		
		elif ship[1] == '"Drone"':
			droneList.append(ship)
			shipList.remove(ship)
	
	return shipList, fighterList, droneList

def SelectShip(min, max, shipList, weightList):
	doSelection = 1
	ship = []
	
	if min > max:
		max = min
	
	selectionRange = GetSelectionRange(max, weightList)
	selection = random.choice(selectionRange)
	
	while doSelection:
		ship = random.choice(shipList)
		shipSum = PARAMS.WEIGHTS[ship[1]] + PARAMS.T_WEIGHTS[ship[2]]
		
		if shipSum <= max:
			if PARAMS.WEIGHTS[ship[1]] == PARAMS.WEIGHTS[selection[0]]:
				if PARAMS.T_WEIGHTS[ship[2]] == PARAMS.T_WEIGHTS[selection[1]]:
					doSelection = 0

	return ship

def GetCheckpoints():
	checkpointList = []
	
	if PARAMS.CHECKPOINTS:
		for i in range(0, PARAMS.GALAXY_SIZE, 10):
			validRange = range(PARAMS.CHECKPOINT_MIN + i, PARAMS.CHECKPOINT_MAX + i)
			choice = random.sample(validRange, PARAMS.CHECKPOINTS)
			checkpointList += choice
	
	return sorted(checkpointList)

def GetCoordinates():
	coordinateList = []
	
	for i in range(PARAMS.GALAXY_SIZE):
		angle = 0.25 * i
		x = (220 * angle) * math.cos(angle)
		y = (220 * angle) * math.sin(angle)
		
		coordinateList.append([x, y])
	
	return coordinateList

def GetValidWeights(shipList):
	weightList = []
	
	for ship in shipList[:]:
		if PARAMS.WEIGHTS[ship[1]] == 0 or PARAMS.T_WEIGHTS[ship[2]] == 0:
			shipList.remove(ship)
	
	for ship in shipList:
		if PARAMS.WEIGHTS[ship[1]] and PARAMS.T_WEIGHTS[ship[2]]:
			weight = [ship[1], ship[2]]
			
			if weight not in weightList:
				weightList.append(weight)

	return shipList, weightList

def GetMinWeight(weightList):
	minList = []
	
	for weight in weightList:
		minList.append(PARAMS.WEIGHTS[weight[0]] + PARAMS.T_WEIGHTS[weight[1]])
	
	return sorted(minList)[0]

def GetSelectionRange(max, weightList):
	selectionList = []
	tmpList = []
	
	for i in PARAMS.WEIGHTS:
		for j in PARAMS.T_WEIGHTS:
			weightSum = PARAMS.WEIGHTS[i] + PARAMS.T_WEIGHTS[j]
			
			if weightSum <= max:
				if [i, j] in weightList:
					tmpList.append([i, j, weightSum])
	
	for i in tmpList:
		for j in range(int(round(i[2]))):
			selectionList.append([i[0], i[1]])
	
	return selectionList

def WriteCache(sourceList, shipList, ammoList):
	try:
		cacheFile = open('cache', 'wb')
		
		for filePath in sourceList:
			cacheFile.write('$' + filePath + '<>' + GetHash(filePath) + '\n')
		
		for ship in shipList:
			formatShip = ('*' + ship[0] + '<>' + ship[1] + '<>' + str(ship[2]) + 
				'<>' + str(ship[3]) + '<>' + str(ship[4]) + '\n')
			
			cacheFile.write(formatShip)
		
		for ammo in ammoList:
			cacheFile.write('^' + ammo + '\n')
		
		cacheFile.close()
		
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def ReadCache():
	try:
		cacheFile = open('cache', 'rb')
		
		sourceList = []
		shipList = []
		ammoList = []
		for line in cacheFile:
			if line.startswith('$'):
				lineTuple = line.strip('$').split('<>')
				
				sourceList.append((lineTuple[0], lineTuple[1].strip()))
			
			elif line.startswith('*'):
				lineTuple = line.strip('*').split('<>')
				ship = [lineTuple[0], lineTuple[1], int(lineTuple[2]),
					int(lineTuple[3]), int(lineTuple[4].strip())]
				
				shipList.append(ship)
			
			elif line.startswith('^'):
				ammoList.append(line.strip('^').strip())
		
		cacheFile.close()
		
		return sourceList, shipList, ammoList
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def CheckCache(sourceList, cacheTuple):
	cacheList = []
	
	for entry in cacheTuple:
		cacheList.append(entry[0])
	
	if sourceList == cacheList:
		if CheckHash(cacheTuple):
			return 1
	
	return 0

def DoBasic(index, coordinateList):
	x = 20000 - coordinateList[index][0]
	y = 14000 - coordinateList[index][1]
	
	data = ['system "VR System {}"\n'.format(index), '\tpos {} {}\n'.format(x, y),
		'\tgovernment "Bounty"\n']
	
	return data

def DoLinks(index):
	if index == 0:
		data = ['\tlink "VR System 1"\n']
		
	elif index == PARAMS.GALAXY_SIZE - 1:
		data = ['\tlink "VR System {}"\n'.format(index - 1)]
		
	else:
		data = ['\tlink "VR System {}"\n'.format(index - 1), 
			'\tlink "VR System {}"\n'.format(index + 1)]
	
	return data

def DoAsteroids(amount):
	asteroidList = ['small metal', 'small rock', 'medium metal', 'medium rock', 
		'large metal', 'large rock']
	data = []
	
	for i in random.sample(asteroidList, amount):
		data.append('\tasteroids "{0}" {1} {2:.4f}\n'.format(i, 
			int(abs(random.gauss(1, 30))+1), random.uniform(1, 10)))
	
	return data

def DoObjects(index, checkpointList):
	starList = ['a0', 'a5', 'b5', 'f0', 'f5', 'g0', 'g5', 'k0', 'k5', 'm0', 'm4', 'm8']
	star = random.choice(starList)
	
	if index:
		data = ['\tobject\n\t\tsprite star/{}\n\t\tperiod 10\n'.format(star)]
		if index in checkpointList:
			dataString = ('\tobject "Checkpoint {}"\n\t\tsprite '
				'planet/digitalplanet\n\t\tdistance 960\n\t\tperiod 450\n')
			
			data.append(dataString.format(checkpointList.index(index)))
	
	else:
		dataString = ('\tobject "The Gauntlet"\n\t\tsprite planet/wormhole\n'
			'\t\tdistance 540.407\n\t\tperiod 206.769\n')
		data = ['\tobject\n\t\tsprite star/{}\n\t\tperiod 10\n'.format(star), dataString]
		
	return data

def DoPlanets(checkpointList):
	data = []
	
	for i in range(len(checkpointList)):
		remaining = len(checkpointList) - (i + 1)
		dataString = ('planet "Checkpoint {0}"\n\tattributes gauntlet\n'
			'\tlandscape land/gauntlet\n\tdescription `You have reached '
			'checkpoint {0}. There are {1} checkpoints remaining.`\n'
			'\tspaceport `The spaceport here is empty.`\n'
			'\toutfitter "Gauntlet Ammo"\n\n')
		
		data.append(dataString.format(i, remaining))
	
	return data

def DoFleet(shipTuple, weightTuple, minTuple):
	fleetSize = PARAMS.FLEET_SIZE + random.randint(-PARAMS.VARIANCE, PARAMS.VARIANCE)
	fleetList = []
	
	while fleetSize > 0.0:
		ship = SelectShip(minTuple[0], fleetSize, shipTuple[0], weightTuple[0])
		fleetList.append(ship[0])
		
		shipSum = PARAMS.WEIGHTS[ship[1]] + PARAMS.T_WEIGHTS[ship[2]]
		fleetSize -= shipSum
		
		maxFighters = ship[3]
		maxDrones = ship[4]
		
		while fleetSize > 0.0 and maxFighters:
			fighter = SelectShip(minTuple[1], fleetSize, shipTuple[1], weightTuple[1])
			fleetList.append(fighter[0])
			
			fighterSum = PARAMS.WEIGHTS[fighter[1]] + PARAMS.T_WEIGHTS[fighter[2]]
			fleetSize -= fighterSum
			maxFighters -= 1
		
		while fleetSize > 0.0 and maxDrones:
			drone = SelectShip(minTuple[2], fleetSize, shipTuple[2], weightTuple[2])
			fleetList.append(drone[0])
			
			droneSum = PARAMS.WEIGHTS[drone[1]] + PARAMS.T_WEIGHTS[drone[2]]
			fleetSize -= droneSum
			maxDrones -= 1
	
	return fleetList
			

def WriteMap():
	try:
		mapFile = open('data/map.txt', 'wb')
		
		checkpointList = GetCheckpoints()
		coordinateList = GetCoordinates()
		
		for i in range(PARAMS.GALAXY_SIZE):
			asteroids = random.randint(0, 6)
			
			for j in DoBasic(i, coordinateList):
				mapFile.write(j)
			
			for j in DoLinks(i):
				mapFile.write(j)
			
			if asteroids:
				for j in DoAsteroids(asteroids):
					mapFile.write(j)
			
			for j in DoObjects(i, checkpointList):
				mapFile.write(j)
			
			mapFile.write('\n')
			
		if checkpointList:
			for j in DoPlanets(checkpointList):
				mapFile.write(j)
			
		mapFile.close()
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def WriteMission(shipList):
	try:
		missionFile = open('data/mission.txt', 'wb')
		
		dataString = ('mission "Gauntlet [{}]"\n\tname "Attempt the Gauntlet!"\n'
			'\tdescription "Travel through the wormhole and destroy all enemies!"\n'
			'\tsource "Mysterious Moon"\n\ton offer\n\t\tconversation\n'
			'\t\t\t`The Pug does little to acknowledge your presence except to ask, '
			'"Will you attempt The Gauntlet?"`\n\t\t\tchoice\n\t\t\t\t`	'
			'"I will."`\n\t\t\t\t\taccept\n\t\t\t\t`	"Not right now."`\n'
			'\t\t\t\t\tdefer\n')
		
		uID = time.time()
		
		missionFile.write(dataString.format(uID))
		
		shipTuple = SplitShipList(shipList)
		
		curatedShips = GetValidWeights(shipTuple[0])
		curatedFighters = GetValidWeights(shipTuple[1])
		curatedDrones = GetValidWeights(shipTuple[2])
		
		shipList = curatedShips[0]
		shipWeights = curatedShips[1]
		
		fighterList = curatedFighters[0]
		fighterWeights = curatedFighters[1]
		
		droneList = curatedDrones[0]
		droneWeights = curatedDrones[1]
		
		shipTuple = (shipList, fighterList, droneList)
		weightTuple = (shipWeights, fighterWeights, droneWeights)
		
		shipMin = GetMinWeight(shipWeights)
		fighterMin = GetMinWeight(fighterWeights)
		droneMin = GetMinWeight(droneWeights)
		
		minTuple = (shipMin, fighterMin, droneMin)
		
		for i in range(PARAMS.GALAXY_SIZE):
			dataString = ('\tnpc kill\n\t\tsystem "VR System {}"\n'
			'\t\tpersonality vindictive staying\n\t\tgovernment "Bounty"\n'
			'\t\tfleet\n\t\t\tnames "pirate"\n\t\t\tfighters "pirate"'
			'\n\t\t\tvariant\n')
			
			missionFile.write(dataString.format(str(i)))
			
			for j in DoFleet(shipTuple, weightTuple, minTuple):
				missionFile.write('\t\t\t\t' + j + '\n')
			
			missionFile.write('\t\tdialog "System Cleared"\n\n')
		
		missionFile.write('\ton accept\n\t\tevent "gauntlet show"\n')
		
		dataString = ('\ton complete\n\t\tevent "gauntlet clear"\n'
		'\t\tevent "gauntlet hide"\n\t\tpayment 1000000\n'
		'\t\tdialog "The Pug says nothing this time, but pays you <payment>."\n')
		
		missionFile.write(dataString)
		
		missionFile.close()
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def WriteEvent():
	try:
		eventFile = open('data/events.txt', 'wb')
		
		eventFile.write('event "gauntlet clear"\n')
		
		for i in range(PARAMS.GALAXY_SIZE):
			eventFile.write('\tunvisit "VR System {}"\n'.format(str(i)))
		
		eventFile.close()
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def WriteOutfitter(ammoList):
	try:
		salesFile = open('data/sales.txt', 'wb')
		
		salesFile.write('outfitter "Gauntlet Ammo"\n')
		
		for ammo in ammoList:
			salesFile.write('\t' + ammo + '\n')
		
		salesFile.close()
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def WriteBackup(savePath):
	try:
		homePath = os.path.normpath(os.getcwd())
		backupPath = os.path.normpath(homePath + '/backup')
		
		if not os.path.isdir(backupPath):
			os.makedirs(backupPath)
		
		for dataFile in os.listdir(savePath):
			sourcePath = os.path.normpath(savePath + '/' + dataFile)
			destinationPath = os.path.normpath(backupPath + '/' + dataFile)
			
			shutil.copy(sourcePath, destinationPath)
	
	except (IOError, OSError) as error:
		message = error.strerror + ' ' + error.filename
		OnFail(message)

def OnFail(message):
	try:
		for dataFile in os.listdir(os.path.normpath(os.getcwd() + '/data')):
			filePath = os.path.normpath('data/' + dataFile)
			
			if dataFile == 'const.txt':
				continue
			
			if os.path.isfile(filePath):
				os.remove(filePath)
		
		if os.path.isfile('cache'):
			os.remove('cache')
	
		sys.exit('\n' + message)
	
	except (IOError, OSError) as error:
		thisMessage = error.strerror + ' ' + error.filename
		sys.exit('\n' + message + '\n' + 'Cleanup failed: ' +
			thisMessage)

def main():
	gamePath = os.path.normpath(PARAMS.GAME_PATH)
	
	if not os.listdir(gamePath):
		sys.exit('Game directory not found')
	
	pluginPath = ''
	
	if PARAMS.USE_PLUGINS:
		pluginPath = os.path.normpath(PARAMS.PLUGIN_PATH)
		
		if not os.listdir(pluginPath):
			sys.exit('Plugin directory not found')
	
	savePath = ''
	
	if PARAMS.BACKUP_SAVES:
		savePath = os.path.normpath(PARAMS.SAVES_PATH)
		
		if not os.listdir(savePath):
			sys.exit('Save directory not found')
		
		WriteBackup(savePath)
	
	sourceList = GetSources(gamePath, pluginPath)
	shipList = []
	ammoList = []
	
	if os.path.isfile('cache'):
		cacheTuple = ReadCache()
		
		if CheckCache(sourceList, cacheTuple[0]):
			shipList = cacheTuple[1]
			ammoList = cacheTuple[2]
		
		else:
			dataTuple = GetDataList(sourceList)
			shipList = dataTuple[0]
			ammoList = dataTuple[1]
			WriteCache(sourceList, shipList, ammoList)
	
	else:
		dataTuple = GetDataList(sourceList)
		shipList = dataTuple[0]
		ammoList = dataTuple[1]
		WriteCache(sourceList, shipList, ammoList)
	
	WriteMap()
	WriteMission(shipList)
	WriteEvent()
	WriteOutfitter(ammoList)
	
	return 0

main()
