class DecisionEngine:
    def analyze(self, detections, sos_flag):
        alerts = []

        if len(detections) > 0:
            alerts.append("VISION_THREAT")

        if sos_flag:
            alerts.append("SOS_GESTURE")

        return alerts
