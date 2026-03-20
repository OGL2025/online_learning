# wipe_neon_clean.py
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Wiping Neon database...")
    # 1. Drop the schema (deletes ALL tables/data)
    db.session.execute(text("DROP SCHEMA public CASCADE;"))
    print("Schema dropped.")
    
    # 2. Recreate the schema (fresh empty container)
    db.session.execute(text("CREATE SCHEMA public;"))
    print("Schema created.")
    
    # 3. Restore permissions (Crucial for Neon)
    db.session.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    db.session.execute(text("GRANT ALL ON SCHEMA public TO neondb_owner;"))
    
    db.session.commit()
    print("Database wiped clean and ready for fresh data.")