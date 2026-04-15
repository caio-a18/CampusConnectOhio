-- Author: Tommaso Beretta

CREATE VIEW UserSummary AS                                                                                                                      
  SELECT                                                                                                                                          
      u.UserID,                                                                                                                                   
      u.Name,                                                                                                                                     
      u.Email,                                              
      u.GPA,
      u.SATScore,
      u.ACTScore,
      u.PreferredState,                                                                                                                           
      COUNT(ss.InstitutionID) AS SavedSchoolCount
  FROM UserProfile u                                                                                                                              
  LEFT JOIN SavedSchools ss ON u.UserID = ss.UserID         
  GROUP BY u.UserID, u.Name, u.Email, u.GPA, u.SATScore, u.ACTScore, u.PreferredState;

CREATE VIEW UserSchoolMatches AS                                                                                                                
  SELECT                                                    
      u.UserID,
      u.Name        AS UserName,
      i.InstitutionID,
      i.Name        AS SchoolName,                                                                                                                
      s.StateCode
  FROM UserProfile u                                                                                                                              
  JOIN Accepts a ON (u.GPA IS NULL      OR a.MinGPA <= u.GPA)
                AND (u.SATScore IS NULL  OR a.MinSAT <= u.SATScore)                                                                               
                AND (u.ACTScore IS NULL  OR a.MinACT <= u.ACTScore)                                                                               
  JOIN Institution i ON a.InstitutionID = i.InstitutionID                                                                                         
  JOIN isIn ii       ON i.InstitutionID = ii.InstitutionID                                                                                        
  JOIN State s       ON ii.StateCode = s.StateCode;