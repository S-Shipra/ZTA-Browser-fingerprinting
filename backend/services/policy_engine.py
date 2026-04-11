def decide_action(risk):
    if risk < 30:
        return "ALLOW"
    elif risk < 85:       # raised from 75 to 85
        return "OTP"
    else:
        return "BLOCK"