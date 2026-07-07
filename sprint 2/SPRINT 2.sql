    -- Nivell 1
    -- Exercici 1
    -- Creamos la base de datos
    CREATE DATABASE IF NOT EXISTS transactions;
    USE transactions;

    -- Creamos la tabla company
    CREATE TABLE IF NOT EXISTS company (
        id VARCHAR(15) PRIMARY KEY,
        company_name VARCHAR(255),
        phone VARCHAR(15),
        email VARCHAR(100),
        country VARCHAR(100),
        website VARCHAR(255)
    );

    -- Creamos la tabla transaction
    CREATE TABLE IF NOT EXISTS transaction (
        id VARCHAR(255) PRIMARY KEY,
        credit_card_id VARCHAR(15) REFERENCES credit_card(id),
        company_id VARCHAR(20), 
        user_id INT REFERENCES user(id),
        lat FLOAT,
        longitude FLOAT,
        timestamp TIMESTAMP,
        amount DECIMAL(10, 2),
        declined BOOLEAN,
        FOREIGN KEY (company_id) REFERENCES company(id) 
    );
    
 -- En este punto se ha de ejecutar el archivo N1-Ex.1__dades_introduir.sql para insertar los datos de company y de transaction:
	-- ejemplo INSERT INTO company (id, company_name, phone, email, country, website) VALUES ('b-2222', 'Ac Fermentum Incorporated', '06 85 56 52 33', 'donec.porttitor.tellus@yahoo.net', 'Germany', 'https://instagram.com/site');
	-- ejemplo INSERT INTO transaction (id, credit_card_id, company_id, user_id, lat, longitude, timestamp, amount, declined) VALUES ('CDDA7E40-544D-47BB-A4ED-671DD8A950D9', 'CcS-6894', 'b-2466', '2313', '59.62050974356148', '16.559977155728436', '2018-12-12 08:05:17', '161.88', '0');


    -- Exercici 2 
    -- Utilitzant JOIN realitzaràs les següents consultes:
    
    -- Llistat dels països que estan generant vendes.
SELECT  country
FROM   transactions.company c
INNER JOIN transactions.transaction t ON c.id = t.company_id
GROUP BY country;
    

    -- Des de quants països es generen les vendes.
SELECT COUNT(DISTINCT Country) AS numero_paises
FROM   transactions.company c
INNER JOIN transactions.transaction t ON c.id = t.company_id;   

    
	-- Identifica la companyia amb la mitjana més gran de vendes.
SELECT ROUND(AVG(t.amount)) as total_ventas, company_name
FROM   transactions.company c
INNER JOIN  transactions.transaction t ON c.id = t.company_id
WHERE declined = 0
GROUP BY company_id
ORDER BY total_ventas
DESC LIMIT 1; 

-- Exercici 3
-- Utilitzant només subconsultes (sense utilitzar JOIN):

-- Mostra totes les transaccions realitzades per empreses d'Alemanya.
SELECT *
FROM transactions.transaction t
WHERE EXISTS (
    SELECT 1
    FROM company c
    WHERE c.id = t.company_id
	AND c.country = 'Germany'
);

-- Llista les empreses que han realitzat transaccions per un amount superior a la mitjana de totes les transaccions.
SELECT company_name
FROM transactions.company c
WHERE EXISTS (
    SELECT 1
    FROM transactions.transaction t
    WHERE c.id = t.company_id
	AND amount > (SELECT ROUND(AVG(t.amount)) FROM transactions.transaction t)
);

-- Eliminaran del sistema les empreses que no tenen transaccions registrades, entrega el llistat d'aquestes empreses.
-- Check:
SELECT *
FROM transactions.company c
WHERE NOT EXISTS (
    SELECT DISTINCT company_id
    FROM transactions.transaction t
    WHERE c.id = t.company_id
);

-- Exercici 4
-- La teva tasca és dissenyar i crear una taula anomenada "credit_card" que emmagatzemi detalls crucials sobre les targetes de crèdit.
-- La nova taula ha de ser capaç d'identificar de manera única cada targeta i establir una relació adequada amb les altres dues taules ("transaction" i "company").
-- Després de crear la taula serà necessari que ingressis la informació del document denominat "dades_introduir_credit". Recorda mostrar el diagrama i realitzar una breu descripció d'aquest.

-- 1. Creamos la tabla credit_card
CREATE TABLE IF NOT EXISTS credit_card (
		id VARCHAR(15) PRIMARY KEY, 
		iban VARCHAR(34), 
		pan VARCHAR(19),
		pin VARCHAR(6),
		cvv VARCHAR(4),
		expiring_date VARCHAR(10)
	);

