# models.py
# Define as estruturas de dados do TimeKeeper.
# Um "model" é simplesmente uma classe que representa um objeto do mundo real —
# aqui, um relógio (Watch) e uma categoria (Category).
# Usamos @dataclass para não precisar escrever __init__ manualmente.

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Category:
    """Representa uma categoria de relógio (ex: Vintage, Dress, Sport)."""
    id: Optional[int] = None
    name: str = ""
    color: str = "#6B7280"   # Cor em hexadecimal para exibir na interface
    is_default: bool = False


@dataclass
class Watch:
    """
    Representa um relógio na coleção.
    Cada campo corresponde a uma coluna no banco de dados SQLite.
    Optional[str] significa que o campo pode estar vazio (None).
    """

    # ── Identificação ──────────────────────────────────────────
    id: Optional[int] = None
    brand: str = ""                          # Marca (obrigatório)
    model: str = ""                          # Modelo (obrigatório)
    reference: Optional[str] = None          # Número de referência (ex: L2.628.4)
    serial_number: Optional[str] = None      # Número de série
    year_made: Optional[str] = None          # Ano de fabricação (texto p/ aceitar "c.1960s")
    origin_market: Optional[str] = None      # Mercado de destino original

    # ── Categoria e status ─────────────────────────────────────
    category_id: Optional[int] = None
    category_name: Optional[str] = None      # Preenchido ao carregar do banco (JOIN)
    # Status possíveis: owned | wishlist | sold | loaned
    status: str = "owned"

    # ── Movimento ──────────────────────────────────────────────
    # Tipo: automatic | manual | quartz | solar | spring_drive | other
    movement_type: Optional[str] = None
    caliber: Optional[str] = None            # Ex: ETA 2892, Miyota 9015
    # Origem: in-house | ebauche | unknown
    movement_origin: Optional[str] = None

    # ── Caixa (case) ───────────────────────────────────────────
    case_diameter: Optional[float] = None    # Em milímetros
    case_thickness: Optional[float] = None   # Em milímetros
    case_material: Optional[str] = None      # Ex: aço inox, ouro 18k
    # Cristal: sapphire | mineral | acrylic | hesalite | other
    crystal: Optional[str] = None
    water_resistance: Optional[str] = None   # Ex: 50m, 10ATM

    # ── Mostrador (dial) ───────────────────────────────────────
    dial_color: Optional[str] = None         # Ex: preto lacado, azul sunburst
    dial_material: Optional[str] = None      # Ex: guilloché, esmalte

    # ── Pulseira / bracelete ───────────────────────────────────
    strap_material: Optional[str] = None
    clasp_material: Optional[str] = None

    # ── Aquisição ──────────────────────────────────────────────
    acquired_from: Optional[str] = None      # Fonte (loja, ML, particular...)
    acquired_date: Optional[str] = None      # Data no formato YYYY-MM-DD
    price_brl: Optional[float] = None        # Preço pago em reais
    price_original: Optional[float] = None   # Preço na moeda original
    price_currency: str = "BRL"
    has_box: bool = False
    has_papers: bool = False

    # ── Condição e conservação ─────────────────────────────────
    # Escala: mint | excellent | good | fair | poor
    condition: Optional[str] = None
    last_service: Optional[str] = None       # Data da última revisão
    next_service: Optional[str] = None       # Data estimada da próxima revisão
    is_insured: bool = False

    # ── Pessoal ────────────────────────────────────────────────
    personal_rating: Optional[int] = None    # 1 a 5 estrelas
    is_for_sale: bool = False
    notes: Optional[str] = None              # Observações livres

    # ── Metadados ──────────────────────────────────────────────
    created_at: Optional[str] = None         # Preenchido automaticamente pelo banco


# Valores fixos usados nos dropdowns da interface
MOVEMENT_TYPES = ["", "automatic", "manual", "quartz", "solar", "spring_drive", "other"]
MOVEMENT_ORIGINS = ["", "in-house", "ebauche", "unknown"]
CRYSTAL_TYPES = ["", "sapphire", "mineral", "acrylic", "hesalite", "other"]
CONDITIONS = ["", "mint", "excellent", "good", "fair", "poor"]
STATUSES = ["owned", "wishlist", "sold", "loaned"]
CURRENCIES = ["BRL", "USD", "EUR", "JPY", "CHF", "GBP"]
