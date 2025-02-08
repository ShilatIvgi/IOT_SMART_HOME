import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QListWidget, QLabel
from PyQt5.QtCore import QTimer

# SQLite database file
DB_FILE = 'mqtt_data.db'

# Function to get the latest sensor data
def get_latest_sensor_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT trashCanID, value, timestamp
    FROM sensor_data s1
    WHERE timestamp = (
        SELECT MAX(timestamp)
        FROM sensor_data s2
        WHERE s2.trashCanID = s1.trashCanID
    )
    ORDER BY trashCanID
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Function to get all alerts
def get_all_alerts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT trashCanID, message, timestamp FROM alerts ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

class SensorDataApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sensor Data and Alerts")
        self.setGeometry(100, 100, 600, 400)

        # Layout for the window
        layout = QVBoxLayout()

        # Table for displaying the latest sensor data
        self.sensor_data_table = QTableWidget(self)
        self.sensor_data_table.setColumnCount(3)
        self.sensor_data_table.setHorizontalHeaderLabels(['Trash Can ID', 'Value', 'Timestamp'])
        layout.addWidget(self.sensor_data_table)

        # List for displaying alerts
        self.alert_list = QListWidget(self)
        layout.addWidget(QLabel("Alerts:"))
        layout.addWidget(self.alert_list)

        # Set up the timer to refresh the data every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(5000)  # Update every 5 seconds

        # Set the layout for the main window
        self.setLayout(layout)

        # Initial data population
        self.refresh_data()

    def refresh_data(self):
        # Get the latest sensor data and alerts
        latest_sensor_data = get_latest_sensor_data()
        all_alerts = get_all_alerts()

        # Update the sensor data table
        self.sensor_data_table.setRowCount(len(latest_sensor_data))
        for row_idx, row in enumerate(latest_sensor_data):
            trashCanID, value, timestamp = row
            self.sensor_data_table.setItem(row_idx, 0, QTableWidgetItem(trashCanID))
            self.sensor_data_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))
            self.sensor_data_table.setItem(row_idx, 2, QTableWidgetItem(timestamp))

        # Update the alerts list
        self.alert_list.clear()
        for alert in all_alerts:
            alert_message = f"Trash Can ID: {alert[0]} - {alert[1]} at {alert[2]}"
            self.alert_list.addItem(alert_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and display the application window
    window = SensorDataApp()
    window.show()

    # Run the application's event loop
    sys.exit(app.exec_())
