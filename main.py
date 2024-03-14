import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

DATABASE_URL = "sqlite:///internet_shop.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('user_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('username', sqlalchemy.String(32)),
    sqlalchemy.Column('last_name', sqlalchemy.String(32)),
    sqlalchemy.Column('email', sqlalchemy.String(128)),
    sqlalchemy.Column('password', sqlalchemy.String(16))
)

products = sqlalchemy.Table(
    'products',
    metadata,
    sqlalchemy.Column('product_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('productname', sqlalchemy.String(128)),
    sqlalchemy.Column('description', sqlalchemy.String(256)),
    sqlalchemy.Column('price', sqlalchemy.Float)
)
orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('order_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.user_id')),
    sqlalchemy.Column('product_id', sqlalchemy.ForeignKey('products.product_id')),
    sqlalchemy.Column('status', sqlalchemy.String(32)),
    sqlalchemy.Column('order_date', sqlalchemy.DateTime),
)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


class UserIn(BaseModel):
    username: str = Field(..., max_length=32)
    last_name: str = Field(..., max_length=32)
    email: str = Field(..., max_length=128)
    password: str = Field(..., max_length=16)


class User(UserIn):
    user_id: int


class ProductIn(BaseModel):
    productname: str = Field(..., max_length=128)
    description: str = Field(..., max_length=256)
    price: float = Field(...)


class Product(ProductIn):
    product_id: int


class OrderIn(BaseModel):
    user_id: int
    product_id: int
    status: str = Field(..., max_length=32)
    order_date: datetime


class Order(OrderIn):
    order_id: int


@app.get('/')
async def root():
    return {'message': 'Hello, World'}


@app.post('/users/', response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(**user.model_dump())
    last_id = await database.execute(query)
    return {**user.model_dump(), 'user_id': last_id}


@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.user_id == user_id)
    return await database.fetch_one(query)


@app.put('/users/{user_id}', response_model=User)
async def reload_user(user_id: int, user: UserIn):
    query = users.update().where(users.c.user_id == user_id).values(**user.model_dump())
    await database.execute(query)
    return {**user.model_dump(), 'user_id': user_id}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    query = users.delete().where(users.c.user_id == user_id)
    await database.execute(query)
    return {'Message': f'User with id-{user_id} deleted'}


@app.post('/products/', response_model=Product)
async def create_product(product: ProductIn):
    query = products.insert().values(**product.model_dump())
    last_id = await database.execute(query)
    return {**product.model_dump(), 'product_id': last_id}


@app.get('/products/', response_model=List[Product])
async def read_products():
    query = products.select()
    return await database.fetch_all(query)


@app.get('/products/{product_id}', response_model=Product)
async def read_product(product_id: int):
    query = products.select().where(products.c.product_id == product_id)
    return await database.fetch_one(query)


@app.put('/products/{product_id}', response_model=Product)
async def reload_product(product_id: int, product: ProductIn):
    query = products.update().where(products.c.product_id == product_id).values(**product.model_dump())
    await database.execute(query)
    return {**product.model_dump(), 'product_id': product_id}


@app.delete('/products/{product_id}')
async def delete_product(product_id: int):
    query = products.delete().where(products.c.product_id == product_id)
    await database.execute(query)
    return {'Message': f'Product with id-{product_id} deleted'}


@app.post('/orders/', response_model=Order)
async def create_order(order: OrderIn):
    order.order_date = datetime.now()
    query = orders.insert().values(**order.model_dump())
    last_id = await database.execute(query)
    return {**order.model_dump(), 'order_id': last_id}


@app.get("/orders/", response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    query = orders.select().where(orders.c.order_id == order_id)
    return await database.fetch_one(query)


@app.put("/orders/{order_id}", response_model=Order)
async def reload_order(order_id: int, order: OrderIn):
    query = orders.update().where(orders.c.order_id == order_id).values(**order.model_dump())
    await database.execute(query)
    return {**order.model_dump(), "order_id": order_id}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.order_id == order_id)
    await database.execute(query)
    return {'Message': f"Order with id-{order_id} deleted"}


