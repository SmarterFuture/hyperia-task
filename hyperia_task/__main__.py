import asyncio
import json

import hyperia_task

WEBPAGE = "https://www.prospektmaschine.de/hypermarkte/"


async def main():
    """main.
    Runs when the module is called directly
    """

    try:
        raw_hypermarkets = hyperia_task.HypermarketExtractor(WEBPAGE)

        raw_json = []
        async for market in raw_hypermarkets.async_hypermarkets:
            raw_json += list(map(lambda x: x.to_json(), market.prospects))

        with open("prospects.tmp.json", "w", encoding="utf8") as file:
            json.dump(raw_json, file)

    except Exception as exc:
        print("Prospects not fetched:", exc)


if __name__ == "__main__":
    asyncio.run(main())
