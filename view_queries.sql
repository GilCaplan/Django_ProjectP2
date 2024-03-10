-- CREATE VIEW StockDays AS
--                 SELECT Distinct Stock.tDate
--                 FROM Stock;
--

-- CREATE VIEW EachDayInvBuy AS
-- SELECT Company.Symbol
-- FROM Buying, Company
-- WHERE Buying.Symbol = Company.Symbol
-- GROUP BY Company.Symbol
-- HAVING COUNT(DISTINCT Buying.tDate) = (SELECT COUNT(*) FROM StockDays);

--
-- CREATE VIEW PopComp AS
-- SELECT Company.Symbol
-- FROM
-- (SELECT Company.Sector
-- FROM EachDayInvBuy, Company
-- WHERE EachDayInvBuy.Symbol = Company.Symbol
-- GROUP BY Company.Sector
-- HAVING COUNT(*) = 1) as Strs, Company
-- Where Company.Sector = Strs.Sector;
--
--
-- CREATE VIEW popQuantity AS
-- SELECT PopComp.Symbol, SUM(Buying.BQuantity) quantity, Buying.ID,
--        RANK() OVER (PARTITION BY PopComp.Symbol ORDER BY SUM(Buying.BQuantity) DESC) InvestorRank
-- FROM PopComp, Buying, Investor
-- WHERE PopComp.Symbol = Buying.Symbol AND Buying.ID = Investor.ID
-- GROUP BY PopComp.Symbol, Buying.ID;