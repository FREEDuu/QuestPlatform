import random
from django.db import connection
from collections import namedtuple
from datetime import datetime, timedelta


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

def get_user_media():
    with connection.cursor() as cursor:
        #calcola la media di quell'utente
        cursor.execute("""

        """)
        result_set = cursor.fetchall()
    return result_set
#tutti_test = Test.objects.select_related('utente').filter(dataOraFine__isnull=False).exclude(Q(tipo="sfida") | Q(tipo__startswith="collettivo")).order_by('-dataOraInizio')
def get_user_test_info():
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH conteggioDomande as (
                SELECT 
                    test_id,
                    COUNT(*) as "nrDomande"
                FROM 
                    webapp_test_domande_varianti
                GROUP BY
                    test_id
            )
            SELECT 
                auth_user.username, 
                webapp_test."idTest", 
                webapp_test."dataOraFine", 
                webapp_test."dataOraInizio", 
                webapp_test."nrGruppo", 
                conteggioDomande."nrDomande",
                webapp_test."numeroErrori", 
                webapp_test."malusF5"
            FROM 
                webapp_test
            JOIN 
                auth_user ON webapp_test.utente_id = auth_user.id
            JOIN 
                conteggioDomande ON conteggioDomande.test_id = webapp_test."idTest"
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


def get_users_tests_week_and_mean():
    with connection.cursor() as cursor:
        cursor.execute("""
            select
                auth_user.username,
                COUNT(*) as test_count,
                case
                    when
                    to_char(AVG((cast(extract(epoch from ("dataOraFine" - "dataOraInizio")) as double precision) )),
                    'FM999999999.00') 
                        is null then '0'
                    else to_char(AVG((cast(extract(epoch from ("dataOraFine" - "dataOraInizio")) as double precision) )),
                    'FM999999999.00')
                end as time_difference_in_seconds
            from
                auth_user
            left join webapp_test 
                on (
                webapp_test.utente_id = auth_user.id
                and webapp_test."dataOraFine" is not null
                and webapp_test."dataOraFine" >= date_trunc('week', CURRENT_DATE)
                )
            where
                auth_user.id not in (1, 2, 3)
            group by
                auth_user.username
            order by
                test_count desc, time_difference_in_seconds asc
        """)
        result_set = cursor.fetchall()
    return result_set 


def get_weekly_test_count(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            select
                COUNT(*) as test_count
            from
                auth_user
            left join webapp_test 
                on ( webapp_test.utente_id = auth_user.id )
            where
                auth_user.id = %s
                and webapp_test."dataOraFine" is not null
                and webapp_test."dataOraFine" >= date_trunc('week', CURRENT_DATE);
            """, [user_id])
        result_set = cursor.fetchall()
    return result_set 

###

### CONTROLLO COLLETTIVI


def get_risultati_collettivo(dataTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH UltimiTest AS (
                SELECT
                    t."idTest",
                    t."utente_id",
                    t."tipo",
                    t."dataOraInizio",
                    t."dataOraFine",
                    t."numeroErrori",
                    ROW_NUMBER() OVER (PARTITION BY t."utente_id" ORDER BY t."dataOraFine" DESC) AS row_num
                FROM
                    webapp_test t
                WHERE
                    t."tipo" LIKE 'collettivo_finito%'
            )
            SELECT
                u.id,
                u.username,
                lt."idTest",
                lt."dataOraInizio",
                lt."dataOraFine",
                lt."numeroErrori",
                EXTRACT(EPOCH FROM (lt."dataOraFine" - lt."dataOraInizio")) AS duration_seconds
            FROM
                UltimiTest lt
            JOIN
                auth_user u ON u.id = lt."utente_id"
            WHERE
                lt.row_num = 1
                AND date_trunc('day', lt."dataOraInizio") = date %s; 
        """, [dataTest])

        columns = [col[0] for col in cursor.description]
        TestCollettivo = namedtuple('TestCollettivo', columns)
        
        results = [TestCollettivo(*row) for row in cursor.fetchall()]
        return results



###


