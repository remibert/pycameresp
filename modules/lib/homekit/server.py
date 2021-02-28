# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit.charact   import *
class Server:
	UUID_ACCESSORY_INFORMATION        = "3E"
	UUID_PROTOCOL_INFORMATION         = "A2"
	UUID_FAN                          = "40"
	UUID_GARAGE_DOOR_OPENER           = "41"
	UUID_LIGHTBULB                    = "43"
	UUID_LOCK_MANAGEMENT              = "44"
	UUID_LOCK_MECHANISM               = "45"
	UUID_SWITCH                       = "49"
	UUID_OUTLET                       = "47"
	UUID_THERMOSTAT                   = "4A"
	UUID_AIR_QUALITY_SENSOR           = "8D"
	UUID_SECURITY_SYSTEM              = "7E"
	UUID_CARBON_MONOXIDE_SENSOR       = "7F"
	UUID_CONTACT_SENSOR               = "80"
	UUID_DOOR                         = "81"
	UUID_HUMIDITY_SENSOR              = "82"
	UUID_LEAK_SENSOR                  = "83"
	UUID_LIGHT_SENSOR                 = "84"
	UUID_MOTION_SENSOR                = "85"
	UUID_OCCUPANCY_SENSOR             = "86"
	UUID_SMOKE_SENSOR                 = "87"
	UUID_STATLESS_PROGRAMMABLE_SWITCH = "89"
	UUID_TEMPERATURE_SENSOR           = "8A"
	UUID_WINDOW                       = "8B"
	UUID_WINDOW_COVERING              = "8C"
	UUID_BATTERY_SERVICE              = "96"
	UUID_CARBON_DIOXIDE_SENSOR        = "97"
	UUID_FAN_V2                       = "B7"
	UUID_SLAT                         = "B9"
	UUID_FILTER_MAINTENANCE           = "BA"
	UUID_AIR_PURIFIER                 = "BB"
	UUID_HEATER_COOLER                = "BC"
	UUID_HUMIDIFIER_DEHUMIDIFIER      = "BD"
	UUID_SERVICE_LABEL                = "CC"
	UUID_IRRIGATION_SYSTEM            = "CF"
	UUID_VALVE                        = "D0"
	UUID_FAUCET                       = "D7"
	UUID_TELEVISION                   = "D8"
	UUID_INPUT_SOURCE                 = "D9"
	def __init__(self, name, serverUuid):
		import homekit_
		self.server = homekit_.Server(serverUuid)
		self.name = Charact(Charact.UUID_NAME, Charact.PERM_READ, Charact.TYPE_STRING, name)
		self.addCharact(self.name)

	def __del__(self):
		#~ print(dir(self.server))
		self.server.deinit()

	def addCharact(self, charact):
		self.server.addCharact(charact.charact)


class ServerProtocolInformation(Server):
	def __init__(self, name, version):
		Server.__init__(self, name, Server.UUID_PROTOCOL_INFORMATION)
		
		self.version = charactStringCreate (Charact.UUID_VERSION, Charact.PERM_READ, version)
		self.addCharact(self.version)








class ServerAirQualitySensor(Server):
	def __init__(self, name, airQuality):
		Server.__init__(self, name, Server.UUID_AIR_QUALITY_SENSOR)
		
		self.airQuality = charactUint8Create (Charact.UUID_AIR_QUALITY, Charact.PERM_READ | Charact.PERM_EVENT, airQuality)
		self.airQuality.setConstraint(0, 5, 1)
		self.addCharact(self.airQuality)

class ServerSecuritySystem(Server):
	def __init__(self, name, securitySysCurrState, securitySysTargState):
		Server.__init__(self, name, Server.UUID_SECURITY_SYSTEM)
		
		self.securitySysCurrState = charactUint8Create (Charact.UUID_SECURITY_SYSTEM_CURRENT_STATE, Charact.PERM_READ | Charact.PERM_EVENT, securitySysCurrState)
		self.securitySysCurrState.setConstraint(0, 4, 1)
		self.addCharact(self.securitySysCurrState)
	
		self.securitySysTargState = charactUint8Create (Charact.UUID_SECURITY_SYSTEM_TARGET_STATE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, securitySysTargState)
		self.securitySysTargState.setConstraint(0, 3, 1)
		self.addCharact(self.securitySysTargState)

