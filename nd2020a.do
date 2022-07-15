////////////////////////////////////////
/*
Kevin DeLuca
Clean ND precinct data 2020 elections

2/23/21
*/
////////////////////////////////////////

clear
set more off

*clean each file, need to go through each county page in each spreadsheet for each 


*first, turn each spreadsheet and all the tabs inside into usable stata data:
/*
xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/PRESIDENT/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/PRESIDENT/Statewide Precinct Results.xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/USHOUSE/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/USHOUSE/Statewide Precinct Results(1).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/GOV/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/GOV/Statewide Precinct Results(2).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AUDITOR/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AUDITOR/Statewide Precinct Results(3).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/TREASURER/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/TREASURER/Statewide Precinct Results(4).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/INSCOM/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/INSCOM/Statewide Precinct Results(5).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/PSC/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/PSC/Statewide Precinct Results(6).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/SUPTPI/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/SUPTPI/Statewide Precinct Results(7).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/SUPCRT/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/SUPCRT/Statewide Precinct Results(8).xlsx"

xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AMEND1/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AMEND1/Statewide Precinct Results(9).xlsx"
 
xls2dta , allsheets save("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AMEND2/") : import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AMEND2/Statewide Precinct Results(10).xlsx"
*/


*clean state leg dataverse


* I think for each spreadsheet, go through every county name to see if a sheet with that county name is there - that gives you countyname and precincts, for the candidates specific to the race, which are generally in the same format
*note: when I export the speadsheet version of the precinct results all the votes are "0"s, so I don't think it will work. Here is some code I started working on...

// global counties = `" "Adams" "Barnes" "Benson" "Billings" "Bottineau" "Bowman" "Burke" "Burleigh" "Cass" "Cavalier" "Dickey" "Divide" "Dunn" "Eddy" "Emmons" "Foster" "Golden Valley" "Grand Forks" "Grant" "Griggs" "Hettinger" "Kidder" "LaMoure" "Logan" "McHenry" "McIntosh" "McKenzie" "McLean" "Mercer" "Morton" "Mountrail" "Nelson" "Oliver" "Pembina" "Pierce" "Ramsey" "Ransom" "Renville" "Richland" "Rolette" "Sargent" "Sheridan" "Sioux" "Slope" "Stark" "Steele" "Stutsman" "Towner" "Traill" "Walsh" "Ward" "Wells" "Williams" "'

// foreach var in $counties{
// 	capture import excel "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/STATELEG/sen2.xlsx", clear sheet("`var'"")
	
// 	tempfile `var'
// 	save ``var''
// }


// foreach var in $counties{
// 	capture append using ``var''
// }

// STOP
// compress
// save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/stateleg.dta", replace 



*cleaning non-state leg data
*PRESIDENT
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/PRESIDENT/Statewide Precinct Results_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	rename F candidate4
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Trump and Pence" if num==1
	replace candidate = "Biden and Harris" if num==2
	replace candidate = "Jorgensen and Cohen" if num==3
	replace candidate = "WRITEIN" if num==4
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Trump and Pence"
replace party_detailed = "DEMOCRATIC-NPL" if candidate=="Biden and Harris"
replace party_detailed = "LIBERTARIAN" if candidate=="Jorgensen and Cohen"

gen office="PRESIDENT"
gen dataverse="PRESIDENT"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/president.dta", replace




*US HOUSE
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/USHOUSE/Statewide Precinct Results(1)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	rename F candidate4
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Kelly  Armstrong" if num==1
	replace candidate = "Zach  Raknerud" if num==2
	replace candidate = "Steven James Peterson" if num==3
	replace candidate = "WRITEIN" if num==4
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Kelly  Armstrong"
replace party_detailed = "DEMOCRATIC-NPL" if candidate=="Zach  Raknerud"
replace party_detailed = "LIBERTARIAN" if candidate=="Steven James Peterson"

gen office="US HOUSE"
gen district="000"
gen dataverse="HOUSE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/ushouse.dta", replace




*GOVERNOR
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/GOV/Statewide Precinct Results(2)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	rename F candidate4
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Doug Burgum and  Brent Sanford" if num==1
	replace candidate = "Shelley Lenz and  Ben Vig" if num==2
	replace candidate = "DuWayne Hendrickson and  Joshua Voytek" if num==3
	replace candidate = "WRITEIN" if num==4
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Doug Burgum and  Brent Sanford"
replace party_detailed = "DEMOCRATIC-NPL" if candidate=="Shelley Lenz and  Ben Vig"
replace party_detailed = "LIBERTARIAN" if candidate=="DuWayne Hendrickson and  Joshua Voytek"

gen office="GOVERNOR"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/governor.dta", replace





*STATE AUDITOR
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AUDITOR/Statewide Precinct Results(3)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Joshua C Gallion" if num==1
	replace candidate = "Patrick  Hart" if num==2
	replace candidate = "WRITEIN" if num==3
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Joshua C Gallion"
replace party_detailed = "DEMOCRATIC-NPL" if candidate=="Patrick  Hart"

gen office="STATE AUDITOR"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/auditor.dta", replace





