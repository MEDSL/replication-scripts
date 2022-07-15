///////////////////////////////////////
/*
Kevin DeLuca
MEDSL Precinct Project

new FL cleaning code
*/
///////////////////////////////////////

clear
set more off


*combine all data, 
local files: dir "/Users/joellegross/Documents/GitHub/2020-precincts/precinct/FL/raw/OutputOfficial" files "*.txt"

di `files'

local x=1
foreach file in `files'{
	display `x'
	import delimited "/Users/joellegross/Documents/GitHub/2020-precincts/precinct/FL/raw/OutputOfficial/`file'", clear stringcols(_all)
	gen filenum = `x'
	tempfile file`x'
	save `file`x''
	local x = `x'+1
}

use `file1'
forval x=2(1)67{
	append using `file`x''
}

//replace v7 = v6 if v7==""

drop v1 v3 v4 v5 v8 v9 v10 v11 v14 v17 v18 filenum
rename v2 county_name
replace county_name = strupper(county_name)
//rename v7 precinct
rename v12 office
rename v13 district
rename v15 candidate
rename v16 party_abbrev
rename v19 votes
destring(votes), replace
gen mode = "TOTAL"
gen magnitude=1

gen precinct = v6 if  v6==v7
replace precinct = v6 + "_" + v7 if v6 != v7
replace precinct = v7 if v6==""
replace precinct = v6 if v7==""
drop v7 v6

order precinct office district candidate party_abbrev mode votes magnitude

*use recount totals rather than original totals
// drop if office=="Circuit Judge"&county_name=="BROWARD"
// append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/FL/raw/brocountyrecount.dta"

// replace district = strtrim(district)
// drop if office=="State Senator"&district=="District 37"&county_name=="MIAMI-DADE"
// append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/FL/raw/dadcountyrecount.dta"


*offices, district, and candidate cleaning
replace office=strupper(office)
replace district = strupper(district)

*circuit court judges/clerks?

replace candidate = strupper(candidate)
replace candidate = office+" - YES" if strpos(office,"RETENTION")>0&candidate=="YES"
replace candidate = office+" - NO" if strpos(office,"RETENTION")>0&candidate=="NO"
replace office = district if strpos(office,"RETENTION")>0
replace candidate = subinstr(candidate,"RETENTION OF ","",.)
replace district = "STATEWIDE" if office=="JUSTICE OF THE SUPREME COURT"
replace district = "001" if district=="FIRST DISTRICT COURT OF APPEAL"
replace district = "002" if district=="SECOND DISTRICT COURT OF APPEAL"
replace district = "003" if district=="THIRD DISTRICT COURT OF APPEAL"
replace district = "004" if district=="FOURTH DISTRICT COURT OF APPEAL"
replace district = "005" if district=="FIFTH DISTRICT COURT OF APPEAL"
replace office = "COURT OF APPEAL" if strpos(office,"COURT OF APPEAL")>0

replace office = "AMENDMENT NO. 2: RAISING FLORIDA'S MINIMUM WAGE" if strpos(office,"AMENDMENT NO. 2")>0

replace district = "STATEWIDE" if strpos(office,"AMEND")>0|office=="PRESIDENT OF THE UNITED STATES"
replace office = "US PRESIDENT" if office=="PRESIDENT OF THE UNITED STATES"

replace office = "US HOUSE" if office=="REPRESENTATIVE IN CONGRESS"
replace office = "STATE HOUSE" if office=="STATE REPRESENTATIVE"
replace office = "STATE SENATE" if office=="STATE SENATOR"

replace district = subinstr(district,"DISTRICT ","",.)
replace district = strtrim(district)
replace district = "00"+district if strlen(district)==1
replace district = "0"+district if strlen(district)==2

replace magnitude = 2 if district=="1 (VOTE FOR 2)"|district=="3 (VOTE FOR 2)"|district=="5 (VOTE FOR 2)"
replace district = "001" if district=="1 (2-YR TERM)"|district=="1 (VOTE FOR 2)"
replace district = "003" if district=="3 (VOTE FOR 2)"
replace district = "005" if district=="5 (VOTE FOR 2)"

replace candidate = "YES" if candidate=="YES FOR APPROVAL"
replace candidate = "NO" if candidate=="NO FOR REJECTION"

replace candidate = "WRITEIN" if candidate=="WRITEINVOTES"
gen writein = "FALSE"
replace writein = "TRUE" if candidate=="WRITEIN"

replace candidate = subinstr(candidate,"Ã±","N",.)
replace candidate = subinstr(candidate,"Ã­","I",.)

