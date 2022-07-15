library(stringi)
library(stringr)
library(haven)
library(foreign)
library(readxl)
library(data.table)
library(tidyr)
library(tidyverse)
library(openxlsx)
options(stringsAsFactors = FALSE)

temp1 = list.files(path="/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/WY/raw/2020_Wyoming_General_Results", pattern="*County_General_PbP.xlsx")
f1 <- file.path(path="/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/WY/raw/2020_Wyoming_General_Results", pattern=temp1)
d1 <- lapply(f1, read.xlsx, fillMergedCells=TRUE, colNames=FALSE)
counties <- gsub("2020_", "", temp1)
counties <- gsub("_County_General_PbP.xlsx", "", counties)
counties <- gsub("_", " ", counties)
#df_1 <- do.call("rbind", d1)
#read.xlsx("~/GitHub/2020-precincts/precinct/WY/county_data/2020_Albany_County_General_PbP.xlsx", fillMergedCells=TRUE, header=FALSE)
clean_county <- function(wy){
  names(wy) <- paste0(wy[1,], ".banana.", wy[2,])
  wy <- wy[-1,]
  wy <- wy[-1,]
  wy <- rename(wy, precinct=NA.banana.Precinct)
  wy <- as.data.frame(pivot_longer(wy, 2:last_col(), names_to = c("race", "candidate"), names_sep=".banana."))
  #wy$county <- county
  wy
}
d2 <- lapply(d1, clean_county)
for (i in 1:length(d2)){
  d2[[i]]$county <- counties[i]
}
#d2 <- mapply(clean_county, d1, as.list(counties))
wy <- do.call("rbind", d2)

