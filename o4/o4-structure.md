# Ontology Structure                                        
                                          
```mermaid                                          
classDiagram    
    class PolicyHolder {    
        %% Data Properties    
        name : string    
        dateOfBirth : date    
        address : string    
        phoneNumber : string    
        %% Object Properties    
        hasPolicy 1--* Policy : one-to-many    
        files *--1 Claim : one-to-many    
    }    
    
    class Insurer {    
        %% Data Properties    
        insurerName : string    
        headquartersLocation : string    
        industryRating : float    
        %% Object Properties    
        issues 1--* Policy : one-to-many    
        handles *--1 Claim: one-to-many    
    }    
    
    class Underwriter {    
        %% Data Properties    
        name : string    
        licenseID : string    
        experienceYears : int    
        %% Object Properties    
        underwrites o--* Policy : many-to-one    
    }    
    
    class Agent {    
        %% Data Properties    
        name : string    
        agencyName : string    
        agentLicense : string    
        %% Object Properties    
        sells o--* Policy : many-to-one    
    }    
    
    class Coverage {    
        %% Data Properties    
        coverageName : string    
        coverageLimit : float    
        deductible : float    
        %% Object Properties    
        policyHas *--1 Policy : one-to-many    
    }    
    
    class Policy {    
        %% Data Properties    
        policyNumber : string    
        policyType : string    
        startDate : date    
        endDate : date    
        premiumAmount : float    
        status : string    
        %% Object Properties    
        hasPolicyHolder 1--1 PolicyHolder : one-to-one    
        issuedBy 1--1 Insurer : one-to-one    
        hasCoverage 1--* Coverage : one-to-many    
        underwrittenBy o--1 Underwriter : one-to-one    
        soldBy o--1 Agent : one-to-one    
        claimFiledFor 1--* Claim : one-to-many    
    
    }    
    
    class Claim {    
        %% Data Properties    
        claimNumber : string    
        claimDate : date    
        claimType : string    
        amountClaimed : float    
        amountSettled : float    
        status : string    
        %% Object Properties    
        filedFor 1--1 Policy : one-to-one    
        filedBy 1--1 PolicyHolder : one-to-one    
        handledBy 1--1 Insurer : one-to-one    
    }    
    
    %% Relationships    
    Policy "1..1" -- "1..1" PolicyHolder : Association (hasPolicyHolder)    
    Policy "1..1" -- "1..1" Insurer : Association (issuedBy)    
    Policy "1..*" -- "1..1" Coverage : Association (hasCoverage)    
    Policy "0..1" -- "1..1" Underwriter : Association (underwrittenBy)    
    Policy "0..1" -- "1..1" Agent : Association (soldBy)    
    Claim "1..1" -- "1..1" Policy : Association (filedFor)    
    Claim "1..1" -- "1..1" PolicyHolder : Association (filedBy)    
    Claim "1..1" -- "1..1" Insurer : Association (handledBy)                
```                             
                                        
---              
              
```pseudocode            
Class: PolicyHolder    
   - name: string    
   - dateOfBirth: date    
   - address: string    
   - phoneNumber: string    
    
Class: Insurer    
   - insurerName: string    
   - headquartersLocation: string    
   - industryRating: float    
    
Class: Underwriter    
   - name: string    
   - licenseID: string    
   - experienceYears: int    
    
Class: Agent (optional)    
   - name: string    
   - agencyName: string    
   - agentLicense: string    
    
Class: Coverage    
   - coverageName: string    
   - coverageLimit: float    
   - deductible: float    
    
Class: Policy    
   - policyNumber: string    
   - policyType: string    
   - startDate: date    
   - endDate: date    
   - premiumAmount: float    
   - status: string    
   - hasPolicyHolder -> PolicyHolder (1..1)    
   - issuedBy -> Insurer (1..1)    
   - hasCoverage -> Coverage (1..*)    
   - underwrittenBy -> Underwriter (0..1)    
   - soldBy -> Agent (0..1) // optional    
    
Class: Claim    
   - claimNumber: string    
   - claimDate: date    
   - claimType: string    
   - amountClaimed: float    
   - amountSettled: float    
   - status: string    
   - filedFor -> Policy (1..1)    
   - filedBy -> PolicyHolder (1..1)    
   - handledBy -> Insurer (1..1)    
        
```             
     