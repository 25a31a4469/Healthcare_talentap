import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models import MedicineCatalogue, BrandMapping
from backend.app.reference_data import seed_reference_data
from backend.app.services.resolver import MedicineResolver

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_reference_data(session)
    yield session
    session.close()

def test_exact_generic_resolution(db_session):
    resolver = MedicineResolver(db_session)
    res = resolver.resolve("metformin")
    assert res.resolved_generic == "metformin"
    assert res.match_method == "exact_generic"
    assert res.match_score == 100.0
    assert res.is_ambiguous is False
    assert "metformin" in res.active_ingredients

def test_exact_brand_resolution(db_session):
    resolver = MedicineResolver(db_session)
    res = resolver.resolve("Coumadin")
    assert res.resolved_generic == "warfarin"
    assert res.brand_name == "Coumadin"
    assert res.match_method == "exact_brand"
    assert res.match_score == 100.0

def test_fuzzy_misspelling_resolution(db_session):
    resolver = MedicineResolver(db_session)
    # Severe typo
    res = resolver.resolve("Metformn")
    assert res.resolved_generic == "metformin"
    assert res.match_score > 80.0

def test_brand_with_dosage_resolution(db_session):
    resolver = MedicineResolver(db_session)
    res = resolver.resolve("Diflucan 200mg")
    assert res.resolved_generic == "fluconazole"
    assert res.match_score >= 90.0

def test_uncatalogued_medicine_handling(db_session):
    resolver = MedicineResolver(db_session)
    res = resolver.resolve("TotallyUnknownDrugXYZ")
    assert res.match_method == "unresolved"
    assert res.resolved_generic is None
    assert res.requires_human_review is True
