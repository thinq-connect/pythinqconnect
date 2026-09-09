# Release Notes

## 1.0.14 (2026-09-09)
### Security
* Replace **pyOpenSSL** with **cryptography** for MQTT certificate signing request generation to address a security vulnerability

## 1.0.13 (2026-06-19)
### Features
* Add **wind direction** property options (air_conditioner): [#19](https://github.com/thinq-connect/pythinqconnect/issues/19)
### Improvements
* Improve error code definitions for better reliability: [#35](https://github.com/thinq-connect/pythinqconnect/issues/35)
### Fixes
* Fix date validation logic for energy usage queries: [#33](https://github.com/thinq-connect/pythinqconnect/pull/33)
* Fix MQTT connection stability issue: [#32](https://github.com/thinq-connect/pythinqconnect/pull/32)

## 1.0.12 (2026-04-22)
### Integration
* Home Assistant compatibility patch (kimchi_refrigerator)

## 1.0.11 (2026-03-27)
### Features
* Add **particulate matter level** properties (air_purifier)
### Improvements
* Support additional **wind strength** modes (air_conditioner, air_purifier): [#19](https://github.com/thinq-connect/pythinqconnect/issues/19)

## 1.0.10 (2026-03-26)
> ⚠️ **Deprecated** — Please use 1.0.11 instead. This version contains a side-effect issue affecting Home Assistant integration.

## 1.0.9 (2025-12-01)
### Features
* Add **sleep timer** properties (air_purifier)
### Fixes
* Fix **TURN_ON/TURN_OFF** commands failing with error when device is already in POWER_ON/POWER_OFF state (home_assistant)


## 1.0.8 (2025-09-11)
### Features
* Support historical **energy consumption** metrics for individual devices
* Add **filter remain percent** and **water filter state** properties (refrigerator)
* Add **target humidity** property (dehumidifier)
### Improvements
* Support extended **wind strength** levels (dehumidifier)
### Fixes
* Resolve incorrect behavior when controlling **cook mode** or **target temperature** (oven)

## 1.0.7 (2025-06-18)
### Features
* Add **auto target temperature, min target temperature, max target temperature** properties (air_conditioner)
### Fixes
* Always include both hour and minute parameters to control the **absolute time to start** property (robot_cleaner)
* Accept only the hour parameter to control the **sleep timer** property (air_purifier_fan)

## 1.0.6 (2025-04-30)
### Features
* Add **washer mode** property (washcombo)
* Add **top filter remain percent** property (air_purifier)
* Support **express fridge** property control (refrigerator)

## 1.0.5 (2025-03-14)
### Features
* Add ventilator device
* Support **current job mode** property control (dehumidifier)

## 1.0.4 (2025-02-03)
### Features
* Add **cycle count** property (washer): [#7](https://github.com/thinq-connect/pythinqconnect/issues/7)
* Add **express mode name**, **express fridge** property (refrigerator)
* Add **hop oil** and **flavor info** property for two capsules (home_brew)
* Add **room temp mode**, **room water mode** property (system_boiler)
* Add **two set enabled** property (air_conditioner)
* Add **display light** property (air_conditioner): [#2](https://github.com/thinq-connect/pythinqconnect/issues/2)
* Add **wind direction** property (air_conditioner)
### Deprecations
* Remove **remain time** properties (hood)
### Improvements
* Add temperature properties in Fahrenheit (air_conditioner, system_boiler, refrigerator, wine_cellar, water_heater)
* Add **temperature unit** property (oven)
### Fixes
* Fix **target temperature** property value from dict to number (oven)
### Documentation
* Update README: Update features roadmap for 2025

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