-- 2. Creamos un trigger para convertir la fecha en formato DATE al importar los datos
DELIMITER //
CREATE TRIGGER convert_expiring_date
BEFORE INSERT ON credit_card
FOR EACH ROW
BEGIN
    SET NEW.expiring_date = STR_TO_DATE(NEW.expiring_date, '%m/%d/%y');
END//
DELIMITER ;


-- 3. En este punto se ha de ejecutar el archivo N1-Ex.4__ datos_introducir_credit.sql para insertar los datos de credit_card
-- ejemplo INSERT INTO credit_card (id, iban, pan, pin, cvv, expiring_date) VALUES ('CcU-2938', 'TR301950312213576817638661', '5424465566813633', '3257', '984', '10/30/22');


-- 4. Se establece la relacion de 1:n con la tabla transaction especificando que transaction.credit_card_id es clave foranea y apunta a credit_card.id :
ALTER TABLE transaction
ADD CONSTRAINT fk_credit_card
FOREIGN KEY (credit_card_id)
REFERENCES credit_card(id);


-- Exercici 5
-- El departament de Recursos Humans ha identificat un error en el número de compte associat a la targeta de crèdit amb ID CcU-2938.
-- La informació que ha de mostrar-se per a aquest registre és: TR323456312213576817699999. Recorda mostrar que el canvi es va realitzar.

-- Check:
SELECT * FROM transactions.credit_card
WHERE id = "CcU-2938";
-- Update:
UPDATE transactions.credit_card
SET iban = "TR323456312213576817699999"
WHERE id = "CcU-2938";
-- Re check:
SELECT * FROM transactions.credit_card
WHERE id = "CcU-2938";


-- Exercici 6
/*En la taula "transaction" ingressa una nova transacció amb la següent informació:
Id 108B1D1D-5B23-A76C-55EF-C568E49A99DD 
credit_card_id CcU-9999 
company_id b-9999 
user_id 9999 
lat 829.999 
longitude -117.999 
amount 111.11 
declined 0*/

INSERT INTO transactions.company (id) VALUES ('b-9999');
INSERT INTO transactions.credit_card (id) VALUES ('CcU-9999');
INSERT INTO transactions.transaction (id, credit_card_id, company_id, user_id, lat, longitude, timestamp, amount, declined) VALUES ('108B1D1D-5B23-A76C-55EF-C568E49A99DD', 'CcU-9999', 'b-9999', '9999', '829.999', '-117.999', NOW(), '111.11', '0');
-- Check:
SELECT * FROM transactions.transaction
WHERE credit_card_id = "CcU-9999";  


-- Exercici 7
-- Des de recursos humans et sol·liciten eliminar la columna "pan" de la taula credit_card. Recorda mostrar el canvi realitzat. 

ALTER TABLE transactions.credit_card DROP COLUMN pan;
-- Check:
SELECT * FROM transactions. credit_card 


-- Exercici 8
-- Descarrega els arxius CSV que trobaràs a l'apartat de recursos:

/*american_users.csv
european_users.csv
companies.csv
credit_cards.csv
transactions.csv
Estudia'ls i dissenya una base de dades amb un esquema d'estrella que contingui, almenys 4 taules de les quals puguis realitzar les següents consultes:
La taula de products.csv l'utilitzarem més endavant.*/     

-- Creamos la base de datos sells
CREATE DATABASE IF NOT EXISTS merchandising;

USE merchandising;

-- Creamos la tabla users
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(15) PRIMARY KEY,
        `name` VARCHAR(255),
        surname VARCHAR(255),
        phone VARCHAR(30),
        email VARCHAR(100),
        birth_date VARCHAR(30),
        country VARCHAR(100),
        city VARCHAR(100),
        postal_code VARCHAR(20),
        address VARCHAR(255),
        signup_date VARCHAR(15),
        user_segment VARCHAR(50),
        income_band	VARCHAR(15),
        continent VARCHAR(15)
    );
-- Creamos la tabla companies
    CREATE TABLE IF NOT EXISTS companies (
        company_id VARCHAR(15) PRIMARY KEY,
		company_name VARCHAR(255),
		phone VARCHAR(30),
		email VARCHAR(100),
		country VARCHAR(100),
        website VARCHAR(100),
        merchant_category VARCHAR(30),
        merchant_price_position VARCHAR(100)
	);    
