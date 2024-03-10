# 解析余票接口的价格码
def get_price_yp(yp_info_new):
    wu = 0
    price = []
    de = bH(yp_info_new)

    # 0.商务座/特等座
    if de.get("9") or de.get("P"):
        price.append(de["9"]) if de.get("9") else price.append(de["P"])
    else:
        price.append(wu)

    # 1.一等座
    price.append(de.get("M", wu))

    # 2.二等座/二等包座
    if de.get("O") or de.get("S"):
        price.append(de["O"]) if de.get("O") else price.append(de["S"])
    else:
        price.append(wu)

    # 3.高级软卧
    if de.get("6") or de.get("A"):
        price.append(de["6"]) if de.get("6") else price.append(de["A"])
    else:
        price.append(wu)

    # 4.软卧/一等卧
    if de.get("4") or de.get("I"):
        price.append(de["4"]) if de.get("4") else price.append(de["I"])
    else:
        price.append(wu)

    # 5.动卧
    price.append(de.get("F", wu))

    # 6.硬卧/二等卧
    if de.get("3") or de.get("J"):
        price.append(de["3"]) if de.get("3") else price.append(de["J"])
    else:
        price.append(wu)

    # 7.软座
    price.append(de.get("2", wu))

    # 8.硬座
    price.append(de.get("1", wu))

    # 9.无座
    price.append(de.get("W", wu))

    # 10.其他
    if de.get("5") or de.get("D") or de.get("E") or de.get("G") or de.get("H") or de.get("Q"):
        price.append(de.get("5", de.get("D", de.get("E", de.get("G", de.get("H", de.get("Q", "")))))))
    else:
        price.append(wu)

    return price


def bH(dd):
    de = {}
    dc = len(dd) // 10
    for price in range(dc):
        db = dd[price * 10: price * 10 + 10]
        c8 = db[0]
        da = db[6]
        df = float(int(db[1:6]) / 10)
        if da == "3":
            de["W"] = df
        else:
            de[c8] = df
    return de


# 解析票价接口的价格码
def get_price_public(param):
    bJ = []
    bF = ah(param)
    bD = 0

    # 0.商务座
    if bF.get("9"):
        bJ.append(bF["9"])
    else:
        bJ.append(bD)

    # 1.特等座
    if bF.get("P"):
        bJ.append(bF["P"])
    else:
        bJ.append(bD)

    # 2.一等座
    if bF.get("M"):
        bJ.append(bF["M"])
    else:
        bJ.append(bD)

    # 3.二等坐/二等包座
    if bF.get("O") or bF.get("S"):
        if bF.get("O"):
            bJ.append(bF["O"])
        else:
            bJ.append(bF["S"])
    else:
        bJ.append(bD)

    # 4.高级软卧
    if bF.get("6"):
        bJ.append(bF["6"])
    else:
        bJ.append(bD)

    # 5.软卧/一等卧
    if bF.get("4") or bF.get("I"):
        if bF.get("4"):
            bJ.append(bF["4"])
        else:
            bJ.append(bF["I"])
    else:
        bJ.append(bD)

    # 6.动卧
    if bF.get("F"):
        bJ.append(bF["F"])
    else:
        bJ.append(bD)

    # 7.硬卧/二等卧
    if bF.get("3") or bF.get("J"):
        if bF.get("3"):
            bJ.append(bF["3"])
        else:
            bJ.append(bF["J"])
    else:
        bJ.append(bD)

    # 8.软座
    if bF.get("2"):
        bJ.append(bF["2"])
    else:
        bJ.append(bD)

    # 9.硬座
    if bF.get("1"):
        bJ.append(bF["1"])
    else:
        bJ.append(bD)

    # 10.无座
    if bF.get("W"):
        bJ.append(bF["W"])
    else:
        bJ.append(bD)

    # 11.其他
    if bF.get("5") or bF.get("D") or bF.get("E") or bF.get("G") or bF.get("H") or bF.get("Q"):
        bK = bF.get("5", bF.get("D", bF.get("E", bF.get("G", bF.get("H", bF.get("Q", ""))))))

        bH = "5" if "5" in bF else "D" if "D" in bF else "E" if "E" in bF else "G" if "G" in bF else "H" if "H" in bF else "Q"
        bJ.append(bK)
    else:
        bJ.append(bD)

    return bJ


def ah(bI):
    bJ = {}
    bH = bI.split("#")
    for bF in bH:
        if bF:
            bE = bF[0]
            bD = "" if bF[9:10] == "0" else bF[9:10]
            bK = float(bF[1:6]) / 10
            bJ[bE + bD] = bK
            if bD != "":
                bJ[bE] = bK
    return bJ
