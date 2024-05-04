from scapy.all import sniff, Packet
import struct
import json
import math

TOKENS = []


def splitToNSize(value: str, n):
    string = value
    return [string[i : i + n] for i in range(0, len(string), n)]


def removeZero(tok: str):
    if tok is None:
        return ""
    while tok.endswith("00"):
        tok = tok[:-2]
    return tok


def toInt(hex):
    strippedhex = removeZero(hex)
    parsedhex = "".join(reversed(splitToNSize(strippedhex, 2)))
    if parsedhex == "":
        return 0
    output = int(parsedhex, 16)
    return output


def toFloat(hex):
    strippedhex = removeZero(hex)
    parsedhex = "".join(reversed(splitToNSize(strippedhex, 2)))
    if parsedhex == "":
        return 0
    output = struct.unpack("!f", bytes.fromhex(parsedhex))[0]
    return output


currenttok = ""


def poptoken():
    global currenttok
    try:
        tok = TOKENS.pop(0)
        currenttok = tok
        if len(tok) == 8:
            return tok
        return None
    except Exception:
        return None


DATATYPES = [
    "01000000",
    "02000000",
    "03000000",
    "04000000",
    "05000000",
    "1b000000",
    "1c000000",
    "1f000000",
]


def getTokens(rawdata: str):
    index = 0
    if rawdata.startswith("000200000000") or rawdata.startswith("000300000000"):
        index = 36
    elif rawdata.startswith("0002000000") or rawdata.startswith("0003000000"):
        index = 28
    else:
        index = 1_000_000
        for datatype in DATATYPES:
            x = rawdata.find(datatype)
            if x > -1 and x < index:
                index = x
    string = rawdata[index:]
    n = 8  # every n characters
    tkns = [string[i : i + n] for i in range(0, len(string), n)]
    return tkns


def parsegodot(rawdata):
    global TOKENS
    TOKENS = getTokens(rawdata=rawdata)
    values = []
    while len(TOKENS) != 0:
        values.append(keywords(poptoken()))
    return values


def getyes():
    charlength1 = toInt(poptoken())
    toklen = math.ceil(charlength1 / 4)
    realtok = "".join([poptoken() for _ in range(toklen)])
    return realtok


def getLenofValue():
    charlength1 = toInt(poptoken())
    toklen = math.ceil(charlength1 / 4)
    return toklen


def getDynamicSizeTok(toklen: int):
    realtok = "".join([poptoken() for _ in range(toklen)])
    return realtok


def keywords(tok):
    if tok is None:
        return None
    elif tok == "00000000":
        return None
    elif tok == "01000000":  # bool
        return bool(toInt(poptoken()))
    elif tok == "02000000":  # integer
        return toInt(poptoken())
    elif tok == "03000000":  # float
        return toFloat(poptoken())
    elif tok == "04000000":  # string
        charlength = toInt(poptoken())
        toklen = math.ceil(charlength / 4)
        realtok = "".join([poptoken() for _ in range(toklen)])
        stringoutput = bytes.fromhex(removeZero(realtok))
        output = stringoutput.decode("utf-8")
        return output
    elif tok == "05000000":  # vector2
        xlen = getLenofValue()
        ylen = getLenofValue()
        x = toInt(getDynamicSizeTok(xlen))
        y = toInt(getDynamicSizeTok(ylen))
        return (x, y)
    elif tok == "1b000000":  # map/dictionary
        temp = {}
        numelements = toInt(poptoken())
        for x in range(numelements):
            key = keywords(poptoken())
            value = keywords(poptoken())
            temp[key] = value
        return temp
    elif tok == "1c000000":  # array
        temp = []
        numelements = toInt(poptoken())
        for x in range(numelements):
            temp.append(keywords(poptoken()))
        return temp
    elif tok == "1f000000":
        temp = []
        numelements = toInt(poptoken())
        for x in range(numelements):
            temp.append(keywords(poptoken()))
        return temp
    return 0


wholepacketdata = ""
previousmiscrit = []


def custom_action(packet: Packet):
    global wholepacketdata, previousmiscrit
    pkt = packet[0][1]
    if (pkt.src == "34.105.0.189" or pkt.dst == "34.105.0.189") and pkt.len > 40:
        if pkt.len < 44:
            return
        try:
            line = pkt.load.hex()
            n = 2
            groupped = [line[i : i + n].capitalize() for i in range(0, len(line), n)]
            joinned = "".join(groupped)
            joinned = joinned[28:]
            if pkt.len >= 1420:
                wholepacketdata += "".join(getTokens(joinned))
                return False

            wholepacketdata += "".join(getTokens(joinned))

            parsedobject = parsegodot(wholepacketdata)
            if isinstance(parsedobject, (list, dict)):
                if parsedobject == []:
                    return False
                try:
                    wildstar = parsedobject[1][0]["Star"]
                    wild = parsedobject[1][0]
                    if wild != previousmiscrit:
                        previousmiscrit = wild
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
                    return True
                except Exception as e:
                    print(e)
                print(json.dumps(parsedobject, indent=2))
            elif parsedobject is None:
                if len(wholepacketdata) != len("9000ed8c8600023a000607012760464e"):
                    print(wholepacketdata)
            else:
                print(parsedobject)

            wholepacketdata = ""
        except Exception as error:
            print("An error occurred:", type(error).__name__, "–", error)

    return False


sniff(filter="udp", stop_filter=custom_action)