def get_user_mean(user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            with Ultimi_100 as (
            Select
                *
            from
                webapp_test
            where
                webapp_test.utente_id = %s
                and webapp_test."dataOraFine" is not null
            order by
                webapp_test."dataOraFine" DESC
            limit 100
            )
                SELECT 
                case
                    WHEN
                    to_char(AVG((cast(extract(epoch FROM ("dataOraFine" - "dataOraInizio")) as double precision) )),
                    'FM999999999.00') 
                IS NULL then '0'
                    else to_char(AVG((cast(extract(epoch FROM ("dataOraFine" - "dataOraInizio")) as double precision) )),
                    'FM999999999.00')
                end AS time_difference_in_seconds
            FROM
                auth_user
            LEFT JOIN 
                Ultimi_100 ON
                Ultimi_100.utente_id = auth_user.id
            WHERE
                auth_user.id = %s
            group by
                auth_user.username
    """,[user_id, user_id])
            result_set = cursor.fetchall()
        return result_set[0][0] 
        
# HOME
def ensure_statistiche_entries(user_id):
    with connection.cursor() as cursor:
        # Define the types you need to ensure exist
        types = ['stelle', 't', 's', 'r']
        for type in types:
            cursor.execute("""
                INSERT INTO webapp_statistiche (utente_id, "tipoDomanda", "nrErrori")
                SELECT %s, %s, 0
                WHERE NOT EXISTS (
                    SELECT 1 FROM webapp_statistiche
                    WHERE utente_id = %s AND "tipoDomanda" = %s
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
        return result[0] if result else 0  


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


###STATISTICHE###
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
                        WHEN 'cr' THEN 4
                        when 'm' THEN 5
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
    
    
def check_statistica_esistente(tipoDomanda, utente_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM webapp_statistiche
            WHERE "tipoDomanda" = %s AND utente_id = %s
        """, [tipoDomanda, utente_id])
        result = cursor.fetchone()
        
        if result[0] > 0:
            return True
        else:
            return False


def bulk_update_statistiche(updates):
    if updates:
        with connection.cursor() as cursor:
            cursor.executemany("""
                UPDATE webapp_statistiche
                SET "nrErrori" = "nrErrori" + 1
                WHERE utente_id = %s AND "tipoDomanda" = %s;
            """, updates)

def bulk_insert_nuova_statistica(new_stats):
    if new_stats:
        with connection.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO webapp_statistiche (utente_id, "tipoDomanda", "nrErrori")
                VALUES (%s, %s, 1);
            """, new_stats)

def bulk_update_test_numero_errori(test_ids):
    if test_ids:
        with connection.cursor() as cursor:
            cursor.executemany("""
                UPDATE webapp_test
                SET "numeroErrori" = "numeroErrori" + 1
                WHERE "idTest" = %s;
            """, [(test_id,) for test_id in test_ids])
            
def insert_nuova_statistica(user_id, type):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO webapp_statistiche (utente_id, "tipoDomanda", "nrErrori")
            SELECT %s, %s, 0
            WHERE NOT EXISTS (
                SELECT 1 FROM webapp_statistiche
                WHERE utente_id = %s AND "tipoDomanda" = %s
            );
        """, [user_id, type, user_id, type])
        
def update_incrementa_statistica(user_id, type):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE webapp_statistiche
            SET "nrErrori" = "nrErrori" + 1
            WHERE utente_id = %s AND "tipoDomanda" = %s;
        """, [user_id, type])
###



### TEST

def get_test_to_render(idTest, displayer):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
            	d."idDomanda",
            	d.corpo as "corpoDomanda",
            	d.tipo,
            	v."idVariante",
            	v.corpo as "corpoVariante",
            	v."rispostaEsatta"
            FROM webapp_test_domande_varianti tdv
            JOIN webapp_domande d ON tdv.domanda_id = d."idDomanda"
            JOIN webapp_varianti v ON tdv.variante_id = v."idVariante"
            WHERE tdv.test_id = %s AND tdv."nrPagina" = %s
            ORDER BY tdv.id;
        """, [idTest, displayer])

        columns = [col[0] for col in cursor.description]
        TestToRender = namedtuple('TestToRender', columns)
        
        results = [TestToRender(*row) for row in cursor.fetchall()]
        return results
    
    
def get_test_details(idTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "nrGruppo", "dataOraInizio", "inSequenza"
            FROM webapp_test
            WHERE "idTest" = %s
            LIMIT 1;
        """, [idTest])
        result = cursor.fetchone()
        return {
            'nrGruppo': result[0],
            'dataOraInizio': result[1],
            'inSequenza': result[2]
        } if result else None

