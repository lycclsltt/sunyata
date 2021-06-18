import asyncio

class EventLoop(object):
    @classmethod
    def runUntilComplete(self, asyncFunc):
        #loop = asyncio.get_event_loop()
        tasks = [ asyncFunc ]
        #loop.run_until_complete(asyncio.gather(*tasks))
        loop = asyncio.new_event_loop() 
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        loop.run_until_complete( asyncio.gather(*tasks) )
        loop.run_forever()
        loop.close()