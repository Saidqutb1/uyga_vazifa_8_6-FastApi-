from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


def init_db():
    db: Session = SessionLocal()

    initial_user = crud.get_user_by_username(db, username="admin")
    if not initial_user:
        admin_user = schemas.UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        crud.create_user(db, user=admin_user)
        print("Created initial admin user with username 'admin' and password 'admin123'")

    if not crud.get_product(db, product_id=1):
        initial_products = [
            schemas.ProductCreate(name="Product 1", description="Description 1", price=10.0, quantity=100),
            schemas.ProductCreate(name="Product 2", description="Description 2", price=20.0, quantity=200),
            schemas.ProductCreate(name="Product 3", description="Description 3", price=30.0, quantity=300),
        ]
        for product in initial_products:
            crud.create_product(db=db, product=product)
        print("Added initial products")

    db.close()


if __name__ == "__main__":
    init_db()
