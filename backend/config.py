class Config:
    SECRET_KEY = "goodyear-secure-key"
    SQLALCHEMY_DATABASE_URI = "postgresql://vulnuser:vulnpass@db/vulndb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "redis"
