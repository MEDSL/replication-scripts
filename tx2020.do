///////////////////////////////////////
/*
Kevin DeLuca
MEDSL Precinct Project

TX cleaning code
*/
///////////////////////////////////////

clear
set more off


*first, quickly clean a VTD to county crosswalk file
import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/VTDsPop_20G.txt", clear
keep cnty cntyvtd
rename cntyvtd precinct
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/countyVTDxwalk.dta", replace



*now, combine all data, 
*get data from individual sheets to dta data, for each office/race
global offices1 = `" "state rep 90" "state rep 67" "state rep 73" "state sen 13" "state sen 12" "travis co comm 1" "sboe 5" "96th district judge" "us sen" "state rep 72" "tarrant co comm 1" "state rep 66" "state sen 6" "state rep 99" "state sen 4" "state rep 148" "469th district judge" "state rep 58" "tarrant co comm 3" "state rep 70" "state rep 64" "coa 8 chief" "nueces sheriff" "61st district judge" "travis co comm 3" "state sen 11" "sboe 10" "sboe 6" "129th district judge" "jefferson sheriff" "montgomery sheriff" "bexar constable 4" "harris crim ct at law 12" "395th district judge" "366th district judge" "state rep 65" "state rep 71" "state rep 59" "state rep 149" "407th district judge" "state sen 1" "state rep 75" "state rep 61" "state rep 49" "harris crim ct at law 16" "harris sheriff" "state sen 29" "sboe 14" "387th district judge" "state sen 28" "sboe 15" "travis co judge" "harris jp 5 pl 1" "nueces da 105th" "hidalgo sheriff" "state rep 48" "state rep 60" "state rep 74" "collin tax ac" "'

global offices2 = `" "431st district judge" "coa 4 chief" "153rd district judge" "state rep 89" "state rep 62" "brazos co attorney" "state rep 76" "cca 9" "fort bend ct at law 5" "sboe 1" "brazoria ct at law 1" "president" "bexar constable 2" "tarrant tax ac" "state rep 77" "state rep 63" "state rep 88" "state rep 114" "state rep 100" "state rep 128" "state rep 38" "coa 5 place 6" "us rep 11" "dallas sheriff" "state rep 10" "state rep 5" "351st district judge" "468th district judge" "brazos sheriff" "nueces co attorney" "bexar sheriff" "us rep 1" "133rd district judge" "state rep 4" "state rep 11" "us rep 10" "56th district judge" "state rep 39" "state rep 129" "state rep 101" "state rep 115" "state rep 103" "state rep 117" "us rep 12" "brazoria tax ac" "state rep 13" "127th district judge" "coa 14 place 7" "state rep 6" "us rep 3" "us rep 2" "travis sheriff" "state rep 7" "352nd district judge" "507th district judge" "state rep 12" "us rep 13" "state rep 116" "state rep 102" "'

global offices3 = `" "state rep 106" "state rep 112" "state rep 16" "us rep 17" "37th district judge" "state rep 3" "347th district judge" "434th district judge" "fort bend tax ac" "us rep 6" "galveston sheriff" "sup ct 8" "us rep 7" "state rep 2" "80th district judge" "us rep 16" "state rep 17" "state rep 113" "state rep 107" "state rep 139" "state rep 111" "386th district judge" "state rep 105" "state rep 15" "us rep 28" "state rep 29" "coa 5 place 3" "us rep 14" "254th district judge" "travis da 53rd" "334th district judge" "us rep 5" "215th district judge" "us rep 4" "471st district judge" "state rep 1" "state rep 28" "us rep 15" "state rep 14" "us rep 29" "state rep 104" "state rep 110" "348th district judge" "state rep 138" "state rep 135" "state rep 121" "state rep 109" "state rep 19" "us rep 24" "us rep 30" "state rep 25" "us rep 18" "state rep 31" "380th district judge" "400th district judge" "us rep 9" "213th district judge" "tarrant constable 7" "sup ct 6" "'

global offices4 = `" "sup ct chief" "sup ct 7" "tarrant constable 6" "us rep 8" "williamson sheriff" "state rep 30" "state rep 24" "harris tax ac" "us rep 19" "us rep 31" "405th district judge" "state rep 18" "us rep 25" "state rep 108" "state rep 120" "state rep 134" "state rep 122" "state rep 136" "48th district judge" "us rep 33" "us rep 27" "state rep 32" "state rep 26" "401st district judge" "tarrant sheriff" "state rep 27" "state rep 33" "us rep 26" "us rep 32" "state rep 137" "state rep 123" "state rep 127" "26th district judge" "state rep 133" "state rep 37" "state rep 23" "us rep 36" "us rep 22" "bexar co comm 3" "464th district judge" "67th district judge" "tarrant constable 1" "tarrant crim ct at law 2" "383rd district judge" "162nd district judge" "coa 13 place 6" "us rep 23" "state rep 22" "coa 5 place 8" "state rep 36" "state rep 132" "state rep 126" "165th district judge" "coa 2 place 6" "state rep 118" "state rep 130" "state rep 124" "state rep 20" "state rep 34" "'

global offices5 = `" "us rep 21" "us rep 35" "coa 13 place 4" "14th district judge" "state rep 9" "harris co clerk" "tarrant constable 2" "state rep 8" "bexar co comm 1" "us rep 34" "us rep 20" "state rep 35" "state rep 21" "state rep 125" "state rep 131" "bexar jp 2" "voter data" "state rep 119" "state rep 142" "state rep 85" "state rep 91" "coa 3 chief" "state rep 46" "state rep 52" "harris constable 3" "339th district judge" "state sen 26" "state sen 27" "342nd district judge" "harris constable 2" "state rep 53" "state rep 47" "cca 4" "fort bend sheriff" "state rep 90" "state rep 84" "state rep 143" "state rep 141" "state rep 92" "state rep 86" "144th district judge" "state rep 79" "state rep 51" "state rep 45" "harris co comm 3" "state sen 19" "state sen 24" "state sen 18" "coa 1 place 5" "state rep 44" "state rep 50" "state rep 78" "travis ct at law 9" "state rep 87" "state rep 93" "state rep 140" "'

global offices6 = `" "state rep 97" "state rep 83" "state rep 144" "state rep 150" "state rep 54" "cca 3" "state rep 40" "state rep 68" "416th district judge" "harris civil ct at law 4" "harris constable 5" "cameron dist clerk" "457th district judge" "state sen 20" "state sen 21" "harris constable 4" "fort bend co attorney" "cameron sheriff" "28th district judge" "williamson co attorney" "bexar tax ac" "state rep 69" "harris co attorney" "dallas co comm 3" "state rep 41" "state rep 55" "state rep 145" "state rep 82" "state rep 96" "360th district judge" "state rep 80" "state rep 94" "travis tax ac" "state rep 147" "state rep 43" "state rep 57" "dallas co comm 1" "coa 14 chief" "95th district judge" "505th district judge" "sboe 8" "rr comm 1" "399th district judge" "164th district judge" "state sen 22" "harris jp 1 pl 1" "sboe 9" "harris da" "coa 1 place 3" "state rep 56" "state rep 42" "state rep 146" "state rep 95" "state rep 81" "460th district judge" "'


