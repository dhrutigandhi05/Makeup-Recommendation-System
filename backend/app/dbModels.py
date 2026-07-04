from sqlalchemy import Boolean, Column, Float, Integer, String, Text
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    source_product_id = Column(String(100), nullable=False, index=True)
    product_name = Column(String(500), nullable=False)
    brand_name = Column(String(300), nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(20), nullable=True)
    image_link = Column(Text, nullable=True)
    product_url = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    highlights = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    category = Column(String(300), nullable=True)
    product_type = Column(String(300), nullable=True)


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    source_product_id = Column(String(100), nullable=False, index=True)
    rating = Column(Float, nullable=True)
    is_recommended = Column(Boolean, nullable=True)
    target_recommended = Column(Integer, nullable=True)
    skin_type = Column(String(100), nullable=True)
    skin_tone = Column(String(100), nullable=True)
    review_title = Column(Text, nullable=True)
    review_text = Column(Text, nullable=True)
    combined_text = Column(Text, nullable=True)