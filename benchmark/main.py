import asyncio
from concrete import DefaultBenchmarkConfig, BenchmarkRunner


async def main():
    config = DefaultBenchmarkConfig()
    runner = BenchmarkRunner(config)
    await runner.run()


if __name__ == "__main__":
    asyncio.run(main())