###

def media_delle_medie():
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH user_last_100_tests AS (
                SELECT 
                    webapp_test.utente_id,
                    webapp_test."dataOraFine",
                    webapp_test."dataOraInizio",
                    ROW_NUMBER() OVER (PARTITION BY webapp_test.utente_id ORDER BY webapp_test."dataOraFine" DESC) AS row_num
                FROM 
                    webapp_test
                WHERE 
                    webapp_test."dataOraFine" IS NOT NULL
            ),
            last_100_tests_per_user AS (
                SELECT 
                    utente_id,
                    "dataOraFine",
                    "dataOraInizio"
                FROM 
                    user_last_100_tests
                WHERE 
                    row_num <= 100
            ),
            average_time_per_user AS (
                SELECT 
                    utente_id,
                    AVG(EXTRACT(EPOCH FROM ("dataOraFine" - "dataOraInizio"))) AS avg_time_seconds
                FROM 
                    last_100_tests_per_user
                GROUP BY 
                    utente_id
            )
            SELECT 
                to_char(AVG(avg_time_seconds), 'FM999999999.00') AS overall_average_time_in_seconds
            FROM 
                average_time_per_user
            WHERE 
                utente_id NOT IN (1, 2, 3);
""")
        result = cursor.fetchall()
        return result


### PRETESTORARIO ###
def get_tests_group_details(idGruppi):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "nrTest", "secondiRitardo", "dataOraInizio", "nrGruppo"
            FROM webapp_testsgroup
            WHERE "idGruppi" = %s;
        """, [idGruppi])
        result = cursor.fetchone()
        if result:
            return {
                'nrTest': result[0],
                'secondiRitardo': result[1],
                'dataOraInizio': result[2],
                'nrGruppo': result[3]
            }
        return None


def get_test_details(idTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "secondiRitardo", "dataOraInizio", "nrGruppo"
            FROM webapp_test
            WHERE "idTest" = %s;
        """, [idTest])
        result = cursor.fetchone()
        if result:
            return {
                'secondiRitardo': result[0],
                'dataOraInizio': result[1],
                'nrGruppo': result[2]
            }
        return None


def update_test_dataOraInizio(idTest, new_time):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE webapp_test
            SET "dataOraInizio" = %s
            WHERE "idTest" = %s;
        """, [new_time, idTest])

def update_testsgroup_dataOraInizio(idGruppi, new_time=None):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE webapp_testsgroup
            SET "dataOraInizio" = %s
            WHERE "idGruppi" = %s;
        """, [new_time, idGruppi])


### CREAZIONETESTORARIO ###


def get_filtered_domande():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "idDomanda", corpo, "dataOraInserimento", tipo, "numeroPagine", attivo 
            FROM webapp_domande
            WHERE "numeroPagine" = -1 AND attivo = TRUE AND tipo != 'cr';
        """)
        result = cursor.fetchall()
        return result

def update_tests_group_nrGruppo(idGruppi):
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE webapp_testsgroup
            SET "nrGruppo" = "nrGruppo" + 1
            WHERE "idGruppi" = %s;
        """, [idGruppi])
        
def create_new_test(user_id):
    now = datetime.now()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO webapp_test (utente_id, "nrGruppo", "inSequenza", "tipo", "secondiRitardo", "dataOraInserimento", "nrTest", "malusF5", "numeroErrori")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, [user_id, random.randint(2, 3), False, "manuale", 1, now, 0, False, 0])
        row = cursor.fetchone()
        if row:
            test_data = {
                'idTest': row[0],
                'nrGruppo': row[4],
            }
            return test_data
        return None

def create_new_test_sfida(user_id, nrGruppo):
    now = datetime.now()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO webapp_test (utente_id, "nrGruppo", "inSequenza", "tipo", "secondiRitardo", "dataOraInserimento", "nrTest", "malusF5", "numeroErrori")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, [user_id, nrGruppo, False, "sfida", 1, now, 0, False, 0])
        row = cursor.fetchone()
        if row:
            test_data = {
                'idTest': row[0],
                'nrGruppo': row[4],
            }
            return test_data
        return None
    
def get_filtered_domande():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "idDomanda", corpo, "dataOraInserimento", tipo, "numeroPagine", attivo 
            FROM webapp_domande
            WHERE "numeroPagine" = -1 AND attivo = TRUE AND tipo != 'cr';
        """)
        domande = cursor.fetchall()
        return domande
    
