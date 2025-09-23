# offline_map_matching_algorithms.py
from processing.core.Processing import Processing
from qgis.core import QgsProcessingProvider, QgsApplication
from Offline_MapMatching.mm_processing.clip_network_algorithm import ClipNetworkAlgorithm
from Offline_MapMatching.mm_processing.offline_map_matching_algorithm import OfflineMapMatchingAlgorithm
from Offline_MapMatching.mm_processing.reduce_trajectory_density import ReduceTrajectoryDensity
# import other algorithm classes similarly, e.g., ReduceTrajectoryDensityAlgorithm


class OMMProvider(QgsProcessingProvider):
    """Provider for all Offline Map Matching algorithms"""

    def __init__(self):
        super().__init__()

    def id(self):
        return "omm"  # unique provider ID

    def name(self):
        return "Offline Map Matching"

    def loadAlgorithms(self):
        self.addAlgorithm(ClipNetworkAlgorithm())
        self.addAlgorithm(OfflineMapMatchingAlgorithm())
        self.addAlgorithm(ReduceTrajectoryDensity())
        # add other algorithms here

def register_algorithms():
    """Register all Offline Map Matching algorithms in a standalone script"""
    # Initialize Processing framework
    Processing.initialize()

    # Create provider and add to registry
    provider = OMMProvider()
    QgsApplication.processingRegistry().addProvider(provider)