local o = 1
foreach off1 in $offices1{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/raw/`off1'.csv", clear
	rename cntyvtd precinct
	capture tostring(precinct),replace
	gen office = "`off1'"
	rename *_20g* **
	tempfile office`o'
	save `office`o''
	display "`off1'"
	local o = `o'+1
}
foreach off2 in $offices2{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/raw/`off2'.csv", clear
	rename cntyvtd precinct
	capture tostring(precinct),replace
	gen office = "`off2'"
	tempfile office`o'
	save `office`o''
	display "`off2'"
	local o = `o'+1
}
foreach off3 in $offices3{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/raw/`off3'.csv", clear
	rename cntyvtd precinct
	capture tostring(precinct),replace
	gen office = "`off3'"
	tempfile office`o'
	save `office`o''
	display "`off3'"
	local o = `o'+1
}
foreach off4 in $offices4{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/raw/`off4'.csv", clear
	rename cntyvtd precinct
	capture tostring(precinct),replace
	gen office = "`off4'"
	tempfile office`o'
	save `office`o''
	display "`off4'"
	local o = `o'+1
}
foreach off5 in $offices5{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/raw/`off5'.csv", clear
	rename cntyvtd precinct
	capture tostring(precinct),replace
	gen office = "`off5'"
	tempfile office`o'
	save `office`o''
	display "`off5'"
	local o = `o'+1
}
foreach off6 in $offices6{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/raw/`off6'.csv", clear
	rename cntyvtd precinct
	capture tostring(precinct),replace
	gen office = "`off6'"
	tempfile office`o'
	save `office`o''
	display "`off6'"
	local o = `o'+1
}

local o = `o'-1

use `office1', clear
forval x=2(1)`o'{
	append using `office`x''
}


replace office = strupper(office)
order precinct office

rename voter_registration voterreg 
rename spanish_surname_voter_registrati spanishvoterreg
rename spanish_surname_turnout spanishturnout

