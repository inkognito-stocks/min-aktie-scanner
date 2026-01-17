# scanner_tickers.py

# "THE BEAST" - En massiv lista för maximal täckning
ticker_lists = {
    "Sverige 🇸🇪": {
        "Large Cap (OMXS30 & Co)": [
            "ABB.ST", "ALFA.ST", "ASSA-B.ST", "AZN.ST", "ATCO-A.ST", "ATCO-B.ST",
            "AXFO.ST", "BOL.ST", "CAST.ST", "ELUX-B.ST", "ERIC-B.ST", "ESSITY-B.ST",
            "EVO.ST", "GETI-B.ST", "HM-B.ST", "SHB-A.ST", "HEXA-B.ST", "HOLM-B.ST",
            "HUSQ-B.ST", "INDT.ST", "INVE-B.ST", "KINN-B.ST", "LATO-B.ST", "LIFCO-B.ST",
            "NIBE-B.ST", "NDA-SE.ST", "SAAB-B.ST", "SAND.ST", "SCA-B.ST", "SEB-A.ST",
            "SECU-B.ST", "SKA-B.ST", "SKF-B.ST", "SWED-A.ST", "TEL2-B.ST", "TELIA.ST",
            "TREL-B.ST", "VOLV-B.ST", "VOLCAR-B.ST", "EQT.ST", "EPI-A.ST", "BALD-B.ST",
            "AZA.ST", "VITR.ST", "THULE.ST", "SINCH.ST", "SBB-B.ST", "WALL-B.ST",
            "LUND-B.ST", "HUFV-A.ST", "BILL.ST", "AAK.ST", "AFRY.ST", "BRAV.ST"
        ],
        "Mid Cap & Small Cap (Blandat)": [
            "ACAD.ST", "ADVE.ST", "ANOD-B.ST", "AQ.ST", "ARJO-B.ST", "ATT.ST", "BACT-B.ST",
            "BEGR.ST", "BETCO.ST", "BHG.ST", "BILI-A.ST", "BIOA-B.ST", "BIOG-B.ST",
            "BIOT.ST", "BONG.ST", "BOOZT.ST", "BOUV.ST", "BTS-B.ST", "BUFAB.ST", "BULT.ST",
            "CALL.ST", "CAMX.ST", "CATE.ST", "CAT-B.ST", "CIBUS.ST", "CLAS-B.ST",
            "COIC.ST", "COLL.ST", "CORE-B.ST", "CTEEK.ST", "DIOS.ST", "DOME.ST", "DOR.ST",
            "DUST.ST", "EAST.ST", "ELOS-B.ST", "ELTEL.ST", "ENRO.ST", "ENQ.ST", "EOLU-B.ST",
            "EPIS-B.ST", "FAG.ST", "FAST.ST", "FING-B.ST", "FMART.ST", "FNM.ST", "GARO.ST",
            "G5EN.ST", "GRNG.ST", "HANZA.ST", "HEBA-B.ST", "HEM.ST", "HEXPOL-B.ST",
            "HMS.ST", "HOIST.ST", "HTRO.ST", "HUM.ST", "INSTAL.ST", "INTRUM.ST", "ITAB.ST",
            "JM.ST", "KABE-B.ST", "KAR.ST", "KNOX.ST", "LAGR-B.ST", "LAMM-B.ST", "LINC.ST",
            "LOOMIS.ST", "LVE.ST", "MEKO.ST", "MIPS.ST", "MQ.ST", "MTG-B.ST", "MYCR.ST",
            "NCC-B.ST", "NCAB.ST", "NETI-B.ST", "NOLA-B.ST", "NOTE.ST", "NP3.ST", "NYF.ST",
            "OEM-B.ST", "ORE.ST", "OX2.ST", "PNDX-B.ST", "PEAB-B.ST", "PLAZ-B.ST",
            "PRIC-B.ST", "PROF-B.ST", "RATO-B.ST", "RAY-B.ST", "READ.ST", "RESURS.ST",
            "SCST.ST", "SECT-B.ST", "SKIS-B.ST", "SSAB-B.ST", "STILL.ST", "STOR-B.ST",
            "SVED-B.ST", "SWEC-B.ST", "SYSR.ST", "TIETOS.ST", "TROAX.ST", "VBG-B.ST",
            "VPLAY-B.ST", "WIHL.ST", "XANO-B.ST", "XVIVO.ST"
        ],
        "First North (Tillväxt & Förhoppning)": [
            "ABLI.ST", "ACNE.ST", "ACTI.ST", "ADVER.ST", "AINO.ST", "ALIG.ST", "ALM.ST",
            "ANOT.ST", "APAB.ST", "ARPL.ST", "ASPIRE.ST", "BIM.ST", "BONE.ST", "BRG-B.ST",
            "CARY.ST", "CHECK.ST", "CINT.ST", "CLEAR.ST", "CLIME.ST", "CRAD-B.ST",
            "DEV.ST", "DIAD.ST", "DIGN.ST", "DIVIO.ST", "DRLN.ST", "ECO.ST", "EBR.ST",
            "ELLT.ST", "EMBRAC-B.ST", "ENEA.ST", "ENRO.ST", "ENVI.ST", "ESEN.ST",
            "EUROP.ST", "EVLI.ST", "EXPR.ST", "FINE.ST", "FIRE.ST", "FLOW.ST", "FPC-B.ST",
            "FRACT.ST", "GAPW-B.ST", "GENO.ST", "GOMR.ST", "HAYPP.ST", "HILD.ST",
            "IMPL-A.ST", "INWI.ST", "IRLAB-A.ST", "ISOFOL.ST", "JETTY.ST", "JOOL.ST",
            "KALLE.ST", "KDEV.ST", "LOGI.ST", "LYKO-A.ST", "MAGN.ST", "MANTEX.ST",
            "MBRS.ST", "MENT-B.ST", "MINT.ST", "MODEL-B.ST", "MOBA.ST", "NANESA.ST",
            "NEXT.ST", "NIV-B.ST", "NORD.ST", "NORVA.ST", "ODD.ST", "ONCO.ST", "OPT.ST",
            "OVZ.ST", "PAX.ST", "PEXA-B.ST", "PHYS.ST", "PIERCE.ST", "PLEJD.ST",
            "POLY.ST", "PREV-B.ST", "PROB.ST", "QLIFE.ST", "QUIA.ST", "RANA.ST", "RETO.ST",
            "RUG.ST", "RVRC.ST", "SALT-B.ST", "SAVOS.ST", "SDIP.ST", "SEZI.ST",
            "SIVERS.ST", "SLP-B.ST", "SMART.ST", "SMOL.ST", "SOLT.ST", "SPEQ.ST",
            "SPECTR.ST", "STORY-B.ST", "STRAX.ST", "SVEA-B.ST", "SYNC-B.ST", "TEQ.ST",
            "THQ.ST", "TOBII.ST", "TOUCH.ST", "TRNST.ST", "TRUE-B.ST", "USER.ST",
            "VESTUM.ST", "VNV.ST", "W5.ST", "WAY.ST", "XBRANE.ST", "XSPRAY.ST", "ZIGN.ST"
        ]
    },
    "Kanada 🇨🇦": {
        "TSX Energy (Oil/Gas Giants)": [
            "SU.TO", "CNQ.TO", "CVE.TO", "IMO.TO", "TRP.TO", "ENB.TO", "PPL.TO",
            "TOU.TO", "ARX.TO", "POW.TO", "VET.TO", "MEG.TO", "CPG.TO", "BTE.TO",
            "WCP.TO", "ERF.TO", "PEY.TO", "BIR.TO", "NVA.TO", "ATH.TO", "KEC.TO",
            "TVE.TO", "IPO.TO", "SES.TO", "CEU.TO", "CJ.TO", "GEI.TO", "KEY.TO",
            "PSI.TO", "MTL.TO", "ALA.TO"
        ],
        "TSX Mining (Global Majors)": [
            "ABX.TO", "AEM.TO", "TECK-B.TO", "IVN.TO", "FM.TO", "WPM.TO", "FNV.TO",
            "LUN.TO", "AGI.TO", "K.TO", "NGD.TO", "PAAS.TO", "SVM.TO", "MAG.TO",
            "DPM.TO", "EDV.TO", "ERO.TO", "LUG.TO", "ORA.TO", "SSRM.TO", "CG.TO",
            "ALS.TO", "TXG.TO", "OSK.TO", "AYA.TO", "ELD.TO", "IMG.TO", "BTO.TO",
            "LGO.TO", "EQX.TO", "YRI.TO", "SSRM.TO", "PVG.TO", "NG.TO"
        ],
        "TSX Venture (Junior Mining - The Goldmine)": [
            "MOG.V", "FIL.V", "LIO.V", "NFG.V", "GBR.V", "SGD.V", "ISO.V", "PMET.V",
            "LI.V", "EU.V", "VPT.V", "GLO.V", "DSV.V", "FL.V", "SKE.V", "PRYM.V",
            "MAX.V", "GIGA.V", "VGCX.V", "ARTG.V", "MAU.V", "FDR.V", "QTWO.V",
            "ATX.V", "ARIC.V", "NICU.V", "KRY.V", "PLSR.V", "FNM.V", "HSTR.V",
            "BFM.V", "DMX.V", "CVV.V", "FPC.V", "LBC.V", "AAG.V", "OGN.V", "EMO.V",
            "HMR.V", "LGC.V", "SHL.V", "GRZ.V", "HAMR.V", "MMY.V", "STD.V", "RRI.V",
            "DEC.V", "DV.V", "EPL.V", "GTT.V", "HIVE.V", "HSTR.V", "KNT.V", "LME.V",
            "NUG.V", "PGM.V", "QPM.V", "RIO.V", "RSLV.V", "RU.V", "SCOT.V", "SGN.V",
            "SIG.V", "SLL.V", "SO.V", "TAU.V", "TDG.V", "TEA.V", "TIG.V", "TUO.V",
            "VLE.V", "VZLA.V", "WM.V", "XTRA.V", "ZEN.V"
        ],
        "TSX Venture (Junior Energy/Tech/Misc)": [
            "SEI.V", "RECO.V", "JOY.V", "TAL.V", "STEP.V", "SDE.V", "TWM.V", "GXE.V",
            "OYL.V", "AAV.TO", "CR.TO", "YGR.TO", "SXE.TO", "VLE.TO", "CMC.V",
            "DM.V", "DOC.V", "ESE.V", "FOBI.V", "GRN.V", "HPQ.V", "PYR.V",
            "QYOU.V", "SOLR.V", "VO.V", "WELL.TO", "XBC.TO"
        ],
        "CSE (High Risk / Speculative)": [
            "KUYA.CN", "AMQ.CN", "API.CN", "ARS.CN", "ACDX.CN", "ACM.CN", "PMAX.CN",
            "NEXU.CN", "EMET.CN", "TUNG.CN", "MSM.CN", "QIMC.CN", "EATH.CN",
            "APXC.CN", "BLLG.CN", "SLV.CN", "CCI.CN", "UUU.CN", "ATMY.CN", "LFLR.CN",
            "AAB.CN", "ABR.CN", "ACT.CN", "AGB.CN", "BIG.CN", "BOSS.CN", "CANS.CN",
            "COOL.CN", "DIGI.CN", "DRUG.CN", "EGLX.TO", "FE.CN", "GLD.CN", "GTII.CN",
            "ION.CN", "JANE.CN", "LIFT.CN", "LITE.CN", "MEDV.CN", "MSET.CN",
            "NUMI.TO", "OPT.CN", "PLTH.CN", "RIV.CN", "RVV.CN", "THRM.CN",
            "TRIP.CN", "TRUL.CN", "VEXT.CN", "XPHY.CN"
        ]
    }
}