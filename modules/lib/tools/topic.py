# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" List topic names used throughout the application.

To listen to these topics with mqtt, you must prefix the topic with the client_id 
(by default the client_id is the hostname).

Example of mosquitto command : 

mosquitto_sub -h $BROKER -p 1883 -t $CLIENT_ID/information -u username -P password

 """

# Value defined for topics
value_on        = "on"
value_off       = "off"
value_binary    = "binary"
value_success   = "success"
value_failed    = "failed"
value_suspended = "suspended"

# Topic defined
motion_detection      = "motion/detection"
motion_detected       = "motion/detected"
motion_image          = "motion/image"
login                 = "login"
presence_detection    = "presence/detection"
presence_detected     = "presence/detected"
information           = "information"
