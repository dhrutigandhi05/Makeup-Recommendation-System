from sqlalchemy.orm import Session
from app.dbModels import Product

def getAvailableProducts(db: Session, maxPrice: float):
    return (
        db.query(Product)
        .filter(Product.price.isnot(None))
        .filter(Product.price > 0)
        .filter(Product.price <= maxPrice)
        .all()
    )