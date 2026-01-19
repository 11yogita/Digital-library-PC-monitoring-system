import sqlite3

# Create or connect to the database
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    roll_no TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')

# Sample student data
students = [
    ('1', 'prachi bhilare'),
    ('2', 'mayank disale'),
    ('3', 'sujay gawari'),
    ('4', 'aditya mathpati'),
    ('5', 'yogita khose'),
    ('6', 'darshana gurav'),
    ('7', 'pranjal patil'),
    ('8', 'komal patil'),
    ('9', 'komal kumari'),
]

# Insert data
cursor.executemany("INSERT OR IGNORE INTO students VALUES (?, ?)", students)
conn.commit()
conn.close()

print("✅ students.db created successfully with 5 students.")
