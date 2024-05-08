-- Query per controllare se ci sono domande con nessuna variante associata
SELECT 
    d.*
FROM 
    webapp_domande d
LEFT JOIN 
    webapp_varianti v ON d."idDomanda" = v.domanda_id
WHERE 
    v."idVariante" IS NULL;


-- (step 1) Query per vedere test con durata anomala (400+ secondi)
SELECT *
FROM webapp_test
WHERE 
    "dataOraFine" IS NOT NULL AND
    "dataOraInizio" IS NOT NULL AND
    EXTRACT('epoch' FROM ("dataOraFine" - "dataOraInizio")) > 400;


-- (step 2) Query per eliminare associazioni su webapp_test_domande_varianti. Necessaria prima di eliminare dalla tabella test. Modifica le condizioni a piacimento
DELETE FROM webapp_test_domande_varianti
WHERE test_id IN (
    SELECT "idTest"
    FROM webapp_test
    WHERE 
        "dataOraFine" IS NOT NULL AND
        "dataOraInizio" IS NOT NULL AND
        EXTRACT('epoch' FROM ("dataOraFine" - "dataOraInizio")) > 400
);


-- (step 3) Query per eliminare i test ormai senza nessuna associazione
DELETE FROM webapp_test
WHERE 
    "dataOraFine" IS NOT NULL AND
    "dataOraInizio" IS NOT NULL AND
    EXTRACT('epoch' FROM ("dataOraFine" - "dataOraInizio")) > 400;



-- Seleziona tutti i test con ancora dataOraFine NULL e più di 1 giorno di tempo dall'inizio (test inutili da eliminare?)
SELECT webapp_test.*, auth_user.username
FROM webapp_test
join auth_user ON auth_user.id  = webapp_test.utente_id 
WHERE 
    "dataOraInizio" IS NOT NULL 
    AND "dataOraFine" IS NULL 
    AND "dataOraInizio" <= CURRENT_DATE - INTERVAL '1 day'
ORDER BY "dataOraInizio" desc;


-- Query per vedere domande con poche varianti associate
SELECT 
    d."idDomanda",
    MAX(d.corpo) as corpo,
    MAX(d.tipo) as tipo,
    COUNT(*)
FROM 
    webapp_domande d
JOIN 
    webapp_varianti v ON d."idDomanda" = v.domanda_id
WHERE 
    d.corpo not like '%(%' 
    AND d.tipo != 'cr'
GROUP BY 
    d."idDomanda" having COUNT(*) <= 3
