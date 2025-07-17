class Sensor:
    def __init__(
        self,
        name,
        descr,
        path,
        position="waybar",
        valueLow=0,
        valueMedium=50,
        valueHigh=100,
        format="{:}",
    ):
        self.name = name
        self.descr = descr
        self.path = path
        self.position = position
        self.valueLow = valueLow
        self.valueMedium = valueMedium
        self.valueHigh = valueHigh
        self.format = format
        self.value = ""
        self.device_class = ""
        self.attributes = dict()
        self.debug_info = ""
        self.error = None

    def fetch(self, url, token, session):
        from decimal import Decimal

        ha_url = url + "/api/states/" + self.path
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        data = session.get(ha_url, headers=headers).json()
        self.debug_info = data
        if self.path == data["entity_id"]:
            self.value = data["state"]
            self.device_class = data["attributes"]["device_class"]
            self.attributes = data["attributes"]
        else:
            self.error = "Invalid sensor"

        match self.device_class:
            case "temperature":
                self.value = Decimal(self.value)
            case "timestamp":
                import datetime

                self.value = datetime.datetime.fromisoformat(self.value)
            case _:
                pass

    def print(self):
        if self.error is None:
            return self.descr + self.format.format(self.value)

    def debug(self):
        return f"""
        name: {self.name}
        descr: {self.descr}
        path: {self.path}
        position: {self.position}
        valueLow: {self.valueLow}
        valueMedium: {self.valueMedium}
        valueHigh: {self.valueHigh}
        format: {self.format}
        value: {self.value}
        device_class: {self.device_class}
        attributes: {self.attributes}
        error: {self.error}
        debug: {self.debug_info}
        """


class Module:
    def __init__(self, config: dict):
        import requests

        self.ha_instance = config["haInstance"]
        self.token = config["haToken"]
        self.session = requests.Session()
        self.sensors = []
        for sensor in config["sensors"]:
            self.sensors.append(Sensor(**sensor))

    def update(self):
        for sensor in self.sensors:
            sensor.fetch(self.ha_instance, self.token, self.session)

    def print(self):
        self.update()
        output = f'{{"text": "{"".join([sensor.print() + " " if sensor.position == "waybar" else "" for sensor in self.sensors]).strip()}", "tooltip": "{"".join([sensor.print() + " " if sensor.position == "tooltip" else "" for sensor in self.sensors]).strip()}", "class": ""}}\\0'
        return output

    def debug(self):
        self.update()
        return " ".join([str(sensor.debug()) for sensor in self.sensors])
