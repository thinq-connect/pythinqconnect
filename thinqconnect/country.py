"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
from enum import Enum


class Country(str, Enum):
    AE = "AE"
    AF = "AF"
    AG = "AG"
    AL = "AL"
    AM = "AM"
    AO = "AO"
    AR = "AR"
    AT = "AT"
    AU = "AU"
    AW = "AW"
    AZ = "AZ"
    BA = "BA"
    BB = "BB"
    BD = "BD"
    BE = "BE"
    BF = "BF"
    BG = "BG"
    BH = "BH"
    BJ = "BJ"
    BO = "BO"
    BR = "BR"
    BS = "BS"
    BY = "BY"
    BZ = "BZ"
    CA = "CA"
    CD = "CD"
    CF = "CF"
    CG = "CG"
    CH = "CH"
    CI = "CI"
    CL = "CL"
    CM = "CM"
    CN = "CN"
    CO = "CO"
    CR = "CR"
    CU = "CU"
    CV = "CV"
    CY = "CY"
    CZ = "CZ"
    DE = "DE"
    DJ = "DJ"
    DK = "DK"
    DM = "DM"
    DO = "DO"
    DZ = "DZ"
    EC = "EC"
    EE = "EE"
    EG = "EG"
    ES = "ES"
    ET = "ET"
    FI = "FI"
    FR = "FR"
    GA = "GA"
    GB = "GB"
    GD = "GD"
    GE = "GE"
    GH = "GH"
    GM = "GM"
    GN = "GN"
    GQ = "GQ"
    GR = "GR"
    GT = "GT"
    GY = "GY"
    HK = "HK"
    HN = "HN"
    HR = "HR"
    HT = "HT"
    HU = "HU"
    ID = "ID"
    IE = "IE"
    IL = "IL"
    IN = "IN"
    IQ = "IQ"
    IR = "IR"
    IS = "IS"
    IT = "IT"
    JM = "JM"
    JO = "JO"
    JP = "JP"
    KE = "KE"
    KG = "KG"
    KH = "KH"
    KN = "KN"
    KR = "KR"
    KW = "KW"
    KZ = "KZ"
    LA = "LA"
    LB = "LB"
    LC = "LC"
    LK = "LK"
    LR = "LR"
    LT = "LT"
    LU = "LU"
    LV = "LV"
    LY = "LY"
    MA = "MA"
    MD = "MD"
    ME = "ME"
    MK = "MK"
    ML = "ML"
    MM = "MM"
    MR = "MR"
    MT = "MT"
    MU = "MU"
    MW = "MW"
    MX = "MX"
    MY = "MY"
    NE = "NE"
    NG = "NG"
    NI = "NI"
    NL = "NL"
    NO = "NO"
    NP = "NP"
    NZ = "NZ"
    OM = "OM"
    PA = "PA"
    PE = "PE"
    PH = "PH"
    PK = "PK"
    PL = "PL"
    PR = "PR"
    PS = "PS"
    PT = "PT"
    PY = "PY"
    QA = "QA"
    RO = "RO"
    RS = "RS"
    RU = "RU"
    RW = "RW"
    SA = "SA"
    SD = "SD"
    SE = "SE"
    SG = "SG"
    SI = "SI"
    SK = "SK"
    SL = "SL"
    SN = "SN"
    SO = "SO"
    SR = "SR"
    ST = "ST"
    SV = "SV"
    SY = "SY"
    TD = "TD"
    TG = "TG"
    TH = "TH"
    TN = "TN"
    TR = "TR"
    TT = "TT"
    TW = "TW"
    TZ = "TZ"
    UA = "UA"
    UG = "UG"
    US = "US"
    UY = "UY"
    UZ = "UZ"
    VC = "VC"
    VE = "VE"
    VN = "VN"
    XK = "XK"
    YE = "YE"
    ZA = "ZA"
    ZM = "ZM"

    def __str__(self):
        return self.name