wy <- wy %>%
  mutate(candidate = gsub("\\s+", " ", candidate),
         candidate = gsub("\\.", "", candidate),
         candidate = toupper(candidate),
         
         
         party_detailed = case_when(str_detect(candidate, "\\(D\\)") ~ "DEMOCRAT",
                           str_detect(candidate, "\\(R\\)") ~ "REPUBLICAN",
                           str_detect(candidate, "\\(L\\)") ~ "LIBERTARIAN",
                           str_detect(candidate, "\\(I\\)") ~ "INDEPENDENT",
                           str_detect(candidate, "CONST") ~ "CONSTITUTION PARTY",
                           str_detect(candidate, "WRITE-INS") | str_detect(candidate, "UNDERVOTES") | str_detect(candidate, "OVERVOTES") ~ "",
                           TRUE ~ "NONPARTISAN"),
         party_simplified = case_when(party_detailed == "CONSTITUTION PARTY" ~ "OTHER",
                                      TRUE ~ party_detailed),
         
         
         candidate = gsub(" AND .+| \\(\\w+\\)", "", candidate),
         
         
         county_name = toupper(county),
         
         
         jurisdiction_name=county_name,
         
         
         office = toupper(race),
         office = case_when(str_detect(office, "PRESIDENT") ~ "US PRESIDENT",
                            str_detect(office, "UNITED STATES SENATOR") ~ "US SENATE",
                            str_detect(office, "UNITED STATES REPRESENTATIVE") ~ "US HOUSE",
                            str_detect(office, "SENATE DISTRICT") ~ "STATE SENATE",
                            str_detect(office, "HOUSE DISTRICT") ~ "STATE HOUSE",
                            TRUE ~ office),
         
         # removing code that does not specify jud candidate names along with overvotes/undervotes. Leads to quasi duplicate rows
         
         # candidate = case_when(str_detect(office, "JUDICIAL DISTRICT") & candidate != "UNDERVOTES" & candidate != "OVERVOTES" ~ paste0(gsub(".*JUDICIAL DISTRICT\\n", "", office), " - ", candidate),
         #                       TRUE ~ candidate),
         # candidate = case_when(str_detect(office, "JUSTICE OF THE SUPREME COURT") & candidate != "UNDERVOTES" & candidate != "OVERVOTES" ~ paste0(gsub("JUSTICE OF THE SUPREME COURT\\n", "", office), " - ", candidate),
         #                       TRUE ~ candidate),
         candidate = case_when(str_detect(office, "JUDICIAL DISTRICT") ~ paste0(gsub(".*JUDICIAL DISTRICT", "", office), " - ", candidate),
                               TRUE ~ candidate),
         candidate = case_when(str_detect(office, "JUSTICE OF THE SUPREME COURT") ~ paste0(gsub("JUSTICE OF THE SUPREME COURT", "", office), " - ", candidate),
                               TRUE ~ candidate),
         candidate = case_when(candidate=="FOR" ~ "FOR THE AMENDMENT",
                               candidate == "AGAINST" ~ "AGAINST THE AMENDMENT",
                               candidate == "WRITE-INS" ~ "WRITEIN",
                               TRUE ~ candidate),
         candidate = gsub("\\s+", " ", candidate),
         candidate = gsub("\\.", "", candidate),
         
         #remove candidate from office field
         office = case_when(str_detect(office, "JUDICIAL DISTRICT") ~ paste0(gsub("JUDICIAL DISTRICT.*", "", office), "JUDICIAL DISTRICT"),
                            TRUE ~ office),
         office = case_when(str_detect(office, "JUSTICE OF THE SUPREME COURT") ~ "JUSTICE OF THE SUPREME COURT",
                            TRUE ~ office),

         district = case_when(office=="US PRESIDENT" ~ "STATEWIDE",
                              office=="US SENATE" ~ "STATEWIDE",
                              office == "US HOUSE" ~ "000",
                              str_detect(office, "JUSTICE OF THE SUPREME COURT") ~ "STATEWIDE",
                              str_detect(office, "CONSTITUTIONAL AMENDMENT") ~ "STATEWIDE",
                              str_detect(race, "District") ~ sub(".*District ", "", race),
                              TRUE ~ ""),
         district = case_when(str_detect(office, "SECOND JUDICIAL") ~ "002",
                              str_detect(office, "FIFTH JUDICIAL") ~ "005",
                              str_detect(office, "EIGHTH JUDICIAL") ~ "008",
                              str_detect(office, "SIXTH JUDICIAL") ~ "006",
                              str_detect(office, "NINTH JUDICIAL") ~ "009",
                              str_detect(office, "FOURTH JUDICIAL") ~ "004",
                              str_detect(office, "FIRST JUDICIAL") ~ "001",
                              str_detect(office, "THIRD JUDICIAL") ~ "003",
                              str_detect(office, "SEVENTH JUDICIAL") ~ "007",
                              TRUE ~ district),
         district = case_when(nchar(district) == 2 ~ paste0("0", district),
                              nchar(district) == 1 ~ paste0("00", district),
                              TRUE ~ district),
         office = case_when(str_detect(office, "JUDGE") ~ paste0(gsub(",.*", "", office), ""),
                            str_detect(office, "CONSTITUTIONAL AMENDMENT") ~ "CONSTITUTIONAL AMENDMENT A DEBT LIMITS FOR MUNICIPAL SEWER PROJECTS",
                            TRUE ~ office),
        

         # Create dataverse variable; values based on race names
         dataverse = case_when(str_detect(office, "US SENATE") ~ "senate",
                               str_detect(office, "US HOUSE") ~ "house",
                               str_detect(office, "PRESIDENT") ~ "president",
                               str_detect(office, "STATE SENATE") |
                                 str_detect(office, "STATE HOUSE") ~ "state",
                               str_detect(office, "DISTRICT COURT JUDGE") ~ "state",
                               str_detect(office, "CONSTITUTIONAL AMENDMENT") ~ "state",
                               str_detect(office, "JUSTICE OF THE SUPREME COURT") ~ "state",
                               TRUE ~ "local"), # assign "local" to all others
         dataverse = toupper(dataverse),
         # Assign year
         year = 2020,
         
         # Assign stage
         stage = "GEN",
         
         # Assign state
         state = "Wyoming",
         
         # Assign special; check on Ballotpedia -- nothing for OK
         special = FALSE,
         
         # Assign writein; checked candidate names and other variables, nothing to suggest writein candidates
         # writein = case_when(Write.In. == "Y" ~ TRUE,
         #                     TRUE ~ FALSE),
         
         # Assign state_po
         state_po = "WY",
         
         # Assign state_fips
         state_fips = 56,
         
         # Assign state_cen
         state_cen = 83,
         
         # Assign state_ic
         state_ic = 68,
         
         date = as.Date("11/03/2020", "%m/%d/%Y"),
         # 
         # Assign readme_check; no problems with data here
         readme_check = FALSE,
         mode = "TOTAL",
         votes = value,
         writein = case_when(str_detect(candidate, "WRITEIN") ~ TRUE,
                             TRUE ~ FALSE)
         
  ) %>%
# Append on county fips codes using county-fips-codes.csv file, merging on state and county_name
# Check if county_fips column doesn't have any missing values

# After county name fix, append on fips codes
left_join(read.csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv"),
          by = c("state", "county_name")) %>%
  mutate(county_fips = case_when(county_name=="ST MARY'S" ~ as.integer(24037),
                                 TRUE ~ county_fips)) %>%
  # # Assign jurisdiction_fips (same as county_fips)

  mutate(jurisdiction_fips = county_fips) %>%
  
  mutate(state = toupper(state)) %>%
  # Now select relevant variables, in order
select(precinct, office, party_detailed, party_simplified, mode, votes, county_name, county_fips, jurisdiction_name,
        jurisdiction_fips, candidate, district, dataverse, year, stage, state, special, writein, state_po, state_fips,
        state_cen, state_ic, date, readme_check)
wy = subset(wy, !str_detect(wy$votes, "-"))
wy = subset(wy, !wy$precinct == "Total")
wy$magnitude = 1
wy$candidate <- trimws(wy$candidate, which = c("both"))
for(i in names(wy)){print(i); print(unique(wy[[i]]))}

filename <- "/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/WY/2020-wy-precinct-general.csv"
write.csv(x = wy,
          file = filename,
          row.names = FALSE)
