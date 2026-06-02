from human_requests.network_analyzer.anomaly_sniffer import WaitHeader, WaitSource

from human_requests.abstraction import Warmup


async def pipeline(warmup: Warmup):
    start_url = warmup.prefixes["MAIN_SITE_URL"]

    await warmup.page.goto(start_url, wait_until="domcontentloaded")
    await warmup.page.wait_for_load_state("networkidle")

    sniffer = warmup.sniffer
    if sniffer is None:
        raise RuntimeError("sniffer is required")

    await sniffer.wait(
        tasks=[
            WaitHeader(
                source=WaitSource.REQUEST,
                headers=["X-Key"],
            )
        ],
        timeout_ms=warmup.timeout_ms,
    )
    # await warmup.page.wait_for_selector(
    #     selector="body > pre",
    #     timeout=warmup.timeout_ms,
    #     state="visible",
    # )