class DomainPrefix(str, Enum):
    KIC = "kic"
    AIC = "aic"
    EIC = "eic"

    def __str__(self):
        return self.name


SUPPORTED_COUNTRIES = {
    DomainPrefix.KIC: [
        Country.AU,
        Country.BD,
        Country.CN,
        Country.HK,
        Country.ID,
        Country.IN,
        Country.JP,
        Country.KH,
        Country.KR,
        Country.LA,
        Country.LK,
        Country.MM,
        Country.MY,
        Country.NP,
        Country.NZ,
        Country.PH,
        Country.SG,
        Country.TH,
        Country.TW,
        Country.VN,
    ],
    DomainPrefix.AIC: [
        Country.AG,
        Country.AR,
        Country.AW,
        Country.BB,
        Country.BO,
        Country.BR,
        Country.BS,
        Country.BZ,
        Country.CA,
        Country.CL,
        Country.CO,
        Country.CR,
        Country.CU,
        Country.DM,
        Country.DO,
        Country.EC,
        Country.GD,
        Country.GT,
        Country.GY,
        Country.HN,
        Country.HT,
        Country.JM,
        Country.KN,
        Country.LC,
        Country.MX,
        Country.NI,
        Country.PA,
        Country.PE,
        Country.PR,
        Country.PY,
        Country.SR,
        Country.SV,
        Country.TT,
        Country.US,
        Country.UY,
        Country.VC,
        Country.VE,
    ],
    DomainPrefix.EIC: [
        Country.AE,
        Country.AF,
        Country.AL,
        Country.AM,
        Country.AO,
        Country.AT,
        Country.AZ,
        Country.BA,
        Country.BE,
        Country.BF,
        Country.BG,
        Country.BH,
        Country.BJ,
        Country.BY,
        Country.CD,
        Country.CF,
        Country.CG,
        Country.CH,
        Country.CI,
        Country.CM,
        Country.CV,
        Country.CY,
        Country.CZ,
        Country.DE,
        Country.DJ,
        Country.DK,
        Country.DZ,
        Country.EE,
        Country.EG,
        Country.ES,
        Country.ET,
        Country.FI,
        Country.FR,
        Country.GA,
        Country.GB,
        Country.GE,
        Country.GH,
        Country.GM,
        Country.GN,
        Country.GQ,
        Country.GR,
        Country.HR,
        Country.HU,
        Country.IE,
        Country.IL,
        Country.IQ,
        Country.IR,
        Country.IS,
        Country.IT,
        Country.JO,
        Country.KE,
        Country.KG,
        Country.KW,
        Country.KZ,
        Country.LB,
        Country.LR,
        Country.LT,
        Country.LU,
        Country.LV,
        Country.LY,
        Country.MA,
        Country.MD,
        Country.ME,
        Country.MK,
        Country.ML,
        Country.MR,
        Country.MT,
        Country.MU,
        Country.MW,
        Country.NE,
        Country.NG,
        Country.NL,
        Country.NO,
        Country.OM,
        Country.PK,
        Country.PL,
        Country.PS,
        Country.PT,
        Country.QA,
        Country.RO,
        Country.RS,
        Country.RU,
        Country.RW,
        Country.SA,
        Country.SD,
        Country.SE,
        Country.SI,
        Country.SK,
        Country.SL,
        Country.SN,
        Country.SO,
        Country.ST,
        Country.SY,
        Country.TD,
        Country.TG,
        Country.TN,
        Country.TR,
        Country.TZ,
        Country.UA,
        Country.UG,
        Country.UZ,
        Country.XK,
        Country.YE,
        Country.ZA,
        Country.ZM,
    ],
}


def get_region_from_country(country_code: Country) -> DomainPrefix:
    for domain_prefix in DomainPrefix:
        if country_code in SUPPORTED_COUNTRIES[domain_prefix]:
            return domain_prefix

    raise RuntimeError("Not supported country_code.")
