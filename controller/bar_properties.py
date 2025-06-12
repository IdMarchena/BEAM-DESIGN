class BarProperties:
    def __init__(self):
        self.bars = {
            "3": {"diametro": 9.5, "area": 71},
            "4": {"diametro": 12.7, "area": 129},
            "5": {"diametro": 15.9, "area": 199},
            "6": {"diametro": 19.1, "area": 284},
            "7": {"diametro": 22.2, "area": 387},
            "8": {"diametro": 25.4, "area": 510},
            "9": {"diametro": 28.7, "area": 645},
            "10": {"diametro": 32.3, "area": 819},
            "11": {"diametro": 35.8, "area": 1006},
            "14": {"diametro": 43.0, "area": 1452},
            "18": {"diametro": 57.3, "area": 2581},
        }

    def get_bar(self, number):
        return self.bars.get(number)

    def get_all_bars(self):
        return list(self.bars.keys())