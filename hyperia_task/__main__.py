import asyncio
import json

import hyperia_task

WEBPAGE = "https://www.prospektmaschine.de/hypermarkte/"


async def main():
    raw_hypermarkets = hyperia_task.HypermarketExtractor(WEBPAGE)

    raw_json = []
    async for market in raw_hypermarkets.async_hypermarkets:
        raw_json += list(map(lambda x: x.to_json(), market.prospekts))

    with open("prospekts.tmp.json", "w", encoding="utf8") as file:
        json.dump(raw_json, file)


if __name__ == "__main__":
    asyncio.run(main())
