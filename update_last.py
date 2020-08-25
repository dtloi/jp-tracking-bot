import datetime

from numpy import long



def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return long(unix_time(dt) * 1000.0)

def update_last(row_id: str, last_item: str, session):
    update_last = session.prepare(
        """
        Update query Set last_item = ?, update_date = ? where id = ?
        """)
    session.execute(update_last, [last_item, unix_time_millis(datetime.datetime.now()), row_id])
    return
