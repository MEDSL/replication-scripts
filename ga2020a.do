// GA 2020 Election Data 
clear
import delimited using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/GA/raw/GA2020_mostrecent.csv", clear

rename race office 
replace office = upper(office)


rename candidates candidate 

gen party_detailed = ""
replace party_detailed = "DEMOCRAT" if strpos(candidate, "(Dem)")>0
replace party_detailed = "REPUBLICAN" if strpos(candidate, "(Rep)")>0
replace party_detailed = "LIBERTARIAN" if strpos(candidate, "(Lib)")>0
replace party_detailed = "NONPARTISAN" if strpos(candidate, "(Ind)")>0
replace party_detailed = "GREEN" if strpos(candidate, "(Grn)")>0


//office
replace office = strtrim(office)

//candidate 
replace candidate = subinstr(candidate, ".", "", .) 
replace candidate = subinstr(candidate, "(Rep)", "", .)
replace candidate = subinstr(candidate, "(Lib)", "", .)
replace candidate = subinstr(candidate, "(Dem)", "", .)
replace candidate = subinstr(candidate, "(I)", "", .)
replace candidate = subinstr(candidate, "(Ind)", "", .)
replace candidate = subinstr(candidate, "(Grn)", "", .)
replace candidate = subinstr(candidate, ",", "", .) 
replace candidate = subinstr(candidate, "  ", "", .) 
replace candidate = subinstr(candidate, "''", `"""', .)
replace candidate = subinstr(candidate, "'", `"""', .)
replace candidate = subinstr(candidate, "(", `"""', .)
replace candidate = subinstr(candidate, ")", `"""', .)
replace candidate = upper(candidate)
replace candidate = strtrim(candidate)
replace candidate = "MATT LIEBERMAN" if strpos(candidate, "MATT LIEBERMAN")>0
//parties for non-specified candidates
//republican
replace party_detailed = "REPUBLICAN" if strpos(candidate, "A WAYNE JOHNSON")>0 | strpos(candidate, "DAVIS JACKSON")>0 | strpos(candidate, "DAVID A PERDUE")>0 | strpos(candidate, "DERRICK E GRAYSON")>0 | strpos(candidate, "DOUG COLLINS")>0 | strpos(candidate, "KANDISS TAYLOR")>0 | strpos(candidate, "KELLY LOEFFLER")>0 | candidate == "A WAYNE JOHNSON" | candidate == "AARON W NOWAK"

//democrat
replace party_detailed = "DEMOCRAT" if strpos(candidate, "DEBORAH JACKSON")>0 | strpos(candidate, "ED TARVER")>0 | strpos(candidate, "JAMESIA JAMES")>0 | strpos(candidate, "JON OSSOFF")>0 | strpos(candidate, "JOY FELICIA SLADE")>0 | strpos(candidate, "MATT LIEBERMAN")>0 | strpos(candidate, "RAPHAEL WARNOCK")>0 | strpos(candidate, "TAMARA JOHNSON-SHEALEY")>0 | strpos(candidate, "JO ANNA POTTS")>0 | candidate == "LINDA PRITCHETT" | candidate == "SONYA HALPERN" | candidate == "ZAN FORT" | candidate == "RICHARD DIEN WINFIELD"

//independent
replace party_detailed = "INDEPENDENT" if strpos(candidate, "BARTELL")>0 | strpos(candidate, "MICHAEL TODD GREENE")>0 | strpos(candidate, "VALENCIA STOVALL")>0 |strpos(candidate, "ALLEN BUCKLEY")

//libertarian
replace party_detailed = "LIBERTARIAN" if strpos(candidate, "BUCKLEY")>0 | strpos(candidate, "SLOWINSKI")>0 | strpos(candidate, "SHANE HAZEL")>0
replace party_detailed = "GREEN" if strpos(candidate, "JOHN FORTUIN")>0 

//nonpartisan 
replace party_detailed = "NONPARTISAN" if strpos(office, "SOIL AND WATER")>0 | strpos(office, "MAYOR")>0 | strpos(office, "CITY COUNCIL")>0 | strpos(office, "BOARD OF EDUCATION")>0 | strpos(office, "FIRE ADVISORY BOARD")>0 | strpos(office, "COUNCIL")>0 | strpos(office, "PROBATE JUDGE")>0 | strpos(office, "COUNTY COMMISSION")>0 | strpos(candidate, "JAMES CHAFIN")>0 | strpos(office, "CHIEF MAGISTRATE")>0
//PARTY DETAILED
gen party_simplified = party_detailed
replace party_simplified = "OTHER" if party_detailed == "INDEPENDENT"|party_detailed=="GREEN"
//mode
rename type mode 
replace mode = upper(mode)
replace mode = "PROVISIONAL" if mode == "PROV"

//county_name 
rename county county_name
replace county_name = upper(county_name)
replace county_name = "BEN HILL" if county_name == "BEN_HILL"
replace county_name = "JEFF DAVIS" if county_name == "JEFF_DAVIS"

//state name 
gen state = "Georgia"

//county_fips 
merge m:1 county_name state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/help-files/county-fips-codes.dta", keep(1 3)

replace state = "GEORGIA"

//jurisdiction fips 
gen jurisdiction_fips = county_fips 

//district 
gen district = ""
replace district = "001" if strpos(office, "DISTRICT 1")>0
replace district = "002" if strpos(office, "DISTRICT 2")>0
replace district = "003" if strpos(office, "DISTRICT 3")>0
replace district = "004" if strpos(office, "DISTRICT 4")>0
replace district = "005" if strpos(office, "DISTRICT 5")>0
replace district = "006" if strpos(office, "DISTRICT 6")>0
replace district = "007" if strpos(office, "DISTRICT 7")>0
replace district = "008" if strpos(office, "DISTRICT 8")>0
replace district = "009" if strpos(office, "DISTRICT 9")>0

replace district = "100" if strpos(office, "DIST 100")>0
replace district = "101" if strpos(office, "DIST 101")>0
replace district = "102" if strpos(office, "DIST 102")>0
replace district = "103" if strpos(office, "DIST 103")>0
replace district = "104" if strpos(office, "DIST 104")>0
replace district = "105" if strpos(office, "DIST 105")>0
replace district = "106" if strpos(office, "DIST 106")>0
replace district = "107" if strpos(office, "DIST 107")>0
replace district = "108" if strpos(office, "DIST 108")>0
replace district = "114" if strpos(office, "DIST 114")>0
replace district = "081" if strpos(office, "DIST 81")>0
replace district = "093" if strpos(office, "DIST 93")>0
replace district = "094" if strpos(office, "DIST 94")>0
replace district = "095" if strpos(office, "DIST 95")>0
replace district = "096" if strpos(office, "DIST 96")>0
replace district = "097" if strpos(office, "DIST 97")>0
replace district = "098" if strpos(office, "DIST 98")>0
replace district = "099" if strpos(office, "DIST 99")>0
replace district = "040" if strpos(office, "DIST 40")>0
replace district = "041" if strpos(office, "DIST 41")>0
replace district = "045" if strpos(office, "DIST 45")>0
replace district = "048" if strpos(office, "DIST 48")>0
replace district = "055" if strpos(office, "DIST 55")>0
replace district = "001" if strpos(office, "DIST 1")>0
replace district = "002" if strpos(office, "DIST 2")>0
replace district = "003" if strpos(office, "DIST 3")>0
replace district = "004" if strpos(office, "DIST 4")>0
replace district = "005" if strpos(office, "DIST 5")>0
replace district = "007" if strpos(office, "DIST 7")>0
replace district = "009" if strpos(office, "DIST 9")>0
replace district = "010" if strpos(office, "DIST 10")>0
replace district = "010" if strpos(office, "DISTRICT 10")>0
replace district = "011" if strpos(office, "DISTRICT 11")>0
replace district = "012" if strpos(office, "DISTRICT 12")>0
replace district = "013" if strpos(office, "DISTRICT 13")>0
replace district = "014" if strpos(office, "DISTRICT 14")>0
replace district = "015" if strpos(office, "DISTRICT 15")>0
replace district = "016" if strpos(office, "DISTRICT 16")>0
replace district = "017" if strpos(office, "DISTRICT 17")>0
replace district = "018" if strpos(office, "DISTRICT 18")>0
replace district = "019" if strpos(office, "DISTRICT 19")>0
replace district = "020" if strpos(office, "DISTRICT 20")>0
replace district = "021" if strpos(office, "DISTRICT 21")>0
replace district = "022" if strpos(office, "DISTRICT 22")>0
replace district = "023" if strpos(office, "DISTRICT 23")>0
replace district = "024" if strpos(office, "DISTRICT 24")>0
replace district = "025" if strpos(office, "DISTRICT 25")>0
replace district = "026" if strpos(office, "DISTRICT 26")>0
replace district = "027" if strpos(office, "DISTRICT 27")>0
replace district = "028" if strpos(office, "DISTRICT 28")>0
replace district = "029" if strpos(office, "DISTRICT 29")>0
replace district = "030" if strpos(office, "DISTRICT 30")>0
replace district = "031" if strpos(office, "DISTRICT 31")>0
replace district = "032" if strpos(office, "DISTRICT 32")>0
replace district = "033" if strpos(office, "DISTRICT 33")>0
replace district = "034" if strpos(office, "DISTRICT 34")>0
replace district = "035" if strpos(office, "DISTRICT 35")>0
replace district = "036" if strpos(office, "DISTRICT 36")>0
replace district = "037" if strpos(office, "DISTRICT 37")>0
replace district = "038" if strpos(office, "DISTRICT 38")>0
replace district = "039" if strpos(office, "DISTRICT 39")>0
replace district = "040" if strpos(office, "DISTRICT 40")>0
replace district = "041" if strpos(office, "DISTRICT 41")>0
replace district = "042" if strpos(office, "DISTRICT 42")>0
replace district = "043" if strpos(office, "DISTRICT 43")>0
replace district = "044" if strpos(office, "DISTRICT 44")>0
replace district = "045" if strpos(office, "DISTRICT 45")>0
replace district = "046" if strpos(office, "DISTRICT 46")>0
replace district = "047" if strpos(office, "DISTRICT 47")>0
replace district = "048" if strpos(office, "DISTRICT 48")>0
replace district = "049" if strpos(office, "DISTRICT 49")>0
replace district = "050" if strpos(office, "DISTRICT 50")>0
replace district = "051" if strpos(office, "DISTRICT 51")>0
replace district = "052" if strpos(office, "DISTRICT 52")>0
replace district = "053" if strpos(office, "DISTRICT 53")>0
replace district = "054" if strpos(office, "DISTRICT 54")>0
replace district = "055" if strpos(office, "DISTRICT 55")>0
replace district = "056" if strpos(office, "DISTRICT 56")>0
replace district = "057" if strpos(office, "DISTRICT 57")>0
replace district = "058" if strpos(office, "DISTRICT 58")>0
replace district = "059" if strpos(office, "DISTRICT 59")>0
replace district = "060" if strpos(office, "DISTRICT 60")>0
replace district = "061" if strpos(office, "DISTRICT 61")>0
replace district = "062" if strpos(office, "DISTRICT 62")>0
replace district = "063" if strpos(office, "DISTRICT 63")>0
replace district = "064" if strpos(office, "DISTRICT 64")>0
replace district = "065" if strpos(office, "DISTRICT 65")>0
replace district = "066" if strpos(office, "DISTRICT 66")>0
replace district = "067" if strpos(office, "DISTRICT 67")>0
replace district = "068" if strpos(office, "DISTRICT 68")>0
replace district = "069" if strpos(office, "DISTRICT 69")>0
replace district = "070" if strpos(office, "DISTRICT 70")>0
replace district = "071" if strpos(office, "DISTRICT 71")>0
replace district = "072" if strpos(office, "DISTRICT 72")>0
replace district = "073" if strpos(office, "DISTRICT 73")>0
replace district = "074" if strpos(office, "DISTRICT 74")>0
replace district = "075" if strpos(office, "DISTRICT 75")>0
replace district = "076" if strpos(office, "DISTRICT 76")>0
replace district = "077" if strpos(office, "DISTRICT 77")>0
replace district = "078" if strpos(office, "DISTRICT 78")>0
replace district = "079" if strpos(office, "DISTRICT 79")>0
replace district = "080" if strpos(office, "DISTRICT 80")>0
replace district = "081" if strpos(office, "DISTRICT 81")>0
replace district = "082" if strpos(office, "DISTRICT 82")>0
replace district = "083" if strpos(office, "DISTRICT 83")>0
replace district = "084" if strpos(office, "DISTRICT 84")>0
replace district = "085" if strpos(office, "DISTRICT 85")>0
replace district = "086" if strpos(office, "DISTRICT 86")>0
replace district = "087" if strpos(office, "DISTRICT 87")>0
replace district = "088" if strpos(office, "DISTRICT 88")>0
replace district = "089" if strpos(office, "DISTRICT 89")>0
replace district = "090" if strpos(office, "DISTRICT 90")>0
replace district = "091" if strpos(office, "DISTRICT 91")>0
replace district = "092" if strpos(office, "DISTRICT 92")>0
replace district = "093" if strpos(office, "DISTRICT 93")>0
replace district = "094" if strpos(office, "DISTRICT 94")>0
replace district = "095" if strpos(office, "DISTRICT 95")>0
replace district = "103" if strpos(office, "DISTRICT 103")>0
replace district = "109" if strpos(office, "DISTRICT 109")>0
replace district = "110" if strpos(office, "DISTRICT 110")>0
replace district = "111" if strpos(office, "DISTRICT 111")>0
replace district = "112" if strpos(office, "DISTRICT 112")>0
replace district = "113" if strpos(office, "DISTRICT 113")>0
replace district = "114" if strpos(office, "DISTRICT 114")>0
replace district = "115" if strpos(office, "DISTRICT 115")>0
replace district = "116" if strpos(office, "DISTRICT 116")>0
replace district = "117" if strpos(office, "DISTRICT 117")>0
replace district = "118" if strpos(office, "DISTRICT 118")>0
replace district = "119" if strpos(office, "DISTRICT 119")>0
replace district = "120" if strpos(office, "DISTRICT 120")>0
replace district = "121" if strpos(office, "DISTRICT 121")>0
replace district = "122" if strpos(office, "DISTRICT 122")>0
replace district = "123" if strpos(office, "DISTRICT 123")>0
replace district = "124" if strpos(office, "DISTRICT 124")>0
replace district = "125" if strpos(office, "DISTRICT 125")>0
replace district = "126" if strpos(office, "DISTRICT 126")>0
replace district = "127" if strpos(office, "DISTRICT 127")>0
replace district = "128" if strpos(office, "DISTRICT 128")>0
replace district = "129" if strpos(office, "DISTRICT 129")>0
replace district = "130" if strpos(office, "DISTRICT 130")>0
replace district = "131" if strpos(office, "DISTRICT 131")>0
replace district = "132" if strpos(office, "DISTRICT 132")>0
replace district = "133" if strpos(office, "DISTRICT 133")>0
replace district = "134" if strpos(office, "DISTRICT 134")>0
replace district = "135" if strpos(office, "DISTRICT 135")>0
replace district = "136" if strpos(office, "DISTRICT 136")>0
replace district = "137" if strpos(office, "DISTRICT 137")>0
replace district = "138" if strpos(office, "DISTRICT 138")>0
replace district = "139" if strpos(office, "DISTRICT 139")>0
replace district = "140" if strpos(office, "DISTRICT 140")>0
replace district = "141" if strpos(office, "DISTRICT 141")>0
replace district = "142" if strpos(office, "DISTRICT 142")>0
replace district = "143" if strpos(office, "DISTRICT 143")>0
replace district = "144" if strpos(office, "DISTRICT 144")>0
replace district = "145" if strpos(office, "DISTRICT 145")>0
replace district = "146" if strpos(office, "DISTRICT 146")>0
replace district = "147" if strpos(office, "DISTRICT 147")>0
replace district = "148" if strpos(office, "DISTRICT 148")>0
replace district = "149" if strpos(office, "DISTRICT 149")>0
replace district = "150" if strpos(office, "DISTRICT 150")>0
replace district = "151" if strpos(office, "DISTRICT 151")>0
replace district = "152" if strpos(office, "DISTRICT 152")>0
replace district = "153" if strpos(office, "DISTRICT 153")>0
replace district = "154" if strpos(office, "DISTRICT 154")>0
replace district = "155" if strpos(office, "DISTRICT 155")>0
replace district = "156" if strpos(office, "DISTRICT 156")>0
replace district = "157" if strpos(office, "DISTRICT 157")>0
replace district = "158" if strpos(office, "DISTRICT 158")>0
replace district = "159" if strpos(office, "DISTRICT 159")>0
replace district = "160" if strpos(office, "DISTRICT 160")>0
replace district = "161" if strpos(office, "DISTRICT 161")>0
replace district = "162" if strpos(office, "DISTRICT 162")>0
replace district = "163" if strpos(office, "DISTRICT 163")>0
replace district = "164" if strpos(office, "DISTRICT 164")>0
replace district = "165" if strpos(office, "DISTRICT 165")>0
replace district = "166" if strpos(office, "DISTRICT 166")>0
replace district = "167" if strpos(office, "DISTRICT 167")>0
replace district = "168" if strpos(office, "DISTRICT 168")>0
replace district = "169" if strpos(office, "DISTRICT 169")>0
replace district = "170" if strpos(office, "DISTRICT 170")>0
replace district = "171" if strpos(office, "DISTRICT 171")>0
replace district = "172" if strpos(office, "DISTRICT 172")>0
replace district = "173" if strpos(office, "DISTRICT 173")>0
replace district = "174" if strpos(office, "DISTRICT 174")>0
replace district = "175" if strpos(office, "DISTRICT 175")>0
replace district = "176" if strpos(office, "DISTRICT 176")>0
replace district = "177" if strpos(office, "DISTRICT 177")>0
replace district = "178" if strpos(office, "DISTRICT 178")>0
replace district = "179" if strpos(office, "DISTRICT 179")>0
replace district = "180" if strpos(office, "DISTRICT 180")>0
replace district = "STATEWIDE" if strpos(office, "STATEWIDE")>0
replace district = "1, SEAT A" if strpos(office, "COUNTY COMMISSION DISTRICT 1, SEAT A")>0
replace district = "2, SEAT A" if strpos(office, "COUNTY COMMISSION DISTRICT 2, SEAT A")>0
replace district = "2, SEAT A" if strpos(office, "COUNTY COMMISSION DISTRICT 2 SEAT A")>0
replace district = "2, SEAT C" if strpos(office, "COUNTY COMMISSION DISTRICT 2, SEAT C")>0
replace district = "2, SEAT B" if strpos(office, "COUNTY COMMISSION DISTRICT 2 SEAT B")>0
replace district = "1, POST 2" if strpos(office, "COUNTY COMMISSION DIST 1 POST 2")>0
replace district = "2, POST 1" if strpos(office, "COUNTY COMMISSION DIST 2 POST 1")>0
replace district = "2, POST 1" if strpos(office, "COUNTY COMMISSION DISTRICT 2 POST 1")>0
replace district = "3, POST 1" if strpos(office, "COUNTY COMMISSION DISTRICT 3 POST 1")>0
replace district = "3, POST 2" if strpos(office, "COUNTY COMMISSION DISTRICT 3 POST 2")>0
replace district = "2, POST 1" if strpos(office, "TENNILLE COUNCIL DISTRICT 2 POST 1")>0
replace district = "3, POST 1" if strpos(office, "TENNILLE COUNCIL DISTRICT 3 POST 1")>0
replace district = "STATEWIDE" if strpos(office, "TAX COMMISSIONER")>0
replace district = "STATEWIDE" if strpos(office, "PUBLIC SERVICE COMMISSION")>0
//office 
replace office = "US SENATE" if strpos(office,"US SENATE")>0
replace office = "PRESIDENT" if strpos(office,"PRESIDENT OF THE UNITED STATES")>0
replace office = "US HOUSE" if strpos(office,"US HOUSE")>0
replace office = "STATE HOUSE" if strpos(office,"STATE HOUSE")>0
replace office = "STATE SENATE" if strpos(office,"STATE SENATE")>0
replace office ="DISTRICT ATTORNEY" if strpos(office,"DISTRICT ATTORNEY")>0
replace office = "SOIL AND WATER" if strpos(office, "SOIL AND WATER")>0
replace office = "COUNTY COMMISSIONER" if strpos(office, "COUNTY COMMISSIONER")>0 | strpos(office, "CO COMMISSION ")>0
replace office = "SOLICITOR GENERAL" if strpos(office, "SOLICITOR-GENERAL")>0
replace office = "CHIEF MAGISTRATE" if strpos(office, "CHIEF MAGISTRATE")>0
replace office = "CLERK OF SUPERIOR COURT" if strpos(office, "CLERK OF SUPERIOR COURT")>0
replace office = "CONSTITUTIONAL AMENDMENT #1" if strpos(office, "CONSTITUTIONAL AMENDMENT #1")>0
replace office = "CONSTITUTIONAL AMENDMENT #2" if strpos(office, "CONSTITUTIONAL AMENDMENT #2")>0
replace office = "CORONER" if strpos(office, "CORONER")>0
replace office = "MAYOR" if strpos(office, "MAYOR")>0
replace office = "COUNTY COMMISSION" if strpos(office, "COUNTY COMMISSION")>0 & strpos(office, "CHAIR")==0 & strpos(office, "POST")==0 & strpos(office, "DIST")>0
replace office = "TENNILLE COUNCIL" if strpos(office, "TENNILLE COUNCIL")>0
replace office = "STATEWIDE REFERENDUM A" if strpos(office, "STATEWIDE REFERENDUM A")>0
replace office = "TAX COMMISSIONER" if strpos(office, "TAX COMMISSIONER")>0
replace office = "TRANSPORTATION SPECIAL PURPOSE LOCAL OPTION SALES TAX" if strpos(office, "TRANSPORTATION SPLOST")>0 | strpos(office, "TSPLOST")>0 | strpos(office, "TRANSPORTATION SPECIAL PURPOSE LOCAL OPTION SALES TAX")>0
replace office = "PUBIC SERVICE COMMISSION" if strpos(office, "PUBIC SERVICE COMMISSION")>0
replace office = "BOARD OF EDUCATION" if (strpos(office, "BOARD OF EDUCATION")>0 | strpos(office, "BRD OF EDUCATION")>0) & strpos(office, "DIST")>0
replace office = "COUNTY COMMISSION" if strpos(office, "COUNTY COMMISSION")>0
replace office = "DORAVILLE CITY COUNCIL" if strpos(office, "DORAVILLE CITY COUNCIL DISTRICT 1")>0
replace office = "MCINTYRE CITY COUNCIL" if strpos(office, "MCINTYRE CITY COUNCIL")>0
replace office = "MONROE COUNCILMEMBER" if strpos(office, "MONROE COUNCILMEMBER DISTRICT 6")>0
replace office = "PUBLIC SERVICE COMMISSION" if strpos(office, "PUBLIC SERVICE COMMISSION")>0
//dataverse
gen dataverse = ""
replace dataverse = "STATE" if strpos(office, "STATE SENATE")>0 | strpos(office, "STATE HOUSE")>0
replace dataverse = "STATE" if strpos(office, "SUPERIOR COURT")>0
replace dataverse = "SENATE" if strpos(office, "US SENATE")>0 
replace dataverse = "HOUSE" if strpos(office, "US HOUSE")>0
replace dataverse = "PRESIDENT" if office == "PRESIDENT"
replace dataverse = "STATE" if strpos(office, "STATEWIDE REFERENDUM A")>0
replace dataverse = "STATE" if strpos(office, "CONSTITUTIONAL REFERENDUM")>0
replace dataverse = "STATE" if strpos(office, "TAX COMMISSIONER")>0
replace dataverse = "STATE" if strpos(office, "CONSTITUTIONAL AMENDMENT")>0
replace dataverse = "STATE" if strpos(office, "PUBLIC SERVICE COMMISSION")>0
replace dataverse = "LOCAL" if dataverse==""


replace district = "001" if office=="PUBLIC SERVICE COMMISSION"&candidate=="JASON SHAW"
replace district = "001" if office=="PUBLIC SERVICE COMMISSION"&candidate=="ROBERT G BRYANT"
replace district = "001" if office=="PUBLIC SERVICE COMMISSION"&candidate=="ELIZABETH MELTON"
replace district = "004" if office=="PUBLIC SERVICE COMMISSION"&candidate=="DANIEL BLACKMAN"
replace district = "004" if office=="PUBLIC SERVICE COMMISSION"&candidate=="LAUREN BUBBA MCDONALD JR"
replace district = "004" if office=="PUBLIC SERVICE COMMISSION"&candidate=="NATHAN WILSON"

replace district="041" if office=="STATE SENATE"&candidate=="KIM JACKSON"
replace district="045" if office=="STATE SENATE"&candidate=="MATIELYN JONES"
replace district="048" if office=="STATE SENATE"&candidate=="MICHELLE AU"
replace district="040" if office=="STATE SENATE"&candidate=="SALLY HARRELL"
replace district="045" if office=="STATE SENATE"&candidate=="CLINT DIXON"
replace district="040" if office=="STATE SENATE"&candidate=="GARRY GUAN"
replace district="048" if office=="STATE SENATE"&candidate=="MATT REEVES"
replace district="041" if office=="STATE SENATE"&candidate=="WILLIAM PARK FREEMAN"
replace district="055" if office=="STATE SENATE"&candidate=="GLORIA S BUTLER"

replace district="114" if office=="STATE HOUSE"&candidate=="TOM KIRBY"
replace district="095" if office=="STATE HOUSE"&candidate=="BETH MOORE"
replace district="093" if office=="STATE HOUSE"&candidate==`"DAR"SHUN KENDRICK"'
replace district="094" if office=="STATE HOUSE"&candidate=="KAREN BENNETT"
replace district="099" if office=="STATE HOUSE"&candidate=="MARVIN LIM"
replace district="097" if office=="STATE HOUSE"&candidate=="MARY BLACKMON CAMPBELL"
replace district="096" if office=="STATE HOUSE"&candidate==`"PEDRO "PETE" MARIN"'
replace district="098" if office=="STATE HOUSE"&candidate=="TAEHO CHO"
replace district="097" if office=="STATE HOUSE"&candidate=="BONNIE RICH"
replace district="098" if office=="STATE HOUSE"&candidate=="DAVID CLARK"
replace district="093" if office=="STATE HOUSE"&candidate=="HUBERT OWENS JR"
replace district="103" if office=="STATE HOUSE"&candidate=="CLIFTONMARSHALL"
replace district="100" if office=="STATE HOUSE"&candidate=="DEWEY L MCCLAIN"
replace district="105" if office=="STATE HOUSE"&candidate=="DONNA MCLEOD"
replace district="102" if office=="STATE HOUSE"&candidate=="GREGG KENNARD"
replace district="108" if office=="STATE HOUSE"&candidate=="JASMINE CLARK"
replace district="104" if office=="STATE HOUSE"&candidate=="NAKITA HEMINGWAY"
replace district="106" if office=="STATE HOUSE"&candidate=="REBECCA MITCHELL"
replace district="101" if office=="STATE HOUSE"&candidate=="SAM PARK"
replace district="107" if office=="STATE HOUSE"&candidate=="SHELLY HUTCHINSON"
replace district="106" if office=="STATE HOUSE"&candidate=="BRETT HARRELL"
replace district="101" if office=="STATE HOUSE"&candidate=="CAROL FIELD"
replace district="104" if office=="STATE HOUSE"&candidate=="CHUCK EFSTRATION"
replace district="105" if office=="STATE HOUSE"&candidate=="ERIC DIERKS"
replace district="108" if office=="STATE HOUSE"&candidate=="JOHNNY CRIST"
replace district="107" if office=="STATE HOUSE"&candidate=="MICHAEL MCCONNELL"
replace district="102" if office=="STATE HOUSE"&candidate=="SOO HONG"
replace district="103" if office=="STATE HOUSE"&candidate=="TIMOTHY BARR"
replace district="095" if office=="STATE HOUSE"&candidate=="ERICA MCCURDY"
//replace district="" if office=="STATE HOUSE"&candidate==""

replace candidate = "MARY WHIPPLE-LUE" if candidate=="MARYWHIPPLE-LUE"
replace candidate = "DAR'SHUN KENDRICK" if candidate==`"DAR"SHUN KENDRICK"'
replace candidate = "CLIFTON MARSHALL" if candidate=="CLIFTONMARSHALL"
replace candidate = "JILL PROUTY" if candidate=="JILLPROUTY"
replace candidate = "MATT LIEBERMAN" if candidate=="MATT LIERBERMAN"
//replace candidate = "" if candidate=="YTERENICKIA ÂYTÂ BELL"

replace dataverse = "LOCAL" if office=="TAX COLLECTOR"
replace dataverse = "LOCAL" if office=="CLERK OF SUPERIOR COURT"

//other 
gen year = "2020"
gen stage = "GEN"
replace stage = "PRI" if office=="STATE SENATE"&district=="039"
gen special = "FALSE"
replace special = "TRUE" if strpos(office, "- SPECIAL")>0
//removing "SPECIAL" from office 
replace office = subinstr(office, "- SPECIAL", "", .)
replace special = "TRUE" if office=="STATE SENATE"&district=="039"
replace special = "TRUE" if office=="US SENATE"
replace special = "FALSE" if office=="US SENATE"&candidate=="DAVID A PERDUE"
replace special = "FALSE" if office=="US SENATE"&candidate=="JON OSSOFF"
replace special = "FALSE" if office=="US SENATE"&candidate=="SHANE HAZEL"
gen writein = "FALSE"
gen state_po = "GA"
gen state_fips = 13
gen state_cen = 58
gen state_ic = 44
gen date = "2020-11-03" 
gen readme_check = "FALSE"
gen jurisdiction_name = county_name
replace state = upper(state)
drop if mode == "TOTAL"
drop if precinct == "-1"
keep precinct office party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips candidate district dataverse year stage state special writein state_po state_fips state_cen state_ic date readme_check

gen magnitude = 1 if dataverse!="LOCAL"

order precinct office party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips candidate district dataverse year stage state special writein state_po state_fips state_cen state_ic date readme_check

format precinct %20s
format office %30s

//save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/GA/2020-ga-precinct-primary", replace
export delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/GA/2020-ga-precinct-general.csv", replace 

