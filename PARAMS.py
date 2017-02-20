# Copyright (c) 2017 by Frederick Goy IV
#
# Endless Gauntlet is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# Endless Gauntlet is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# Parameters for building the gauntlet

# The path to the Endless Sky directory. Use forward slashes: /
# ex. 'C:/Program Files (x86)/Steam/steamapps/common/Endless Sky'
GAME_PATH = ''

# Boolean. Set to 1 if plugin ships should be used to build the gauntlet.
USE_PLUGINS = 0

# The path to the plugin directory. Use forward slashes: /
# ex. 'C:/Users/MyUserName/AppData/Roaming/endless-sky/plugins'
PLUGIN_PATH = ''

# Boolean. Set to 1 if a backup of the save directory should be made.
BACKUP_SAVES = 0

# The path to the save directory. Use forward slashes: /
# ex. 'C:/Users/MyUserName/AppData/Roaming/endless-sky/saves'
SAVES_PATH = ''

# The number of systems in the gauntlet.
GALAXY_SIZE = 10

# The number of planets per ten systems to refuel/restock ammo
CHECKPOINTS = 1
# Every ten systems, place a checkpoint in a random system between min and max.
# ex. first checkpoint is between 3 and 6, second is between 13 and 16, etc.
CHECKPOINT_MIN = 3
CHECKPOINT_MAX = 6

# Frequency of the healthpack ships in milliseconds.
HEALTHPACK_FREQUENCY = 4000

# Difficulty of the individual fleets using WEIGHTS below.
# ex. FLEET_SIZE = 10, T1 = .5, Interceptor = .5
# the size of the fleet could be 10/(.5 + .5) = 10 T1 interceptors
# ex. FLEET_SIZE = 10, T5 = 5, Heavy Warship = 5
# the size of the fleet could be 10/(5 + 5) = 1 T5 heavy warship
FLEET_SIZE = 5.0
# Random variance for FLEET_SIZE
VARIANCE = 0.0

WEIGHTS = {
'"Heavy Warship"': 3.5, 
'"Medium Warship"': 2.5, 
'"Light Warship"': 1.5, 
'"Interceptor"': 0.5, 
'"Fighter"': 0.5, 
'"Drone"': 0.5, 
'"Heavy Freighter"': 0.0, 
'"Light Freighter"': 0.0, 
'"Transport"': 0.0
}
T_WEIGHTS = {
5: 4.5, 
4: 3.5, 
3: 2.5, 
2: 1.5, 
1: 0.5
}

# Ships that won't be used to build the fleets.
# Ships with no category are excluded by default.
EXCLUDE = [
'"Deep River 0"', 
'"Deep River 1"', 
'"Deep River 2"', 
'"Deep River 3"', 
'"Deep River 4"'
]
