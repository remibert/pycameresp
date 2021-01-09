# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET 
from asyncio import *

async def sleep_ms(duration):
	await sleep(duration/1000)