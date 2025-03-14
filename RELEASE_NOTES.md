# Release Notes

## 1.0.5 (2025-03-14)
### Features
* Add ventilator device
* Support **current job mode** property control (dehumidifier)

## 1.0.4 (2025-02-03)
### Features
*  Add **cycle count** property (washer): [#7](https://github.com/thinq-connect/pythinqconnect/issues/7)
*  Add **express mode name**, **express fridge** property (refrigerator)
*  Add **hop oil** and **flavor info** property for two capsules (home_brew)
*  Add **room temp mode**, **room water mode** property (system_boiler)
*  Add **two set enabled** property (air_conditioner)
*  Add **display light** property (air_conditioner): [#2](https://github.com/thinq-connect/pythinqconnect/issues/2)
*  Add **wind direction** property (air_conditioner)
### Deprecations
*  Remove **remain time** properties (hood)
### Improvements
*  Add temperature properties in Fahrenheit (air_conditioner, system_boiler, refrigerator, wine_cellar, water_heater)
*  Add **temperature unit** property (oven)
### Fixes
*  Fix **target temperature** property value from dict to number (oven)
### Documentation
*  Update README: Update features roadmap for 2025

## 1.0.3 (2024-12-03)
### Documentation
* Update README: Change the old developer site link to the new one.

## 1.0.2 (2024-12-03)
### Documentation
* Update README: Add notice and update features

## 1.0.1 (2024-11-21)
### Features
* Add **filter remain percent** property (air conditioner, air purifier)
* Remove **end hour** property (plant_cultivator)

## 1.0.0 (2024-11-07)
### Improvements
* Add exception handling with invalid device profile
### Fixes
* Support device doesn't have operation_mode property (cooktop)

## 0.9.9 (2024-10-29)
### Improvements
* Update notification property in device profile (washcombo)

## 0.9.8 (2024-09-25)
### Initial Release
