from scapy.all import sniff, Packet
import struct
import json
import math

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
        self.previousmiscrit = []
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
        string = rawdata[index:]
        n = 8  # every n characters
        tkns = [string[i : i + n] for i in range(0, len(string), n)]
        return tkns

    def parsegodot(self, rawdata):
        self.TOKENS = self.getTokens(rawdata=rawdata)
        values = []
        while len(self.TOKENS) != 0:
            values.append(self.keywords(self.poptoken()))
        return values

    def getyes():
        charlength1 = self.toInt(self.poptoken())
        toklen = math.ceil(charlength1 / 4)
        realtok = "".join([self.poptoken() for _ in range(toklen)])
        return realtok

    def getLenofValue(self):
        charlength1 = self.toInt(self.poptoken())
        toklen = math.ceil(charlength1 / 4)
        return toklen

    def getDynamicSizeTok(self, toklen: int):
        realtok = "".join([self.poptoken() for _ in range(toklen)])
        return realtok

    def keywords(self, tok):
        if tok is None:
            return None
        elif tok == "00000000":
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
        elif tok == "1c000000":  # array
            temp = []
            numelements = self.toInt(self.poptoken())
            for x in range(numelements):
                temp.append(self.keywords(self.poptoken()))
            return temp
        elif tok == "1f000000":
            temp = []
            numelements = self.toInt(self.poptoken())
            for x in range(numelements):
                temp.append(self.keywords(self.poptoken()))
            return temp
        return 0

    def _getStats(self, packet: Packet):
        pkt = packet[0][1]
        if (pkt.src == "34.105.0.189" or pkt.dst == "34.105.0.189") and pkt.len > 40:
            if pkt.len < 44:
                return
            try:
                line = pkt.load.hex()
                n = 2
                groupped = [
                    line[i : i + n].capitalize() for i in range(0, len(line), n)
                ]
                joinned = "".join(groupped)
                joinned = joinned[28:]
                if pkt.len >= 1420:
                    self.wholepacketdata += "".join(self.getTokens(joinned))
                    return False

                self.wholepacketdata += "".join(self.getTokens(joinned))

                parsedobject = self.parsegodot(self.wholepacketdata)
                if isinstance(parsedobject, (list, dict)):
                    if parsedobject == []:
                        return False
                    try:
                        wildstar = parsedobject[1][0]["Star"]
                        wild = parsedobject[1][0]
                        if wild != self.previousmiscrit:
                            self.previousmiscrit = wild
                        else:
                            return
                        wildstar = wild["Star"]
                        wildstardict = {
                            "hp": wildstar[2],
                            "spd": wildstar[3],
                            "ea": wildstar[0],
                            "pa": wildstar[1],
                            "ed": wildstar[5],
                            "pd": wildstar[4],
                        }
                        print(wildstardict)
                        self.output = wildstardict
                        return True
                    except Exception as e:
                        print(e)
                    print(json.dumps(parsedobject, indent=2))
                elif parsedobject is None:
                    if len(self.wholepacketdata) != len(
                        "9000ed8c8600023a000607012760464e"
                    ):
                        print(self.wholepacketdata)
                else:
                    print(parsedobject)

                self.wholepacketdata = ""
            except Exception as error:
                print("An error occurred:", type(error).__name__, "–", error)

        return False

    def getStats(self) -> dict:
        sniff(filter="udp", stop_filter=self._getStats)
        return self.output


if __name__ == "__main__":
    mcdata = MiscritsData()
    mcdata.getStats()
