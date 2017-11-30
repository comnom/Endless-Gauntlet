# generate.py
# Copyright (C) 2017 Frederick W. Goy IV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



from core.event import Event
from core.map import Map
from core.mission import Mission
from core.params import Params
from core.sales import Sales
from core.ship import Ship

from core.ESParserPy.dataFile import DataFile
from core.ESParserPy.dataWriter import DataWriter
from core.ESParserPy.getSources import GetSources

import os
import sys


def Init(params):
	print("Init sources...")
	ships = {}
	variants = []
	ammo = []
	files = GetSources(params.gamePath, params.pluginPath)
	for file in files[:]:
		if not file:
			continue
		if not params.rootPath in file.root.Token(1):
			for node in file.Begin():
				key = node.Token(0)
				size = node.Size()
				if key == "ship":
					ship = Ship(node)
					if ship.variantName:
						variants.append(ship)
					else:
						ships[ship.modelName] = ship
				elif key == "outfit":
					isAmmo = False
					hasAmmo = False
					for child in node.BeginFlat():
						childKey = child.Token(0)
						childSize = child.Size()
						if childKey == "category" and childSize >= 2:
							if child.Token(1) == "Ammunition":
								isAmmo = True
						elif childKey == "ammo":
							hasAmmo = True
					if isAmmo and not hasAmmo:
						ammo.append(node.Token(1))
		file.root.Delete()
			
	for variant in variants:
		variant.GetBase(ships[variant.modelName])
		ships[variant.variantName] = variant
		
	fighters = {}
	drones = {}
	for key in list(ships):
		ship = ships[key]
		name = (ship.variantName if ship.variantName else ship.modelName)
		if not ship.category or name in params.excludeShips:
			ships.pop(key)
		else:
			ship.SetTier()
			weight = params.categoryWeights[ship.category]
			tWeight = params.tierWeights[ship.tier]
			if not weight or not tWeight:
				ships.pop(key)
				continue
			else:
				ship.cost = weight + tWeight
				
			isFighter = (True if ship.category == "Fighter" else False)
			isDrone = (True if ship.category == "Drone" else False)
			if isFighter:
				fighters[key] = ships.pop(key)
			elif isDrone:
				drones[key] = ships.pop(key)
		
	return ships, fighters, drones, ammo
	
	
if __name__ == "__main__":
	if sys.version_info[0] < 3:
		print("This program requires version 3 of Python")
		print("Visit: https://www.python.org/downloads/")
		sys.exit("Aborting...")
		
	thisDir = os.path.normpath(os.path.dirname(__file__))
	paramDir = thisDir + os.path.normpath("/params.txt")
	if not os.path.isfile(paramDir):
		print("Cannot locate params.txt in " + paramDir)
		input("Press enter to abort.")
		sys.exit("Aborting...")
		
	paramsFile = DataFile(thisDir + "/params.txt")
	params = Params(thisDir, paramsFile.root)
	paramsFile.root.Delete()
	
	if not params.gamePath.endswith("data"):
		if params.gamePath.endswith("/") or params.gamePath.endswith("\\"):
			params.gamePath += "data"
		else:
			params.gamePath += os.path.normpath("/data")
	if not params.gamePath or not os.path.isdir(params.gamePath):
		print("Cannot locate game data files in " + params.gamePath)
		input("Press enter to abort.")
		sys.exit("Aborting...")
		
	if params.usePlugins:
		if not params.pluginPath.endswith("plugins"):
			if params.pluginPath.endswith("/") or params.pluginPath.endswith("\\"):
				params.pluginPath += "plugins"
			else:
				params.pluginPath += os.path.normpath("/plugins")
		if not params.pluginPath or not os.path.isdir(params.pluginPath):
			print("Cannot find plugin directory in " + params.pluginPath)
			userIn = input("Continue with only vanilla ships? y/n:")
			no = ("n", "no", "No", "NO")
			if userIn in no:
				sys.exit("Aborting...")
			else:
				params.pluginPath = ""
				print("Using only vanilla ships")
			
	ships, fighters, drones, ammo = Init(params)
	allShips = (ships, fighters, drones)
	missionRoot = Mission(params, allShips)
	missionFile = DataWriter(thisDir + "/data/mission.txt")
	for node in missionRoot.Begin():
		missionFile.Write(node)
	
	mapRoot = Map(params)
	mapFile = DataWriter(thisDir + "/data/map.txt")
	for node in mapRoot.Begin():
		mapFile.Write(node)
		
	salesRoot = Sales(ammo)
	salesFile = DataWriter(thisDir + "/data/sales.txt")
	for node in salesRoot.Begin():
		salesFile.Write(node)
		
	eventRoot = Event(params.galaxySize)
	eventFile = DataWriter(thisDir + "/data/events.txt")
	for node in eventRoot.Begin():
		eventFile.Write(node)
		
	print("Saving...")
	missionFile.Save()
	mapFile.Save()
	salesFile.Save()
	eventFile.Save()
	print("Done!")
	
	input("Press enter to close.")
