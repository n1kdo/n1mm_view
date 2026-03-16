import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('n1mm_view.db')  # Replace with your database file
cursor = conn.cursor()

# Query to join qso_log and operator tables
query = """
SELECT qso_log.*, operator.name
FROM qso_log
JOIN operator ON qso_log.operator_id = operator.id
"""
cursor.execute(query)
qsos = cursor.fetchall()

# Function to convert frequency from integer to string with MHz unit
def convert_freq(freq):
    return f"{freq / 1000000:.3f}"

# Function to convert timestamp to date and time in ADIF format
from datetime import datetime

def convert_timestamp(timestamp):
    dt = datetime.utcfromtimestamp(timestamp)
    date_str = dt.strftime('%Y%m%d')
    time_str = dt.strftime('%H%M%S')
    return date_str, time_str

# Start writing the ADIF file
with open('n1mm_view_output.adi', 'w') as f:
    # Write the ADIF header
    f.write("<ADIF_VER:5>3.0.4\n")
    f.write("<EOH>\n")

    # Write each QSO record
    for qso in qsos:
        timestamp, mycall, band_id, mode_id, operator_id, station_id, rx_freq, tx_freq, callsign, rst_sent, rst_recv, exchange, section, comment, qso_id, operator_name = qso
        
        date_str, time_str = convert_timestamp(timestamp)
        rx_freq_str = convert_freq(rx_freq)
        tx_freq_str = convert_freq(tx_freq)

        f.write(f"<QSO_DATE:{len(date_str)}>{date_str}\n")
        f.write(f"<TIME_ON:{len(time_str)}>{time_str}\n")
        f.write(f"<CALL:{len(callsign)}>{callsign}\n")
        f.write(f"<BAND:{len(str(band_id))}>{band_id}M\n")  # Assuming band_id directly translates to band string
        f.write(f"<MODE:{len(str(mode_id))}>{mode_id}\n")  # Assuming mode_id directly translates to mode string
        f.write(f"<RST_SENT:{len(rst_sent)}>{rst_sent}\n")
        f.write(f"<RST_RCVD:{len(rst_recv)}>{rst_recv}\n")
        f.write(f"<OPERATOR:{len(operator_name)}>{operator_name}\n")
        if exchange:
            f.write(f"<STX_STRING:{len(exchange)}>{exchange}\n")
        if section:
            f.write(f"<SRX_STRING:{len(section)}>{section}\n")
        if comment:
            f.write(f"<COMMENT:{len(comment)}>{comment}\n")
        f.write(f"<FREQ:{len(rx_freq_str)}>{rx_freq_str}\n")
        f.write(f"<EOR>\n")

# Close the database connection
conn.close()

