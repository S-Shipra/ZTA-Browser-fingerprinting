def decide_action(risk):
    if risk < 40:
        return "ALLOW"
    elif risk < 80:
        return "OTP"
    else:
        return "BLOCK"