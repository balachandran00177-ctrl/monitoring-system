import numpy as np
from datetime import datetime, timedelta

class EnergyPredictor:
    """
    AI-powered energy consumption predictor using time series analysis
    and exponential smoothing
    """

    def __init__(self, alpha=0.3, beta=0.1):
        self.alpha = alpha  # Level smoothing parameter
        self.beta = beta    # Trend smoothing parameter

    def predict(self, historical_data, days=7):
        """
        Predict future energy consumption using exponential smoothing

        Args:
            historical_data: List of historical consumption values
            days: Number of days to predict

        Returns:
            List of predictions with confidence scores
        """
        if len(historical_data) < 2:
            return []

        # Reverse to get chronological order
        data = list(reversed(historical_data))

        # Initialize level and trend
        level = data[0]
        trend = (data[-1] - data[0]) / len(data)

        predictions = []

        # Calculate exponential smoothing for historical data
        for value in data[1:]:
            last_level = level
            level = self.alpha * value + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend

        # Generate future predictions
        for i in range(days):
            prediction_value = level + (i + 1) * trend

            # Add some variance based on historical data
            std_dev = np.std(data)
            confidence = max(0.5, 1 - (i * 0.05))  # Confidence decreases over time

            # Ensure non-negative predictions
            prediction_value = max(0, prediction_value)

            predictions.append({
                'day': i + 1,
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'value': round(prediction_value, 2),
                'confidence': round(confidence, 2),
                'range_low': round(max(0, prediction_value - std_dev), 2),
                'range_high': round(prediction_value + std_dev, 2)
            })

        return predictions

    def calculate_trend(self, historical_data):
        """Calculate consumption trend"""
        if len(historical_data) < 2:
            return 0

        data = list(reversed(historical_data))

        # Simple linear regression
        n = len(data)
        x = np.arange(n)
        y = np.array(data)

        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            return 0

        slope = numerator / denominator

        return slope

    def get_insights(self, historical_data):
        """Generate insights from historical data"""
        if len(historical_data) < 7:
            return {"message": "Not enough data for insights"}

        data = list(reversed(historical_data))

        avg_consumption = np.mean(data)
        max_consumption = np.max(data)
        min_consumption = np.min(data)
        trend = self.calculate_trend(data)

        insights = {
            'average_consumption': round(avg_consumption, 2),
            'max_consumption': round(max_consumption, 2),
            'min_consumption': round(min_consumption, 2),
            'trend': 'increasing' if trend > 0.5 else 'decreasing' if trend < -0.5 else 'stable',
            'trend_value': round(trend, 2),
            'variability': 'high' if np.std(data) > avg_consumption * 0.3 else 'low',
            'efficiency_score': self._calculate_efficiency(data)
        }

        return insights

    def _calculate_efficiency(self, data):
        """Calculate efficiency score (0-100)"""
        if len(data) == 0:
            return 0

        avg = np.mean(data)
        std = np.std(data)

        # Lower average and lower variability = higher efficiency
        variability_penalty = min(30, (std / avg * 100) if avg > 0 else 0)

        # Trend penalty (increasing consumption = lower score)
        trend = self.calculate_trend(data)
        trend_penalty = max(0, trend * 10)

        score = 100 - variability_penalty - trend_penalty

        return round(max(0, min(100, score)), 2)