-- Creamos la tabla transactions
    CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(100) PRIMARY KEY,
    card_id VARCHAR(15),
    business_id VARCHAR(15),
    timestamp TIMESTAMP,
    amount VARCHAR(30),
    declined VARCHAR(30),
    product_ids VARCHAR(30),
    user_id VARCHAR(30),
    lat VARCHAR(100),
    longitude VARCHAR(100),
    discount_amount VARCHAR(30),
    tax_amount VARCHAR(30),
    shipping_amount VARCHAR(30),
    channel VARCHAR(30),
    campaign_id VARCHAR(30),
    device_type VARCHAR(30),
    is_international VARCHAR(1),
    decline_reason VARCHAR(100),
    distance_km VARCHAR(30)
 );   
-- Creamos la tabla credit_cards
    CREATE TABLE IF NOT EXISTS credit_cards ( 
    id VARCHAR(150) PRIMARY KEY,
    user_id VARCHAR(30),
    iban VARCHAR(100),
    pan VARCHAR(30),
    pin VARCHAR(30),
    cvv VARCHAR(30),
    track1 VARCHAR(100),
    track2 VARCHAR(100),
    expiring_date VARCHAR(15),
    card_type VARCHAR(30),
    card_renewal_flag VARCHAR(30)
  );

-- En este punto se ejecutan los archivos csv correspondientes para insertar los datos de las tablas que acabamos de crear.
-- ejemplo:
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/N1-Ex.8__transactions.csv'
INTO TABLE transactions
FIELDS TERMINATED BY ';'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Se crean las relaciones entre las tablas, de 1:n, donde "1" es transactions, y "n" son las tablas companies, credit_cards y users:
ALTER TABLE merchandising.transactions
ADD CONSTRAINT fk_transactions_companies
FOREIGN KEY (business_id) REFERENCES companies(company_id),
ADD CONSTRAINT fk_transactions_credit_cards
FOREIGN KEY (card_id) REFERENCES credit_cards(id),
ADD CONSTRAINT fk_transactions_users
FOREIGN KEY (user_id) REFERENCES users(id);

-- Exercici 9
-- Realitza una subconsulta que mostri tots els usuaris amb més de 80 transaccions utilitzant almenys 2 taules.

SELECT u.id, u.`name`, u.surname
FROM users u
WHERE EXISTS (
    SELECT 1
    FROM transactions t
    WHERE t.user_id = u.id
      AND t.declined = 0
    GROUP BY t.user_id
    HAVING COUNT(t.id) > 80
);

-- Exercici 10
-- Mostra la mitjana d'amount per IBAN de les targetes de crèdit a la companyia Donec Ltd, utilitza almenys 2 taules.

SELECT cc.iban, ROUND(AVG(t.amount), 2) AS media_amount
FROM transactions t
JOIN credit_cards cc ON t.card_id = cc.id
JOIN companies c ON t.business_id = c.company_id
WHERE c.company_name = 'Donec Ltd'
AND t.declined = 0
GROUP BY cc.iban;

-- Nivell 2
-- Exercici 1
-- Identifica els cinc dies que es va generar la quantitat més gran d'ingressos a l'empresa per vendes. Mostra la data de cada transacció juntament amb el total de les vendes.

SELECT DATE(timestamp) AS dia, ROUND(SUM(amount), 2) AS ingresos
FROM transactions t
WHERE t.declined = 0
GROUP BY DATE(timestamp)
ORDER BY ingresos DESC
LIMIT 5;

-- Exercici 2
-- Presenta el nom, telèfon, país, data i amount, d'aquelles empreses que van realitzar transaccions amb un valor comprès entre 350 i 400 euros i en alguna d'aquestes dates: 29 d'abril del 2015, 20 de juliol del 2018 i 13 de març del 2024. Ordena els resultats de major a menor quantitat.

SELECT company_name, phone, country, DATE(timestamp) AS fecha, ROUND(amount, 2) AS valor
FROM   companies c
INNER JOIN  transactions t ON c.company_id = t.business_id
WHERE amount BETWEEN 350 AND 400 AND DATE(timestamp) IN ('2015-04-29','2018-07-20','2024-03-13')
ORDER BY amount DESC;

-- Exercici 3
-- Necessitem optimitzar l'assignació dels recursos i dependrà de la capacitat operativa que es requereixi, per la qual cosa et demanen la informació sobre la quantitat
-- de transaccions que realitzen les empreses, però el departament de recursos humans és exigent i vol un llistat de les empreses
-- on especifiquis si tenen igual o més de 400 transaccions o menys.

