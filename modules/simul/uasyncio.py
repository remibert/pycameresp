# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint: disable=redefined-builtin
""" Simulate uasyncio module """
from asyncio import *

async def sleep_ms(duration):
	""" Sleep milliseconds """
	await sleep(duration/1000)
