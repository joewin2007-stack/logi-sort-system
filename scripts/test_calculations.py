import unittest

def calculate_fallback_duration(distance_km: float, traffic_density: float) -> float:
    """The core computational logic pulled directly from our application's fallback route."""
    if distance_km <= 0:
        raise ValueError("Distance must be greater than zero.")
    if not (0.0 <= traffic_density <= 1.0):
        raise ValueError("Traffic density must be between 0.0 and 1.0 inclusive.")
        
    return (distance_km * 1.5) + (traffic_density * 30.0)


class TestLogisticsCalculations(unittest.TestCase):

    def test_standard_trip_estimation(self):
        """Validates that normal operational metrics compute perfect baseline values."""
        # Distance: 10km, Traffic: 0.5 -> (10 * 1.5) + (0.5 * 30.0) = 15.0 + 15.0 = 30.0
        result = calculate_fallback_duration(10.0, 0.5)
        self.assertEqual(result, 30.0)

    def test_zero_traffic_clear_run(self):
        """Validates calculations under ideal conditions with zero traffic density."""
        # Distance: 50km, Traffic: 0.0 -> (50 * 1.5) + 0 = 75.0
        result = calculate_fallback_duration(50.0, 0.0)
        self.assertEqual(result, 75.0)

    def test_invalid_negative_distance_exception(self):
        """Ensures the computational block rejects negative spatial data immediately."""
        with self.assertRaises(ValueError):
            calculate_fallback_duration(-15.0, 0.4)

    def test_out_of_bounds_traffic_exception(self):
        """Ensures traffic anomalies outside our 0.0-1.0 range trigger input errors."""
        with self.assertRaises(ValueError):
            calculate_fallback_duration(25.0, 4.5)

if __name__ == "__main__":
    unittest.main()