def get_filtered_domande_cr():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "idDomanda", corpo, "dataOraInserimento", tipo, "numeroPagine", attivo 
            FROM webapp_domande
            WHERE "numeroPagine" = -1 AND attivo = TRUE AND tipo = 'cr';
        """)
        domande_cr = cursor.fetchall()
        return domande_cr
    
def get_varianti_for_domande(domanda_ids):
    if not domanda_ids:
        return []
    
    with connection.cursor() as cursor:
        # Ensure domanda_ids is a tuple
        cursor.execute("""
            SELECT "idVariante", domanda_id, corpo, "dataOraInserimento", "rispostaEsatta"
            FROM webapp_varianti
            WHERE domanda_id IN %s;
        """, [tuple(domanda_ids)])
        varianti = cursor.fetchall()
        return varianti

    
def bulk_create_test_domande_varianti(test_id, domanda_id, variante_id, nrPagina):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO webapp_test_domande_varianti (test_id, domanda_id, variante_id, "nrPagina")
            VALUES (%s, %s, %s, %s);
        """, [test_id, domanda_id, variante_id, nrPagina])
###



### FINISHTESTORARIO ###
def get_test_end_data(idTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "dataOraFine", "malusF5"
            FROM webapp_test
            WHERE "idTest" = %s;
        """, [idTest])
        return cursor.fetchone()

def update_test_end_time(idTest, end_time=None):
    if end_time is None:
        end_time = datetime.now()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE webapp_test
            SET "dataOraFine" = %s
            WHERE "idTest" = %s;
        """, [end_time, idTest])

def get_test_times(idTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "dataOraFine", "dataOraInizio"
            FROM webapp_test
            WHERE "idTest" = %s;
        """, [idTest])
        return cursor.fetchone()

def update_test_end_time_with_malus(idTest, end_time):
    malus_seconds = 5
    new_end_time = end_time + timedelta(seconds=malus_seconds)
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE webapp_test
            SET "dataOraFine" = %s
            WHERE "idTest" = %s;
        """, [new_end_time, idTest])
    return new_end_time


###



### TEST COLLETTIVI/PROGRAMMATI ###

def get_nr_gruppo(idTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "nrGruppo"
            FROM webapp_test
            WHERE "idTest" = %s;
        """, [idTest])
        row = cursor.fetchone()
        return row[0] if row else None

def get_test_domande_varianti(idTest, nrPagina):
    with connection.cursor() as cursor:
        cursor.execute("""
            select
                d."idDomanda",
                d.corpo as "corpoDomanda",
                d.tipo,
                d."numeroPagine",
                v."idVariante",
                v.corpo as "corpoVariante",
                v."rispostaEsatta"
            from
                webapp_test_domande_varianti tdv
            join webapp_domande d on
                tdv.domanda_id = d."idDomanda"
            join webapp_varianti v on
                tdv.variante_id = v."idVariante"
            where
                tdv.test_id = %s and tdv."nrPagina" = %s
            order by
                tdv.id;
        """, [idTest, nrPagina])
        columns = [col[0] for col in cursor.description]
        TestToRender = namedtuple('TestToRender', columns)
        
        results = [TestToRender(*row) for row in cursor.fetchall()]
        return results


def get_test_data(idTest):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT "nrGruppo", "dataOraInizio"
            FROM webapp_test
            WHERE "idTest" = %s;
        """, [idTest])
        row = cursor.fetchone()
        return dict(zip([col[0] for col in cursor.description], row)) if row else None


###