*STATE TREASURER
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/TREASURER/Statewide Precinct Results(4)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Thomas  Beadle" if num==1
	replace candidate = "Mark  Haugen" if num==2
	replace candidate = "WRITEIN" if num==3
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Thomas  Beadle"
replace party_detailed = "DEMOCRATIC-NPL" if candidate=="Mark  Haugen"

gen office="STATE TREASURER"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/treasurer.dta", replace





*INSURANCE COMMISSIONER
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/INSCOM/Statewide Precinct Results(5)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Jon  Godfread" if num==1
	replace candidate = "WRITEIN" if num==2
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Jon  Godfread"

gen office="INSURANCE COMMISSIONER"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/inscom.dta", replace





*PUBLIC SERVICE COMMISSIONER
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/PSC/Statewide Precinct Results(6)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Brian  Kroshus" if num==1
	replace candidate = "Casey D Buchmann" if num==2
	replace candidate = "WRITEIN" if num==3
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""
replace party_detailed = "REPUBLICAN" if candidate=="Brian  Kroshus"
replace party_detailed = "DEMOCRATIC-NPL" if candidate=="Casey D Buchmann"

gen office="PUBLIC SERVICE COMMISSIONER"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/psc.dta", replace






*SUPERINTENDENT OF PUBLIC INSTRUCTION
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/SUPTPI/Statewide Precinct Results(7)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	rename E candidate3
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Kirsten  Baesler" if num==1
	replace candidate = "Brandt J Dick" if num==2
	replace candidate = "WRITEIN" if num==3
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = "NONPARTISAN"

gen office="SUPERINTENDENT OF PUBLIC INSTRUCTION"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/suptpi.dta", replace




*SUPREME COURT JUSTICE
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/SUPCRT/Statewide Precinct Results(8)_`x'.dta", clear
	rename A precinct
	rename B candidate1
	rename C candidate2
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "Jon Jay Jensen" if num==1
	replace candidate = "WRITEIN" if num==2
	destring(votes), replace
	drop if votes==.
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = "NONPARTISAN"

gen office="SUPREME COURT JUSTICE"
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/supcrt.dta", replace





*MEASURE 1
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AMEND1/Statewide Precinct Results(9)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "YES" if num==1
	replace candidate = "NO" if num==2
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""

gen office="Constitutional Measure No. 1 Relating to the state board of higher education"
replace office=strupper(office)
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/amend1.dta", replace






*MEASURE 2
forval x=1(1)53{
	use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/AMEND2/Statewide Precinct Results(10)_`x'.dta", clear
	rename B precinct
	rename C candidate1
	rename D candidate2
	drop A
	keep if precinct!=""
	drop if precinct=="TOTALS"|precinct=="Precinct"
	reshape long candidate, i(precinct) j(num)
	rename candidate votes
	gen candidate = ""
	replace candidate = "YES" if num==1
	replace candidate = "NO" if num==2
	destring(votes), replace
	drop num
	gen countynum = `x'
	tempfile temp`x'
	save `temp`x''
}

use `temp1', clear
forval x=2(1)53{
	append using `temp`x''
}

gen party_detailed = ""

gen office="Constitutional Measure No. 2 Relating to initiated constitutional amendments."
replace office=strupper(office)
gen dataverse="STATE"
gen special="FALSE"

compress
save "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/amend2.dta", replace






use "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/president.dta", clear
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/ushouse.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/governor.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/auditor.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/treasurer.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/inscom.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/psc.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/suptpi.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/supcrt.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/amend1.dta"
append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/amend2.dta"

//append using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/raw/stateleg.dta"










gen party_simplified = ""
replace party_simplified = "REPUBLICAN" if party_detailed=="REPUBLICAN"
replace party_simplified = "DEMOCRATIC" if party_detailed=="DEMOCRATIC-NPL"
replace party_simplified = "LIBERTARIAN" if party_detailed=="LIBERTARIAN"
replace party_simplified = "NONPARTISAN" if party_detailed=="NONPARTISAN"

gen writein="FALSE"
replace writein="TRUE" if candidate=="WRITEIN"
gen mode = "TOTAL"
replace candidate = strupper(candidate)
replace candidate = subinstr(candidate,"  "," ",.)

replace district = "STATEWIDE" if office!="US HOUSE"&office!="PRESIDENT"
tab office district

merge m:1 countynum using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/countynumxwalk.dta", nogen keep(1 3)
drop countynum

*final vars
gen state="North Dakota"
merge m:1 state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/merge_on_statecodes.dta", nogen keep(1 3)
merge m:1 county_name state using "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/primary-precincts/help-files/county-fips-codes.dta", nogen keep(1 3)
tostring(county_fips), replace
gen jurisdiction_name = county_name
gen jurisdiction_fips = county_fips
gen stage = "GEN"
replace state = "NORTH DAKOTA"

gen date = "2020-11-03"
gen readme_check="FALSE"
gen year = 2020
gen magnitude=1

compress
order precinct office district candidate party_detailed party_simplified mode votes county_name county_fips jurisdiction_name jurisdiction_fips dataverse year stage state* special writein date read
sort office district county_name precinct


export delimited  "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/ND/2020-nd-precinct-general.csv", replace