class ServerCarbonMonoxideSensor(Server):
	def __init__(self, name, carbonMonoxideDetected):
		Server.__init__(self, name, Server.UUID_CARBON_MONOXIDE_SENSOR)
		
		self.carbonMonoxideDetected = charactUint8Create (Charact.UUID_CARBON_MONOXIDE_DETECTED, Charact.PERM_READ | Charact.PERM_EVENT, carbonMonoxideDetected)
		self.carbonMonoxideDetected.setConstraint(0, 1, 1)
		self.addCharact(self.carbonMonoxideDetected)

class ServerContactSensor(Server):
	def __init__(self, name, contactSensorState):
		Server.__init__(self, name, Server.UUID_CONTACT_SENSOR)
		
		self.contactSensorState = charactUint8Create (Charact.UUID_CONTACT_SENSOR_STATE, Charact.PERM_READ | Charact.PERM_EVENT, contactSensorState)
		self.contactSensorState.setConstraint(0, 1, 1)
		self.addCharact(self.contactSensorState)

class ServerDoor(Server):
	def __init__(self, name, currPos, targPos, posState):
		Server.__init__(self, name, Server.UUID_DOOR)
		
		self.currPos = charactUint8Create (Charact.UUID_CURRENT_POSITION, Charact.PERM_READ | Charact.PERM_EVENT, currPos)
		self.currPos.setConstraint(0, 100, 1)
		self.currPos.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.currPos)
		
		self.targPos = charactUint8Create (Charact.UUID_TARGET_POSITION, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, targPos)
		self.targPos.setConstraint(0, 100, 1)
		self.targPos.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.targPos)
		
		self.posState = charactUint8Create (Charact.UUID_POSITION_STATE, Charact.PERM_READ | Charact.PERM_EVENT, posState)
		self.posState.setConstraint(0, 2, 1)
		self.addCharact(self.posState)

class ServerHumiditySensor(Server):
	def __init__(self, name, currRelHumidity):
		Server.__init__(self, name, Server.UUID_HUMIDITY_SENSOR)
		
		self.currRelHumidity = charactFloatCreate (Charact.UUID_CURRENT_RELATIVE_HUMIDITY, Charact.PERM_READ | Charact.PERM_EVENT, currRelHumidity)
		self.currRelHumidity.setConstraint(0.0, 100.0, 1.0)
		self.currRelHumidity.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.currRelHumidity)

class ServerLeakSensor(Server):
	def __init__(self, name, leakDetected):
		Server.__init__(self, name, Server.UUID_LEAK_SENSOR)
		
		self.leakDetected = charactUint8Create (Charact.UUID_LEAK_DETECTED, Charact.PERM_READ | Charact.PERM_EVENT, leakDetected)
		self.leakDetected.setConstraint(0, 1, 1)
		self.addCharact(self.leakDetected)

class ServerLightSensor(Server):
	def __init__(self, name, currAmbientLightLevel):
		Server.__init__(self, name, Server.UUID_LIGHT_SENSOR)
		
		self.currAmbientLightLevel = charactFloatCreate (Charact.UUID_CURRENT_AMBIENT_LIGHT_LEVEL, Charact.PERM_READ | Charact.PERM_EVENT, currAmbientLightLevel)
		self.currAmbientLightLevel.setConstraint(0.0001, 100000.0, 0.0)
		self.currAmbientLightLevel.setUnit(Charact.UNIT_LUX)
		self.addCharact(self.currAmbientLightLevel)

class ServerMotionSensor(Server):
	def __init__(self, name, motionDetected):
		Server.__init__(self, name, Server.UUID_MOTION_SENSOR)
		
		self.motionDetected = charactBoolCreate (Charact.UUID_MOTION_DETECTED, Charact.PERM_READ | Charact.PERM_EVENT, motionDetected)
		self.addCharact(self.motionDetected)