gen candidate = ""
local s=1
foreach var of varlist voterreg turnout spanishvoterreg spanishturnout romerod_staterep90 camachor_staterep90 leachr_staterep67 sanchezd_staterep67 biedermannr_staterep73 phillipsd_staterep73 milesd_statesen13 morrisr_statesen13 nelsonr_statesen12 zitoond_statesen12 travilliond_traviscocomm1 arcovenr_traviscocomm1 bellmetereaud_sboe5 poppr_sboe5 berlinl_sboe5 brandenburgd_96thdistrictjud gallagherr_96thdistrictjudge cornynr_ussen hegard_ussen mckennonl_ussen collinsg_ussen darbyr_staterep72 brooksd_tarrantcocomm1 lozanor_tarrantcocomm1 shaheenr_staterep66 hirschd_staterep66 jonesl_staterep66 alvaradod_statesen6 duffieldl_statesen6 gerenr_staterep99 creightonr_statesen4 stittleburgd_statesen4 brockl_statesen4 shawd_staterep148 larottar_staterep148 mccrawr_469thdistrictjudge huffmand_469thdistrictjudge burnsr_staterep58 rochad_staterep58 fickesr_tarrantcocomm3 braatzd_tarrantcocomm3 sanfordr_staterep70 badod_staterep70 stuckyr_staterep64 brewerd_staterep64 alleyr_coa8chief rodriguezd_coa8chief hooperr_nuecessheriff torresd_nuecessheriff phillipsd_61stdistrictjudge luncefordr_61stdistrictjudge howardd_traviscocomm3 brayr_traviscocomm3 taylorr_statesen11 crissd_statesen11 wissell_statesen11 maynardr_sboe10 burnettwebsterd_sboe10 seiboldl_sboe10 palmerd_sboe6 hickmanr_sboe6 bilyeul_sboe6 gomezd_129thdistrictjudge archerr_129thdistrictjudge stephensd_jeffersonsheriff odomr_jeffersonsheriff broussardl_jeffersonsheriff hendersonr_montgomerysheriff husseinid_montgomerysheriff brownd_bexarconstable4 rickettsr_bexarconstable4 draperd_harriscrimctatlaw12 garciar_harriscrimctatlaw12 larsonr_395thdistrictjudge deltorod_395thdistrictjudge nowakr_366thdistrictjudge johnsond_366thdistrictjudge beckleyd_staterep65 thimeschr_staterep65 lambertr_staterep71 hattond_staterep71 slawsonr_staterep59 vod_staterep149 truongr_staterep149 torresd_407thdistrictjudge walshr_407thdistrictjudge hughesr_statesen1 spankod_statesen1 gonzalezd_staterep75 kingr_staterep61 coxd_staterep61 stephensonl_staterep61 hinojosad_staterep49 meyerr_staterep49 moorel_staterep49 jordand_harriscrimctatlaw16 harmonr_harriscrimctatlaw16 gonzalezd_harrissheriff dannar_harrissheriff blancod_statesen29 hatchr_statesen29 meltonr_sboe14 alvordd_sboe14 mullinixr_387thdistrictjudge bueningheppardd_387thdistric perryr_statesen28 betancourtd_sboe15 johnsonr_sboe15 brownd_traviscojudge lovinsr_traviscojudge ridgwayr_harrisjp5pl1 garciad_harrisjp5pl1 gonzalezd_nuecesda105th westr_nuecesda105th guerrad_hidalgosheriff jurador_hidalgosheriff howardd_staterep48 strieberr_staterep48 rogersr_staterep60 moralesd_staterep74 falconr_staterep74 maunr_collintaxac turnermcclellandd_collintaxa weitzeld_20g_431stdistrictjudge johnsonr_20g_431stdistrictjudge martinezd_20g_coa4chief yantar_20g_coa4chief mccoyr_20g_153rddistrictjudge dardend_20g_153rddistrictjudge nobler_20g_staterep89 ashd_20g_staterep89 klessl_20g_staterep89 smithr_20g_staterep62 thomasd_20g_staterep62 medinad_20g_brazoscoattorney grayr_20g_brazoscoattorney ordazperezd_20g_staterep76 newellr_20g_cca9 birminghamd_20g_cca9 watsond_20g_fortbendctatlaw5 hrbacekr_20g_fortbendctatlaw5 perezd_20g_sboe1 iveyr_20g_sboe1 normand_20g_brazoriactatlaw1 gilbertr_20g_brazoriactatlaw1 bidend_20g_president trumpr_20g_president jorgensenl_20g_president hawkinsg_20g_president writeinw_20g_president vazquezd_20g_bexarconstable2 penar_20g_bexarconstable2 burgessr_20g_tarranttaxac andersond_20g_tarranttaxac ortegad_20g_staterep77 parkerr_20g_staterep63 peelerd_20g_staterep63 kingr_20g_staterep88 turnerd_20g_staterep114 delrosalr_20g_staterep114 crockettd_20g_staterep100 cainr_20g_staterep128 williamsd_20g_staterep128 luciod_20g_staterep38 browningr_20g_coa5place6 smithd_20g_coa5place6 hoggd_20g_usrep11 pflugerr_20g_usrep11 codyl_20g_usrep11 brownd_20g_dallassheriff prdar_20g_dallassheriff ellzeyr_20g_staterep10 savinol_20g_staterep10 hefnerr_20g_staterep5 princed_20g_staterep5 corneliod_20g_351stdistrictjudge hechtr_20g_351stdistrictjudge wynner_20g_468thdistrictjudge albanod_20g_468thdistrictjudge logand_20g_brazossheriff dickyr_20g_brazossheriff garlandl_20g_brazossheriff floresd_20g_nuecescoattorney dorseyr_20g_nuecescoattorney salazard_20g_bexarsheriff rickhoffr_20g_bexarsheriff gohmertr_20g_usrep1 gilbertd_20g_usrep1 mcfarlandd_20g_133rddistrictjudg deanr_20g_133rddistrictjudge bellr_20g_staterep4 sprabaryl_20g_staterep4 clardyr_20g_staterep11 johnsond_20g_staterep11 mccaulr_20g_usrep10 siegeld_20g_usrep10 eriksenl_20g_usrep10 coxr_20g_56thdistrictjudge lindseyd_20g_56thdistrictjudge martinezd_20g_staterep39 paulr_20g_staterep129 alixd_20g_staterep129 turnerd_20g_staterep101 johnsond_20g_staterep115 brownleer_20g_staterep115 anchiad_20g_staterep103 fortenberryr_20g_staterep103 cortezd_20g_staterep117 raymondr_20g_staterep117 quinonesl_20g_staterep117 grangerr_20g_usrep12 welchd_20g_usrep12 holcombl_20g_usrep12 belld_20g_brazoriataxac bulanekr_20g_brazoriataxac lemanr_20g_staterep13 sandilld_20g_127thdistrictjudge copelandr_20g_127thdistrictjudge wiser_20g_coa14place7 craftd_20g_coa14place7 schaeferr_20g_staterep6 gobbled_20g_staterep6 taylorr_20g_usrep3 seikalyd_20g_usrep3 claytorl_20g_usrep3 crenshawr_20g_usrep2 ladjevardiand_20g_usrep2 scheirmanl_20g_usrep2 hernandezd_20g_travissheriff vargasr_20g_travissheriff deanr_20g_staterep7 burgessr_20g_352nddistrictjudge pooled_20g_352nddistrictjudge maldonadod_20g_507thdistrictjudg lemkuilr_20g_507thdistrictjudge kacalr_20g_staterep12 trujillod_20g_usrep13 jacksonr_20g_usrep13 westbrookl_20g_usrep13 martinezfischerd_20g_staterep116 litoffr_20g_staterep116 ramosd_20g_staterep102 koopr_20g_staterep102 pattersonr_20g_staterep106 skidonenkod_20g_staterep106 buttonr_20g_staterep112 chambersd_20g_staterep112 newsoml_20g_staterep112 metcalfr_20g_staterep16 sessionsr_20g_usrep17 kennedyd_20g_usrep17 brownl_20g_usrep17 garzad_20g_37thdistrictjudge appeltr_20g_37thdistrictjudge bellr_20g_staterep3 shuppd_20g_staterep3 medaryr_20g_347thdistrictjudge riosd_20g_347thdistrictjudge shoemaker_20g_434thdistrictjudge becerrad_20g_434thdistrictjudge turnerd_20g_fortbendtaxac presslerr_20g_fortbendtaxac wrightr_20g_usrep6 danield_20g_usrep6 blackl_20g_usrep6 trochessetr_20g_galvestonsheriff salinasd_20g_galvestonsheriff busbyr_20g_supct8 trianad_20g_supct8 oxfordl_20g_supct8 fletcherd_20g_usrep7 huntr_20g_usrep7 kellyl_20g_usrep7 brannond_20g_staterep2 slatonr_20g_staterep2 manord_20g_80thdistrictjudge hemphillr_20g_80thdistrictjudge escobard_20g_usrep16 armendarizjacksonr_20g_usrep16 cyrierr_20g_staterep17 edend_20g_staterep17 bowersd_20g_staterep113 douglasr_20g_staterep113 neaved_20g_staterep107 smithr_20g_staterep107 johnsond_20g_staterep139 trojacekl_20g_staterep139 davisd_20g_staterep111 valdesd_20g_386thdistrictjudge austinr_20g_386thdistrictjudge mezad_20g_staterep105 hernandezr_20g_staterep105 boltonl_20g_staterep105 tothr_20g_staterep15 perezmcgilld_20g_staterep15 cuellard_20g_usrep28 whittenr_20g_usrep28 congdonl_20g_usrep28 thompsonr_20g_staterep29 boldtd_20g_staterep29 evansr_20g_coa5place3 goldsteind_20g_coa5place3 weberr_20g_usrep14 belld_20g_usrep14 wysockir_20g_254thdistrictjudge brownd_20g_254thdistrictjudge garzad_20g_travisda53rd harryr_20g_travisda53rd rogersd_20g_334thdistrictjudge lemkuilr_20g_334thdistrictjudge goodenr_20g_usrep5 salterd_20g_usrep5 halel_20g_usrep5 palmerd_20g_215thdistrictjudge shuchartr_20g_215thdistrictjudge fallonr_20g_usrep4 fosterd_20g_usrep4 antonellil_20g_usrep4 jonesw_20g_usrep4 bouressar_20g_471stdistrictjudge paymad_20g_471stdistrictjudge vandeaverr_20g_staterep1 gatesr_20g_staterep28 markowitzd_20g_staterep28 gonzalezd_20g_usrep15 delacruzhernandezr_20g_usrep15 leonel_20g_usrep15 raneyr_20g_staterep14 duddingd_20g_staterep14 garciad_20g_usrep29 blancor_20g_usrep29 kurtzl_20g_usrep29 gonzalezd_20g_staterep104 rosed_20g_staterep110 faheyr_20g_348thdistrictjudge whitlockhicksd_20g_348thdistrict bacyd_20g_staterep138 hullr_20g_staterep138 rosenthald_20g_staterep135 rayr_20g_staterep135 bilyeul_20g_staterep135 allisonr_20g_staterep121 montoyad_20g_staterep121 shermand_20g_staterep109 allenr_20g_staterep109 whiter_20g_staterep19 vanduyner_20g_usrep24 valenzuelad_20g_usrep24 hamiltonl_20g_usrep24 baueri_20g_usrep24 kuzmichi_20g_usrep24 bernicejohnsond_20g_usrep30 pennier_20g_usrep30 williamsi_20g_usrep30 henryd_20g_staterep25 vasutr_20g_staterep25 jacksonleed_20g_usrep18 championr_20g_usrep18 spencerl_20g_usrep18 duncani_20g_usrep18 guillend_20g_staterep31 knowltonr_20g_staterep31 smithr_20g_380thdistrictjudge robed_20g_380thdistrictjudge jaramillor_20g_400thdistrictjudg carterd_20g_400thdistrictjudge greend_20g_usrep9 teaguer_20g_usrep9 sosal_20g_usrep9 wolfer_20g_213thdistrictjudge smithd_20g_213thdistrictjudge burgessr_20g_tarrantconstable7 leed_20g_tarrantconstable7 blandr_20g_supct6 chengd_20g_supct6 hechtr_20g_supctchief meachumd_20g_supctchief ashl_20g_supctchief boydr_20g_supct7 strangel_20g_supct7 williamsd_20g_supct7 siegelr_20g_tarrantconstable6 lyonsd_20g_tarrantconstable6 bradyr_20g_usrep8 hernandezd_20g_usrep8 duncanl_20g_usrep8 chodyr_20g_williamsonsheriff gleasond_20g_williamsonsheriff morrisonr_20g_staterep30 bonnenr_20g_staterep24 rogersd_20g_staterep24 illyesl_20g_staterep24 bennettd_20g_harristaxac danielr_20g_harristaxac piercel_20g_harristaxac arringtonr_20g_usrep19 watsond_20g_usrep19 burnesl_20g_usrep19 carterr_20g_usrep31 imamd_20g_usrep31 pattersonl_20g_usrep31 robinsonr_20g_405thdistrictjudge hudsond_20g_405thdistrictjudge bailesr_20g_staterep18 williamsr_20g_usrep25 oliverd_20g_usrep25 kelseyl_20g_usrep25 meyerr_20g_staterep108 cattanachd_20g_staterep108 rankinl_20g_staterep108 gervinhawkinsd_20g_staterep120 payner_20g_staterep120 huckabayl_20g_staterep120 davisr_20g_staterep134 johnsond_20g_staterep134 larsonr_20g_staterep122 barnettd_20g_staterep122 bucyd_20g_staterep136 guevarar_20g_staterep136 elliottl_20g_staterep136 evansr_20g_48thdistrictjudge meyersd_20g_48thdistrictjudge veaseyd_20g_usrep33 cordovavasquezr_20g_usrep33 reevesl_20g_usrep33 quintanillai_20g_usrep33 weltoni_20g_usrep33 cloudr_20g_usrep27 grayl_20g_usrep27 delafuented_20g_usrep27 hunterr_20g_staterep32 holguind_20g_staterep32 demerchantd_20g_staterep26 jettonr_20g_staterep26 holtd_20g_401stdistrictjudge flintr_20g_401stdistrictjudge waybournr_20g_tarrantsheriff keyesd_20g_tarrantsheriff reynoldsd_20g_staterep27 virippanr_20g_staterep27 hollandr_20g_staterep33 rosed_20g_staterep33 burgessr_20g_usrep26 iannuzzid_20g_usrep26 bolerl_20g_usrep26 allredd_20g_usrep32 collinsr_20g_usrep32 mowreypetersonl_20g_usrep32 sigmoni_20g_usrep32 wud_20g_staterep137 sharpl_20g_staterep137 bernald_20g_staterep123 hubertyr_20g_staterep127 antonioul_20g_staterep127 kingr_20g_26thdistrictjudge mcconnelld_20g_26thdistrictjudge murphyr_20g_staterep133 moored_20g_staterep133 harrenl_20g_staterep133 dominguezd_20g_staterep37 middletonr_20g_staterep23 antonellid_20g_staterep23 babinr_20g_usrep36 lewisd_20g_usrep36 abbeyl_20g_usrep36 ridleyg_20g_usrep36 kulkarnid_20g_usrep22 nehlsr_20g_usrep22 leblancl_20g_usrep22 hortickd_20g_bexarcocomm3 deberryr_20g_bexarcocomm3 fonsecar_20g_464thdistrictjudge ramirezd_20g_464thdistrictjudge cosbyr_20g_67thdistrictjudge hegemand_20g_67thdistrictjudge clarkr_20g_tarrantconstable1 gerlikovskid_20g_tarrantconstabl salvantr_20g_tarrantcrimctatlaw2 williamsd_20g_tarrantcrimctatlaw nessgarciad_20g_383rddistrictjud martinezgonzalezr_20g_383rddistr moored_20g_162nddistrictjudge lewisr_20g_162nddistrictjudge lopezsingleterryd_20g_coa13place silvar_20g_coa13place6 gonzalesr_20g_usrep23 ortizjonesd_20g_usrep23 villelal_20g_usrep23 deshoteld_20g_staterep22 randler_20g_staterep22 whitehillr_20g_coa5place8 garciad_20g_coa5place8 munozd_20g_staterep36 calannid_20g_staterep132 schofieldr_20g_staterep132 bentonw_20g_staterep132 harlessr_20g_staterep126 hurtadod_20g_staterep126 halld_20g_165thdistrictjudge bainr_20g_165thdistrictjudge wallachr_20g_coa2place6 watsond_20g_coa2place6 pachecod_20g_staterep118 salyerr_20g_staterep118 velasquezl_20g_staterep118 oliversonr_20g_staterep130 henryd_20g_staterep130 minjarezd_20g_staterep124 wilsonr_20g_staterep20 tiedtd_20g_staterep20 herrerod_20g_staterep34 hernandezr_20g_staterep34 royr_20g_usrep21 davisd_20g_usrep21 dibiancal_20g_usrep21 wakelyg_20g_usrep21 doggettd_20g_usrep35 garciasharonr_20g_usrep35 loewel_20g_usrep35 matai_20g_usrep35 tijerinar_20g_coa13place4 lopezd_20g_coa13place4 moyed_20g_14thdistrictjudge voycelewisr_20g_14thdistrictjudg paddier_20g_staterep9 hudspethd_20g_harriscoclerk stanartr_20g_harriscoclerk woodruffr_20g_tarrantconstable2 mcgintyd_20g_tarrantconstable2 harrisr_20g_staterep8 adamsl_20g_staterep8 clayfloresd_20g_bexarcocomm1 larar_20g_bexarcocomm1 velad_20g_usrep34 gonzalezr_20g_usrep34 cristol_20g_usrep34 royali_20g_usrep34 castrod_20g_usrep20 garzar_20g_usrep20 bluntl_20g_usrep20 longoriad_20g_staterep35 phelanr_20g_staterep21 lopezd_20g_staterep125 valdivial_20g_staterep125 allend_20g_staterep131 vasquezd_20g_bexarjp2 smithl_20g_bexarjp2 camposd_20g_staterep119 garzar_20g_staterep119 thomasl_20g_staterep119 padrong_20g_staterep119 duttond_20g_staterep142 rower_20g_staterep142 cardenasd_20g_staterep85 millerl_20g_staterep85 stephensonr_20g_staterep85 klickr_20g_staterep91 simsd_20g_staterep91 roser_20g_coa3chief byrned_20g_coa3chief coled_20g_staterep46 talaricod_20g_staterep52 valdezr_20g_staterep52 eagletond_20g_harrisconstable3 hinesr_20g_harrisconstable3 mcclurer_20g_339thdistrictjudge belld_20g_339thdistrictjudge menendezd_20g_statesen26 villarrealg_20g_statesen26 luciod_20g_statesen27 tijerinar_20g_statesen27 fitzpatrickr_20g_342nddistrictju bastond_20g_342nddistrictjudge garciad_20g_harrisconstable2 velar_20g_harrisconstable2 murrr_20g_staterep53 herrerad_20g_staterep53 goodwind_20g_staterep47 berryr_20g_staterep47 clarkl_20g_staterep47 yearyr_20g_cca4 clintond_20g_cca4 fagand_20g_fortbendsheriff nehlsr_20g_fortbendsheriff romerod_20g_staterep90 camachor_20g_staterep90 frullor_20g_staterep84 gibsond_20g_staterep84 hernandezd_20g_staterep143 thompsond_20g_staterep141 whitfieldd_20g_staterep92 casonr_20g_staterep92 mulligang_20g_staterep92 smitheer_20g_staterep86 meryd_20g_144thdistrictjudge skinnerr_20g_144thdistrictjudge fierrod_20g_staterep79 rodriguezd_20g_staterep51 reynoldsr_20g_staterep51 zwienerd_20g_staterep45 isaacr_20g_staterep45 moored_20g_harriscocomm3 ramseyr_20g_harriscocomm3 floresr_20g_statesen19 gutierrezd_20g_statesen19 valdivial_20g_statesen19 buckinghamr_20g_statesen24 tuckerd_20g_statesen24 kolkhorstr_20g_statesen18 antaland_20g_statesen18 guerrad_20g_coa1place5 adamsr_20g_coa1place5 kuempelr_20g_staterep44 bohmfalkd_20g_staterep44 mardockl_20g_staterep44 israeld_20g_staterep50 delaroser_20g_staterep50 moodyd_20g_staterep78 laner_20g_staterep78 williamsd_20g_travisctatlaw9 davidl_20g_travisctatlaw9 pricer_20g_staterep87 krauser_20g_staterep93 beand_20g_staterep93 walled_20g_staterep140 goldmanr_20g_staterep97 beckd_20g_staterep97 wingol_20g_staterep97 burrowsr_20g_staterep83 perryfranksd_20g_staterep83 perezd_20g_staterep144 salasr_20g_staterep144 swansonr_20g_staterep150 walshd_20g_staterep150 herreral_20g_staterep150 buckleyr_20g_staterep54 williamsd_20g_staterep54 richardsonr_20g_cca3 davisfrizelld_20g_cca3 canalesd_20g_staterep40 springerr_20g_staterep68 ledbetterd_20g_staterep68 thompsonr_20g_416thdistrictjudge creevyd_20g_416thdistrictjudge brionesd_20g_harriscivilctatlaw4 leuchtagr_20g_harriscivilctatlaw heapr_20g_harrisconstable5 harrisond_20g_harrisconstable5 perezreyesd_20g_camerondistclerk deatonr_20g_camerondistclerk santinir_20g_457thdistrictjudge meyerd_20g_457thdistrictjudge hinojosad_20g_statesen20 cutrightr_20g_statesen20 zaffirinid_20g_statesen21 pomeroyr_20g_statesen21 hermanr_20g_harrisconstable4 mcgowend_20g_harrisconstable4 smithlawsond_20g_fortbendcoattor rogersr_20g_fortbendcoattorney garzad_20g_cameronsheriff chambersr_20g_cameronsheriff hasetted_20g_28thdistrictjudge perkesr_20g_28thdistrictjudge hobbsr_20g_williamsoncoattorney springerleyd_20g_williamsoncoatt urestid_20g_bexartaxac penningtonr_20g_bexartaxac frankr_20g_staterep69 menefeed_20g_harriscoattorney nationr_20g_harriscoattorney priced_20g_dallascocomm3 russellr_20g_dallascocomm3 jewelll_20g_dallascocomm3 guerrad_20g_staterep41 guerrar_20g_staterep41 shiner_20g_staterep55 moralesd_20g_staterep145 fierror_20g_staterep145 howelll_20g_staterep145 craddickr_20g_staterep82 dragod_20g_staterep96 cookr_20g_staterep96 rangel_20g_staterep96 bacabennettr_20g_360thdistrictju munozd_20g_360thdistrictjudge kingd_20g_staterep80 tinderholtr_20g_staterep94 simmonsd_20g_staterep94 pallettl_20g_staterep94 elfantd_20g_travistaxac jacksonr_20g_travistaxac lockwoodl_20g_travistaxac colemand_20g_staterep147 lozanor_20g_staterep43 ashbyr_20g_staterep57 rogersd_20g_staterep57 danield_20g_dallascocomm1 hardenr_20g_dallascocomm1 robinsond_20g_coa14chief christopherr_20g_coa14chief leer_20g_95thdistrictjudge purdyd_20g_95thdistrictjudge perwinr_20g_505thdistrictjudge morgand_20g_505thdistrictjudge youngr_20g_sboe8 berryl_20g_sboe8 castanedad_20g_rrcomm1 wrightr_20g_rrcomm1 sterettl_20g_rrcomm1 grueneg_20g_rrcomm1 castrod_20g_399thdistrictjudge sheltonr_20g_399thdistrictjudge landrumr_20g_164thdistrictjudge thorntond_20g_164thdistrictjudge birdwellr_20g_statesen22 vickd_20g_statesen22 carterd_20g_harrisjp1pl1 dugatr_20g_harrisjp1pl1 ellisr_20g_sboe9 davisd_20g_sboe9 oggd_20g_harrisda huffmanr_20g_harrisda lloydr_20g_coa1place3 rivasmalloyd_20g_coa1place3 andersonr_20g_staterep56 turnerpearsond_20g_staterep56 raymondd_20g_staterep42 thierryd_20g_staterep146 campbelll_20g_staterep146 collierd_20g_staterep95 landgrafr_20g_staterep81 puryearr_20g_460thdistrictjudge alvarengad_20g_460thdistrictjudg{
	preserve
	keep precinct office candidate `var'
	keep if `var'!=.
	replace candidate = "`var'"
	rename `var' votes
	tempfile vfile`s'
	save `vfile`s''
	restore
	local s = `s'+1
}

local s = `s'-1
use `vfile1', clear
forval x=2(1)`s'{
	append using `vfile`x''
}


