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
from core.sales import Sales
from core.ship import Ship

from core.ESParserPy.dataWriter import DataWriter
from core.ESParserPy.getSources import GetSources

from core import PARAMS



def Init(dataPath, pluginPath):
	print "Init sources..."
	ships = {}
	variants = []
	ammo = []
	files = GetSources(dataPath, pluginPath)
	for file in files[:]:
		if not "EndlessGauntlet" in file.root.Token(1):
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
	for ship in ships.values():
		name = (ship.variantName if ship.variantName else ship.modelName)
		if not ship.category or name in PARAMS.EXCLUDE:
			ships.pop(name)
		else:
			ship.SetTier()
			weight = PARAMS.WEIGHTS[ship.category]
			tWeight = PARAMS.T_WEIGHTS[ship.tier]
			if not weight or not tWeight:
				ships.pop(name)
			else:
				ship.cost = weight + tWeight
				
			isFighter = (True if ship.category == "Fighter" else False)
			isDrone = (True if ship.category == "Drone" else False)
			if isFighter:
				fighters[name] = ships.pop(name)
			elif isDrone:
				drones[name] = ships.pop(name)
		
	return ships, fighters, drones, ammo
	
	
if __name__ == "__main__":
	dataPath = PARAMS.GAME_PATH
	pluginPath = ""
	if PARAMS.USE_PLUGINS:
		pluginPath = PARAMS.PLUGIN_PATH
		
	ships, fighters, drones, ammo = Init(dataPath, pluginPath)
	allShips = (ships, fighters, drones)
	missionRoot = Mission(allShips)
	missionFile = DataWriter("data/mission.txt")
	for node in missionRoot.Begin():
		missionFile.Write(node)
	
	galaxySize = PARAMS.GALAXY_SIZE
	checkpoints = [PARAMS.CHECKPOINTS, PARAMS.CHECKPOINT_MIN, PARAMS.CHECKPOINT_MAX]
	mapRoot = Map(galaxySize, checkpoints, PARAMS.HEALTHPACK_FREQUENCY)
	mapFile = DataWriter("data/map.txt")
	for node in mapRoot.Begin():
		mapFile.Write(node)
		
	salesRoot = Sales(ammo)
	salesFile = DataWriter("data/sales.txt")
	for node in salesRoot.Begin():
		salesFile.Write(node)
		
	eventRoot = Event(galaxySize)
	eventFile = DataWriter("data/events.txt")
	for node in eventRoot.Begin():
		eventFile.Write(node)
		
	print "Saving..."
	missionFile.Save()
	mapFile.Save()
	salesFile.Save()
	eventFile.Save()
	print "Done!"