class ServerOccupancySensor(Server):
	def __init__(self, name, occupancyDetected):
		Server.__init__(self, name, Server.UUID_OCCUPANCY_SENSOR)
		
		self.occupancyDetected = charactUint8Create (Charact.UUID_OCCUPANCY_DETECTED, Charact.PERM_READ | Charact.PERM_EVENT, occupancyDetected)
		self.occupancyDetected.setConstraint(0, 1, 1)
		self.addCharact(self.occupancyDetected)

class ServerSmokeSensor(Server):
	def __init__(self, name, smokeDetected):
		Server.__init__(self, name, Server.UUID_SMOKE_SENSOR)
		
		self.smokeDetected = charactUint8Create (Charact.UUID_SMOKE_DETECTED, Charact.PERM_READ | Charact.PERM_EVENT, smokeDetected)
		self.smokeDetected.setConstraint(0, 1, 1)
		self.addCharact(self.smokeDetected)

class ServerStatelessProgrammableSwitch(Server):
	def __init__(self, name, programmableSwitchEvent):
		Server.__init__(self, name, Server.UUID_STATLESS_PROGRAMMABLE_SWITCH)
		
		self.programmableSwitchEvent = charactUint8Create (Charact.UUID_PROGRAMMABLE_SWITCH_EVENT, Charact.PERM_READ | Charact.PERM_EVENT | Charact.PERM_SPECIAL_READ, programmableSwitchEvent)
		self.programmableSwitchEvent.setConstraint(0, 2, 1)
		self.addCharact(self.programmableSwitchEvent)

class ServerWindow(Server):
	def __init__(self, name, currPos, targPos, posState):
		Server.__init__(self, name, Server.UUID_WINDOW)
		
		self.currPos = charactUint8Create (Charact.UUID_CURRENT_POSITION, Charact.PERM_READ | Charact.PERM_EVENT, currPos)
		self.currPos.setConstraint(0, 100, 1)
		self.currPos.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.currPos)

		self.targPos = charactUint8Create (Charact.UUID_TARGET_POSITION, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, targPos)
		self.targPos.setConstraint(0, 100, 1)
		self.targPos.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.targPos)
		
		self.posState = charactUint8Create (Charact.UUID_POSITION_STATE, Charact.PERM_READ | Charact.PERM_EVENT, posState)
		self.posState.setConstraint(0, 2, 1)
		self.addCharact(self.posState)

class ServerWindowCovering(Server):
	def __init__(self, name, targPos, currPos, posState):
		Server.__init__(self, name, Server.UUID_WINDOW_COVERING)
		
		self.targPos = charactUint8Create (Charact.UUID_TARGET_POSITION, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, targPos)
		self.targPos.setConstraint(0, 100, 1)
		self.targPos.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.targPos)

		self.currPos = charactUint8Create (Charact.UUID_CURRENT_POSITION, Charact.PERM_READ | Charact.PERM_EVENT, currPos)
		self.currPos.setConstraint(0, 100, 1)
		self.currPos.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.currPos)

		self.posState = charactUint8Create (Charact.UUID_POSITION_STATE, Charact.PERM_READ | Charact.PERM_EVENT, posState)
		self.posState.setConstraint(0, 2, 1)
		self.addCharact(self.posState)

class ServerBatteryService(Server):
	def __init__(self, name, batteryLevel, chargingState, statusLowBattery):
		Server.__init__(self, name, Server.UUID_BATTERY_SERVICE)
		
		self.batteryLevel = charactUint8Create (Charact.UUID_BATTERY_LEVEL, Charact.PERM_READ | Charact.PERM_EVENT, batteryLevel)
		self.batteryLevel.setConstraint(0, 100, 1)
		self.batteryLevel.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.batteryLevel)
		
		self.chargingState = charactUint8Create (Charact.UUID_CHARGING_STATE, Charact.PERM_READ | Charact.PERM_EVENT, chargingState)
		self.chargingState.setConstraint(0, 2, 1)
		self.addCharact(self.chargingState)

		self.statusLowBattery = charactUint8Create (Charact.UUID_STATUS_LOW_BATTERY, Charact.PERM_READ | Charact.PERM_EVENT, statusLowBattery)
		self.statusLowBattery.setConstraint(0, 1, 1)
		self.addCharact(self.statusLowBattery)

