from scapy.all import sniff, Packet
import struct
import math
import json
import logging

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
        self.TOKENS = []
        self.currenttok = ""
        self.wholepacketdata = ""
        self.previousWild = []
        self.currentWild = []
        self.output = {}

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
            self.currenttok = tok
            if len(tok) == 8:
                return tok
            return None
        except Exception:
            return None

    def splitToN(self, inputstr: str, n: int):
        return [inputstr[i : i + n] for i in range(0, len(inputstr), n)]

    def getTokens(self, rawdata: str):
        index = 0
        if rawdata.startswith("000200000000") or rawdata.startswith("000300000000"):
            index = 36
        elif rawdata.startswith("0002000000") or rawdata.startswith("0003000000"):
            index = 28
        else:
            index = 1_000_000
            for datatype in GODOT_DATATYPES:
                x = rawdata.find(datatype)
                if x > -1 and x < index:
                    index = x

        # every 8 characters
        tkns = self.splitToN(rawdata[index:], 8)
        return tkns

    def parsegodot(self, rawdata):
        self.TOKENS = self.getTokens(rawdata=rawdata)
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

    def _getStats(self, packet: Packet):
        pkt = packet[0][1]

        if (pkt.src == "34.105.0.189" or pkt.dst == "34.105.0.189") and pkt.len > 44:
            try:
                line = pkt.load.hex()
                n = 2
                temp_hex = self.splitToN(line, n)
                temp_hex = "".join(temp_hex)

                # remove first 28 characters, TODO: determine what is the purpose
                temp_hex = temp_hex[28:]

                # if udp packet is greater len than 1420 it means it has a next part
                if pkt.len >= 1420:
                    self.wholepacketdata += "".join(self.getTokens(temp_hex))
                    return False

                self.wholepacketdata += "".join(self.getTokens(temp_hex))

                parsedobject = self.parsegodot(self.wholepacketdata)

                if isinstance(parsedobject, (list, dict)):
                    if parsedobject == []:
                        return False
                    try:
                        wildstar = parsedobject[1][0]["Star"]
                        self.currentWild = parsedobject[1][0]

                        if self.currentWild == self.previousWild:
                            return False

                        self.previousWild = self.currentWild
                        wildstardict = {
                            "hp": wildstar[2],
                            "spd": wildstar[3],
                            "ea": wildstar[0],
                            "pa": wildstar[1],
                            "ed": wildstar[5],
                            "pd": wildstar[4],
                        }
                        self.output = wildstardict
                        return True
                    except Exception as e:
                        logger.warning(e)

                    logger.info(json.dumps(parsedobject, indent=2))

                self.wholepacketdata = ""
            except Exception as error:
                logger.warning("An error occurred:", type(error).__name__, "–", error)

        return False

    def getStats(self) -> dict:
        sniff(filter="udp", stop_filter=self._getStats)
        return self.output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mcdata = MiscritsData()
    stats = mcdata.getStats()
    logger.info(stats)
