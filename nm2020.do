///////////////////////////////////////
/*
Kevin DeLuca
MEDSL Precinct Project

new NM cleaning code for 2020
*/
///////////////////////////////////////

clear
set more off


*clean crosswalk real fast
import excel using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/NM/candtoparty.xlsx", clear firstrow
tempfile xwalk
save `xwalk'



*get data from individual sheets to dta data, for each office/race
global offices = `" "amend1" "amend2" "bondA" "bondB" "bondC" "judgecoa1" "judgecoa2" "judgecoa3" "judgeretentioncoa" "pres" "scjustice1" "scjustice2" "usrepdist1" "usrepdist2" "usrepdist3" "ussenate" "staterep1" "staterep2" "staterep3" "staterep4" "staterep5" "staterep6" "staterep7" "staterep8" "staterep9" "staterep10" "staterep11" "staterep12" "staterep13" "staterep14" "staterep15" "staterep16" "staterep17" "staterep18" "staterep19" "staterep20" "staterep21" "staterep22" "staterep23" "staterep24" "staterep25" "senatedist1" "senatedist2" "senatedist3" "senatedist4" "senatedist5" "senatedist6" "senatedist7" "senatedist8" "senatedist9" "senatedist10" "senatedist11" "senatedist12" "senatedist13" "senatedist14" "senatedist15" "senatedist16" "senatedist17" "senatedist18" "senatedist19" "senatedist20" "senatedist21" "senatedist22" "senatedist23" "senatedist24" "senatedist25" "'


foreach off in $offices{
	import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/NM/raw/`off'.xlsx", describe
	
	local N1 = `r(N_worksheet)'
	forvalues x=1/`N1' {
		local sheet`x' "`r(worksheet_`x')'"
	}

	local s=1
	forval x=1/`N1' {
		import excel using  "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/NM/raw/`off'.xlsx", sheet(`"`sheet`x''"') clear
		drop if B==""
		rename B precinct
		rename A office
		local c=-2
		foreach var of varlist _all{
			local c = `c'+1
			if `c'>=1{
				gen candname`c' = `var'[1]
				rename `var' candidate`c'
			}
		}
		local N2 = _N
		forval y=2(1)`N2'{
			quietly replace office = office[`y'-1] in `y'
		}
		drop in 1
		reshape long candidate candname, i(precinct) j(cand_n)
		rename candidate votes
		replace votes = "-1" if votes=="*"
		destring(votes), replace
		rename candname candidate
		drop cand_n
		gen county_name = `"`sheet`x''"'
		tempfile county`x'
		save `county`x''
		local s = `s'+1
	}
	local s = `s'-1

	use `county1', clear
	forval x=1(1)`s' {
		append using `county`x''
	}
	drop if precinct=="TOTALS"
	
	tempfile pct_`off'
	save `pct_`off''
	display "`off'"
}

global offices2 = `" "amend2" "bondA" "bondB" "bondC" "judgecoa1" "judgecoa2" "judgecoa3" "judgeretentioncoa" "pres" "scjustice1" "scjustice2" "usrepdist1" "usrepdist2" "usrepdist3" "ussenate" "staterep1" "staterep2" "staterep3" "staterep4" "staterep5" "staterep6" "staterep7" "staterep8" "staterep9" "staterep10" "staterep11" "staterep12" "staterep13" "staterep14" "staterep15" "staterep16" "staterep17" "staterep18" "staterep19" "staterep20" "staterep21" "staterep22" "staterep23" "staterep24" "staterep25" "senatedist1" "senatedist2" "senatedist3" "senatedist4" "senatedist5" "senatedist6" "senatedist7" "senatedist8" "senatedist9" "senatedist10" "senatedist11" "senatedist12" "senatedist13" "senatedist14" "senatedist15" "senatedist16" "senatedist17" "senatedist18" "senatedist19" "senatedist20" "senatedist21" "senatedist22" "senatedist23" "senatedist24" "senatedist25" "'

use `pct_amend1', clear
foreach off in $offices2{
	append using `pct_`off''
}



*candidate to party crosswalk here... also include districts for people


replace candidate = strupper(candidate)
replace county_name = strupper(county_name)

merge m:1 office candidate using `xwalk', nogen keep(1 3)

order precinct county_name office candidate party_d party_s

gen date = "2020-11-03"


*offices, district, and candidate cleaning
replace office = strupper(office)
replace office = strtrim(office)

gen special = "FALSE"


replace office = "BOND A" if strpos(office,"BOND QUESTION A")>0
replace office = "BOND B" if strpos(office,"BOND QUESTION B")>0
replace office = "BOND C" if strpos(office,"BOND QUESTION C")>0

replace office = "CONSTITUTIONAL AMENDMENT 1" if strpos(office,"CONSTITUTIONAL AMENDMENT 1")>0
replace office = "CONSTITUTIONAL AMENDMENT 2" if strpos(office,"CONSTITUTIONAL AMENDMENT 2")>0

replace office = "RETENTION - COURT OF APPEALS" if office=="JUDICIAL RETENTION: SHALL JACQUELINE R MEDINA BE RETAINED AS JUDGE OF THE COURT OF APPEALS?"
replace office = "COURT OF APPEALS JUDGE" if strpos(office,"JUDGE OF THE COURT OF APPEALS")
replace candidate = "JACQUELINE R MEDINA - NO" if office=="RETENTION - COURT OF APPEALS"&candidate=="NO"
replace candidate = "JACQUELINE R MEDINA - YES" if office=="RETENTION - COURT OF APPEALS"&candidate=="YES"

replace office = "STATE HOUSE" if office=="STATE REPRESENTATIVE"
replace office = "STATE SENATE" if office=="STATE SENATOR"
replace office = "US SENATE" if office=="UNITED STATES SENATOR"
replace office = "US HOUSE" if office=="UNITED STATES REPRESENTATIVE"
replace office = "US PRESIDENT" if office=="PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES"

format office %50s

gen dataverse="STATE"
replace dataverse="PRESIDENT" if office=="US PRESIDENT"
replace dataverse="SENATE" if office=="US SENATE"
replace dataverse="HOUSE" if office=="US HOUSE"


*candidate stuff
gen writein = "FALSE"
replace writein = "TRUE" if strpos(candidate,"WRITE IN")>0
replace candidate = subinstr(candidate,"(WRITE IN)","",.)

replace candidate = subinstr(candidate,"(",`"""',.) 
replace candidate = subinstr(candidate,")",`"""',.) 
replace candidate = subinstr(candidate,".","",.) 
replace candidate = subinstr(candidate,",","",.) 
replace candidate = subinstr(candidate,"'",`"""',.) 
replace candidate = subinstr(candidate,"  "," ",.) 
replace candidate = strtrim(candidate)


gen mode = "TOTAL"


*final vars
gen state="New Mexico"
merge m:1 state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/merge_on_statecodes.dta", nogen keep(1 3)
merge m:1 county_name state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/county-fips-codes.dta", nogen keep(1 3)
tostring(county_fips), replace
replace county_name = subinstr(county_name,"ST.","ST",.)
gen jurisdiction_name = county_name
gen jurisdiction_fips = county_fips
replace state = strupper(state)
gen stage = "GEN"

gen readme_check="TRUE"
gen year = 2020
gen magnitude=1

duplicates drop


compress
order precinct office district candidate party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips dataverse year stage state* special writein date read
sort office district county_name precinct

export delimited  "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/NM/2020-nm-precinct-general.csv", replace





