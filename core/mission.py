# mission.py
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



from ESParserPy.dataNode import DataNode

import PARAMS

import random
import time



def Mission(allShips):
	print "Building mission..."
	root = DataNode()
	
	uID = time.time()
	mission = DataNode(tokens=["mission", "Gauntlet ({})".format(uID)])
	root.Append(mission)
	
	mission.Append(DataNode(tokens=["name", "Attempt the Gauntlet!"]))
	
	description = "Travel through the wormhole and destroy all enemies!"
	mission.Append(DataNode(tokens=["description", description]))
	mission.Append(DataNode(tokens=["source", "Mysterious Moon"]))
	
	onOffer = DataNode(tokens=["on", "offer"])
	mission.Append(onOffer)
	
	conversation = DataNode(tokens=["conversation"])
	onOffer.Append(conversation)
	
	dialog = ('The Pug does little to acknowledge your presence except to ask, ' +
		'"Will you attempt the Gauntlet?"')
	conversation.Append(DataNode(tokens=[dialog]))
	
	choice = DataNode(tokens=["choice"])
	conversation.Append(choice)
	
	confirm = DataNode(tokens=['"I will"'])
	choice.Append(confirm)
	confirm.Append(DataNode(tokens=["accept"]))
	
	decline = DataNode(tokens=['"Not right now."'])
	choice.Append(decline)
	decline.Append(DataNode(tokens=["defer"]))
	
	for i in range(PARAMS.GALAXY_SIZE):
		npc = DataNode(tokens=["npc", "kill"])
		mission.Append(npc)
		
		npc.Append(DataNode(tokens=["government", "Bounty"]))
		npc.Append(DataNode(tokens=["personality", "vindictive", "staying"]))
		npc.Append(DataNode(tokens=["system", "VR System {}".format(i)]))
		
		fleet = DataNode(tokens=["fleet"])
		npc.Append(fleet)
		fleet.Append(DataNode(tokens=["names", "pirate"]))
		
		variant = DataNode(tokens=["variant"])
		fleet.Append(variant)
		ships = GetFleet(allShips)
		for ship in ships:
			variant.Append(DataNode(tokens=[ship]))
			
		npc.Append(DataNode(tokens=["dialog", "System Cleared!"]))
		
	onAccept = DataNode(tokens=["on", "accept"])
	mission.Append(onAccept)
	
	onAccept.Append(DataNode(tokens=["event", "gauntlet show"]))
	
	onComplete = DataNode(tokens=["on", "complete"])
	mission.Append(onComplete)
	
	onComplete.Append(DataNode(tokens=["event", "gauntlet clear"]))
	onComplete.Append(DataNode(tokens=["event", "gauntlet hide"]))
	onComplete.Append(DataNode(tokens=["payment", "1000000"]))
	
	dialog = "The Pug says nothing this time, but pays you <payment>."
	onComplete.Append(DataNode(tokens=["dialog", dialog]))
	
	return root
	
	
def GetFleet(allShips):
	print "	Adding fleet..."
	ships = allShips[0]
	fighters = allShips[1]
	drones = allShips[2]
	
	minShip = GetMin(ships)
	minFighter = GetMin(fighters)
	minDrone = GetMin(drones)
	
	fleetSize = PARAMS.FLEET_SIZE
	fleetSize += random.randint(-PARAMS.VARIANCE, PARAMS.VARIANCE)
	fleet = []
	while round(fleetSize, 1) > round(minShip, 1):
		ship = GetShip(ships, fleetSize)
		if ship == None:
			break
			
		shipName = (ship.variantName if ship.variantName else ship.modelName)
		fleet.append(shipName)
		fleetSize -= ship.cost
		
		fCount = ship.fighters
		dCount = ship.drones
		while round(fleetSize, 1) > round(minFighter, 1) and fCount:
			print "in fighters", fleetSize, minFighter, dCount
			fighter = GetShip(fighters, fleetSize)
			if ship == None:
				break
				
			fighterName = (fighter.variantName if fighter.variantName else fighter.modelName)
			fleet.append(fighterName)
			print fighterName
			fleetSize -= fighter.cost
			fCount -= 1
			
		while round(fleetSize, 1) > round(minDrone, 1) and dCount:
			print "in drones", fleetSize, minDrone, dCount
			drone = GetShip(drones, fleetSize)
			if drone == None:
				break
				
			droneName = (drone.variantName if drone.variantName else drone.modelName)
			print droneName
			fleet.append(droneName)
			fleetSize -= drone.cost
			dCount -= 1
			
	return fleet
	
	
def GetShip(ships, fleetSize):
	validShips = []
	validWeights = []
	for ship in ships.values():
		if round(ship.cost, 1) <= round(fleetSize, 1):
			validShips.append(ship)
			combo = [ship.tier, ship.category]
			if combo not in validWeights:
				validWeights.append(combo)
				
	weightedList = []
	for combo in validWeights:
		sum = int(PARAMS.T_WEIGHTS[combo[0]] + PARAMS.WEIGHTS[combo[1]])
		for i in range(sum):
			weightedList.append(combo)
			
	selection = random.choice(weightedList)
	doSelection = 1000
	while doSelection > 0:
		doSelection -= 1
		ship = random.choice(validShips)
		if ship.tier == selection[0] and ship.category == selection[1]:
			return ship
			
	return None
	
def GetMin(ships):
	cost = 0
	start = True
	for ship in ships.values():
		if start:
			cost = ship.cost
			start = False
		else:
			if round(ship.cost, 1) < round(cost, 1):
				cost = ship.cost
				
	return cost
	
	
