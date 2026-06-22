# database.py
# Camada de acesso ao banco de dados.
# Toda comunicação com o SQLite passa por aqui — a interface gráfica
# nunca escreve SQL diretamente, ela chama métodos desta classe.
# Isso facilita manutenção: se mudar o banco, só muda este arquivo.

import sqlite3
import os
from typing import List, Optional
from models import Watch, Category

# O banco de dados fica na pasta do usuário, não na pasta do app.
# Assim os dados não somem se o usuário reinstalar o app.
DB_PATH = os.path.join(os.path.expanduser("~"), ".timekeeper", "timekeeper.db")


class Database:
    """
    Gerencia a conexão e todas as operações no banco SQLite.
    SQLite é um banco de dados que fica num único arquivo .db no computador —
    sem servidor, sem internet, sem configuração.
    """

    def __init__(self):
        # Cria a pasta ~/.timekeeper/ se não existir
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        # Conecta ao banco (cria o arquivo se não existir)
        self.conn = sqlite3.connect(DB_PATH)
        # Row factory: faz as linhas retornadas se comportarem como dicionários
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")  # Ativa chaves estrangeiras
        self._create_tables()
        self._seed_categories()

    # ── Criação das tabelas ────────────────────────────────────────────────────

    def _create_tables(self):
        """
        Cria as tabelas no banco se ainda não existirem.
        'IF NOT EXISTS' garante que isso é seguro de rodar sempre que o app abre.
        """
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL UNIQUE,
                color      TEXT NOT NULL DEFAULT '#6B7280',
                is_default INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS watches (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                brand            TEXT NOT NULL,
                model            TEXT NOT NULL,
                reference        TEXT,
                serial_number    TEXT,
                year_made        TEXT,
                origin_market    TEXT,
                category_id      INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                status           TEXT NOT NULL DEFAULT 'owned',
                movement_type    TEXT,
                caliber          TEXT,
                movement_origin  TEXT,
                case_diameter    REAL,
                case_thickness   REAL,
                case_material    TEXT,
                crystal          TEXT,
                water_resistance TEXT,
                dial_color       TEXT,
                dial_material    TEXT,
                strap_material   TEXT,
                clasp_material   TEXT,
                acquired_from    TEXT,
                acquired_date    TEXT,
                price_brl        REAL,
                price_original   REAL,
                price_currency   TEXT DEFAULT 'BRL',
                has_box          INTEGER DEFAULT 0,
                has_papers       INTEGER DEFAULT 0,
                condition        TEXT,
                last_service     TEXT,
                next_service     TEXT,
                is_insured       INTEGER DEFAULT 0,
                personal_rating  INTEGER,
                is_for_sale      INTEGER DEFAULT 0,
                notes            TEXT,
                created_at       TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS service_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                watch_id     INTEGER NOT NULL REFERENCES watches(id) ON DELETE CASCADE,
                service_date TEXT NOT NULL,
                service_type TEXT,
                performed_by TEXT,
                cost_brl     REAL,
                notes        TEXT,
                created_at   TEXT DEFAULT (datetime('now'))
            );
        """)
        self.conn.commit()

    def _seed_categories(self):
        """Insere as categorias padrão na primeira execução."""
        defaults = [
            ("Dress",    "#1E3A5F", 1),
            ("Sport",    "#1A4731", 1),
            ("Dive",     "#0F4C75", 1),
            ("Pilot",    "#2D2D2D", 1),
            ("Vintage",  "#5C3D11", 1),
            ("Casual",   "#3D2B5C", 1),
            ("Pocket",   "#4A3728", 1),
        ]
        for name, color, is_default in defaults:
            # INSERT OR IGNORE: não faz nada se a categoria já existe (UNIQUE no nome)
            self.conn.execute(
                "INSERT OR IGNORE INTO categories (name, color, is_default) VALUES (?, ?, ?)",
                (name, color, is_default)
            )
        self.conn.commit()

    # ── Categorias ─────────────────────────────────────────────────────────────

    def get_categories(self) -> List[Category]:
        """Retorna todas as categorias ordenadas por nome."""
        rows = self.conn.execute(
            "SELECT * FROM categories ORDER BY name"
        ).fetchall()
        return [Category(
            id=r["id"], name=r["name"],
            color=r["color"], is_default=bool(r["is_default"])
        ) for r in rows]

    def add_category(self, name: str, color: str) -> Category:
        cur = self.conn.execute(
            "INSERT INTO categories (name, color) VALUES (?, ?)", (name, color)
        )
        self.conn.commit()
        return Category(id=cur.lastrowid, name=name, color=color)

    def delete_category(self, category_id: int):
        self.conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()

    # ── Relógios ───────────────────────────────────────────────────────────────

    def get_watches(self, status_filter: str = None, category_id: int = None,
                    search: str = None) -> List[Watch]:
        """
        Busca relógios com filtros opcionais.
        O JOIN com categories traz o nome da categoria junto.
        """
        query = """
            SELECT w.*, c.name as category_name
            FROM watches w
            LEFT JOIN categories c ON w.category_id = c.id
            WHERE 1=1
        """
        params = []

        if status_filter:
            query += " AND w.status = ?"
            params.append(status_filter)

        if category_id:
            query += " AND w.category_id = ?"
            params.append(category_id)

        if search:
            # Busca em vários campos ao mesmo tempo
            query += """ AND (
                w.brand LIKE ? OR w.model LIKE ? OR w.reference LIKE ?
                OR w.caliber LIKE ? OR w.serial_number LIKE ? OR w.notes LIKE ?
            )"""
            term = f"%{search}%"
            params.extend([term] * 6)

        query += " ORDER BY w.created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_watch(r) for r in rows]

    def get_watch(self, watch_id: int) -> Optional[Watch]:
        """Busca um relógio específico pelo ID."""
        row = self.conn.execute(
            """SELECT w.*, c.name as category_name
               FROM watches w LEFT JOIN categories c ON w.category_id = c.id
               WHERE w.id = ?""",
            (watch_id,)
        ).fetchone()
        return self._row_to_watch(row) if row else None

    def save_watch(self, watch: Watch) -> Watch:
        """
        Insere ou atualiza um relógio.
        Se watch.id for None, é uma inserção (novo relógio).
        Se watch.id existir, é uma atualização.
        """
        data = (
            watch.brand, watch.model, watch.reference, watch.serial_number,
            watch.year_made, watch.origin_market, watch.category_id, watch.status,
            watch.movement_type, watch.caliber, watch.movement_origin,
            watch.case_diameter, watch.case_thickness, watch.case_material,
            watch.crystal, watch.water_resistance, watch.dial_color, watch.dial_material,
            watch.strap_material, watch.clasp_material, watch.acquired_from,
            watch.acquired_date, watch.price_brl, watch.price_original,
            watch.price_currency, int(watch.has_box), int(watch.has_papers),
            watch.condition, watch.last_service, watch.next_service,
            int(watch.is_insured), watch.personal_rating, int(watch.is_for_sale),
            watch.notes
        )

        if watch.id is None:
            cur = self.conn.execute("""
                INSERT INTO watches (
                    brand, model, reference, serial_number, year_made, origin_market,
                    category_id, status, movement_type, caliber, movement_origin,
                    case_diameter, case_thickness, case_material, crystal, water_resistance,
                    dial_color, dial_material, strap_material, clasp_material,
                    acquired_from, acquired_date, price_brl, price_original, price_currency,
                    has_box, has_papers, condition, last_service, next_service,
                    is_insured, personal_rating, is_for_sale, notes
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, data)
            watch.id = cur.lastrowid
        else:
            self.conn.execute("""
                UPDATE watches SET
                    brand=?, model=?, reference=?, serial_number=?, year_made=?,
                    origin_market=?, category_id=?, status=?, movement_type=?, caliber=?,
                    movement_origin=?, case_diameter=?, case_thickness=?, case_material=?,
                    crystal=?, water_resistance=?, dial_color=?, dial_material=?,
                    strap_material=?, clasp_material=?, acquired_from=?, acquired_date=?,
                    price_brl=?, price_original=?, price_currency=?, has_box=?, has_papers=?,
                    condition=?, last_service=?, next_service=?, is_insured=?,
                    personal_rating=?, is_for_sale=?, notes=?
                WHERE id=?
            """, data + (watch.id,))

        self.conn.commit()
        return watch

    def delete_watch(self, watch_id: int):
        self.conn.execute("DELETE FROM watches WHERE id = ?", (watch_id,))
        self.conn.commit()

    # ── Estatísticas ───────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Retorna números para o painel de estatísticas."""
        owned = self.conn.execute(
            "SELECT COUNT(*) FROM watches WHERE status = 'owned'"
        ).fetchone()[0]

        wishlist = self.conn.execute(
            "SELECT COUNT(*) FROM watches WHERE status = 'wishlist'"
        ).fetchone()[0]

        total_brl = self.conn.execute(
            "SELECT COALESCE(SUM(price_brl), 0) FROM watches WHERE status = 'owned'"
        ).fetchone()[0]

        avg_rating = self.conn.execute(
            "SELECT AVG(personal_rating) FROM watches WHERE status = 'owned' AND personal_rating IS NOT NULL"
        ).fetchone()[0]

        by_movement = self.conn.execute("""
            SELECT movement_type, COUNT(*) as n
            FROM watches WHERE status = 'owned' AND movement_type IS NOT NULL
            GROUP BY movement_type ORDER BY n DESC
        """).fetchall()

        return {
            "owned": owned,
            "wishlist": wishlist,
            "total_brl": total_brl or 0,
            "avg_rating": round(avg_rating, 1) if avg_rating else None,
            "by_movement": [(r["movement_type"], r["n"]) for r in by_movement],
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _row_to_watch(self, row) -> Watch:
        """Converte uma linha do banco num objeto Watch."""
        r = dict(row)
        return Watch(
            id=r["id"], brand=r["brand"], model=r["model"],
            reference=r.get("reference"), serial_number=r.get("serial_number"),
            year_made=r.get("year_made"), origin_market=r.get("origin_market"),
            category_id=r.get("category_id"), category_name=r.get("category_name"),
            status=r.get("status", "owned"),
            movement_type=r.get("movement_type"), caliber=r.get("caliber"),
            movement_origin=r.get("movement_origin"),
            case_diameter=r.get("case_diameter"), case_thickness=r.get("case_thickness"),
            case_material=r.get("case_material"), crystal=r.get("crystal"),
            water_resistance=r.get("water_resistance"),
            dial_color=r.get("dial_color"), dial_material=r.get("dial_material"),
            strap_material=r.get("strap_material"), clasp_material=r.get("clasp_material"),
            acquired_from=r.get("acquired_from"), acquired_date=r.get("acquired_date"),
            price_brl=r.get("price_brl"), price_original=r.get("price_original"),
            price_currency=r.get("price_currency", "BRL"),
            has_box=bool(r.get("has_box")), has_papers=bool(r.get("has_papers")),
            condition=r.get("condition"),
            last_service=r.get("last_service"), next_service=r.get("next_service"),
            is_insured=bool(r.get("is_insured")),
            personal_rating=r.get("personal_rating"),
            is_for_sale=bool(r.get("is_for_sale")),
            notes=r.get("notes"), created_at=r.get("created_at"),
        )

    def close(self):
        self.conn.close()
