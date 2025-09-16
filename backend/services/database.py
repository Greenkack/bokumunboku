"""
Database Service (migriert aus database.py)

Diese Datei enthält die Datenbank-Funktionen aus dem ursprünglichen
Streamlit-Code, angepasst für den FastAPI-Backend-Kontext.
"""

from __future__ import annotations

import sys
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Legacy-Import-Pfad
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Legacy-Database-Module importieren
try:
    from database import (
        init_db as legacy_init_db,
        get_active_company as legacy_get_active_company,
        save_admin_setting as legacy_save_admin_setting,
        load_admin_setting as legacy_load_admin_setting,
        get_db_connection as legacy_get_db_connection
    )
    LEGACY_DATABASE_AVAILABLE = True
except ImportError as e:
    LEGACY_DATABASE_AVAILABLE = False
    print(f"Warning: Legacy database module not available: {e}")

# CRM-Module importieren
try:
    from crm import (
        save_customer as legacy_save_customer,
        save_project as legacy_save_project,
        list_customers as legacy_list_customers
    )
    LEGACY_CRM_AVAILABLE = True
except ImportError as e:
    LEGACY_CRM_AVAILABLE = False
    print(f"Warning: Legacy CRM module not available: {e}")

# Fallback-Datenbankpfad
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "app_data.db"

def init_db():
    """Datenbank initialisieren"""
    if LEGACY_DATABASE_AVAILABLE:
        try:
            legacy_init_db()
            return
        except Exception as e:
            print(f"Legacy database init failed: {e}")
    
    # Fallback: Basic database setup
    _init_fallback_db()

def get_db_connection():
    """Datenbankverbindung erhalten"""
    if LEGACY_DATABASE_AVAILABLE:
        try:
            return legacy_get_db_connection()
        except Exception as e:
            print(f"Legacy database connection failed: {e}")
    
    # Fallback: Direct SQLite connection
    return sqlite3.connect(str(DEFAULT_DB_PATH))

def get_active_company() -> Dict[str, Any]:
    """Aktive Firmeninformationen abrufen"""
    if LEGACY_DATABASE_AVAILABLE:
        try:
            return legacy_get_active_company()
        except Exception as e:
            print(f"Legacy get_active_company failed: {e}")
    
    # Fallback: Standard-Firmendaten
    return _get_default_company_info()

def save_admin_setting(key: str, value: Any) -> bool:
    """Admin-Einstellung speichern"""
    if LEGACY_DATABASE_AVAILABLE:
        try:
            return legacy_save_admin_setting(key, value)
        except Exception as e:
            print(f"Legacy save_admin_setting failed: {e}")
    
    # Fallback: In-Memory oder File-basiert
    return _save_setting_fallback(key, value)

def load_admin_setting(key: str, default: Any = None) -> Any:
    """Admin-Einstellung laden"""
    if LEGACY_DATABASE_AVAILABLE:
        try:
            return legacy_load_admin_setting(key, default)
        except Exception as e:
            print(f"Legacy load_admin_setting failed: {e}")
    
    # Fallback
    return _load_setting_fallback(key, default)

def save_customer(
    first_name: str,
    last_name: str,
    email: str,
    phone: str = "",
    address: str = "",
    city: str = "",
    postal_code: str = ""
) -> Dict[str, Any]:
    """Kunde speichern"""
    if LEGACY_CRM_AVAILABLE:
        try:
            return legacy_save_customer(
                first_name, last_name, email, phone, address, city, postal_code
            )
        except Exception as e:
            print(f"Legacy save_customer failed: {e}")
    
    # Fallback: Direct database insert
    return _save_customer_fallback(
        first_name, last_name, email, phone, address, city, postal_code
    )

def save_project(
    customer_id: int,
    project_name: str,
    notes: str = "",
    offer_type: str = "pv"
) -> Dict[str, Any]:
    """Projekt speichern"""
    if LEGACY_CRM_AVAILABLE:
        try:
            return legacy_save_project(customer_id, project_name, notes, offer_type)
        except Exception as e:
            print(f"Legacy save_project failed: {e}")
    
    # Fallback: Direct database insert
    return _save_project_fallback(customer_id, project_name, notes, offer_type)

