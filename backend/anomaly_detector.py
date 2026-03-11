import numpy as np
from scipy import stats

class AnomalyDetector:
    """
    AI-powered anomaly detection for unusual energy consumption patterns
    Uses statistical methods and Z-score analysis
    """

    def __init__(self, threshold=2.5):
        self.threshold = threshold  # Z-score threshold for anomaly detection

    def detect(self, historical_data, current_value):
        """
        Detect if current consumption is an anomaly

        Args:
            historical_data: List of historical consumption values
            current_value: Current consumption value to check

        Returns:
            Boolean indicating if value is an anomaly
        """
        if len(historical_data) < 5:
            return False

        mean = np.mean(historical_data)
        std = np.std(historical_data)

        if std == 0:
            return False

        # Calculate Z-score
        z_score = abs((current_value - mean) / std)

        return z_score > self.threshold

    def detect_batch(self, data):
        """
        Detect anomalies in a batch of data

        Args:
            data: List of consumption values

        Returns:
            List of indices where anomalies are detected
        """
        if len(data) < 5:
            return []

        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return []

        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std)
            if z_score > self.threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'z_score': round(z_score, 2),
                    'deviation': round(((value - mean) / mean * 100), 2)
                })

        return anomalies

    def detect_pattern_anomaly(self, data, window_size=7):
        """
        Detect pattern-based anomalies using moving average

        Args:
            data: List of consumption values
            window_size: Size of the moving window

        Returns:
            List of anomaly points
        """
        if len(data) < window_size * 2:
            return []

        anomalies = []

        # Calculate moving average
        for i in range(window_size, len(data)):
            window = data[i - window_size:i]
            window_mean = np.mean(window)
            window_std = np.std(window)

            if window_std == 0:
                continue

            current_value = data[i]
            z_score = abs((current_value - window_mean) / window_std)

            if z_score > self.threshold:
                anomalies.append({
                    'index': i,
                    'value': current_value,
                    'expected': round(window_mean, 2),
                    'z_score': round(z_score, 2)
                })

        return anomalies

    def get_anomaly_severity(self, historical_data, current_value):
        """
        Get severity level of anomaly

        Returns:
            Severity level: 'low', 'medium', 'high', 'critical'
        """
        if len(historical_data) < 5:
            return 'unknown'

        mean = np.mean(historical_data)
        std = np.std(historical_data)

        if std == 0:
            return 'unknown'

        z_score = abs((current_value - mean) / std)

        if z_score < 2:
            return 'normal'
        elif z_score < 3:
            return 'low'
        elif z_score < 4:
            return 'medium'
        elif z_score < 5:
            return 'high'
        else:
            return 'critical'

    def detect_consecutive_increases(self, data, threshold=3):
        """
        Detect consecutive increasing consumption pattern

        Args:
            data: List of consumption values
            threshold: Number of consecutive increases to flag

        Returns:
            Boolean indicating if pattern detected
        """
        if len(data) < threshold + 1:
            return False

        consecutive = 0
        for i in range(1, len(data)):
            if data[i] > data[i-1]:
                consecutive += 1
                if consecutive >= threshold:
                    return True
            else:
                consecutive = 0

        return False

    def detect_sudden_spike(self, historical_data, current_value, spike_factor=2.0):
        """
        Detect sudden spike in consumption

        Args:
            historical_data: List of historical values
            current_value: Current value to check
            spike_factor: Multiplier to consider as spike

        Returns:
            Boolean indicating if spike detected
        """
        if len(historical_data) < 3:
            return False

        recent_avg = np.mean(historical_data[-3:])

        return current_value > (recent_avg * spike_factor)

    def get_consumption_health_score(self, data):
        """
        Calculate overall consumption health score (0-100)

        Args:
            data: List of consumption values

        Returns:
            Health score and analysis
        """
        if len(data) < 7:
            return {'score': 0, 'message': 'Insufficient data'}

        score = 100

        # Check for anomalies
        anomalies = self.detect_batch(data)
        anomaly_penalty = min(30, len(anomalies) * 10)
        score -= anomaly_penalty

        # Check for stability (lower std is better)
        mean = np.mean(data)
        std = np.std(data)
        variability = (std / mean * 100) if mean > 0 else 0
        variability_penalty = min(30, variability)
        score -= variability_penalty

        # Check for increasing trend
        if self.detect_consecutive_increases(data, 4):
            score -= 20

        score = max(0, min(100, score))

        # Determine status
        if score >= 80:
            status = 'Excellent'
        elif score >= 60:
            status = 'Good'
        elif score >= 40:
            status = 'Fair'
        else:
            status = 'Poor'

        return {
            'score': round(score, 2),
            'status': status,
            'anomalies_detected': len(anomalies),
            'variability': round(variability, 2),
            'message': f'Your consumption pattern is {status.lower()}'
        }