class ServerCarbonDioxideSensor(Server):
	def __init__(self, name, carbonDioxideDetected):
		Server.__init__(self, name, Server.UUID_CARBON_DIOXIDE_SENSOR)
		
		self.carbonDioxideDetected = charactUint8Create (Charact.UUID_CARBON_DIOXIDE_DETECTED, Charact.PERM_READ | Charact.PERM_EVENT, carbonDioxideDetected)
		self.carbonDioxideDetected.setConstraint(0, 1, 1)
		self.addCharact(self.carbonDioxideDetected)

class ServerSlat(Server):
	def __init__(self, name, currSlatState, slatType):
		Server.__init__(self, name, Server.UUID_SLAT)
		
		self.currSlatState = charactUint8Create (Charact.UUID_CURRENT_SLAT_STATE, Charact.PERM_READ | Charact.PERM_EVENT, currSlatState)
		self.currSlatState.setConstraint(0, 2, 1)
		self.addCharact(self.currSlatState)
		
		self.slatType = charactUint8Create (Charact.UUID_SLAT_TYPE, Charact.PERM_READ, slatType)
		self.slatType.setConstraint(0, 1, 1)
		self.addCharact(self.slatType)

class ServerFilterMaintenance(Server):
	def __init__(self, name, filterChangeIndication):
		Server.__init__(self, name, Server.UUID_FILTER_MAINTENANCE)
		
		self.filterChangeIndication = charactUint8Create (Charact.UUID_FILTER_CHANGE_INDICATION, Charact.PERM_READ | Charact.PERM_EVENT, filterChangeIndication)
		self.filterChangeIndication.setConstraint(0, 1, 1)
		self.addCharact(self.filterChangeIndication)

class ServerAirPurifier(Server):
	def __init__(self, name, active, currAirPurifierState, targAirPurifierState):
		Server.__init__(self, name, Server.UUID_AIR_PURIFIER)
		
		self.active = charactUint8Create (Charact.UUID_ACTIVE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, active)
		self.active.setConstraint(0, 1, 1)
		self.addCharact(self.active)
		
		self.currAirPurifierState = charactUint8Create (Charact.UUID_CURRENT_AIR_PURIFIER_STATE, Charact.PERM_READ | Charact.PERM_EVENT, currAirPurifierState)
		self.currAirPurifierState.setConstraint(0, 2, 1)
		self.addCharact(self.currAirPurifierState)
		
		self.targAirPurifierState = charactUint8Create (Charact.UUID_TARGET_AIR_PURIFIER_STATE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, targAirPurifierState)
		self.targAirPurifierState.setConstraint(0, 1, 1)
		self.addCharact(self.targAirPurifierState)

class ServerHeaterCooler(Server):
	def __init__(self, name, active, currTemp, currHeaterCoolerState, targHeaterCoolerState):
		Server.__init__(self, name, Server.UUID_HEATER_COOLER)
		
		self.active = charactUint8Create (Charact.UUID_ACTIVE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, active)
		self.active.setConstraint(0, 1, 1)
		self.addCharact(self.active)
		
		self.currTemp = charactFloatCreate (Charact.UUID_CURRENT_TEMPERATURE, Charact.PERM_READ | Charact.PERM_EVENT, currTemp)
		self.currTemp .setConstraint(0.0, 100.0, 0.1)
		self.currTemp .setUnit(Charact.UNIT_CELSIUS)
		self.addCharact(self.currTemp)
		
		self.currHeaterCoolerState = charactUint8Create (Charact.UUID_CURRENT_HEATER_COOLER_STATE, Charact.PERM_READ | Charact.PERM_EVENT, currHeaterCoolerState)
		self.currHeaterCoolerState.setConstraint(0, 3, 1)
		self.addCharact(self.currHeaterCoolerState)
		
		self.targHeaterCoolerState = charactUint8Create (Charact.UUID_TARGET_HEATER_COOLER_STATE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, targHeaterCoolerState)
		self.targHeaterCoolerState.setConstraint(0, 2, 1)
		self.addCharact(self.targHeaterCoolerState)

