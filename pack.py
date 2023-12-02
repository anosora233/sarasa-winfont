from platform import system

assert system() == "Windows"

from fontTools.ttLib import TTFont, TTCollection

# In | WinFont | Out | fWeight | xAvgCharWidth
fDATA = [
    ("sarasa-ui-sc-regular.ttf", "C:\Windows\Fonts\msyh.ttc", "msyh.ttc", 400, 500),
    ("sarasa-ui-sc-light.ttf", "C:\Windows\Fonts\msyhl.ttc", "msyhl.ttc", 290, 500),
    ("sarasa-ui-sc-bold.ttf", "C:\Windows\Fonts\msyhbd.ttc", "msyhbd.ttc", 700, 500),
]

for sIN, sCOL, sOUT, fWGHT, fWIDTH in fDATA:
    fCOL = TTCollection(sCOL)
    fCOLn = TTCollection()

    for fWIN in fCOL.fonts:
        fIN = TTFont(sIN, recalcBBoxes=False)

        # Fix
        fIN["name"] = fWIN["name"]
        fIN["OS/2"].usWeightClass = fWGHT
        fIN["OS/2"].xAvgCharWidth = fWIDTH

        # Purge
        GSUB = fIN["GSUB"].table

        ScriptRecord = GSUB.ScriptList.ScriptRecord
        FeatureRecord = GSUB.FeatureList.FeatureRecord
        Lookup = GSUB.LookupList.Lookup

        # Fetch
        RemainFeat = []
        RemainFeatIndex = []
        for i in range(len(FeatureRecord) - 1, -1, -1):
            if FeatureRecord[i].FeatureTag == "vert":
                RemainFeatIndex.append(i)
                RemainFeat.append(FeatureRecord[i])
        # Merge
        LookupListIndex = set()
        for F in RemainFeat:
            LookupListIndex |= set(F.Feature.LookupListIndex)

        # Simplify
        RemainFeat[0].Feature.LookupListCount = len(LookupListIndex)
        RemainFeat[0].Feature.LookupListIndex = list(range(0, len(LookupListIndex)))
        GSUB.LookupList.Lookup = [Lookup[Index] for Index in LookupListIndex]
        GSUB.FeatureList.FeatureRecord = RemainFeat[0:1]

        for m in range(len(ScriptRecord) - 1, -1, -1):
            # DEFAULT
            del ScriptRecord[m].Script.DefaultLangSys

            # SPECIAL
            for n in range(len(ScriptRecord[m].Script.LangSysRecord) - 1, -1, -1):
                LangSys = ScriptRecord[m].Script.LangSysRecord[n].LangSys
                if "JAN" in ScriptRecord[m].Script.LangSysRecord[n].LangSysTag and set(
                    RemainFeatIndex
                ) & set(LangSys.FeatureIndex):
                    LangSys.FeatureIndex, LangSys.FeatureCount = [0], 1
                else:
                    del ScriptRecord[m].Script.LangSysRecord[n]

        fCOLn.fonts.append(fIN)
    fCOLn.save(sOUT)
