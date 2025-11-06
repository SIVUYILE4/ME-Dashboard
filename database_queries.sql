-- SQL Queries for Policy Performance Dashboard
-- Database: Quill on CL-JHB-SQL-01
-- Date: November 2025

-- ============================================================================
-- SALES QUERY
-- Gets new business sales (not upgrades) by month and product category
-- ============================================================================
SELECT 
  Count(distinct PM.PolicyMasterID) as Policies, 
  ProductionPeriod as Period, 
  ProductCategoryDescription as ProductType
FROM 
  vw_ssrs_sales_1 SV 
  INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
WHERE 
  NewBusinessWithUpgradeSale = 1 
  AND ProductCategoryID NOT IN (8, 11) 
  AND ProductionPeriod IS NOT NULL
  AND ProductionPeriod >= '2024-1' 
GROUP BY 
  ProductionPeriod, 
  ProductCategoryDescription
ORDER BY
  ProductionPeriod DESC,
  ProductCategoryDescription;

-- ============================================================================
-- REINSTATEMENTS QUERY
-- Gets policy reinstatements by month and product category
-- ============================================================================
select 
  Count(distinct PM.PolicyMasterID) as Policies, 
  CONCAT(YEAR(PM.Reinstdate), '-', MONTH(PM.Reinstdate)) as Period, 
  ProductCategoryDescription ProductType 
from 
  vw_ssrs_sales_1 SV 
  inner join PolicyMaster PM on PM.PolicyMasterID = SV.PolicyMasterID 
where productcategoryid not in (8, 11) 
AND SV.ProductionPeriod >= '2024-1' 
AND PM.Reinstdate IS NOT NULL
group by 
  CONCAT(
    YEAR(PM.Reinstdate), 
    '-', 
    MONTH(PM.Reinstdate)
  ), 
  ProductCategoryDescription;

-- ============================================================================
-- LAPSES QUERY
-- Gets lapsed and cancelled policies by month, status, and product category
-- ============================================================================
SELECT 
  COUNT(DISTINCT PM.PolicyMasterID) AS Policies, 
  PM.Status, 
  CONCAT(
    YEAR(PM.StatusDate), 
    '-', 
    RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
  ) AS Period, 
  ProductCategoryDescription AS ProductType 
FROM 
  vw_ssrs_sales_1 SV 
  INNER JOIN PolicyMaster PM ON PM.PolicyMasterID = SV.PolicyMasterID 
WHERE 
  PM.Status IN ('Auto-Lapse', 'Cancelled') 
  AND ProductCategoryID NOT IN (8, 11) 
  AND sv.newbusinesswithupgradesale = 1
GROUP BY 
  PM.Status, 
  CONCAT(
    YEAR(PM.StatusDate), 
    '-', 
    RIGHT('0' + CAST(MONTH(PM.StatusDate) AS VARCHAR(2)), 2)
  ), 
  ProductCategoryDescription
ORDER BY
  Period DESC,
  PM.Status,
  ProductCategoryDescription;

-- ============================================================================
-- SUMMARY OF QUERIES
-- ============================================================================
-- Sales Query:
--   - Uses ProductionPeriod (when policy was sold)
--   - Filters: NewBusinessWithUpgradeSale = 1 (new business only)
--   - Excludes: ProductCategoryID 8 and 11
--   - Date range: From 2024-1 onwards
--   - Groups by: Period and ProductType
--
-- Reinstatements Query:
--   - Uses Reinstdate (when policy was reinstated)
--   - Filters: PM.Reinstdate IS NOT NULL
--   - Excludes: ProductCategoryID 8 and 11
--   - Date range: From 2024-1 onwards
--   - Groups by: Period and ProductType
--
-- Lapses Query:
--   - Uses StatusDate (when policy lapsed/cancelled)
--   - Filters: PM.Status IN ('Auto-Lapse', 'Cancelled')
--   - Excludes: ProductCategoryID 8 and 11
--   - Additional filter: sv.newbusinesswithupgradesale = 1
--   - Groups by: Status, Period, and ProductType
