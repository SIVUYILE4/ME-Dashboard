-- Sales Count Trend Query
-- Database: Quill on CL-JHB-SQL-01
-- Date: November 2025
-- Description: Analysis of sales trends with commission data by year, month, and personality type

DECLARE @sdate DATE = '2022-01-01';  
DECLARE @edate DATE = CAST(GETDATE() AS DATE);  

WITH CTE AS (
  SELECT 
    Year(CommissionDate) as Year, 
    Month(CommissionDate) as Month, 
    SV.ProductCategoryDescription, 
    CASE WHEN SV.IncepDate = SV.CommencementDate THEN CAST(0 as bit) ELSE CAST(1 as bit) END as InternalReplacement, 
    C.PolicyDetailID, 
    C.Type, 
    C.CommissionDate, 
    CASE WHEN SV.IncepDate = SV.CommencementDate THEN C.NewBusinessMonthlyPRemium ELSE 0 END as NewBusinessMonthlyPRemium, 
    SV.NewbusinessWithupgradeSale, 
    SV.RiderBenefit, 
    CASE 
      WHEN C.PolicyHolderID IS NOT NULL THEN 'WillURefer Incentive' 
      WHEN C.MaxLTIA = 1 THEN 'Max LTIA' 
      WHEN PM.RoleMasterId = 25 THEN 'TestementaryAgent' 
      WHEN C.IntMasterID IS NOT NULL THEN 'Intermediary' 
      WHEN C.BCMasterID IS NOT NULL THEN 'Broker Consultant' 
      WHEN C.BDMasterID IS NOT NULL THEN 'BusinessDeveloper' 
      WHEN C.FranchiseMasterID IS NOT NULL THEN 'Franchise' 
      WHEN C.TelephonistID IS NOT NULL THEN 'Teleconsultant' 
      WHEN C.FulfilmentID IS NOT NULL THEN 'Consultant' 
      ELSE P.Description 
    END AS PersonalityToUse, 
    Amount, 
    SV.CommissionRunCompleted 
  FROM 
    Commission C 
    LEFT JOIN vw_ssrs_sales_1 SV ON C.PolicyDetailID = SV.PolicyDetailID 
    LEFT JOIN IntMaster IM ON C.IntMasterID = IM.IntMasterID 
    LEFT JOIN PayrollMaster PM ON IM.EmployeeNumber = PM.EmployeeNumber 
    LEFT JOIN Personality P ON C.PersonalityTypeID = P.PersonalityID 
  WHERE 
    CAST(CommissionDate AS DATE) BETWEEN @sdate AND @edate 
    AND C.Amount <> 0 
    AND ISNULL(C.IsReserve, 0) = 0 
    AND C.Type NOT LIKE '%Benefactor%' 
    AND C.Type NOT LIKE '%Share of%' 
    AND C.Type NOT LIKE '%Book Value%' 
    AND SV.ProductCategoryID NOT IN (8, 11)
), 
CTE2 as (
  SELECT 
    Year, 
    Month, 
    ProductCategoryDescription, 
    InternalReplacement, 
    Type, 
    PersonalityToUse Personality_To_Use, 
    SUM(Amount) AS Amount, 
    PolicyDetailID, 
    MAX(
      CASE WHEN CTE.Type = 'initial' AND ISNULL(CTE.CommissionRunCompleted, 0) = 1 
      THEN NewBusinessMonthlyPremium ELSE 0 END
    ) NewBusinessMonthlyPremium, 
    MAX(
      CASE WHEN cte.NewbusinessWithupgradeSale = 1 AND Type = 'initial' THEN 1 ELSE 0 END
    ) as SalesCount_Clients, 
    MAX(
      CASE WHEN cte.RiderBenefit = 0 AND Type = 'initial' AND cte.NewBusinessMonthlyPRemium > 0 THEN 1 ELSE 0 END
    ) as SalesCount_Product 
  FROM 
    CTE 
  GROUP BY 
    ProductCategoryDescription, 
    InternalReplacement, 
    Type, 
    PersonalityToUse, 
    Year, 
    Month, 
    PolicyDetailID
), 
CTE_SS AS (
  SELECT 
    Year(CommissionDate) as Year, 
    Month(CommissionDate) as Month, 
    SV.ProductCategoryDescription, 
    CASE WHEN SV.IncepDate = SV.CommencementDate THEN CAST(0 as bit) ELSE CAST(1 as bit) END as InternalReplacement, 
    C.PolicyDetailID, 
    C.Type, 
    C.CommissionDate, 
    C.NewBusinessMonthlyPRemium, 
    CASE 
      WHEN C.AbcMasterID IS NOT NULL THEN 'ABC' 
      WHEN C.ACMasterID IS NOT NULL THEN 'AC' 
      WHEN C.ConsultantManagerID IS NOT NULL THEN 'Sales Consultant Leader' 
      WHEN C.Type = 'Retention Fee' THEN 'Retention Officer' 
      WHEN C.Type = 'WillURefer Incentive' THEN 'WillURefer Incentive' 
      WHEN C.CLDSMasterID IS NOT NULL THEN 'CLDF' 
      WHEN C.SalesManagementID IS NOT NULL AND R.name = 'Executive Manager' THEN 'New Business Executive Manager' 
      WHEN C.SalesManagementID IS NOT NULL THEN ISNULL(R.name, 'Sales Management') 
      ELSE P.Description 
    END AS PersonalityToUse, 
    Amount 
  FROM 
    SupportSalesCommissions C 
    LEFT JOIN vw_ssrs_sales_1 SV ON C.PolicyDetailID = SV.PolicyDetailID 
    LEFT JOIN Personality P ON C.PersonalityTypeID = P.PersonalityID 
    LEFT JOIN CLDSMaster CLDS ON C.CLDSMasterID = CLDS.CLDSMasterID 
    LEFT JOIN SalesManagementMaster SMM ON C.SalesManagementID = SMM.SalesManagementID 
    LEFT JOIN ConsultantManagerMaster CMM on C.ConsultantManagerID = CMM.ConsultantManagerID 
    LEFT JOIN business_information..Employees E on SMM.EmployeeNumber = E.Number COLLATE DATABASE_DEFAULT 
    LEFT JOIN business_information..roles R on E.role_id = R.ID 
  WHERE 
    CAST(CommissionDate AS DATE) BETWEEN @sdate AND @edate 
    AND C.Amount <> 0 
    AND SV.ProductCategoryID NOT IN (8, 11)
), 
CTE2_SS as (
  SELECT 
    Year, 
    Month, 
    ProductCategoryDescription, 
    InternalReplacement, 
    Type, 
    PersonalityToUse COLLATE DATABASE_DEFAULT Personality_To_Use, 
    SUM(Amount) AS Amount, 
    PolicyDetailID, 
    MAX(
      CASE WHEN CTE_SS.Type = 'initial' THEN NewBusinessMonthlyPremium ELSE 0 END
    ) NewBusinessMonthlyPremium 
  FROM 
    CTE_SS 
  GROUP BY 
    ProductCategoryDescription, 
    InternalReplacement, 
    Type, 
    PersonalityToUse COLLATE DATABASE_DEFAULT, 
    Year, 
    Month, 
    PolicyDetailID
) 
SELECT 
  Year, 
  Month, 
  ProductCategoryDescription, 
  InternalReplacement, 
  Type, 
  Personality_To_Use, 
  SUM(Amount) AS Amount, 
  SUM(NewBusinessMonthlyPremium) NewBusinessMonthlyPremium, 
  SUM(SalesCount_Clients) as SalesCount_Client, 
  SUM(SalesCount_Product) as SalesCount_Product 
FROM 
  CTE2 
WHERE Personality_To_Use = 'Max LTIA'
GROUP BY 
  ProductCategoryDescription, 
  InternalReplacement, 
  Type, 
  Personality_To_Use, 
  Year, 
  Month 
UNION 
SELECT 
  Year, 
  Month, 
  ProductCategoryDescription, 
  InternalReplacement, 
  Type, 
  Personality_To_Use, 
  SUM(Amount) AS Amount, 
  0 NewBusinessMonthlyPremium, 
  0 as SalesCount_Client, 
  0 as SalesCount_Product 
FROM 
  CTE2_SS 
WHERE Personality_To_Use = 'Max LTIA'
GROUP BY 
  ProductCategoryDescription, 
  InternalReplacement, 
  Type, 
  Personality_To_Use, 
  Year, 
  Month;
