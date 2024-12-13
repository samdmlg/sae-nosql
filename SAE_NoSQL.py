# Importation des modules utilis√©s
import sqlite3
import pandas

# Cr√©ation de la connexion
conn = sqlite3.connect("ClassicModel.sqlite")


customers = pandas.read_sql_query("SELECT * FROM Customers;", conn)
print(customers)

# Lister les clients n’ayant jamais effecuté une commande

liste_clients_sans_achats = pandas.read_sql_query(
    """
    SELECT customerNumber, customerName
    FROM Customers
    WHERE customerNumber NOT IN (SELECT customerNumber FROM Orders);
    """, conn)
                                 
print("requête 1\n",liste_clients_sans_achats)

# Pour chaque employé, le nombre de clients, le nombre de commandes et le montant total de celles-ci ;

requete_2 = pandas.read_sql_query(
    """
    SELECT 
    e.employeeNumber,
    e.firstName,
    e.lastName,
    COUNT(DISTINCT c.customerNumber) AS nombre_clients,
    COUNT(o.orderNumber) AS nombre_commandes,
    COALESCE(SUM(od.quantityOrdered * od.priceEach), 0) AS montant_total_commandes
    FROM 
    Employees e
    LEFT JOIN Customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    LEFT JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    GROUP BY 
    e.employeeNumber, e.firstName, e.lastName
    ORDER BY 
    e.employeeNumber;

    """,conn)
    
print("requête 2\n",requete_2)  

# pour chaque bureau
#(nombre de clients, nombre de commandes et montant total),
#avec en plus le nombre de clients d‚Äôun pays diff√©rent, s‚Äôil y en a

requete_3 = pandas.read_sql_query(
    """
    Select
    o.officeCode,
    o.country,
    c.customerNumber,
    c.customerName,
    count(DISTINCT c.customerNumber) AS Nombre_de_clients,
    count(DISTINCT ord.orderNumber) AS Nombre_de_commandes,
    SUM(p.amount) AS Montant_total,
    COUNT(DISTINCT CASE WHEN c.country <> o.country THEN c.customerNumber END) AS nombre_clients_pays_different
    FROM offices o
    LEFT JOIN Employees e ON o.officeCode= e.officeCode
    LEFT JOIN Customers c  ON e.employeeNumber= c.salesRepEmployeeNumber
    LEFT JOIN Orders ord  ON c.customerNumber= ord.customerNumber
    LEFT JOIN Payments p  ON ord.customerNumber= p.customerNumber
    GROUP BY o.officeCode, o.country;
   
   
    """,conn)

print("requête 3\n",requete_3)

# Pour chaque produit, donner le nombre de commandes, la quantité totale commandée, et le nombre de clients différents ;

requete_4 = pandas.read_sql_query(
    """
    SELECT 
    p.productCode,
    p.productName,
    COUNT(DISTINCT o.orderNumber) AS nombre_commandes,
    SUM(od.quantityOrdered) AS quantite_totale_commandee,
    COUNT(DISTINCT o.customerNumber) AS nombre_clients_differents
    FROM 
    Products p
    JOIN OrderDetails od ON p.productCode = od.productCode
    JOIN Orders o ON od.orderNumber = o.orderNumber
    GROUP BY 
    p.productCode, p.productName
    ORDER BY 
    p.productCode;

    """,conn)
    
print("requête 4\n",requete_4)

#Donner le nombre de commande pour chaque pays du client,
#ainsi que le montant total des commandes et le montant total pay√©
# : on veut conserver les clients n‚Äôayant jamais command√©
#dans le r√©sultat final


requete_5 = pandas.read_sql_query(
    """
    SELECT
    c.country AS pays_client,
    c.customerNumber,
    c.customerName,
    COUNT(DISTINCT ord.orderNumber) AS nombre_commandes,
    SUM(p.amount) AS Montant_total,
    SUM(orddeta.quantityOrdered * orddeta.priceEach) AS Montant_total_commandes
    FROM Customers c
    LEFT JOIN Orders ord  ON c.customerNumber= ord.customerNumber
    LEFT JOIN Payments p  ON c.customerNumber= p.customerNumber
    LEFT JOIN OrderDetails orddeta  ON ord.orderNumber= orddeta.orderNumber
   GROUP BY c.country;
    """,conn)