order precinct office candidate
replace candidate = substr(candidate,1,strpos(candidate,"_")) if strpos(candidate,"_")>0
replace candidate = subinstr(candidate,"_","",.)
gen temp = substr(candidate,strlen(candidate),1)
order temp, after(candidate)
gen party_detailed=""
replace party_detailed = "DEMOCRAT" if temp=="d"&party_detailed==""
replace party_detailed = "REPUBLICAN" if temp=="r"&party_detailed==""
replace party_detailed = "LIBERTARIAN" if temp=="l"&party_detailed==""
replace party_detailed = "GREEN" if temp=="g"&party_detailed==""
replace party_detailed = "INDEPENDENT" if temp=="i"&party_detailed==""

gen party_simplified = ""
replace party_simplified = "DEMOCRAT" if party_detailed=="DEMOCRAT"
replace party_simplified = "REPUBLICAN" if party_detailed=="REPUBLICAN"
replace party_simplified = "LIBERTARIAN" if party_detailed=="LIBERTARIAN"
replace party_simplified = "NONPARTISAN" if party_detailed=="NONPARTISAN"
replace party_simplified = "OTHER" if party_detailed=="REFORM"
replace party_simplified = "OTHER" if party_detailed=="CONSTITUTION"
replace party_simplified = "OTHER" if party_detailed=="GREEN"
replace party_simplified = "OTHER" if party_detailed=="INDEPENDENT"
replace party_simplified = "OTHER" if party_detailed=="ECOLOGY"
replace party_simplified = "OTHER" if party_detailed=="SOCIALIST"

