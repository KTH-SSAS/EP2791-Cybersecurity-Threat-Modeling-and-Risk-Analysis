### Yacraf Phase 1 relations:

Stage 1, Activity 1 -list of business requirements/use cases
S1, A2 -list how assets need to comply with rules and regulations. (An “inverse” loss, non-compliance lead to loss..)
S1, A3 -describe the impact of confidentiality, integrity, and availability + compliance breaches per asset.
S1, A4 -List People/process/technology vulnerabilities (inherent risk) -Quite unclear structure and purpose. Not really addressed in Yacraf.

### Yacraf Phase 2 relations:

Corresponds to stage 2 (Definition of Technical Scope) and stage 3 (Application Decomposition). Overall Yacraf and PASTA are well aligned here. 
Step 1 -Listing data and functions corresponds to roughly to stage 2 activities 1, 3, 4, 5.
Step 1 -Accounts and authorization corresponds roughly to stage 2 activity 2 and stage 3 activity 1.
Step 2 -Corresponds to stage 3 activities 2 and 3.

### Yacraf Phase 3 relations:

Step 1 -corresponds roughly to stage 4 activities 1, 2, 3, 6. (Stage 4 activity 4 is not considered in Yacraf since it is more related to vulnerabilities and system. Phase 3 focus is on the attackers.)
Step 2 -corresponds roughly to stage 4 activity 5 and partly stage 5 activity 3.

### Yacraf Phase 4 relations:

Step 1 -Corresponds roughly to stage 5 activity 1 and 2.
Step 2 -Corresponds roughly to stage 5 activity 3 and stage 6 activities 1, 3, and 4 (However in 4 impact is not assigned in phase 1).
S5;A4 -PASTA wants to make a risk weighted scoring. This is wrong in relation to Yacraf (since this depends on attack aggregations (coming in Phase 5). Only local difficulty is what should be assigned.
S5;A5 -Scanning and pentest. out of scope -unless ethical hacking is included.
S6;A2 -Build your own attack library. -Don’t (normally)! Use Attack libraries as source of inspiration rather than maintaining this yourself. S6;A5 -Counter measure testing is out of scope.
S6;A6 –Pentest is out of scope (for this course).

### Yacraf Phase 5 relations:

S7;A1 -Calculate overall risk for base case. (This includes several abuse cases/threats that needs to be summarized).
S7;A2 -Identify countermeasures. Component based and architecture based. (Removing vulnerabilities/weaknesses is a form of countermeasure. sometimes we explicitly give these countermeasures names a treat them as official countermeasure, e.g. patching, other times we just remove things, remove account.)
S7;A3 -Devise a number of scenarios and calculate risk for them. (Defense effectiveness cannot be calculated in isolation, it depend on the attack vector. Thus defenses constitute different scenarios). Defenses are either architectural or component based.
S7;A4 -The conclusion what is your recommendation in terms of future security development/implementation.