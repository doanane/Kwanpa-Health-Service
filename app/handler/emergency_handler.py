# ideally, we should have a calling service here, but since none are free,
#  I am moving this to the front-end. In the client side we
#  chekc the heart rete and call the caregiver using the devices resources
#  and sound an alarm also


def emergency_handler(heart_rate: int):
    if heart_rate > 120:
        print(f"Emergency detected! Heart rate: {heart_rate}")
