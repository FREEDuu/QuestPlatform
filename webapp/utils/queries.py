from django.db import connection

# CONTROLLO
def get_user_test_count():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT auth_user.id, auth_user.username, COUNT(webapp_test.idTest) AS test_count
            FROM auth_user
            LEFT JOIN webapp_test ON webapp_test.utente_id = auth_user.id
            WHERE webapp_test."dataOraFine" IS NOT NULL
            GROUP BY auth_user.id
            HAVING COUNT(webapp_test.idTest) <= 100;
        """)
        result_set = cursor.fetchall()
    return result_set


#tutti_test = Test.objects.select_related('utente').filter(dataOraFine__isnull=False).exclude(Q(tipo="sfida") | Q(tipo__startswith="collettivo")).order_by('-dataOraInizio')
def get_user_test_info():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                auth_user.username, 
                webapp_test."idTest", 
                webapp_test."dataOraFine", 
                webapp_test."dataOraInizio", 
                webapp_test."nrGruppo", 
                webapp_test."nrTest", 
                webapp_test."numeroErrori", 
                webapp_test."malusF5"
            FROM 
                webapp_test
            JOIN 
                auth_user ON webapp_test.utente_id = auth_user.id
            WHERE 
                webapp_test."dataOraFine" IS NOT NULL AND 
                NOT (webapp_test.tipo = 'sfida' OR webapp_test.tipo LIKE 'collettivo%')
                AND webapp_test.utente_id NOT IN (1,2,3)
            ORDER BY 
                webapp_test."dataOraInizio" DESC;
        """)
        result_set = cursor.fetchall()
    return result_set


def get_stelle_statistics():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT auth_user.username, webapp_statistiche."nrErrori"
            FROM webapp_statistiche
            JOIN auth_user ON webapp_statistiche.utente_id = auth_user.id
            WHERE webapp_statistiche."tipoDomanda" = 'stelle'
            ORDER BY webapp_statistiche."nrErrori" DESC;
        """)
        result_set = cursor.fetchall()
    return result_set 


def get_users_tests_100():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                auth_user.username, 
                COUNT(webapp_test."idTest") AS test_count
            FROM 
                auth_user
            LEFT JOIN 
                webapp_test ON webapp_test.utente_id = auth_user.id
                    AND webapp_test."dataOraFine" IS NOT NULL
                    AND webapp_test."dataOraFine" >= date_trunc('week', CURRENT_DATE)
            GROUP BY 
                auth_user.username
            HAVING 
                COUNT(webapp_test."idTest") < 100
            ORDER BY test_count DESC;
        """)
        result_set = cursor.fetchall()
    return result_set 
###


# HOME
def ensure_statistiche_entries(user_id):
    with connection.cursor() as cursor:
        # Define the types you need to ensure exist
        types = ['stelle', 't', 's', 'r']
        for type in types:
            cursor.execute("""
                INSERT INTO webapp_statistiche (utente_id, tipoDomanda, nrErrori)
                SELECT %s, %s, 0
                WHERE NOT EXISTS (
                    SELECT 1 FROM webapp_statistiche
                    WHERE utente_id = %s AND tipoDomanda = %s
                );
            """, [user_id, type, user_id, type])

def get_stelle_errors(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nrErrori FROM webapp_statistiche
            WHERE utente_id = %s AND tipoDomanda = 'stelle'
            LIMIT 1;
        """, [user_id])
        result = cursor.fetchone()
        return result[0] if result else 0  # Default to 0 if no entry found


def get_tests_group_data(user_id, test_type):
    with connection.cursor() as cursor:
        if test_type in ['manuale', 'orario']:
            cursor.execute(f"""
                SELECT "idGruppi", "dataOraInserimento", "nrTest", "nrGruppo", "dataOraInizio", "secondiRitardo"
                FROM webapp_testsgroup
                WHERE utente_id = %s AND tipo = %s;
            """, [user_id, test_type])
        else:
            cursor.execute(f"""
                SELECT "idGruppi", "dataOraInserimento", "nrTest", "nrGruppo"
                FROM webapp_testsgroup
                WHERE utente_id = %s AND tipo = %s;
            """, [user_id, test_type])
        return cursor.fetchall()


def get_test_programmati():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "idTest", "dataOraInizio"
            FROM webapp_test
            WHERE tipo = 'collettivo';
        """)
        return cursor.fetchall()

def get_tests_group_by_type(user_id, test_type):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT webapp_testsgroup."dataOraInizio", webapp_testsgroup."idGruppi", webapp_testsgroup."nrTest"
            FROM webapp_testsgroup
            WHERE utente_id = %s AND tipo = %s;
        """, [user_id, test_type])
        return cursor.fetchall()
###


# STATISTICHE
def get_test_incompleti(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM webapp_test
            WHERE utente_id = %s
            AND "dataOraFine" IS NULL
            ORDER BY "dataOraInizio" DESC;            
        """, [user_id])
        return cursor.fetchall()
    
    
def get_numero_errori(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "nrErrori", "tipoDomanda"
            FROM webapp_statistiche
            WHERE utente_id = %s
            AND "tipoDomanda" != 'stelle'
            ORDER BY CASE "tipoDomanda"
                        WHEN 't' THEN 1
                        WHEN 's' THEN 2
                        WHEN 'c' THEN 3
                        when 'r' then 4
                    END;
        """, [user_id])
        return cursor.fetchall()

def get_errori_per_tipo(user_id, tipologia):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "nrErrori"
            FROM webapp_statistiche
            WHERE utente_id = %s
            AND "tipoDomanda" = %s
            LIMIT 1;        
        """, [user_id, tipologia])
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return 0
    
###