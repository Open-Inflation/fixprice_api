from human_requests.abstraction import Warmup


async def pipeline(warmup: Warmup):
    """Optional hook for function-specific page choreography."""
    return None
