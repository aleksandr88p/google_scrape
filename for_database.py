from mysql.connector import connect, Error
import csv

config = {
    'user': 'user_google_api',
    'password': 'mY@we$omeP@$$w0rd',
    'host': '185.51.121.22',
    'database': 'for_google_api',
    'port': '3306'
}
#
#
#
# create_table_query = """
# CREATE TABLE Locations (
#     CriteriaID INT,
#     Name VARCHAR(255),
#     CanonicalName TEXT,
#     ParentID INT,
#     CountryCode VARCHAR(5),
#     TargetType VARCHAR(255),
#     Status VARCHAR(255),
#     CountryName VARCHAR(255),
#     GoogleDomain VARCHAR(255),
#     Gl VARCHAR(5),
#     Hl VARCHAR(5)
# );
# """
# try:
#     with connect(**config) as connection:
#         print(connection)
#         with connection.cursor() as cursor:
#             cursor.execute(create_table_query)
# except Error as e:
#     print(e)

# def process_row(row):
#     return [value if value else None for value in row]
#
# try:
#     with connect(**config) as connection:
#         with connection.cursor() as cursor:
#             with open('locations.csv', 'r') as file:
#                 csv_reader = csv.reader(file)
#                 next(csv_reader)  # Пропускаем заголовок
#                 c = 0
#                 for row in csv_reader:
#                     print(row)
#                     c += 1
#                     processed_row = process_row(row)
#                     cursor.execute("""
#                         INSERT INTO Locations
#                         (CriteriaID, Name, CanonicalName, ParentID, CountryCode,
#                         TargetType, Status, CountryName, GoogleDomain, Gl, Hl)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                     """, processed_row)
#                 print(c)
#         connection.commit()
# except Error as e:
#     print(e)
#
# except Error as e:
#     print(e)