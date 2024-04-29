-- Query per controllare se ci sono domande con nessuna variante associata
SELECT 
    d.*
FROM 
    webapp_domande d
LEFT JOIN 
    webapp_varianti v ON d."idDomanda" = v.domanda_id
WHERE 
    v."idVariante" IS NULL;
