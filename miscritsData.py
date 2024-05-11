from scapy.all import sniff, Packet
import struct
import math
import json
import logging
import time

logger = logging.getLogger("MISCRITSDATA")
logger.disabled = True

GODOT_DATATYPES = [
    "01000000",
    "02000000",
    "03000000",
    "04000000",
    "05000000",
    "1b000000",
    "1c000000",
    "1f000000",
]


class MiscritsData:
    def __init__(self):
        self.clear()

    def clear(self):
        self.timeStarted = time.perf_counter()
        self.timeElapsed = 0
        self.timeoutThreshold = 60
        self.TOKENS = []
        self.currentWild = []
        self.output = {}
        self.databuilder = {}
        self.ID = ""
    
    def checkSearchLocation(self, input):
        if isinstance(input,list):
            if isinstance(input[0],list):
                if isinstance(input[0][0],list) and isinstance(input[0][2],int):
                    return input[0][2]
        return None

    def setTimeStarted(self):
        self.timeStarted = time.perf_counter()

    def elapsedTime(self):
        return time.perf_counter() - self.timeStarted

    def splitToNSize(self, value: str, n):
        string = value
        return [string[i : i + n] for i in range(0, len(string), n)]

    def removeZero(self, tok: str):
        if tok is None:
            return ""
        while tok.endswith("00"):
            tok = tok[:-2]
        return tok

    def toInt(self, hex: str):
        strippedhex = self.removeZero(hex)
        parsedhex = "".join(reversed(self.splitToNSize(strippedhex, 2)))
        if parsedhex == "":
            return 0
        output = int(parsedhex, 16)
        return output

    def toFloat(self, hex):
        strippedhex = self.removeZero(hex)
        parsedhex = "".join(reversed(self.splitToNSize(strippedhex, 2)))
        if parsedhex == "":
            return 0
        output = struct.unpack("!f", bytes.fromhex(parsedhex))[0]
        return output

    def poptoken(self):
        try:
            tok = self.TOKENS.pop(0)
            if len(tok) == 8:
                return tok
        except Exception as error:
            logger.warning("exception pop:", error)

        return None

    def splitToN(self, inputstr: str, n: int):
        return [inputstr[i : i + n] for i in range(0, len(inputstr), n)]

    def mergePackets(self, rawdata: str):
        packetGroup = rawdata[16:20]
        rawdatalen = len(rawdata)

        if rawdatalen > 32 + 8:
            packetCount = int(rawdata[24 : 24 + 8], 16)
            packetIndex = int(rawdata[32 : 32 + 8], 16)

        if rawdatalen > 64 + 8 and rawdata[64 : 64 + 8] == "80120801":  # login data
            body = rawdata[72:]
            self.databuilder[packetGroup] = [None for _ in range(packetCount)]
            self.databuilder[packetGroup][packetIndex] = body
        elif rawdatalen > 58 + 8 and rawdata[56 : 56 + 8] == "00010e03":  # battle data
            body = rawdata[64:]
            self.databuilder[packetGroup] = [None for _ in range(packetCount)]
            self.databuilder[packetGroup][packetIndex] = body
        elif packetGroup in self.databuilder.keys():
            body = rawdata[56:]
            self.databuilder[packetGroup][packetIndex] = body
            if None not in self.databuilder[packetGroup]:
                return True, "".join(self.databuilder[packetGroup])
        else:
            index = 1_000_000
            for datatype in GODOT_DATATYPES:
                x = rawdata.find(datatype)
                if x > -1 and x < index:
                    index = x
            return True, rawdata[index:]

        return False, None

    def parseGodotData(self, rawdata):
        self.TOKENS = self.splitToN(rawdata, 8)
        values = []
        while len(self.TOKENS) != 0:
            values.append(self.keywords(self.poptoken()))
        return values

    def getLenofValue(self):
        charlength1 = self.toInt(self.poptoken())
        toklen = math.ceil(charlength1 / 4)
        return toklen

    def getDynamicSizeTok(self, toklen: int):
        realtok = "".join([self.poptoken() for _ in range(toklen)])
        return realtok

    def keywords(self, tok):
        if tok is None or tok == "00000000":
            return None
        elif tok == "01000000":  # bool
            return bool(self.toInt(self.poptoken()))
        elif tok == "02000000":  # integer
            return self.toInt(self.poptoken())
        elif tok == "03000000":  # float
            return self.toFloat(self.poptoken())
        elif tok == "04000000":  # string
            charlength = self.toInt(self.poptoken())
            toklen = math.ceil(charlength / 4)
            realtok = "".join([self.poptoken() for _ in range(toklen)])
            stringoutput = bytes.fromhex(self.removeZero(realtok))
            output = stringoutput.decode("utf-8")
            return output
        elif tok == "05000000":  # vector2
            xlen = self.getLenofValue()
            ylen = self.getLenofValue()
            x = self.toInt(self.getDynamicSizeTok(xlen))
            y = self.toInt(self.getDynamicSizeTok(ylen))
            return (x, y)
        elif tok == "1b000000":  # map/dictionary
            temp = {}
            numelements = self.toInt(self.poptoken())
            for x in range(numelements):
                key = self.keywords(self.poptoken())
                value = self.keywords(self.poptoken())
                temp[key] = value
            return temp
        elif tok == "1c000000" or tok == "1f000000":  # array
            temp = []
            numelements = self.toInt(self.poptoken())
            for x in range(numelements):
                temp.append(self.keywords(self.poptoken()))
            return temp
        return 0

    def packetFilter(self, packet: Packet):
        pkt = packet[0][1]

        if self.elapsedTime() > self.timeoutThreshold:
            logger.info("Timed out")
            return True

        if (pkt.src == "34.105.0.189" or pkt.dst == "34.105.0.189") and pkt.len > 44:
            try:
                validPacket, mergedPacket = self.mergePackets(pkt.load.hex())
                if not validPacket:
                    return False

                parsedObject = self.parseGodotData(mergedPacket)
                # with open(f"testing\\testData{time.time()}.json5", "w") as file:
                #     file.write(str(json.dumps(parsedObject, indent=2)))

                if (searchloc := self.checkSearchLocation(parsedObject)) is not None:
                    # print(f"Search Location: {searchloc}")
                    pass

                if isinstance(parsedObject, (list, dict)):
                    if parsedObject == []:
                        return False
                    try:
                        wildstar = parsedObject[1][0]["Star"]
                        self.currentWild = parsedObject[1][0]
                        wildstardict = {
                            "hp": wildstar[2],
                            "spd": wildstar[3],
                            "ea": wildstar[0],
                            "pa": wildstar[1],
                            "ed": wildstar[5],
                            "pd": wildstar[4],
                        }
                        self.output = wildstardict
                        self.ID = parsedObject[1][0]["Id"]
                        logger.info(json.dumps(parsedObject, indent=2))
                        return True
                    except Exception as e:
                        logger.warning(e)

                    logger.info(json.dumps(parsedObject, indent=2))

            except Exception as error:
                logger.warning("An error occurred:", error)

        return False

    def getData(self, timeout: int = 60):
        self.clear()
        self.timeoutThreshold = timeout
        self.setTimeStarted()
        sniff(filter="udp", stop_filter=self.packetFilter)
        self.timeElapsed = self.elapsedTime()

    def getStats(self, timeout: int = 60) -> dict:
        self.getData(timeout=timeout)
        return self.output

    def getWildData(self, timeout: int = 60) -> dict:
        self.getData(timeout=timeout)
        return self.currentWild
    
    def getStatsID(self, timeout: int = 60) -> str:
        self.getData(timeout=timeout)
        return self.output, self.ID


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mcdata = MiscritsData()
    stats = mcdata.getStatsID(10)
    logger.info(stats)
