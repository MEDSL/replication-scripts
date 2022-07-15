library(medslcleaner)
library(data.table)
library(dplyr)
library(readxl)
library(stringr)
library(lettercase)
library(tools)

stateinfo <- read.csv("~/GitHub/2018-precincts/merge_on_statecodes.csv")

ar <- read.csv("~/GitHub/2018-precincts/AR/raw/AR_precinct.csv", stringsAsFactors = FALSE)
ar <- data.table(ar)
setnames(ar, c("X", "X0", "vote_type", "county"), c("precinct", "votes", "mode", "jurisdiction"))

# Rewrite office names
ar[office %=% 'district', district := as.character(as.numeric(str_extract(office, '\\d+$')))]
ar[office %=% 'u.s. congress', office := 'US House']
ar[office %=% 'state representative', office := 'State House']
ar[office %=% 'state senat', office := 'State Senate']
ar[office %=% 'governor|attorney general|secretary of state|auditor|state treasurer|state lands|supreme court|issue no.',
   district := 'statewide']

# # Code starting to process local offices

# # The names of cities appear twice in the "office" entries corresponding to most mayors. Function to remove
# # duplicates adapted from https://stackoverflow.com/questions/20283624/removing-duplicate-words-in-a-string-in-r
# rem_dup.one <- function(x){
#   paste(trimws(unique(toTitleCase(tolower(trimws(unlist(strsplit(x,split="(?!')[[:punct:]]",fixed=F,perl=T))))))),collapse = " ")
# }
# rem_dup.vector <- Vectorize(rem_dup.one, USE.NAMES = F)
# 
# ar[office %=% 'mayor', `:=`(office = 'Mayor', district = rem_dup.vector(office %-% '(mayor)'))]

ar = assign_fixed(ar)
ar = assign_match(ar, 'governor|attorney general|secretary of state|auditor|state treasurer|state lands|supreme court|issue no.', 'state')
ar = ar[!is.na(dataverse)]

party_codes <- read.csv('~/GitHub/2018-precincts/AR/raw/summary.csv', stringsAsFactors = FALSE)[, c("choice.name", "party.name")]
colnames(party_codes) <- c("candidate", "party")
ar <- merge(as.data.frame(ar), party_codes, all.x = TRUE)
ar <- data.table(ar)

ar$party <- recode(ar$party, `Dem` = 'democratic', `DEM` = 'democratic', `IND` = 'independent', `LIB` = 'libertarian', 
                   `Lib` = 'libertarian', `REP` = 'republican', `Rep` = 'republican', `NON` = 'nonpartisan')

# Fix inconsistent candidate names
ar[candidate %=% 'leslie rutledge', candidate := 'Attorney General Leslie Rutledge']
ar[candidate %=% 'andrea lea', candidate := 'Auditor Andrea Lea']
ar[candidate %=% 'dinwidd', candidate := 'David E. Dinwiddie']
ar[candidate %=% 'asa hutchinson', candidate := 'Governor Asa Hutchinson']
ar[candidate %=% 'anothony bland', candidate := 'Anthony Bland']
ar[candidate %=% 'john thurston', candidate := 'John Thurston Commissioner of State Lands']
ar[candidate %=% 'bobbie hicks', candidate := 'Bobbi Hicks']
ar[candidate %=% 't. j. campbell', candidate := 'T.J. Campbell']
ar[candidate == 'For', candidate := 'FOR']
ar[candidate == 'Against', candidate := 'AGAINST']

ar$stage <- "gen"
ar$state_po <- "AR"
ar$special <- FALSE
ar$year <- 2018
ar$writein <- FALSE
ar[candidate %=% 'write-in', `:=`(candidate = NA, writein = TRUE)]
ar <- ar[mode != "total", ]
ar[jurisdiction %=% '_', jurisdiction := str_replace(jurisdiction, '_', ' ')]
ar[jurisdiction %=% 'st francis', jurisdiction := 'st. francis']

ar <- ar %>% left_join(stateinfo, by = 'state_po') %>% select("precinct", "office", "party", "mode", "votes", "jurisdiction",
                                                              "candidate", "district", "dataverse", "year", "stage", "state", 
                                                              "special", "writein", "state_po", "state_fips", "state_cen", "state_ic")

ar <- unique(ar)

precinct_totals = ar %>%
  group_by(office, district, candidate) %>%
  summarize(votes = sum(votes))
print(precinct_totals, n = 200, width = Inf)

# Totals don't match the official results for Ouachita and Woodruff Counties, possibly because of an error on the state's end

auditor_totals = ar %>% subset(office == "Auditor of State") %>% group_by(jurisdiction, candidate) %>% summarize(votes = sum(votes))
print(auditor_totals, n = 200)

write.csv(ar, '~/GitHub/2018-precincts/AR/2018-ar-precinct.csv', row.names = FALSE)