SELECT 
    t.business_id,
    COUNT(t.id) AS total_transacciones,
    CASE 
        WHEN COUNT(t.id) >= 400 THEN 'igual_o_mas_de_400'
        ELSE 'menos_de_400'
    END AS Transacciones
FROM transactions t
GROUP BY t.business_id
ORDER BY Transacciones DESC;

-- Exercici 4
-- Elimina de la taula transaction el registre amb ID 000447FE-B650-4DCF-85DE-C7ED0EE1CAAD de la base de dades.

-- Check
SELECT * FROM transactions t
WHERE id = "000447FE-B650-4DCF-85DE-C7ED0EE1CAAD";
-- Delete en la tabla transactions
DELETE FROM transactions t
WHERE id = "000447FE-B650-4DCF-85DE-C7ED0EE1CAAD";
-- Recheck
SELECT * FROM transactions t
WHERE id = "000447FE-B650-4DCF-85DE-C7ED0EE1CAAD";

-- Exercici 5
-- La secció de màrqueting desitja tenir accés a informació específica per a realitzar anàlisi i estratègies efectives.S'ha sol·licitat crear una vista que proporcioni
-- detalls clau sobre les companyies i les seves transaccions. Serà necessària que creïs una vista anomenada VistaMarketing que contingui la següent informació:
-- Nom de la companyia. Telèfon de contacte. País de residència. Mitjana de compra realitzat per cada companyia.
-- Presenta la vista creada, ordenant les dades de major a menor mitjana de compra.

CREATE VIEW VistaMarketing AS
SELECT company_name, country, phone, ROUND(AVG(t.amount), 2) as media_compras
FROM   companies c
INNER JOIN  transactions t ON c.company_id = t.business_id
GROUP BY business_id;

SELECT * FROM VistaMarketing        
ORDER BY media_compras DESC;

-- Nivell 3
-- Exercici 1
-- Crea una nova taula que reflecteixi l'estat de les targetes de crèdit basat en si les tres últimes transaccions han estat declinades aleshores és inactiu,
-- si almenys una no és rebutjada aleshores és actiu.

CREATE TABLE credit_cards_status AS
WITH orden_tarjetas AS (
    SELECT card_id, declined, `timestamp`,
        ROW_NUMBER() OVER (PARTITION BY card_id ORDER BY timestamp DESC) AS orden
    FROM transactions
)
SELECT card_id, `timestamp`,
    IF(declined = 0, 'activa', 'inactiva') AS estado_tarjeta
FROM orden_tarjetas
WHERE orden IN (1,2,3);

-- Partint d’aquesta taula respon: Quantes targetes estan actives?

SELECT COUNT(*) AS tarjetas_activas
FROM (
    SELECT card_id
    FROM credit_cards_status
    GROUP BY card_id
    HAVING COUNT(CASE WHEN estado_tarjeta = 'inactiva' THEN 1 END) < 3
) AS activas;

-- Exercici 2
-- Crea una taula amb la qual puguem unir les dades de l'arxiu de products.csv amb la base de dades creada (ja que fins ara no podíem fer-ho), 
-- tenint en compte que des de transaction tens product_ids. Genera la següent consulta: Necessitem conèixer el nombre de vegades que s'ha venut cada producte.

-- Creamos la tabla products
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(200) PRIMARY KEY,
    product_name VARCHAR(200),
    price VARCHAR(15),
    colour VARCHAR(30),
    weight VARCHAR(15),
    warehouse_id VARCHAR(15),
    category VARCHAR(200),
    brand VARCHAR(200),
    cost VARCHAR(30),
    launch_date VARCHAR(30)
 ); 
 
 -- En este punto se ejecuta el archivo csv correspondiente para insertar los datos en la tabla products
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\N1-Ex.8__products.csv'
INTO TABLE products
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Se crea una tabla intermedia entre transactions y products
CREATE TABLE transaction_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Se emparejan transaction_id con product_id con JOIN JSON_TABLE. Para ello se convierten primero los product_ids separados por comas en filas (array JSON)
INSERT INTO transaction_products (transaction_id, product_id)
SELECT 
    t.id,
    CAST(jt.product_id AS UNSIGNED)
FROM transactions t
JOIN JSON_TABLE(
        CONCAT('[', t.product_ids, ']'),
        '$[*]' COLUMNS (
            product_id VARCHAR(50) PATH '$'
        )
    ) AS jt;

-- Se extrae cuantas veces se ha vendido cada producto
SELECT product_id, COUNT(product_id) AS recuento
FROM transaction_products
GROUP BY product_id
ORDER BY COUNT(product_id) DESC;