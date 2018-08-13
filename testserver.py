from rainbowsocks.RainbowSocksServer import RainbowSocksServer
        

if __name__ == "__main__":
    rainbow = RainbowSocksServer()

    @rainbow.event("return.hello")
    async def returnhello(socket, data):
        await socket.respond("hello back!")

    @rainbow.event("return.echo")
    async def returnecho(socket, data):
        await socket.respond(f"ECHO: {data}")

    @rainbow.event("update.status")
    async def telleveryone(socket, data):
        await socket.broadcast(f"{socket.host} requested broadcast: {data}")

    @rainbow.event("connected.nodes")
    async def returnnodes(socket, data):
        await socket.respond([x.id for x in rainbow.connected_clients])

    @rainbow.event("reverse")
    async def reverse(socket, data):
        data = [x for x in data]
        data = list(reversed(data))
        print(data)
        await socket.respond("".join(data))

    rainbow.run("nokusu", 1190)