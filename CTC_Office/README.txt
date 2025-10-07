OP Code for sending data into CTC_data.txt:

TP \n <value> \n <value> \n <line> - throughput data, tickets sold, people disembarking, line
LS \n <value> \n <bool><bool> \n <line> - light state data, location, light op code, line
    - light op code: 00 = red, 01 = yellow, 10 = green, 11 = supergreen