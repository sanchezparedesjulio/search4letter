from constants import *


def search4vowels(word: str) -> set:
    """ Return any vowels found in word"""
    vowels = set('aeiou')
    return vowels.intersection(set(word))


def search4letters(phrase: str, letters: str = 'aeiou') -> set:
    """ Return any letters found in phrase """
    return set(letters).intersection(set(phrase))


def log_request(req: 'flask_request', res: str) -> None:
    """ logger for web operations """

    dbconfig = {'host': '127.0.0.1',
                'user': 'root',
                'password': '1234',
                'database': 'search_log', }
    import mysql.connector
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """insert into log
        (phrase, letters, ip, browser_string, results)
        values
        (%s, %s, %s, %s, %s)"""
    cursor.execute(_SQL, (req.form["phrase"], req.form["letters"],
                          req.remote_addr,
                          str(req.user_agent), res,))
    conn.commit()
    cursor.close()
    conn.close()
    """
    with open(LOG_FILE_PATH, 'a') as log:
        print(req.form["phrase"], req.form["letters"],
              req.remote_addr,
              req.user_agent, res,
              file=log, sep=LOG_FILE_SEPARATOR)"""