replace candidate = substr(candidate,1,strlen(candidate)-1)
replace candidate = strupper(candidate)
drop temp*


replace party_detailed = "" if office=="VOTER DATA"
replace party_simplified = "" if office=="VOTER DATA"
replace office = candidate if office=="VOTER DATA"
replace candidate = "" if candidate==office
replace office = "REGISTERED VOTERS" if office=="VOTERRE"
replace office = "SPANISH SURNAME REGISTRATION" if office=="SPANISHVOTERRE"
replace office = "SPANISH SURNAME TURNOUT" if office=="SPANISHTURNOU"
replace office = "TURNOUT" if office=="TURNOU"


tab office


gen district = ""
replace district = substr(office,strpos(office,"US REP")+7,.) if strpos(office,"US REP")>0
replace office = "US HOUSE" if strpos(office,"US REP")>0
replace district = substr(office,strpos(office,"STATE REP")+10,.) if strpos(office,"STATE REP")>0
replace office = "STATE HOUSE" if strpos(office,"STATE REP")>0
replace district = substr(office,strpos(office,"STATE SEN")+10,.) if strpos(office,"STATE SEN")>0
replace office = "STATE SENATE" if strpos(office,"STATE SEN")>0
replace district = substr(office,1,strpos(office,"DISTRICT JUDGE")-1) if strpos(office,"DISTRICT JUDGE")>0
replace district = subinstr(district,"TH","",.)
replace district = subinstr(district,"ND","",.)
replace district = subinstr(district,"RD","",.)
replace district = subinstr(district,"ST","",.)
replace office = "DISTRICT JUDGE" if strpos(office,"DISTRICT JUDGE")>0
replace district = substr(office,strpos(office,"SBOE")+5,.) if strpos(office,"SBOE")>0
replace office = "STATE BOARD OF EDUCATION" if strpos(office,"SBOE")>0
replace district = "006" if office=="SUP CT 6"
replace district = "007" if office=="SUP CT 7"
replace district = "008" if office=="SUP CT 8"
replace district = substr(office,strpos(office,"CONSTABLE")+10,.) if strpos(office,"CONSTABLE")>0
replace office = substr(office,1,strpos(office,"CONSTABLE")+9) if strpos(office,"CONSTABLE")>0
replace district = substr(office,strpos(office,"CO COMM")+8,.) if strpos(office,"CO COMM")>0
replace office = substr(office,1,strpos(office,"CO COMM")+7) if strpos(office,"CO COMM")>0
replace district = "001" if office=="RR COMM 1"
replace office = "RAILROAD COMMISSIONER" if office=="RR COMM 1"
replace office = subinstr(office,"CO COMM","COUNTY COMMISSIONER",.)
replace office = "SUPREME COURT CHIEF JUSTICE" if office=="SUP CT CHIEF"
replace office = "SUPREME COURT JUSTICE" if strpos(office,"SUP CT")>0
replace district = substr(office,strpos(office,"COA")+3,.) if strpos(office,"COA")>0
replace office = "COURT OF APPEALS" if strpos(office,"COA")>0
order district, after(office)
sort office district
replace district = substr(office,strpos(office,"CCA")+3,.) if strpos(office,"CCA")>0
replace office = "COURT OF CRIMINAL APPEALS" if strpos(office,"CCA")>0

