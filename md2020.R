library(stringi)
library(stringr)
library(haven)
library(foreign)
library(readxl)
library(data.table)
library(tidyr)
library(tidyverse)
options(stringsAsFactors = FALSE)

#kevin edits, 03/29/21 (adding magnitude field)

#md <- read.csv("~/GitHub/2020-precincts/precinct/MD/raw/All_By_Precinct_2020_General.csv")
md <- read.csv("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/MD/raw/All_By_Precinct_2020_General.csv")

md$candidate <- md$Candidate.Name
md <- mutate(md, candidate = toupper(candidate),
             candidate = trimws(candidate))
md <- mutate(md, office = trimws(Office.Name))
md <- gather(md, key = "mode", value = "votes", Early.Voting.Votes:Total.Votes.Against)

md <- md %>%
  
  # Create new variables
  mutate(precinct = case_when(nchar(Election.Precinct) == 1 & nchar(Election.District) == 2 ~ paste0(Election.District, "-00", Election.Precinct),
                              nchar(Election.Precinct) == 2 & nchar(Election.District) == 2 ~ paste0(Election.District, "-0", Election.Precinct),
                              nchar(Election.Precinct) == 1 & nchar(Election.District) == 1 ~ paste0("0", Election.District, "-00", Election.Precinct),
                              nchar(Election.Precinct) == 2 & nchar(Election.District) == 1 ~ paste0("0", Election.District, "-0", Election.Precinct)),
         
         # Clean RaceName variable in raw data to create office variable
         # Fix names, make sure districts are not a part of office for big ones, etc.
         # For later dataverse coding, checked court races in Montana and found district races should be state -- code office and district accordingly
         
         
         race_description = toupper(Office.Name),
         race_description = trimws(race_description),
         office = case_when(str_detect(race_description, "PRESIDENT - VICE PRES") ~ "US PRESIDENT",
                            str_detect(race_description, "REPRESENTATIVE IN CONGRESS") ~ "US HOUSE",
                            str_detect(race_description, "JUDGE SPECIAL APPEALS AT LARGE") ~ "RETENTION JUDGE SPECIAL APPEALS AT LARGE",
                            race_description=="JUDGE SPECIAL APPEALS" ~ "RETENTION JUDGE SPECIAL APPEALS",
                            str_detect(race_description, "JUDGE COURT OF APPEALS") ~ "RETENTION JUDGE COURT OF APPEALS",
                            TRUE ~ race_description),
         office = case_when(str_detect(office, ",") ~ gsub("\\,", "", office),
                            TRUE ~ office),
         office = case_when(str_detect(office, ".") ~ gsub("\\.", "", office),
                            TRUE ~ office),
         office = case_when(str_detect(office, "(VOTE FOR 3)") ~ gsub("(VOTE FOR 3)", "", office, fixed = TRUE),
                            TRUE ~ office),
         #office = case_when(str_detect(district, "Judicial Circuit") ~ paste0(office, " ", as.character(trimws(toupper(str_sub(district, 1,4)))), " CIRCUIT"),
        #                    TRUE ~ office),
         office = case_when( str_detect(race_description, "18TH JUDICIAL COURT") ~ "CIRCUIT JUDGE 18TH CIRCUIT",
                             TRUE ~ office),
         office = trimws(office),
         
        candidate = case_when(str_detect(race_description, "JUDGE SPECIAL APPEALS AT LARGE") & str_detect(md$mode, "Against")
                              ~ paste0(candidate, " - NO"),
                              str_detect(race_description, "JUDGE SPECIAL APPEALS AT LARGE") & !str_detect(md$mode, "Against")
                              ~ paste0(candidate, " - YES"),
                              race_description=="JUDGE SPECIAL APPEALS" & str_detect(md$mode, "Against")
                              ~ paste0(candidate, " - NO"),
                              race_description=="JUDGE SPECIAL APPEALS" & !str_detect(md$mode, "Against")
                              ~ paste0(candidate, " - YES"),
                              str_detect(race_description, "JUDGE COURT OF APPEALS") & str_detect(md$mode, "Against")
                              ~ paste0(candidate, " - NO"),
                              str_detect(race_description, "JUDGE COURT OF APPEALS") & !str_detect(md$mode, "Against") 
                              ~ paste0(candidate, " - YES"),
                              TRUE ~ candidate),
         
         # For local-level races, less important to parse information
         # (E.g. leave entirety of "COUNTY COMMISSIONER - DISTRICT 3" in office variable)
         # TRUE ~ toupper(race_description)) # everything else keeps the same office value in RaceName
         
         # Clean PartyCode to create party variables
         party = Party,
         party_detailed = case_when(party=="REP" ~ "REPUBLICAN",
                                    str_detect(party, "REP") ~ "REPUBLICAN",
                                    party=="DEM" ~ "DEMOCRAT",
                                    str_detect(party, "DEM") ~ "DEMOCRAT",
                                    party=="LIB" ~ "LIBERTARIAN",
                                    str_detect(party, "LIB") ~ "LIBERTARIAN",
                                    party=="GRN" ~ "GREEN",
                                    str_detect(party, "GRN") ~ "GREEN",
                                    party=="BAR" ~ "BREAD AND ROSES",
                                    party=="OTH" ~ "OTHER",
                                    party=="WCP" ~ "WORKING CLASS",
                                    party=="NP" ~ "NONPARTISAN",
                                    party=="NOP"~ "NONPARTISAN",
                                    TRUE ~ "OTHER"),
         party_detailed = case_when(is.na(party_detailed) ~ "NONPARTISAN",
                                    TRUE ~ party_detailed),
         party_simplified = case_when(party=="REP" ~ "REPUBLICAN",
                                      str_detect(party, "REP") ~ "REPUBLICAN",
                                      party=="DEM" ~ "DEMOCRAT",
                                      str_detect(party, "DEM") ~ "DEMOCRAT",
                                      party=="LIB" ~ "LIBERTARIAN",
                                      str_detect(party, "LIB") ~ "LIBERTARIAN",
                                      party=="IND" ~ "INDEPENDENT",
                                      str_detect(party, "IND") ~ "INDEPENDENT",
                                      party=="NP" ~ "NONPARTISAN",
                                      party=="NOP"~ "NONPARTISAN",
                                      TRUE ~ "OTHER"),
         party_simplified = case_when(is.na(party_simplified) ~ "OTHER",
                                      TRUE ~ party_simplified),
         
        
         # Votes are broken down by voting mode
         
         
         mode = case_when(mode == "Early.Voting.Votes" ~ "EARLY VOTING",
                          mode == "Election.Day.Votes" ~ "ELECTION DAY",
                          mode == "By.Mail.Votes" ~ "ABSENTEE",
                          mode== "Prov..Votes" ~ "PROVISIONAL",
                          mode== "By.Mail.2.Votes" ~ "2ND ABSENTEE",
                          mode == "Early.Voting.Votes.Against" ~ "EARLY VOTING",
                          mode == "Election.Day.Votes.Against" ~ "ELECTION DAY",
                          mode == "By.Mail.Votes.Against" ~ "ABSENTEE",
                          mode== "Prov..Votes.Against" ~ "PROVISIONAL",
                          mode== "By.Mail.2.Votes.Against" ~ "2ND ABSENTEE",
                          TRUE ~ mode),
         votes = case_when(votes=="NULL" ~ as.integer(0),
                           TRUE ~ as.integer(votes)),
         # Create county name variable
         county = County,
         county_name = case_when(county==1 ~ "Allegany",
                                 county==2 ~ "Anne Arundel",
                                 county==3 ~ "Baltimore City",
                                 county==4 ~ "Baltimore",
                                 county==5 ~ "Calvert",
                                 county==6 ~ "Caroline",
                                 county==7 ~ "Carroll",
                                 county==8 ~ "Cecil",
                                 county==9 ~ "Charles",
                                 county==10 ~ "Dorchester",
                                 county==11 ~ "Frederick",
                                 county==12 ~ "Garrett",
                                 county==13 ~ "Harford",
                                 county==14 ~ "Howard",
                                 county==15 ~ "Kent", 
                                 county==16 ~ "Montgomery",
                                 county==17 ~ "Prince George's",
                                 county==18 ~ "Queen Anne's",
                                 county==19 ~ "St Mary's",
                                 county==20 ~ "Somerset",
                                 county==21 ~ "Talbot",
                                 county==22 ~ "Washington",
                                 county==23 ~ "Wicomico",
                                 county==24 ~ "Worcester"),
         county_name = toupper(county_name),
         county_name = case_when(str_detect(county_name, ".") ~ gsub("\\.", "", county_name),
                                 TRUE ~ county_name),
         
         # Add county_fips later, after this mutate() command and after creating state name (necessary in the merging)
         
         # Create jurisdiction name variable, same as county_name for this state
         jurisdiction_name = toupper(county_name),
         
         # Add jurisdiction_fips later (will be same as county_fips)
         
         # Create candidate name variable, make everything upper case
         candidate = toupper(candidate),
         candidate = case_when(str_detect(candidate, "FOR THE PROPOSITION") ~ "PROPOSITION FOR",
                               str_detect(candidate, "AGAINST THE PROPOSITION") ~ "PROPOSITION AGAINST",
                               str_detect(candidate, "UNDER VOTES") |
                                 str_detect(candidate, "BLANK VOTED") ~ "UNDERVOTES",
                               str_detect(candidate, "OVER VOTES") |
                                 str_detect(candidate, "OVER VOTED") ~ "OVERVOTES",
                               str_detect(candidate, "OTHER WRITE-INS")~ "WRITEIN",
                               candidate == "WILLIAM BILLY WALTERS" ~ "WILLIAM \"BILLY\" WALTERS",
                               candidate == "RICHARD DICK SMITH" ~ "RICHARD \"DICK\" SMITH",
                               candidate == "ISAAC YITZY SCHLEIFER" ~ "ISAAC \"YITZY\" SCHLEIFER",
                               candidate == "ROQUE ROCKY DE LA FUENTE" ~ "ROQUE \"ROCKY\" DE LA FUENTE",
                               TRUE ~ toupper(candidate)),
         candidate = case_when(str_detect(candidate, ",") ~ gsub("\\,", "", candidate),
                               TRUE ~ candidate),
         candidate = case_when(str_detect(candidate, ".") ~ gsub("\\.", "", candidate),
                               TRUE ~ candidate),
         candidate = gsub("\\(", "\"", candidate),
         candidate = gsub("\\)", "\"", candidate),
         candidate = gsub(' \'', " \"", candidate),
         candidate = gsub('\' ', "\" ", candidate),
         candidate = gsub("\'", "", candidate),
         candidate = gsub('  ', " ", candidate),
         candidate = trimws(candidate),
         
         # Create district variable -- based on structure of each race name
         # First take last element of COUNTY COMMISSIONER race values, make sure it retains character class; add padding
         district = case_when(office=="US PRESIDENT" ~ "STATEWIDE",
                              office=="US SENATE" ~ "STATEWIDE",
                              TRUE ~ Office.District),
        district = case_when(str_detect(district, "0") & nchar(district) == 2 ~ paste0("0", district),
                             TRUE ~ district),
         
         # Create dataverse variable; values based on race names
         dataverse = case_when(str_detect(office, "US SENATE") ~ "senate",
                               str_detect(office, "US HOUSE") ~ "house",
                               str_detect(office, "US PRESIDENT") ~ "president",
                               str_detect(office, "STATE SENATE") |
                                 str_detect(office, "STATE HOUSE") ~ "state",
                               str_detect(office, "SOLAR DEVICES") ~ "state",
                               str_detect(office, "JUDGE") ~ "state",
                               str_detect(office, "CLERK OF THE CIRCUIT COURT") ~ "state",
                               str_detect(office, "STATE ATTORNEY") ~ "state",
                               str_detect(office, "SUPERVISOR OF ELECTIONS") ~ "state",
                               str_detect(office, "PUBLIC DEFENDER") ~ "state",
                               str_detect(office, "STATE COMMITTEEMAN") ~ "local",
                               str_detect(office, "CIRCUIT COURT CLERK") ~ "state",
                               TRUE ~ "local"), # assign "local" to all others
         dataverse = toupper(dataverse),
         # Assign year
         year = 2020,
         
         # Assign stage
         stage = "GEN",
         
         # Assign state
         state = "Maryland",
         
         # Assign special; check on Ballotpedia -- nothing for OK
         special = FALSE,
         
         # Assign writein; checked candidate names and other variables, nothing to suggest writein candidates
         writein = case_when(Write.In. == "Y" ~ TRUE,
                             TRUE ~ FALSE),
         
         # Assign state_po
         state_po = "MD",
         
         # Assign state_fips
         state_fips = 24,
         
         # Assign state_cen
         state_cen = 52,
         
         # Assign state_ic
         state_ic = 52,
         
         date = as.Date("11/03/2020", "%m/%d/%Y"),
         
         #Add on magnitude field (03/29/21)
         magnitude = 1,
         # 
         # Assign readme_check; no problems with data here
         readme_check = FALSE) %>%
  
         
         
  
  # Append on county fips codes using county-fips-codes.csv file, merging on state and county_name
  # Check if county_fips column doesn't have any missing values
  
  # After county name fix, append on fips codes
  left_join(read.csv("/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/help-files/county-fips-codes.csv"),
            by = c("state", "county_name")) %>%
  mutate(county_fips = case_when(county_name=="ST MARY'S" ~ as.integer(24037),
                   TRUE ~ county_fips)) %>%
  # # Assign jurisdiction_fips (same as county_fips)
  
  mutate(jurisdiction_fips = county_fips) %>%
  # mutate(jurisdiction_fips = county_fips) %>%
  mutate(state = toupper(state)) %>%
  
  mutate(party_detailed = case_when(str_detect(office, "JUDGE") ~ "NONPARTISAN",
                                    TRUE ~ party_detailed),
         party_simplified = case_when(str_detect(office, "JUDGE") ~ "NONPARTISAN",
                                      TRUE ~ party_simplified),) %>%
  # Now select relevant variables, in order
  select(precinct, office, party_detailed, party_simplified, mode, votes, county_name, county_fips, jurisdiction_name,
         jurisdiction_fips, candidate, district, dataverse, year, stage, state, special, writein, state_po, state_fips,
         state_cen, state_ic, date, readme_check, magnitude)