print("requête 5\n",requete_5)


# On veut la table de contigence du nombre de commande 
# entre la ligne de produits et le pays du client 
requete_6 = pandas.read_sql_query(
    """
    SELECT 
    c.country AS pays_client,
    p.productLine AS ligne_produit,
    COUNT(DISTINCT o.orderNumber) AS nombre_commandes
    FROM 
    Customers c
    JOIN Orders o ON c.customerNumber = o.customerNumber
    JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    JOIN Products p ON od.productCode = p.productCode
    GROUP BY c.country, p.productLine
    ORDER BY c.country, p.productLine;
    """
    ,conn)


print("requête 6\n",requete_6)


# On veut la m√™me table croisant la ligne de produits et le pays du client, 
# mais avec le montant total pay√© dans chaque cellule

requete_7 = pandas.read_sql_query(
    """
    SELECT
    
    c.country AS pays_client,
    p.productLine AS ligne_produit,
    SUM(pay.amount) AS Montant_total
    FROM 
    Customers c
    JOIN Orders o ON c.customerNumber = o.customerNumber
    JOIN OrderDetails od ON o.orderNumber = od.orderNumber
    JOIN Products p ON od.productCode = p.productCode
    LEFT JOIN Payments pay  ON c.customerNumber= pay.customerNumber
    GROUP BY c.country, p.productLine
    ORDER BY c.country, p.productLine;
    
    """
    ,conn)


print("requête 7\n",requete_7)



# Donner les 10 produits pour lesquels la marge moyenne est la plus importante
# (cf buyPrice et priceEach)

requete_8 = pandas.read_sql_query(
    """
    SELECT 
    p.productCode, 
    p.productName, 
    AVG(od.priceEach - p.buyPrice) AS marge_moyenne
    FROM 
    Products p
    JOIN OrderDetails od ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY marge_moyenne DESC
    LIMIT 10;

    """
    ,conn)


print("requête 8\n",requete_8)



# Lister les produits (avec le nom et le code du client) qui ont √©t√© vendus √† perte :
### - Si un produit a √©t√© dans cette situation plusieurs fois,  
###  il doit appara√Ætre plusieurs fois,
### - Une vente √† perte arrive quand le prix de vente est inf√©rieur au prix d‚Äôachat ;


requete_9 = pandas.read_sql_query(
    """
    SELECT 
    c.customerNumber, 
    c.customerName, 
    p.productCode, 
    p.productName, 
    od.priceEach, 
    p.buyPrice
    FROM 
    OrderDetails od
    JOIN Products p ON od.productCode = p.productCode
    JOIN Orders o ON od.orderNumber = o.orderNumber
    JOIN Customers c ON o.customerNumber = c.customerNumber
    WHERE 
    od.priceEach < p.buyPrice;

    """
    ,conn)

print("requête 9\n",requete_9)



#  Lister les clients pour lesquels le montant total pay√© est sup√©rieur
# aux montants totals des achats ;

requete_10 = pandas.read_sql_query(
    """
    SELECT 
    c.customerNumber, 
    c.customerName, 
    SUM(p.amount) AS montant_total_paye,
    SUM(od.quantityOrdered * od.priceEach) AS montant_total_achats
    FROM 
    Customers c
    LEFT JOIN Payments p ON c.customerNumber = p.customerNumber
    LEFT JOIN Orders o ON c.customerNumber = o.customerNumber
    LEFT JOIN  OrderDetails od ON o.orderNumber = od.orderNumber
    GROUP BY c.customerNumber, c.customerName
    HAVING SUM(p.amount) > SUM(od.quantityOrdered * od.priceEach);
    
    """
    ,conn)

print("requête 10\n",requete_10)

# Fermeture de la connexion : IMPORTANT √† faire dans un cadre professionnel
conn.close()