replace office = strtrim(office)
replace district = "002" if office=="BEXAR JP 2"
replace office = "BEXAR JUSTICE OF THE PEACE" if office=="BEXAR JP 2"
replace office = subinstr(office,"CO ","COUNTY ",.)
replace district = "DISTRICT 1 PLACE 1" if office=="HARRIS JP 1 PL 1"
replace district = "DISTRICT 5 PLACE 1" if office=="HARRIS JP 5 PL 1"
replace office = "HARRIS JUSTICE OF THE PEACE" if office=="HARRIS JP 1 PL 1"|office=="HARRIS JP 5 PL 1"
replace office = "HARRIS COUNTY DISTRICT ATTORNEY" if office=="HARRIS DA"
replace district = "053" if office=="TRAVIS DA 53RD"
replace office = "TRAVIS COUNTY DISTRICT ATTORNEY" if office=="TRAVIS DA 53RD"

replace district = strtrim(district)
tab district if office=="COURT OF APPEALS"
replace district = "001, PLACE 3" if district=="1 PLACE 3"&office=="COURT OF APPEALS"
replace district = "001, PLACE 5" if district=="1 PLACE 5"&office=="COURT OF APPEALS"
replace district = "013, PLACE 4" if district=="13 PLACE 4"&office=="COURT OF APPEALS"
replace district = "013, PLACE 6" if district=="13 PLACE 6"&office=="COURT OF APPEALS"
replace district = "014, PLACE 7" if district=="14 PLACE 7"&office=="COURT OF APPEALS"
replace district = "014, CHIEF" if district=="14 CHIEF"&office=="COURT OF APPEALS"
replace district = "002, PLACE 6" if district=="2 PLACE 6"&office=="COURT OF APPEALS"
replace district = "003, CHIEF" if district=="3 CHIEF"&office=="COURT OF APPEALS"
replace district = "004, CHIEF" if district=="4 CHIEF"&office=="COURT OF APPEALS"
replace district = "005, PLACE 3" if district=="5 PLACE 3"&office=="COURT OF APPEALS"
replace district = "005, PLACE 6" if district=="5 PLACE 6"&office=="COURT OF APPEALS"
replace district = "005, PLACE 8" if district=="5 PLACE 8"&office=="COURT OF APPEALS"
replace district = "008, CHIEF" if district=="8 CHIEF"&office=="COURT OF APPEALS"

