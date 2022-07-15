////////////////////////
/*
Kevin DeLuca
Clean AR General Data 2020
2/16/21
*/
////////////////////////

clear
set more off



*local data xwalk
import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/localxwalk.xlsx", clear firstrow
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/localxwalk.dta", replace

*problem with JACKSON county totals, so I clean those separately here
import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/raw/jacksoncountyclean.xlsx", clear firstrow

gen county = "Jackson"
gen mode="total"

tempfile jackson
save `jackson'



*make a party info sheet for merging later
import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/raw/summary.csv", clear

rename contestname office
rename choicename candidate
rename totalvotes finalvotes
keep office candidate party finalvotes
recast str300 office
gen magnitude=1

replace office = subinstr(office," (Vote For 1)","",.)

tempfile parties
save `parties'


*clean AR 2020 data
import delimited  "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/raw/AR2020_mostrecent.csv", clear

drop v1 raceid candids registration time
rename race office
rename type mode
rename candidates candidate

drop if county=="Jackson"
*append on corrected Jackson county precinct votes
append using `jackson'
replace office = subinstr(office," (Vote For 1)","",.)



*party 
recast str300 office
merge m:1 office candidate using `parties', nogen keep(1 3)

replace office = strupper(office)
replace mode = strupper(mode)
replace mode = "PROVISIONAL" if mode=="PROV"
drop if mode!="TOTAL"
drop if precinct=="-1"
replace candidate = strupper(candidate)