def list_customers(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Kunden auflisten"""
    if LEGACY_CRM_AVAILABLE:
        try:
            return legacy_list_customers(limit, offset)
        except Exception as e:
            print(f"Legacy list_customers failed: {e}")
    
    # Fallback: Direct database query
    return _list_customers_fallback(limit, offset)

def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    """Kunde anhand ID abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone, address, city, postal_code, created_at
            FROM customers 
            WHERE id = ?
        """, (customer_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "address": row[5],
                "city": row[6],
                "postal_code": row[7],
                "created_at": row[8]
            }
        return None
        
    except Exception as e:
        print(f"get_customer_by_id failed: {e}")
        return None

def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Projekt anhand ID abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, customer_id, project_name, status, offer_type, notes, created_at
            FROM projects 
            WHERE id = ?
        """, (project_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "customer_id": row[1],
                "project_name": row[2],
                "status": row[3],
                "offer_type": row[4],
                "notes": row[5],
                "created_at": row[6]
            }
        return None
        
    except Exception as e:
        print(f"get_project_by_id failed: {e}")
        return None

def get_projects_by_customer_id(customer_id: int) -> List[Dict[str, Any]]:
    """Projekte eines Kunden abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, customer_id, project_name, status, offer_type, notes, created_at
            FROM projects 
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """, (customer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        projects = []
        for row in rows:
            projects.append({
                "id": row[0],
                "customer_id": row[1],
                "project_name": row[2],
                "status": row[3],
                "offer_type": row[4],
                "notes": row[5],
                "created_at": row[6]
            })
        
        return projects
        
    except Exception as e:
        print(f"get_projects_by_customer_id failed: {e}")
        return []

def list_projects_with_customers(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Projekte mit Kundendaten auflisten"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id as project_id,
                p.project_name,
                p.status,
                p.offer_type,
                p.notes,
                p.created_at as project_created_at,
                c.id as customer_id,
                c.first_name,
                c.last_name,
                c.email
            FROM projects p
            JOIN customers c ON p.customer_id = c.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        projects = []
        for row in rows:
            projects.append({
                "project_id": row[0],
                "project_name": row[1],
                "status": row[2],
                "offer_type": row[3],
                "notes": row[4],
                "project_created_at": row[5],
                "customer_id": row[6],
                "customer_name": f"{row[7]} {row[8]}",
                "customer_email": row[9]
            })
        
        return projects
        
    except Exception as e:
        print(f"list_projects_with_customers failed: {e}")
        return []

def add_customer_document(
    customer_id: int,
    project_id: Optional[int],
    document_path: str,
    document_label: str = "PDF Angebot"
) -> int:
    """Dokument zu Kunde/Projekt hinzufügen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO customer_documents (customer_id, project_id, path, label, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (customer_id, project_id, document_path, document_label))
        
        document_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return document_id
        
    except Exception as e:
        print(f"add_customer_document failed: {e}")
        return 0

def get_customer_documents(customer_id: int) -> List[Dict[str, Any]]:
    """Dokumente eines Kunden abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, project_id, path, label, created_at
            FROM customer_documents 
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """, (customer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            documents.append({
                "id": row[0],
                "project_id": row[1],
                "path": row[2],
                "label": row[3],
                "created_at": row[4]
            })
        
        return documents
        
    except Exception as e:
        print(f"get_customer_documents failed: {e}")
        return []

# Fallback-Funktionen

def _init_fallback_db():
    """Fallback-Datenbank-Initialisierung"""
    try:
        conn = sqlite3.connect(str(DEFAULT_DB_PATH))
        cursor = conn.cursor()
        
        # Basis-Tabellen erstellen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                city TEXT,
                postal_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                offer_type TEXT DEFAULT 'pv',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                project_id INTEGER,
                path TEXT NOT NULL,
                label TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("Fallback database initialized successfully")
        
    except Exception as e:
        print(f"Fallback database init failed: {e}")

def _get_default_company_info() -> Dict[str, Any]:
    """Standard-Firmeninformationen"""
    return {
        "name": "Solar Company",
        "address": "Musterstraße 1, 12345 Musterstadt",
        "email": "info@solar-company.de",
        "phone": "+49 123 456789",
        "website": "www.solar-company.de",
        "logo_path": None
    }

def _save_customer_fallback(
    first_name: str, last_name: str, email: str,
    phone: str, address: str, city: str, postal_code: str
) -> Dict[str, Any]:
    """Fallback-Kunde speichern"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Prüfen ob Kunde bereits existiert
        cursor.execute("SELECT id FROM customers WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return {
                "customer_id": existing[0],
                "message": "Kunde bereits vorhanden"
            }
        
        # Neuen Kunden erstellen
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, email, phone, address, city, postal_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, address, city, postal_code))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "customer_id": customer_id,
            "message": "Kunde erfolgreich erstellt"
        }
        
    except Exception as e:
        print(f"_save_customer_fallback failed: {e}")
        return {"customer_id": 0, "message": f"Fehler: {str(e)}"}

def _save_project_fallback(
    customer_id: int, project_name: str, notes: str, offer_type: str
) -> Dict[str, Any]:
    """Fallback-Projekt speichern"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (customer_id, project_name, notes, offer_type)
            VALUES (?, ?, ?, ?)
        """, (customer_id, project_name, notes, offer_type))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "project_id": project_id,
            "message": "Projekt erfolgreich erstellt"
        }
        
    except Exception as e:
        print(f"_save_project_fallback failed: {e}")
        return {"project_id": 0, "message": f"Fehler: {str(e)}"}

def _list_customers_fallback(limit: int, offset: int) -> List[Dict[str, Any]]:
    """Fallback-Kunden auflisten"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone, created_at
            FROM customers 
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        customers = []
        for row in rows:
            customers.append({
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "created_at": row[5]
            })
        
        return customers
        
    except Exception as e:
        print(f"_list_customers_fallback failed: {e}")
        return []

def _save_setting_fallback(key: str, value: Any) -> bool:
    """Fallback-Setting speichern"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        cursor.execute("""
            INSERT OR REPLACE INTO admin_settings (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        """, (key, value_str))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"_save_setting_fallback failed: {e}")
        return False

def _load_setting_fallback(key: str, default: Any) -> Any:
    """Fallback-Setting laden"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM admin_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            try:
                return json.loads(row[0])
            except:
                return row[0]
        
        return default
        
    except Exception as e:
        print(f"_load_setting_fallback failed: {e}")
        return default