replace office = "US SENATE" if office=="US SEN"
replace office = "US PRESIDENT" if office=="PRESIDENT"
replace district = "STATEWIDE" if office=="US SENATE"|office=="PRESIDENT"

replace district = "STATEWIDE, "+district if office=="SUPREME COURT JUSTICE"|office=="COURT OF CRIMINAL APPEALS"|office=="RAILROAD COMMISSIONER"
replace district = "STATEWIDE, PLACE 1" if district=="STATEWIDE, 001"
replace district = "STATEWIDE, PLACE 3" if district=="STATEWIDE, 003"
replace district = "STATEWIDE, PLACE 4" if district=="STATEWIDE, 004"
replace district = "STATEWIDE, PLACE 6" if district=="STATEWIDE, 006"
replace district = "STATEWIDE, PLACE 7" if district=="STATEWIDE, 007"
replace district = "STATEWIDE, PLACE 8" if district=="STATEWIDE, 008"
replace district = "STATEWIDE, PLACE 9" if district=="STATEWIDE, 009"

replace district = "00"+district if strlen(district)==1
replace district = "0"+district if strlen(district)==2

order district, after(office)
sort office district

*dataverse
*court check: https://www.courtstatistics.org/state_court_structure_charts/texas
gen dataverse = "LOCAL"
replace dataverse = "STATE" if office=="STATE SENATE"|office=="STATE HOUSE"|office=="SUPREME COURT CHIEF JUSTICE"|office=="SUPREME COURT JUSTICE"|office=="RAILROAD COMMISSIONER"|office=="DISTRICT JUDGE"|office=="COURT OF APPEALS"|office=="COURT OF CRIMINAL APPEALS"|office=="STATE BOARD OF EDUCATION"
replace dataverse = "HOUSE" if office=="US HOUSE"
replace dataverse = "SENATE" if office=="US SENATE"
replace dataverse = "PRESIDENT" if office=="US PRESIDENT"
replace dataverse = "" if office=="REGISTERED VOTERS"|office=="SPANISH SURNAME REGISTRATION"|office=="SPANISH SURNAME TURNOUT"|office=="TURNOUT"
tab office dataverse


gen writein = "FALSE"
replace writein = "TRUE" if candidate=="WRITEIN"


tab candidate