#fixing magnitude and special 3/30/21 Declan Chin
md$special = ifelse((md$district =='007')&(md$office=='US HOUSE'), TRUE,md$special)
md$magnitude = ifelse((md$county_name =='FREDERICK')&(md$office=='BOARD OF EDUCATION'), 3,md$magnitude)


md <- subset(md, md$mode != "Total.Votes" & md$mode != "Total.Votes.Against")
md <- subset(md, !is.na(md$votes))
# unique(fl$race_description)
# unique(fl$office[is.na(fl$votes)])
# unique(fl$dataverse[str_detect(fl$office, "STATE ATTORNEY")])
# unique(fl$candidate[str_detect(fl$candidate, "\\\\")])
# unique(fl$elec_date[fl$candidate=="MICHAEL MIKE HAVARD"])
# 
# unique(fl$candidate)

#unique(fl$votes)


# # Run through checks
# nrow(fl) # number of rows
# names(fl) # names of variables
# length(names(fl)) # should be 24 variables
# head(ok) # look at first six rows of cleaned data frame
for(i in names(md)){print(i); print(unique(md[[i]]))} # print out unique values for every variable and inspect
# length(unique(ok$county_name)) # look up right unique county number
# length(unique(ok$jurisdiction_name)) # look up right unique county number (though not for certain states; see codebook)
# summary(ok$votes) # check for oddities (should be numeric, no missing values, etc.)
# View(unique(ok$candidate)) # inspet unique candidate names for any oddities
# # check if dataverse is coded correctly
#for(i in c("senate", "house", "state", "local")){print(paste0(i, "----------------")); print(unique(fl$office[fl$dataverse==i]))}
# # quickly check over aggregated results (closer inspection will be done by data quality checkers)
# ok %>%
#   group_by(office, district, dataverse, candidate, party_detailed, writein, special, mode) %>%
#   summarize(votes = sum(votes, na.rm = T)) %>%
#   View()

# Now write out data file
# Set location for outputted clean dataset; place in right folder and follow right naming ("2018-xx-precinct-general.csv", where xx = lower case state initial)
filename <- "/Users/cantstopkevin/Documents/HarvardDesktop/MEDSL/github/2020-precincts/precinct/MD/2020-md-precinct-general.csv"
write.csv(x = md,
          file = filename,
          row.names = FALSE) # don't include row names


