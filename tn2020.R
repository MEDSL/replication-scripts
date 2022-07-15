library(stringi)
library(stringr)
library(haven)
library(foreign)
library(readxl)
library(data.table)
library(tidyr)
library(tidyverse)
options(stringsAsFactors = FALSE)

tn <- read_excel("~/GitHub/2020-precincts/precinct/TN/raw/Nov2020PrecinctDetail.xlsx")
tn <- as.data.frame(tn)
newdf1 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME1, party = tn$PARTY1, votes = tn$PVTALLY1)
newdf2 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME2, party = tn$PARTY2, votes = tn$PVTALLY2)
newdf3 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME3, party = tn$PARTY3, votes = tn$PVTALLY3)
newdf4 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME4, party = tn$PARTY4, votes = tn$PVTALLY4)
newdf5 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME5, party = tn$PARTY5, votes = tn$PVTALLY5)
newdf6 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME6, party = tn$PARTY6, votes = tn$PVTALLY6)
newdf7 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME7, party = tn$PARTY7, votes = tn$PVTALLY7)
newdf8 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME8, party = tn$PARTY8, votes = tn$PVTALLY8)
newdf9 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME9, party = tn$PARTY9, votes = tn$PVTALLY9)
newdf10 <- data.frame(county = tn$COUNTY, precinct = tn$PRECINCT, office = tn$OFFICENAME, date = tn$ELECTDATE, candidate = tn$RNAME10, party = tn$PARTY10, votes = tn$PVTALLY10)
tn <- do.call("rbind", list(newdf1, newdf2, newdf3, newdf4, newdf5, newdf6, newdf7, newdf8, newdf9, newdf10))
tn$districtoffice <- tn$office
tn <- tn %>%

         # Create new variables
  mutate(precinct = precinct,
         # Clean RaceName variable in raw data to create office variable
         # Fix names, make sure districts are not a part of office for big ones, etc.
         # For later dataverse coding, checked court races in Montana and found district races should be state -- code office and district accordingly
         race_description = toupper(office),
         race_description = trimws(race_description),
         office = case_when(str_detect(race_description, "PRESIDENT") ~ "US PRESIDENT",
                            str_detect(race_description, "UNITED STATES HOUSE OF REPRESENTATIVES") ~ "US HOUSE",
                            str_detect(race_description, "UNITED STATES SENATE") ~ "US SENATE",
                            str_detect(race_description, "TENNESSEE HOUSE OF REPRESENTATIVES") ~ "STATE HOUSE",
                            str_detect(race_description, "TENNESSEE SENATE") ~ "STATE SENATE",
                            TRUE ~ race_description),
         office = case_when(str_detect(office, ",") ~ gsub("\\,", "", office),
                            TRUE ~ office),
         office = case_when(str_detect(office, ".") ~ gsub("\\.", "", office),
                            TRUE ~ office),
         office = trimws(office),
         
         
         
         # For local-level races, less important to parse information
         # (E.g. leave entirety of "COUNTY COMMISSIONER - DISTRICT 3" in office variable)
         # TRUE ~ toupper(race_description)) # everything else keeps the same office value in RaceName
         
         # Clean PartyCode to create party variables
         
         party_detailed = case_when(party == "Republican" ~ "REPUBLICAN",
                                    party == "Independent" ~ "INDEPENDENT",
                                    party == "Democratic" ~ "DEMOCRATIC",
                                    TRUE ~ party),
         party_detailed = case_when(is.na(party_detailed) ~ "NONPARTISAN",
                                    TRUE ~ party_detailed),
         party_simplified = party_detailed,
         
         # Votes are broken down by voting mode
         
         
         mode = "TOTAL",
         votes = case_when(votes=="NULL" ~ as.integer(0),
                           TRUE ~ as.integer(votes)),
         # Create county name variable
         county_name = county,
         county_name = toupper(county_name),
         county_name = case_when(str_detect(county_name, ".") ~ gsub("\\.", "", county_name),
                                 TRUE ~ county_name),
         
         # Add county_fips later, after this mutate() command and after creating state name (necessary in the merging)
         
         # Create jurisdiction name variable, same as county_name for this state
         jurisdiction_name = toupper(county_name),
         
         # Add jurisdiction_fips later (will be same as county_fips)
         
         # Create candidate name variable, make everything upper case
         candidate = toupper(candidate),
         writein = case_when(str_detect(candidate, "WRITE-IN") ~ TRUE,
                             TRUE ~ FALSE),
         candidate = case_when(candidate == "SABI (DOC) KUMAR" ~ "SABI \"DOC\" KUMAR",
                               TRUE ~ toupper(candidate)),
         candidate = case_when(str_detect(candidate, ",") ~ gsub("\\,", "", candidate),
                               TRUE ~ candidate),
         candidate = case_when(str_detect(candidate, ".") ~ gsub("\\.", "", candidate),
                               TRUE ~ candidate),
         candidate = gsub("WRITE-IN - ", "", candidate),
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
                              str_detect(districtoffice, "District") ~ sub(".*District ", "", districtoffice),
                              TRUE ~ districtoffice),
         district = case_when(nchar(district) == 2 ~ paste0("0", district),
                              nchar(district) == 1 ~ paste0("00", district),
                              TRUE ~ district),
         
         # Create dataverse variable; values based on race names
         dataverse = case_when(str_detect(office, "US SENATE") ~ "senate",
                               str_detect(office, "US HOUSE") ~ "house",
                               str_detect(office, "PRESIDENT") ~ "president",
                               str_detect(office, "STATE SENATE") |
                                 str_detect(office, "STATE HOUSE") ~ "state",
                               str_detect(office, "SOLAR DEVICES") ~ "state",
                               str_detect(office, "CIRCUIT JUDGE") ~ "state",
                               str_detect(office, "CLERK OF THE CIRCUIT COURT") ~ "state",
                               str_detect(office, "STATE ATTORNEY") ~ "state",
                               str_detect(office, "SUPERVISOR OF ELECTIONS") ~ "state",
                               str_detect(office, "PUBLIC DEFENDER") ~ "state",
                               str_detect(office, "STATE COMMITTEEMAN") ~ "local",
                               str_detect(office, "CIRCUIT COURT CLERK") ~ "state",
                               TRUE ~ "local"), # assign "local" to all others
         
         # Assign year
         year = 2020,
         
         # Assign stage
         stage = "gen",
         
         # Assign state
         state = "Tennessee",
         
         # Assign special; check on Ballotpedia -- nothing for OK
         special = FALSE,
         
         # Assign writein; checked candidate names and other variables, nothing to suggest writein candidates
         # writein = case_when(Write.In. == "Y" ~ TRUE,
         #                     TRUE ~ FALSE),
         
         # Assign state_po
         state_po = "TN",
         
         # Assign state_fips
         state_fips = 47,
         
         # Assign state_cen
         state_cen = 62,
         
         # Assign state_ic
         state_ic = 54,
         
         date = as.Date("11/03/2020", "%m/%d/%Y"),
         # 
         # Assign readme_check; no problems with data here
         readme_check = FALSE) %>%
  
  
  
  # Append on county fips codes using county-fips-codes.csv file, merging on state and county_name
  # Check if county_fips column doesn't have any missing values
  
  # After county name fix, append on fips codes
  left_join(read.csv("~/GitHub/primary-precincts/help-files/county-fips-codes.csv"),
            by = c("state", "county_name")) %>%
  mutate(county_fips = case_when(county_name=="ST MARY'S" ~ as.integer(24037),
                                 TRUE ~ county_fips)) %>%
  # # Assign jurisdiction_fips (same as county_fips)
  
  mutate(jurisdiction_fips = county_fips) %>%
  # mutate(jurisdiction_fips = county_fips) %>%
  
  # Now select relevant variables, in order
  select(precinct, office, party_detailed, party_simplified, mode, votes, county_name, county_fips, jurisdiction_name,
         jurisdiction_fips, candidate, district, dataverse, year, stage, state, special, writein, state_po, state_fips,
         state_cen, state_ic, date, readme_check)

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
for(i in names(tn)){print(i); print(unique(tn[[i]]))} # print out unique values for every variable and inspect
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
tn <- na.omit(tn)
filename <- "~/GitHub/2020-precincts/precinct/TN/2020-tn-precinct-general.csv"
write.csv(x = tn,
          file = filename,
          row.names = FALSE) # don't include row names