replace candidate = "ARMENDARIZ-JACKSON" if candidate=="ARMENDARIZJACKSON"
replace candidate = "BACA BENNETT" if candidate=="BACABENNETT"
replace candidate = "BELL-METEREAU" if candidate=="BELLMETEREAU"
replace candidate = "BERNICE JOHNSON" if candidate=="BERNICEJOHNSON"
replace candidate = "BUENING HEPPARD" if candidate=="BUENINGHEPPARD"
replace candidate = "BURNETT-WEBSTER" if candidate=="BURNETTWEBSTER"
replace candidate = "CLAY-FLORES" if candidate=="CLAYFLORES"
replace candidate = "CORDOVA VASQUEZ" if candidate=="CORDOVAVASQUEZ"
replace candidate = "DAVIS FRIZELL" if candidate=="DAVISFRIZELL"
replace candidate = "DE LA CRUZ HERNANDEZ" if candidate=="DELACRUZHERNANDEZ"
replace candidate = "DE LA FUENTE" if candidate=="DELAFUENTE"
replace candidate = "DEL ROSAL" if candidate=="DELROSAL"
replace candidate = "DEL TORO" if candidate=="DELTORO"
replace candidate = "GARCIA SHARON" if candidate=="GARCIASHARON"
replace candidate = "GERVIN-HAWKINS" if candidate=="GERVINHAWKINS"
replace candidate = "JACKSON LEE" if candidate=="JACKSONLEE"
replace candidate = "LOPEZ-SINGLETERRY" if candidate=="LOPEZSINGLETERRY"
replace candidate = "MARTINEZ FISCHER" if candidate=="MARTINEZFISCHER"
replace candidate = "MARTINEZ GONZALEZ" if candidate=="MARTINEZGONZALEZ"
replace candidate = "MOWREY PETERSON" if candidate=="MOWREYPETERSON"
replace candidate = "NESS-GARCIA" if candidate=="NESSGARCIA"
replace candidate = "ORDAZ PEREZ" if candidate=="ORDAZPEREZ"
replace candidate = "ORTIZ JONES" if candidate=="ORTIZJONES"
replace candidate = "PEREZ MCGILL" if candidate=="PEREZMCGILL"
replace candidate = "PEREZ-REYES" if candidate=="PEREZREYES"
replace candidate = "PERRY-FRANKS" if candidate=="PERRYFRANKS"
replace candidate = "RIVAS-MALLOY" if candidate=="RIVASMALLOY"
replace candidate = "SMITH-LAWSON" if candidate=="SMITHLAWSON"
replace candidate = "TURNER-MCCLELLAND" if candidate=="TURNERMCCLELLAND"
replace candidate = "TURNER-PEARSON" if candidate=="TURNERPEARSON"
replace candidate = "VOYCE LEWIS" if candidate=="VOYCELEWIS"
replace candidate = "WHITLOCK HICKS" if candidate=="WHITLOCKHICKS"

replace candidate = "JOSEPH R BIDEN" if strpos(candidate,"BIDEN")>0&office=="US PRESIDENT"
replace candidate = "DONALD J TRUMP" if strpos(candidate,"TRUMP")>0&office=="US PRESIDENT"
replace candidate = "JO JORGENSEN" if strpos(candidate,"JORGENSEN")>0&office=="US PRESIDENT"
replace candidate = "HOWIE HAWKINS" if strpos(candidate,"HAWKINS")>0&office=="US PRESIDENT"

tab candidate

*county fips is just state fips + first three of VTD
gen county_fips = "48"+substr(precinct,1,3)

*some are city codes, rather than county. And some are the wrong length...
replace county_fips = "48001" if county_fips=="48100"
replace county_fips = "48041" if county_fips=="48410"
replace county_fips = "48053" if county_fips=="48530"
replace county_fips = "48061" if county_fips=="48610"
replace county_fips = "48025" if county_fips=="48250"
replace county_fips = "48035" if county_fips=="48350"
replace county_fips = "48085" if county_fips=="48850"
replace county_fips = "48065" if county_fips=="48650"
replace county_fips = "48029" if county_fips=="48294"
replace county_fips = "48029" if county_fips=="48292"



*final vars
gen state="Texas"
merge m:1 state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/merge_on_statecodes.dta", nogen keep(1 3)
destring(county_fips), replace
merge m:1 county_fips state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/county-fips-codes.dta", nogen keep(1 3)
tostring(county_fips), replace
gen jurisdiction_name = county_name
gen jurisdiction_fips = county_fips

*fix some county names and fips, get rid of county names in office field.
replace office = subinstr(office,"WILLIAMSON ","",.)
replace office = subinstr(office,"BEXAR ","",.)
replace county_name = "BRAZOS" if strpos(office,"BRAZOS")>0
replace office = subinstr(office,"BRAZOS ","",.)
replace office = subinstr(office,"BRAZORIA ","",.)
replace office = subinstr(office,"TRAVIS ","",.)
replace office = subinstr(office,"TARRANT ","",.)
replace office = subinstr(office,"NUECES ","",.)
replace office = subinstr(office,"MONTGOMERY ","",.)
replace office = subinstr(office,"JEFFERSON ","",.)
replace office = subinstr(office,"HIDALGO ","",.)
replace office = subinstr(office,"HARRIS ","",.)
replace office = subinstr(office,"GALVESTON ","",.)
replace office = subinstr(office,"FORT BEND ","",.)
replace office = subinstr(office,"DALLAS ","",.)
replace office = subinstr(office,"COLLIN ","",.)
replace county_name = "CAMERON" if strpos(office,"CAMERON")>0
replace office = subinstr(office,"CAMERON ","",.)

*standardize more local offices
replace office = "TAX ASSESSOR COLLECTOR" if office=="TAX AC"
replace office = "DISTRICT CLERK" if office=="DIST CLERK"
replace district = "105" if office=="DA 105TH"
replace office = "DISTRICT ATTORNEY" if office=="DA 105TH"

replace district = "012" if office=="CRIM CT AT LAW 12"
replace district = "016" if office=="CRIM CT AT LAW 16"
replace district = "002" if office=="CRIM CT AT LAW 2"
replace district = "001" if office=="CT AT LAW 1"
replace district = "005" if office=="CT AT LAW 5"
replace district = "009" if office=="CT AT LAW 9"
replace district = "004" if office=="CIVIL CT AT LAW 4"

replace office = "CIVIL CT AT LAW" if office=="CIVIL CT AT LAW 4"
replace office = "CRIM CT AT LAW" if strpos(office,"CRIM CT AT LAW")
replace office = "CT AT LAW" if office=="CT AT LAW 1"|office=="CT AT LAW 5"|office=="CT AT LAW 9"

gen stage = "GEN"
replace state = "TEXAS"

gen date = "2020-11-03"
gen readme_check="FALSE"
gen year = 2020
gen mode="TOTAL"
gen magnitude=1

gen special = "FALSE"

compress
order precinct office district candidate party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips dataverse year stage state* special writein date read
sort office district county_name precinct

export delimited  "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/TX/2020-tx-precinct-general.csv", replace


/*Issues


readme for texas - the precinct variable is really VTDs





