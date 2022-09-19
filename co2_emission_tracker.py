from codecarbon import EmissionTracker

tracker = EmissionTracker()
tracker.start()
# GPU intense code goes here
tracker.stop()
