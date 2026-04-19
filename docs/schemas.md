<!-- Author: tommaso beretta -->

Institution(<u>InstitutionId</u>, Name, Type, Size, WebsiteURL)

Program(<u>ProgramCode</u>, ProgramName, Field)

State(<u>StateCode</u>, StateName, Region)

UserProfile(<u>UserID</u>, Name, Email, Password, GPA, SATScore, ACTScore, PreferredState)

isIn(<u>InstitutionID</u>, StateCode)

Offers(<u>InstitutionID</u>, <u>ProgramCode</u>)

SavedSchools(<u>InstitutionID</u>, <u>UserId</u>, SavedDate)

Costs_Tuition(<u>InstitutionID</u>, TuitionInState, TuitionOutOfState, RoomAndBoard)

Accepts_Assessments(<u>InstitutionId</u>, MinGPA, MinSAT, MinACT)