*candidates
replace candidate = subinstr(candidate,".","",.)
replace candidate = subinstr(candidate,", SR"," SR",.)
replace candidate = subinstr(candidate,", JR"," JR",.)
replace candidate = subinstr(candidate,",JR"," JR",.)
replace candidate = subinstr(candidate,", II"," II",.)
replace candidate = subinstr(candidate,"MAYOR ","",.)
replace candidate = subinstr(candidate,"JUDGE ","",.)
replace candidate = subinstr(candidate,"JUSTICE OF THE PEACE ","",.)
replace candidate = subinstr(candidate,"JUSTICE ","",.)
replace candidate = subinstr(candidate,"STATE REPRESENTATIVE ","",.)
replace candidate = subinstr(candidate,"REPRESENTATIVE ","",.)
replace candidate = subinstr(candidate,"STATE REP ","",.)
replace candidate = subinstr(candidate,"REP ","",.)
replace candidate = subinstr(candidate,"SENATOR ","",.)
replace candidate = subinstr(candidate,"CONGRESSMAN ","",.)
replace candidate = subinstr(candidate,"COUNCILMAN ","",.)
replace candidate = subinstr(candidate,"COUCILMAN ","",.)
replace candidate = subinstr(candidate,"COUNCIL MEMBER ","",.)
replace candidate = subinstr(candidate,"COUNCILMEMBER ","",.)
replace candidate = `""THORIUM" GLEN SCHWARZ"' if candidate=="'THORIUM' GLEN SCHWARZ"
replace candidate = `""TOM BOY" RHOADS"' if candidate=="'TOM BOY' RHOADS"
replace candidate = `"ALDERMAN JAMES "JIM" WOZNIAK"' if candidate=="ALDERMAN JAMES 'JIM' WOZNIAK"
replace candidate = `"ANDREW "ANDY" BALLARD"' if candidate=="ANDREW 'ANDY' BALLARD"
replace candidate = `"ANTONIO "TONY" RUCKER"' if candidate=="ANTONIO 'TONY' RUCKER"
replace candidate = `"CARLTON "STONEY" FORTENBERRY"' if candidate=="CARLTON 'STONEY' FORTENBERRY"
replace candidate = `"CATHERINE "CATHIE" MAINORD"' if candidate=="CATHERINE 'CATHIE' MAINORD"
replace candidate = `"CHRISTOPHER "FOE FOE" FRANKLIN"' if candidate=="CHRISTOPHER 'FOE FOE' FRANKLIN"
replace candidate = `"CLINTON "HAMP" HAMPTON"' if candidate=="CLINTON 'HAMP' HAMPTON"
replace candidate = `"DANIELLE "ROSE" RAINS"' if candidate=="DANIELLE 'ROSE' RAINS"
replace candidate = `"DARLENE "LAWRENCE" GARMAN"' if candidate=="DARLENE (LAWRENCE) GARMAN"
replace candidate = `"DAVID "BUTCH" HOYT"' if candidate=="DAVID 'BUTCH' HOYT"
replace candidate = `"FERGUSON STEWART "FERGIE"""' if candidate=="FERGUSON STEWART (FERGIE)"
replace candidate = subinstr(candidate,"CITY ATTORNEY ","",.)

replace candidate = subinstr(candidate," (I)","",.)
replace candidate = subinstr(candidate," (R)","",.)
replace candidate = subinstr(candidate," (D)","",.)

replace candidate = subinstr(candidate,"(",`"""',.) 
replace candidate = subinstr(candidate,")",`"""',.) 
replace candidate = subinstr(candidate,"'",`"""',.) 

replace candidate = "JIM MEDLEY" if candidate=="JP 7 JIM MEDLEY"
replace candidate = "BARBARA WEINSTOCK" if candidate=="JP BARBARA WEINSTOCK"
replace candidate = "LUCAS M POINTER" if candidate=="LUCAS M POINTER, TRUSTEE"

gen writein = "FALSE"
replace writein = "TRUE" if candidate=="WRITE-IN"
replace candidate="WRITEIN" if candidate=="WRITE-IN"


*party
gen party_detailed = ""
replace party_detailed = "AMERICAN" if partyname=="Ame"
replace party_detailed = "CONSTITUTION" if partyname=="Cns"
replace party_detailed = "DEMOCRAT" if partyname=="Dem"
replace party_detailed = "GREEN" if partyname=="Grn"
replace party_detailed = "INDEPENDENT" if partyname=="Ind"
replace party_detailed = "LIBERTARIAN" if partyname=="Lib"
replace party_detailed = "LIFE" if partyname=="Lif"
replace party_detailed = "NONPARTISAN" if partyname=="Non"
replace party_detailed = "REPUBLICAN" if partyname=="Rep"
replace party_detailed = "SOCIALIST" if partyname=="Soc"

drop partyname


*manually fill out the rest of the partys for candidates that are missing their party info
replace party_detailed="DEMOCRAT" if candidate=="CHRISTOPHER OGBURN"
replace party_detailed="REPUBLICAN" if candidate=="JEFFREY R WARDLAW"
replace party_detailed="REPUBLICAN" if candidate=="HOWARD BEATY"
replace party_detailed="DEMOCRAT" if candidate=="LEANNE BURCH"
replace party_detailed="DEMOCRAT" if candidate=="DON GLOVER"
replace party_detailed="REPUBLICAN" if candidate=="MARK D MCELROY"
replace party_detailed="DEMOCRAT" if candidate=="KEN FERGUSON"
replace party_detailed="DEMOCRAT" if candidate=="VIVIAN FLOWERS"
replace party_detailed="REPUBLICAN" if candidate=="JOHN MADDOX"
replace party_detailed="REPUBLICAN" if candidate=="MARCUS RICHMOND"
replace party_detailed="LIBERTARIAN" if candidate=="JUDY BOWERS"
replace party_detailed="REPUBLICAN" if candidate=="RICHARD MCGREW"
replace party_detailed="REPUBLICAN" if candidate=="LANNY FITE"
replace party_detailed="REPUBLICAN" if candidate=="BRUCE COZART"
replace party_detailed="REPUBLICAN" if candidate=="LES WARREN"
replace party_detailed="REPUBLICAN" if candidate=="RICK MCCLURE"
replace party_detailed="DEMOCRAT" if candidate=="JOYCE SCHIMENTI"
replace party_detailed="REPUBLICAN" if candidate=="JULIE MAYBERRY"
replace party_detailed="REPUBLICAN" if candidate=="TONY FURMAN"
replace party_detailed="DEMOCRAT" if candidate=="FRED LOVE"
replace party_detailed="DEMOCRAT" if candidate=="FRED ALLEN"
replace party_detailed="REPUBLICAN" if candidate=="KEITH BROOKS"
replace party_detailed="DEMOCRAT" if candidate=="MAZHIL RAJENDRAN"
replace party_detailed="DEMOCRAT" if candidate=="ASHLEY HUDSON"
replace party_detailed="REPUBLICAN" if candidate=="JIM SORVILLO"
replace party_detailed="DEMOCRAT" if candidate=="TIPPI MCCULLOUGH"
replace party_detailed="DEMOCRAT" if candidate=="JOY C SPRINGER"
replace party_detailed="INDEPENDENT" if candidate=="RODERICK GREER TALLEY"
replace party_detailed="DEMOCRAT" if candidate=="ANDREW COLLINS"
replace party_detailed="DEMOCRAT" if candidate=="DENISE ENNETT"
replace party_detailed="DEMOCRAT" if candidate=="JAMIE SCOTT"
replace party_detailed="REPUBLICAN" if candidate=="CARLTON WING"
replace party_detailed="DEMOCRAT" if candidate=="MATTHEW STALLINGS"
replace party_detailed="DEMOCRAT" if candidate=="KAYLA APPLEGATE"
replace party_detailed="REPUBLICAN" if candidate=="MARK LOWERY"
replace party_detailed="REPUBLICAN" if candidate=="DAVID RAY"
replace party_detailed="DEMOCRAT" if candidate=="JANNIE M COTTON"
replace party_detailed="REPUBLICAN" if candidate=="KARILYN BROWN"
replace party_detailed="DEMOCRAT" if candidate=="MARK PERRY"
replace party_detailed="REPUBLICAN" if candidate=="BRIAN S EVANS"
replace party_detailed="REPUBLICAN" if candidate=="CAMERON COOPER"
replace party_detailed="DEMOCRAT" if candidate=="RODNEY GOVENS"
replace party_detailed="REPUBLICAN" if candidate=="CRAIG CHRISTIANSEN"
replace party_detailed="DEMOCRAT" if candidate=="JUSTIN REEVES"
replace party_detailed="REPUBLICAN" if candidate=="STEVE HOLLOWELL"
replace party_detailed="REPUBLICAN" if candidate=="JOHNNY RYE"
replace party_detailed="REPUBLICAN" if candidate=="MARSH DAVIS"
replace party_detailed="REPUBLICAN" if candidate=="MICHELLE GRAY"
replace party_detailed="REPUBLICAN" if candidate=="STU SMITH"
replace party_detailed="DEMOCRAT" if candidate=="DAVID NORMAN"
replace party_detailed="REPUBLICAN" if candidate=="RICK BECK"
replace party_detailed="REPUBLICAN" if candidate=="JOSH MILLER"
replace party_detailed="REPUBLICAN" if candidate=="STEPHEN MEEKS"
replace party_detailed="DEMOCRAT" if candidate=="STEVE WILSON"
replace party_detailed="REPUBLICAN" if candidate=="AARON PILKINGTON"
replace party_detailed="REPUBLICAN" if candidate=="SPENCER HAWKS"
replace party_detailed="REPUBLICAN" if candidate=="JAMES B PHILLIPS"
replace party_detailed="DEMOCRAT" if candidate=="STEVE MAGIE"
replace party_detailed="REPUBLICAN" if candidate=="MARY BENTLEY"
replace party_detailed="DEMOCRAT" if candidate=="CALEB HARWELL"
replace party_detailed="REPUBLICAN" if candidate=="CINDY CRAWFORD"
replace party_detailed="REPUBLICAN" if candidate=="JUSTIN BOYD"
replace party_detailed="LIBERTARIAN" if candidate=="STEPHEN EDWARDS"
replace party_detailed="DEMOCRAT" if candidate=="JAY RICHARDSON"
replace party_detailed="REPUBLICAN" if candidate=="KEITH SLAPE"
replace party_detailed="DEMOCRAT" if candidate=="DENISE GARNER"
replace party_detailed="REPUBLICAN" if candidate=="BRIAN HESTER"
replace party_detailed="DEMOCRAT" if candidate=="DAVID WHITAKER"
replace party_detailed="REPUBLICAN" if candidate=="JOHN S LATOUR"
replace party_detailed="DEMOCRAT" if candidate=="NICOLE CLOWNEY"
replace party_detailed="DEMOCRAT" if candidate=="MICHAEL BENNETT-SPEARS"
replace party_detailed="REPUBLICAN" if candidate=="ROBIN LUNDSTRUM"
replace party_detailed="REPUBLICAN" if candidate=="CLINT PENZO"
replace party_detailed="DEMOCRAT" if candidate=="HAWLEY WOODS"
replace party_detailed="REPUBLICAN" if candidate=="JED DUGGAR"
replace party_detailed="DEMOCRAT" if candidate=="MEGAN GODFREY"
replace party_detailed="DEMOCRAT" if candidate=="KELLY ROSS KROUT"
replace party_detailed="REPUBLICAN" if candidate=="KENDON UNDERWOOD"
replace party_detailed="REPUBLICAN" if candidate=="DELIA HAAK"
replace party_detailed="DEMOCRAT" if candidate=="NICK JONES"
replace party_detailed="REPUBLICAN" if candidate=="GAYLA HENDREN MCKENZIE"
replace party_detailed="DEMOCRAT" if candidate=="DAISY BONILLA"
replace party_detailed="REPUBLICAN" if candidate=="JIM DOTSON"
replace party_detailed="DEMOCRAT" if candidate=="JENE HUFFMAN-GILREATH"
replace party_detailed="REPUBLICAN" if candidate=="JOHN P CARR"
replace party_detailed="REPUBLICAN" if candidate=="AUSTIN MCCOLLUM"
replace party_detailed="REPUBLICAN" if candidate=="JILL BRYANT"
replace party_detailed="DEMOCRAT" if candidate=="JON COMSTOCK"
replace party_detailed="REPUBLICAN" if candidate=="JOSHUA BRYANT"
replace party_detailed="REPUBLICAN" if candidate=="HARLAN BREAUX"
replace party_detailed="DEMOCRAT" if candidate=="SUZIE BELL"
replace party_detailed="REPUBLICAN" if candidate=="RON MCNAIR"
replace party_detailed="REPUBLICAN" if candidate=="BART HESTER"
replace party_detailed="DEMOCRAT" if candidate=="RONETTA J FRANCIS"
replace party_detailed="REPUBLICAN" if candidate=="JIM HENDREN"
replace party_detailed="DEMOCRAT" if candidate=="RYAN CRAIG"
replace party_detailed="REPUBLICAN" if candidate=="LANCE EADS"
replace party_detailed="REPUBLICAN" if candidate=="JIMMY HICKEY JR"
replace party_detailed="REPUBLICAN" if candidate=="ALAN CLARK"
replace party_detailed="DEMOCRAT" if candidate=="BRANDON OVERLY"
replace party_detailed="REPUBLICAN" if candidate=="BREANNE DAVIS"
replace party_detailed="REPUBLICAN" if candidate=="RONALD CALDWELL"
replace party_detailed="REPUBLICAN" if candidate=="BEN GILMORE"
replace party_detailed="DEMOCRAT" if candidate=="EDDIE L CHEATHAM"
replace party_detailed="REPUBLICAN" if candidate=="RICKY HILL"
replace party_detailed="REPUBLICAN" if candidate=="BOB THOMAS"
replace party_detailed="DEMOCRAT" if candidate=="CLARKE TUCKER"
replace party_detailed="DEMOCRAT" if candidate=="ALISA BLAIZE DIXON"
replace party_detailed="REPUBLICAN" if candidate=="JANE ENGLISH"
replace party_detailed="REPUBLICAN" if candidate=="FRENCH HILL"
replace party_detailed="DEMOCRAT" if candidate=="JOYCE ELLIOTT"
replace party_detailed="DEMOCRAT" if candidate=="CELESTE WILLIAMS"
replace party_detailed="LIBERTARIAN" if candidate=="MICHAEL J KALAGIAS"
replace party_detailed="REPUBLICAN" if candidate=="STEVE WOMACK"
replace party_detailed="REPUBLICAN" if candidate=="BRUCE WESTERMAN"
replace party_detailed="LIBERTARIAN" if candidate=="FRANK GILBERT"
replace party_detailed="DEMOCRAT" if candidate=="WILLIAM H HANSON"



gen party_simplified = ""
replace party_simplified = "DEMOCRAT" if party_detailed=="DEMOCRAT"
replace party_simplified = "REPUBLICAN" if party_detailed=="REPUBLICAN"
replace party_simplified = "LIBERTARIAN" if party_detailed=="LIBERTARIAN"
replace party_simplified = "NONPARTISAN" if party_detailed=="NONPARTISAN"
replace party_simplified = "OTHER" if party_detailed=="AMERICAN"
replace party_simplified = "OTHER" if party_detailed=="CONSTITUTION"
replace party_simplified = "OTHER" if party_detailed=="GREEN"
replace party_simplified = "OTHER" if party_detailed=="INDEPENDENT"
replace party_simplified = "OTHER" if party_detailed=="LIFE"
replace party_simplified = "OTHER" if party_detailed=="SOCIALIST"


gen special = "FALSE"
replace special = "TRUE" if strpos(office,"SPECIAL")>0


*dataverse
gen dataverse = "LOCAL"
replace dataverse = "STATE" if strpos(office,"CIRCUIT JUDGE")>0|strpos(office,"AMENDMENT")>0|office=="SPECIAL ELECTION FOR STATE HOUSE DISTRICT 96"|strpos(office,"STATE REP")>0|strpos(office,"STATE REPRESENTATIVE")>0|strpos(office,"STATE SENATE")>0 //|strpos(office,"UNOPPOSED STATE REP")>0|strpos(office,"UNOPPOSED STATE SEN")>0
replace dataverse = "HOUSE" if strpos(office,"U.S. CONGRESS")>0
replace dataverse = "SENATE" if office=="U.S. SENATE"
replace dataverse = "PRESIDENT" if office=="U.S. PRESIDENT, VICE PRESIDENT"

*ballot measures: https://ballotpedia.org/Arkansas_2020_ballot_measures

*district - nonlocal stuff
//keep if dataverse!="LOCAL"



gen district = ""
replace district = substr(office,strpos(office,"DISTRICT"),.) if strpos(office,"DISTRICT")>0
replace district = substr(office,strpos(office,"DIST"),.) if strpos(office,"DIST ")>0
replace district = subinstr(district,"DISTRICT ","",.) if strpos(office,"CIRCUIT JUDGE")==0
replace district = subinstr(district,"DIST ","",.) if strpos(office,"CIRCUIT JUDGE")==0
replace district = strtrim(district)
replace district = "00"+district if strlen(district)==1
replace district = "0"+district if strlen(district)==2

*typo/errors
replace candidate = "DAVE WALLACE" if candidate=="RONALD CALDWELL"&district=="022" //https://ballotpedia.org/Dave_Wallace_(Arkansas)

*office - only nonlocal offices
replace office = "CIRCUIT JUDGE" if strpos(office,"CIRCUIT JUDGE")>0
replace office = "STATE HOUSE" if office=="SPECIAL ELECTION FOR STATE HOUSE DISTRICT 96"|strpos(office,"STATE REP")>0|strpos(office,"STATE REPRESENTATIVE")>0 //|strpos(office,"UNOPPOSED STATE REP")>0
replace office = "STATE SENATE" if strpos(office,"STATE SENATE")>0 //|strpos(office,"UNOPPOSED STATE SEN")>0
replace office = "US HOUSE" if strpos(office,"U.S. CONGRESS")>0
replace office = "US SENATE" if office=="U.S. SENATE"
replace office = "PRESIDENT" if office=="U.S. PRESIDENT, VICE PRESIDENT"
format office %30s

replace party_detailed = "NONPARTISAN" if office=="CIRCUIT JUDGE"
replace party_simplified = "NONPARTISAN" if office=="CIRCUIT JUDGE"


drop if candidate=="FOR"&strpos(office,"AMENDMENT")==0
drop if candidate=="AGAINST"&strpos(office,"AMENDMENT")==0

*statewide districts
replace district = "STATEWIDE" if district==""&dataverse=="STATE"|dataverse=="SENATE"|dataverse=="PRESIDENT"

*more district stuff
replace district = "DISTRICT 3, DIVISION 3" if district=="DISTRICT 03, DIVISION 03"
replace district = "DISTRICT 6, DIVISION 2, SUBDISTRICT 6.2" if district=="DISTRICT 06, DIVISION 02, SUBDISTRICT 6.2"
replace district = "DISTRICT 6, DIVISION 10, SUBDISTRICT 6.1" if district=="DISTRICT 06, DIVISION 10, SUBDISTRICT 6.1"
replace district = "DISTRICT 6, DIVISION 14, SUBDISTRICT 6.2" if district=="DISTRICT 06, DIVISION 14, SUBDISTRICT 6.2"
replace district = "DISTRICT 6, DIVISION 15, SUBDISTRICT 6.2" if district=="DISTRICT 06, DIVISION 15, SUBDISTRICT 6.2"
replace district = "DISTRICT 10, DIVISION 1, SUBDISTRICT 10.2" if district=="DISTRICT 10, DIVISION 01, SUBDISTRICT 10.2"
replace district = "DISTRICT 11-WEST, DIVISION 3, SUBDISTRICT 11.2" if district=="DISTRICT 11-WEST, DIVISION 3, SUBDISTRICT 11.2"
replace district = "DISTRICT 12, DIVISION 6" if district=="DISTRICT 12, DIVISION 06"
replace district = "DISTRICT 18-EAST, DIVISION 2" if district=="DISTRICT 18-EAST, DIVISION 02"


*final vars
gen state="Arkansas"
merge m:1 state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/merge_on_statecodes.dta", nogen keep(1 3)
rename county county_name
replace county_name = strupper(county_name)
replace county_name = "HOT SPRING" if county_name=="HOT_SPRING"
replace county_name = "LITTLE RIVER" if county_name=="LITTLE_RIVER"
replace county_name = "ST. FRANCIS" if county_name=="ST_FRANCIS"
replace county_name = "VAN BUREN" if county_name=="VAN_BUREN"
merge m:1 county_name state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/county-fips-codes.dta", nogen keep(1 3)
tostring(county_fips), replace
replace county_fips = "0"+county_fips
gen jurisdiction_name = county_name
gen jurisdiction_fips = county_fips
gen stage = "GEN"
replace state = "ARKANSAS"

gen date = "2020-11-03"
gen readme_check="FALSE"
gen year = 2020

drop if county_name=="BAXTER"&candidate=="MARSH DAVIS"
replace party_detailed="" if strpos(office,"ISSUE")>0
replace party_simplified="" if strpos(office,"ISSUE")>0
replace magnitude=1
drop finalvotes


merge m:1 office county_n dataverse using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/localxwalk.dta", gen(merge_local)

replace office = office_new if merge_local==3
replace district = district_new if merge_local==3

drop office_new district_new merge_local

*some final cleaning of local offices


compress
order precinct office district candidate party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips dataverse year stage state* special writein date read
sort office district county_name precinct


export delimited  "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/AR/2020-ar-precinct-general.csv", replace



STOP

keep candidate office district party_*
duplicates drop
sort office district candidate
duplicates r candidate
duplicates tag candidate, gen(tag)