replace candidate = subinstr(candidate,"(",`"""',.) 
replace candidate = subinstr(candidate,")",`"""',.) 
replace candidate = subinstr(candidate,".","",.) 
replace candidate = subinstr(candidate,",","",.) 
replace candidate = subinstr(candidate,"'",`"""',.) 
replace candidate = subinstr(candidate,"  "," ",.) 


tab office


gen special = "FALSE"


*dataverse
gen dataverse = "LOCAL"
replace dataverse = "STATE" if strpos(office,"CIRCUIT JUDGE")>0|strpos(office,"AMENDMENT")>0|strpos(office,"STATE HOUSE")>0|strpos(office,"STATE SENATE")>0|office=="JUSTICE OF THE SUPREME COURT"
replace dataverse = "HOUSE" if office=="US HOUSE"
replace dataverse = "PRESIDENT" if office=="US PRESIDENT"
tab office dataverse


*party
gen party_detailed = "NONPARTISAN" if party_abbrev=="NOP"
replace party_detailed = "DEMOCRAT" if party_abbrev=="DEM"
replace party_detailed = "REPUBLICAN" if party_abbrev=="REP"
replace party_detailed = "LIBERTARIAN" if party_abbrev=="LPF"
replace party_detailed = "REFORM" if party_abbrev=="REF"
replace party_detailed = "SOCIALIST" if party_abbrev=="PSL"
replace party_detailed = "GREEN" if party_abbrev=="GRE"
replace party_detailed = "CONSTITUTION" if party_abbrev=="CPF"
replace party_detailed = "INDEPENDENT" if party_abbrev=="IND"
replace party_detailed = "ECOLOGY" if party_abbrev=="ECO"
replace party_detailed = "" if strpos(office,"AMEND")>0

drop party_abbrev

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








*final vars
gen state="Florida"
merge m:1 state using "/Users/joellegross/Documents/GitHub/2020-precincts/help-files/merge_on_statecodes.dta", nogen keep(1 3)
merge m:1 county_name state using "/Users/joellegross/Documents/GitHub/2020-precincts/help-files/county-fips-codes.dta", nogen keep(1 3)
tostring(county_fips), replace
replace county_name = subinstr(county_name,"ST.","ST",.)
gen jurisdiction_name = county_name
gen jurisdiction_fips = county_fips
gen stage = "GEN"
replace state = "FLORIDA"

gen date = "2020-11-03"
gen readme_check="FALSE"
gen year = 2020

compress
order precinct office district candidate party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips dataverse year stage state* special writein date read
sort office district county_name precinct

export delimited  "/Users/joellegross/Documents/GitHub/2020-precincts/precinct/FL/2020-fl-precinct-general.csv", replace



STOP


/* OLD - trying to fix Sam's code, probably easier to write my own which can be used here, and on the primary data for 2016, 2018, and 2020

import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/resources/kmd code/checks/FL/2020-fl-precinct-general.csv"

*non-local offices only
replace dataverse = "STATE" if strpos(office,"AMEND")>0
replace dataverse = "STATE" if strpos(office,"CIRCUIT")>0
replace dataverse = "STATE" if strpos(office,"DISTRICT COURT")>0
replace dataverse = "STATE" if office=="STATE ATTORNEY"
replace dataverse = "STATE" if office=="PUBLIC DEFENDER"
//keep if dataverse!="LOCAL"

*candidates
replace candidate = subinstr(candidate,"(",`"""',.)
replace candidate = subinstr(candidate,")",`"""',.)

replace candidate = "YES" if candidate=="YES FOR APPROVAL"
replace candidate = "NO" if candidate=="NO FOR REJECTION"
replace candidate = "WRITEIN" if candidate=="WRITEINVOTES"

*districts
replace district = "STATEWIDE" if strpos(office,"AMEND")>0

*state's attorney
*public defenders 
*circuit judges

*check write ins (are these reported at the precinct level - i.e. with candidate names?)


//replace candidate = "LEO VALENTIN" if name=="LEO VALENTÃ­N"

export delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/FL/2020-fl-precinct-general_kmd.csv", replace



*raw data

local files: dir "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/FL/raw/OutputOfficial" files "*.txt"

di `files'
local x = 1

foreach file in `files'{
	import delimited "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/FL/raw/OutputOfficial/`file'", stringcols(_all) clear
	display `x'
	display v1[1]
	tempfile temp`x'
	save `temp`x''
	local x = `x'+1
}
duplicates drop

use `temp1'
forvalues x=2(1)69{
	append using `temp`x''
	display `x'
}

destring(v19), replace

bysort v13 v15 v12: egen tvotes = sum(v19)
bysort v1 v13 v15 v12: egen tvotescounty = sum(v19)

sort v1 v12 v13 v7 v15
br if v1=="DAD"&v12=="Representative in Congress"&v15!="OverVotes"&v15!="UnderVotes"&v14=="140260"
br if v1=="MON"&v12=="Representative in Congress"&v15!="OverVotes"&v15!="UnderVotes"



/*ok so the issue is, the monroe county results at the precinct level don't match the downloaded data in the folder (not sure where it comes from). When checking US house district 26 votes from monroe, on the Florida sos page it reports:

United States Representative
District: 26
County	Carlos Gimenez (REP)	Debbie Mucarsel-Powell (DEM)
Miami-Dade	151,669				144,010
Monroe	25,554					21,397
Total	177,223					165,407

But when I add up all the county-level votes, in our data AND by using the offical monroe county website (https://www.keys-elections.org/Election-Data/Past-County-Results-2009-Current) I find that Carlos gets 25546 (-8 votes) and Debbie gets 21391 (-6 votes) in monroe county (miami-dade totals match). Every precinct in our data matches what monroe county is reporting on their page, so I think this must be an issue of either our precinct data or of the FL page data being a slightly different version, maybe once they finaled the tallies later. 