class ServerHumidifierDehumidifier(Server):
	def __init__(self, name, active, currRelHumidity, currHumidDehumidState, targHumidDehumidState):
		Server.__init__(self, name, Server.UUID_HUMIDIFIER_DEHUMIDIFIER)
		
		self.active = charactUint8Create (Charact.UUID_ACTIVE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, active)
		self.active.setConstraint(0, 1, 1)
		self.addCharact(self.active)

		self.currRelHumidity = charactFloatCreate (Charact.UUID_CURRENT_RELATIVE_HUMIDITY, Charact.PERM_READ | Charact.PERM_EVENT, currRelHumidity)
		self.currRelHumidity.setConstraint(0.0, 100.0, 1.0)
		self.currRelHumidity.setUnit(Charact.UNIT_PERCENTAGE)
		self.addCharact(self.currRelHumidity)

		self.currHumidDehumidState = charactUint8Create (Charact.UUID_CURRENT_HUMIDIFIER_DEHUMIDIFIER_STATE, Charact.PERM_READ | Charact.PERM_EVENT, currHumidDehumidState)
		self.currHumidDehumidState .setConstraint(0, 3, 1)
		self.addCharact(self.currHumidDehumidState)

		self.targHumidDehumidState = charactUint8Create (Charact.UUID_TARGET_HUMIDIFIER_DEHUMIDIFIER_STATE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, targHumidDehumidState)
		self.targHumidDehumidState.setConstraint(0, 2, 1)
		self.addCharact(self.targHumidDehumidState)

class ServerServiceLabel(Server):
	def __init__(self, name, serviceLabelNamespace):
		Server.__init__(self, name, Server.UUID_SERVICE_LABEL)
		
		self.serviceLabelNamespace = charactUint8Create (Charact.UUID_SERVICE_LABEL_NAMESPACE, Charact.PERM_READ, serviceLabelNamespace)
		self.serviceLabelNamespace.setConstraint(0, 1, 1)
		self.addCharact(self.serviceLabelNamespace)

class ServerIrrigationSystem(Server):
	def __init__(self, name, active, progMode, inUse):
		Server.__init__(self, name, Server.UUID_IRRIGATION_SYSTEM)
		
		self.active = charactUint8Create (Charact.UUID_ACTIVE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, active)
		self.active.setConstraint(0, 1, 1)
		self.addCharact(self.active)
		
		self.progMode = charactUint8Create (Charact.UUID_PROGRAM_MODE, Charact.PERM_READ | Charact.PERM_EVENT, progMode)
		self.progMode.setConstraint(0, 2, 1)
		self.addCharact(self.progMode)
		
		self.inUse = charactUint8Create (Charact.UUID_IN_USE, Charact.PERM_READ | Charact.PERM_EVENT, inUse)
		self.inUse.setConstraint(0, 1, 1)
		self.addCharact(self.inUse)

class ServerValve(Server):
	def __init__(self, name, active, inUse, valveType):
		Server.__init__(self, name, Server.UUID_VALVE)
		
		self.active = charactUint8Create (Charact.UUID_ACTIVE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, active)
		self.active.setConstraint(0, 1, 1)
		self.addCharact(self.active)
		
		self.inUse = charactUint8Create (Charact.UUID_IN_USE, Charact.PERM_READ | Charact.PERM_EVENT, inUse)
		self.inUse.setConstraint(0, 1, 1)
		self.addCharact(self.inUse)
		
		self.valveType = charactUint8Create (Charact.UUID_VALVE_TYPE, Charact.PERM_READ | Charact.PERM_EVENT, valveType)
		self.valveType.setConstraint(0, 3, 1)
		self.addCharact(self.valveType)

class ServerFaucet(Server):
	def __init__(self, name, active):
		Server.__init__(self, name, Server.UUID_FAUCET)
		self.active = charactUint8Create (Charact.UUID_ACTIVE, Charact.PERM_READ | Charact.PERM_WRITE | Charact.PERM_EVENT, active)
		self.active.setConstraint(0, 1, 1)
		self.addCharact(self.active)


